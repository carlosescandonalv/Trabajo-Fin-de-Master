import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from mplsoccer.pitch import Pitch, VerticalPitch
from mplsoccer import lines
from scipy.ndimage import gaussian_filter
import datetime
from mplsoccer import FontManager
import matplotlib.font_manager
from IPython.core.display import HTML
import matplotlib as mpl
from PIL import Image
from mplsoccer import VerticalPitch, add_image, FontManager
import os
import plotly.graph_objects as go
import plotly.express as px
import json 
def create_connection():
    conn = psycopg2.connect(
            user = "postgres.ztcwzgcdqaecducpznat",
            password= 'PTNRNRWooVK0bmvr',
            host="aws-0-eu-west-2.pooler.supabase.com",
            port="6543",
            database ="postgres"
        )
    return conn

def season_list():
    conn = create_connection() 
    cursor = conn.cursor()
    cursor.execute("""
       SELECT season_id FROM season
        """)
    records = cursor.fetchall()
    seasons = [season[0] for season in records]
    return seasons

def team_list(season):    # Create a list with all the teams avilable
    conn = create_connection() 
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT participants FROM season
        WHERE season_id = '{season}'
        """)
    records = cursor.fetchall()
    teamslist = json.loads(records[0][0])
    if "Atletico Madrid" in teamslist:
        teamslist[teamslist.index("Atletico Madrid")] = "Atletico"
    return teamslist

def table_extraction(season):    # Classification Dataframe extraction (W,D,L, Points)
    conn = create_connection() 
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT * FROM matches WHERE season = '{season}'
        """)
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    team_stats = {}
    def initialize_team(team_name):
        return {
            'matches_won': 0,
            'matches_drawn': 0,
            'matches_lost': 0,
            'goals_scored': 0,
            'goals_received': 0
        }
    # Update the team statistics based on match outcomes
    for index, row in df.iterrows():
        home_team = row['home']
        away_team = row['away']
        goals_h = row['goals_h']
        goals_a = row['goals_a']
        
        if home_team not in team_stats:
            team_stats[home_team] = initialize_team(home_team)
        if away_team not in team_stats:
            team_stats[away_team] = initialize_team(away_team)
        
        team_stats[home_team]['goals_scored'] += goals_h
        team_stats[home_team]['goals_received'] += goals_a
        team_stats[away_team]['goals_scored'] += goals_a
        team_stats[away_team]['goals_received'] += goals_h
        
        if goals_h > goals_a:
            team_stats[home_team]['matches_won'] += 1
            team_stats[away_team]['matches_lost'] += 1
        elif goals_h < goals_a:
            team_stats[away_team]['matches_won'] += 1
            team_stats[home_team]['matches_lost'] += 1
        else:
            team_stats[home_team]['matches_drawn'] += 1
            team_stats[away_team]['matches_drawn'] += 1

    # Convert the team_stats dictionary to a DataFrame
    team_stats_df = pd.DataFrame.from_dict(team_stats, orient='index')

    team_stats_df['points'] = team_stats_df['matches_won']*3+team_stats_df['matches_drawn']
    team_stats_df = team_stats_df.sort_values(by='points', ascending=True)
    team_stats_df = team_stats_df.reset_index().rename(columns={'index': 'team'})

    return team_stats_df

def table_plot(df):
    fig = px.bar(df, x='team', y='points', title='Points of Each Team', 
                labels={'team': 'Teams', 'points': 'Points'}, 
                color='points', 
                color_continuous_scale='Blues')

    fig.update_layout(xaxis_tickangle=-45)
    return fig
 
def color_rows(row):    # Color the rows of the team classification table
    if row.name < 5:
        return ['background-color: #9CFC97']*len(row) 
    elif row.name < 7:
        return ['background-color: #5BC0EB']*len(row)
    elif row.name >17:
        return ['background-color: #D37773']*len(row)



def goals_development(team,season):   # Goals development plot for a spcefic team
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT * from matches
       WHERE matches.home = '{team}' OR matches.away = '{team}'
       AND matches.season = '{season}'      
        """)
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    
    df['match_date'] = pd.to_datetime(df['match_date'])
    df = df.sort_values('match_date')
    unique_dates = df['match_date'].unique()
    date_to_label = {date: f'J{i+1}' for i, date in enumerate(unique_dates)}
    df['match_label'] = df['match_date'].map(date_to_label)

    for index, row in df.iterrows():
        if row['home'] == team:
            df.at[index, 'goals_scored'] = row['goals_h']
            df.at[index, 'goals_conceded'] = row['goals_a']
        elif row['away'] == team:
            df.at[index, 'goals_scored'] = row['goals_a']
            df.at[index, 'goals_conceded'] = row['goals_h']
    df = df.sort_values('match_date')
    goals_scored = int(df['goals_scored'].sum())
    goals_conceded = int(df['goals_conceded'].sum())
    # Create the Plotly line chart
    fig = go.Figure()

    # Add trace for goals scored
    fig.add_trace(go.Scatter(
        x=df['match_label'],
        y=df['goals_scored'],
        mode='lines+markers',
        name='Goals Scored',
        line=dict(color='blue'),
        fill='tozeroy',  # Fill the area below the line to the x-axis
        fillcolor='rgba(0, 0, 255, 0.2)'

    ))

    # Add trace for goals conceded
    fig.add_trace(go.Scatter(
        x=df['match_label'],
        y=df['goals_conceded'],
        mode='lines+markers',
        name='Goals Conceded',
        line=dict(color='red'),
        fill='tozeroy',  # Fill the area below the line to the x-axis
        fillcolor='rgba(255, 0, 0, 0.2)'
    ))

    # Update layout
    fig.update_layout(
        title=f'Goals Scored and Conceded by {team} Each Match',
        xaxis_title='Match Date',
        yaxis_title='Goals',
        hovermode='x unified',
        plot_bgcolor = 'white'
    )

    return fig,goals_scored,goals_conceded

def determine_outcome(row, variable_team):
        if row['home_team'] == variable_team:
            if row['goals_home'] > row['goals_away']:
                return 'Win'
            elif row['goals_home'] < row['goals_away']:
                return 'Lose'
            else:
                return 'Draw'
        elif row['away_team'] == variable_team:
            if row['goals_away'] > row['goals_home']:
                return 'Win'
            elif row['goals_away'] < row['goals_home']:
                return 'Lose'
            else:
                return 'Draw'
        else:
            return 'N/A'  #
        
def pass_development(team,season):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT match_event.*, teams.name AS team_name,matches.match_date AS match_date, 
       matches.home AS home_team, matches.away AS away_team, matches.goals_h AS goals_home, matches.goals_a AS goals_away
       FROM match_event
       JOIN teams ON match_event.team_id = teams.team_id
       JOIN matches ON match_event.match_id = matches.match_id
       WHERE teams.name = '{team}' AND type = 'Pass'AND matches.season = '{season}'
        """)
    records = cursor.fetchall()
    
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    df = df[df['outcome'] =='Successful']

    df['match_outcome'] = df.apply(lambda row: determine_outcome(row, team), axis=1)

    df['match_date'] = pd.to_datetime(df['match_date'])
    df['match_result'] = df.apply(lambda row: f"{row['home_team']} ({row['goals_home']}) - ({row['goals_away']}) {row['away_team']}", axis=1)

    passes_df = df.sort_values('match_date')
    unique_dates = passes_df['match_date'].unique()
    date_to_label = {date: f'J{i+1}' for i, date in enumerate(unique_dates)}


    grouped = passes_df.groupby('match_date').agg({'type': 'size', 'match_result': 'first','match_outcome':'first'}).reset_index()
    grouped['label'] = grouped['match_result'].astype(str) + ' - ' + grouped['type'].astype(str) + ' Passes'
    
    # Assign colors based on outcome
    color_map = {'Win': '#8ac926', 'Lose': '#ff595e', 'Draw': '#ffca3a'}
    grouped['color'] = grouped['match_outcome'].map(color_map)

    # Create the Plotly bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=[date_to_label[date] for date in grouped['match_date']],
            y=grouped['type'],
            text=grouped['label'],  # Custom labels
            textposition='none',    # Hide text on bars
            hovertemplate='%{text}<extra></extra>',  # Show text on hover
            marker_color=grouped['color']  # Set bar color based on outcome
        )
    ])

    # Update layout
    fig.update_layout(
        title=f'Number of Passes of {team} per Match Date',
        xaxis_title='Match Date',
        yaxis_title='Number of Passes',
        plot_bgcolor = "white"
    )

    return fig


def get_team_info(team):
  team_data = [
    {'Team': 'Deportivo Alaves', 'Crest': 'Alaves.png', 'Color': '#0761AF', 'Color2':'white'},
    {'Team': 'Almeria', 'Crest': 'Almería.png', 'Color': '#ee1119','Color2':'white'},
    {'Team': 'Athletic Club', 'Crest': 'Athletic.png', 'Color': '#EE2523','Color2':'white'},
    {'Team': 'Atletico', 'Crest': 'atletico.png', 'Color': '#CB3524','Color2':'white'},
    {'Team': 'Barcelona', 'Crest': 'Barcelona.png', 'Color': '#A50044','Color2':'#EDBB00'},
    {'Team': 'Real Betis', 'Crest': 'Betis.png', 'Color': '#0BB363','Color2':'white'},
    {'Team': 'Cadiz', 'Crest': 'Cadiz.png', 'Color': '#ffe500','Color2':'blue'},
    {'Team': 'Celta Vigo', 'Crest': 'Celta.png', 'Color': '#8AC3EE','Color2':'#E5254E'},
    {'Team': 'Getafe', 'Crest': 'Getafe.png', 'Color': '#004fa3', 'Color2':'white'},
    {'Team': 'Girona', 'Crest': 'Girona.png', 'Color': '#cd2534','Color2':'#ffee00'},
    {'Team': 'Granada', 'Crest': 'Granada.png', 'Color': '#A61B2B','Color2':'white'},
    {'Team': 'Las Palmas', 'Crest': 'LasPalmas.png', 'Color': '#ffe400','Color2':'blue'},
    {'Team': 'Mallorca', 'Crest': 'Mallorca.png', 'Color': '#E20613','Color2':'yellow'},
    {'Team': 'Osasuna', 'Crest': 'Osasuna.png', 'Color': '#D91A21','Color2':'#0A346F'},
    {'Team': 'Rayo Vallecano', 'Crest': 'RayoVallecano.png', 'Color': '#ff0000','Color2':'white'},
    {'Team': 'Real Madrid', 'Crest': 'RealMadrid.png', 'Color': 'white','Color2':'blue'},
    {'Team': 'Real Sociedad', 'Crest': 'RealSociedad.png', 'Color': '#0067B1','Color2':'white'},
    {'Team': 'Sevilla', 'Crest': 'Sevilla.png', 'Color': '#F43333','Color2':'white'},
    {'Team': 'Valencia', 'Crest': 'Valencia.png', 'Color': '#D18816','Color2':'black'},
    {'Team': 'Villarreal', 'Crest': 'Villarreal.png', 'Color': '#FFE667','Color2':'#005187'}
    ]
  team_info_a = next((item for item in team_data if item['Team'] == team), None)
  crest_filename_a = team_info_a['Crest']
  teamcrest_path_a = os.path.join('imgs_app/LaLigaCrests', crest_filename_a)
  crest_img = Image.open(teamcrest_path_a)
  crest_img = crest_img.resize((150, 150),Image.ADAPTIVE)

  color1= next((item['Color'] for item in team_data if item['Team'] == team), None)
  color2= next((item['Color2'] for item in team_data if item['Team'] == team), None)
  return crest_img,color1,color2

def get_team_event_xi(team,season):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT match_event.*, matches.season AS season, players.name AS player_name, players.shirt_no AS number,
                   teams.name AS team_name FROM match_event
        JOIN players ON match_event.player_id = players.player_id
        JOIN teams ON match_event.team_id = teams.team_id
        JOIN matches ON match_event.match_id = matches.match_id
        WHERE teams.name = '{team}' AND matches.season = '{season}'
        """)
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    return df


def get_xi(df):
  match_ids = df['match_id'].unique()
  total_player_minutes = {}
  player_numbers = {}
  for match_id in match_ids:
      match_events = df[df['match_id'] == match_id]
      max_minute = 90
      player_minutes = {}

      for index, row in match_events.iterrows():
          player = row['player_name']
          minute = row['minute']
          event_type = row['type']
          player_number = row['number']

          if player not in player_numbers:
              player_numbers[player] = player_number
          if event_type == 'SubstitutionOn':
              if player not in player_minutes:
                  player_minutes[player] = max_minute - minute
              else:
                  player_minutes[player] += max_minute - minute
          elif event_type == 'SubstitutionOff':
              if player not in player_minutes:
                  player_minutes[player] = minute
              else:
                  player_minutes[player] += minute

      all_players = set(match_events['player_name'].unique())
      for player in all_players:
          if player not in player_minutes:
              player_minutes[player] = max_minute

      for player, minutes in player_minutes.items():
          if player in total_player_minutes:
              total_player_minutes[player] += minutes
          else:
              total_player_minutes[player] = minutes
  season_minutes_df = pd.DataFrame(total_player_minutes.items(), columns=['player_name', 'total_minutes_played'])
  season_minutes_df['player_number'] = season_minutes_df['player_name'].map(player_numbers)

  sorted_minutes_df = season_minutes_df.sort_values(by='total_minutes_played',ascending=False)
  top_eleven_players = sorted_minutes_df.head(11)
  return top_eleven_players,sorted_minutes_df


def draw_initial_xi(xi_df,team,c1,c2):
    pitch = VerticalPitch(pitch_color='#1B2632', line_color='#EEE9DF', pitch_type='opta',linewidth=0.5,goal_type='box')
    fig, ax = pitch.draw(figsize=(12, 6))
    fig.set_facecolor('#1B2632')
    ax.set_facecolor('#1B2632')
    nodes = pitch.scatter(xi_df.x,xi_df.y,
                            ax=ax,
                            s=420, color=c1,edgecolors=c2,linewidth=1,zorder=1)


    for index, row in xi_df.iterrows():
        pitch.annotate(row.player_number, xy=(row.x,row.y), c=c2,zorder=4,
                    va='center', ha='center', size=9,ax=ax, fontweight= 'bold')
        words = row.player_name.split()
        if len(words)>1:
            first_letters = ''.join(word[0] for word in words[:-1])
            row.player_name= f"{first_letters}.{words[-1]}"
        if row.x > np.mean(xi_df['x']):
            pitch.annotate(row.player_name, xy=(row.x+4,row.y), c='#EEE9DF',zorder=4,
                        va='center', ha='center', size=10,ax=ax, fontweight= 'bold')

        else:
            pitch.annotate(row.player_name, xy=(row.x-4,row.y), c='#EEE9DF',zorder=4,
                        va='center', ha='center', size=10,ax=ax, fontweight= 'bold')

    plt.title(f'{team} most frequent XI',loc='center', fontweight='bold',color='white')

    return fig

##### MATCHES

def match_info(home,away,season):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT match_event.*, players.name AS player_name, teams.name AS team_name
    FROM match_event
    JOIN matches ON match_event.match_id = matches.match_id
    JOIN players ON match_event.player_id = players.player_id
    JOIN teams ON match_event.team_id = teams.team_id
    WHERE matches.home = '{home}' AND matches.away = '{away}'
    AND matches.season = '{season}'
    """)
    records = cursor.fetchall()
    xT = pd.read_csv("imgs_app/xT_Grid.csv")
    xT = np.array(xT)
    xT_rows, xT_cols = xT.shape
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    df_pass = df.loc[(df['type']=="Pass") & (df['outcome']=='Successful')].reset_index()
    df_pass['x1_bin'] = pd.cut(df_pass['x'], bins=xT_cols, labels=False)
    df_pass['y1_bin'] = pd.cut(df_pass['y'], bins=xT_rows, labels=False)
    df_pass['x2_bin'] = pd.cut(df_pass['end_x'], bins=xT_cols, labels=False)
    df_pass['y2_bin'] = pd.cut(df_pass['end_y'], bins=xT_rows, labels=False)

    df_pass['start_zone_value'] = df_pass[['x1_bin', 'y1_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    df_pass['end_zone_value'] = df_pass[['x2_bin', 'y2_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    df_pass['xT'] = df_pass['end_zone_value'] - df_pass['start_zone_value']
    game_totals = df_pass.groupby('player_name').agg({'xT':['sum']})
    game_totals.sort_values(by=('xT','sum'),ascending=False)
    

    pass_data_1 = df[df['team_name']==home].reset_index()
    pass_data_2 = df[df['team_name']==away].reset_index()

    return pass_data_1,pass_data_2,df_pass

def pass_network(df,df_pass,team,opponent,minimum,color1,color2,team_img):
  team = team
  df['passer'] = df['player_name']
  df['recipient'] = df['player_name'].shift(-1)

  team_against = opponent
  subs1 = df[df['team_name']==team]
  subs1 = subs1[subs1['type']=='SubstitutionOff']
  firstSub = subs1['minute']
  firstSub=firstSub.min()
  succesful = df[df['minute']<firstSub]
  average_locations = succesful.groupby('passer').agg({'x':['mean'],'y':['mean','count']})

  # x Threat summatory team (highest xT of the whole match)
  x_threat = df_pass[df_pass['team_name']==team]
  x_threat = x_threat.groupby('player_name').agg({'xT':['sum']})
  x_threat.columns=['sum']
  x_threat = x_threat.sort_values(by='sum',ascending=False)
  highest_xT = x_threat.iloc[0]

  highest_xT_name = highest_xT.name
  highest_xT_value = round(highest_xT['sum'],2)

  average_locations.columns=['x','y','count']
  average_locations = average_locations.sort_values(by='count', ascending=False)


  # Calculate highest nº of passes of the match
  passer_df =  df.groupby('passer').agg({'x':['mean'],'y':['mean','count']})
  passer_df.columns=['x','y','count']

  passer_df = passer_df.sort_values(by='count', ascending=False)

  highest_passer = passer_df.iloc[0]
  highest_passer_name = highest_passer.name
  highest_passer_passes = int(highest_passer['count'])

  # Pass between calculation
  pass_between = succesful.groupby(['passer','recipient']).id.count().reset_index()
  pass_between.rename({'id':'pass_count'},axis='columns',inplace=True)

  pass_between = pass_between.merge(average_locations, left_on='passer',right_index=True)
  pass_between = pass_between.merge(average_locations, left_on='recipient',right_index=True,suffixes=['','_end'])

  pass_between = pass_between[pass_between['pass_count']>minimum]


  # Plot the pitch
  pitch = VerticalPitch(pitch_color='#1B2632', line_color='#EEE9DF', pitch_type='opta',linewidth=0.5,goal_type='box')
  fig, ax = pitch.draw(figsize=(12, 6))
  fig.set_facecolor('#1B2632')
  ax.set_facecolor('#1B2632')
  pitch.annotate(f"0-{firstSub} \'", xy=(96,50), c='white',zorder=2,
                    va='center', ha='center', size=10,ax=ax)

  arrows = pitch.arrows(pass_between.x,pass_between.y,pass_between.x_end,pass_between.y_end,
                        ax=ax, lw=3,
                        width=3,headwidth=3,headlength=4,
                        color='#B2FFA9',zorder=1,alpha=(pass_between.pass_count / pass_between.pass_count.max()))

  x_threat = df_pass[(df_pass['team_name']==team) & (df_pass['minute']<firstSub)]
  x_threat = x_threat.groupby('player_name').agg({'xT':['sum']})
  x_threat.columns=['sum']

  average_locations = average_locations.merge(x_threat, left_on='passer', right_index=True)

  nodes = pitch.scatter(average_locations.x,average_locations.y,
                        ax=ax,
                        s=200+(800*average_locations['sum']), color=color1,edgecolors=color2,linewidth=1,zorder=1)

  plt.text(-42, 67,f'{highest_passer_name}', fontsize=14, ha='center', va='center',color='white',fontfamily="Liberation Sans Narrow")
  plt.text(-15, 72,f'HIGHEST Nº OF PASSES: ', fontsize=14, ha='left', va='center',color='white',fontfamily="Liberation Sans Narrow",fontweight='bold')
  plt.text(-42, 50,f'{highest_xT_name} ({highest_xT_value})', fontsize=14, ha='center', va='center',color='white',fontproperties="Liberation Sans Narrow")
  plt.text(-15, 55,f'HIGHEST xT (via pass):', fontsize=14, ha='left', va='center',color='white',fontfamily="Liberation Sans Narrow",fontweight='bold')

  ax.set_xlim(105, -60)

  mSize = [0.05,0.20,0.6,0.8]
  mSizeS = [700 * i for i in mSize]
  mx = [-28,-33,-41,-51]
  my = [35,35,35,35]

  # Plot circles (xT) and arrow
  plt.scatter(mx, my, s=mSizeS, facecolors=color1, edgecolor=color2)
  arrow_x = -25  # X-coordinate for the arrow
  arrow_y = 30  # Y-coordinate for the arrow
  arrow = mpl.patches.FancyArrowPatch((arrow_x, arrow_y), (arrow_x-34, arrow_y), color='white',arrowstyle='-|>', mutation_scale=12, lw=1)
  plt.text(-38, 28, 'xT', va='center', fontfamily="Liberation Sans Narrow", fontsize=12,fontweight='bold',color='white')
  ax.add_patch(arrow)

  # Plot arrows intensity
  arrow = mpl.patches.FancyArrowPatch((-29, 15), (-38, 24), color='#B2FFA9',arrowstyle='-|>', mutation_scale=12, lw=4,alpha=0.2)
  ax.add_patch(arrow)
  arrow = mpl.patches.FancyArrowPatch((-38, 15), (-47, 24), color='#B2FFA9',arrowstyle='-|>', mutation_scale=12, lw=4,alpha=0.6)
  ax.add_patch(arrow)
  arrow = mpl.patches.FancyArrowPatch((-47, 15), (-56, 24), color='#B2FFA9',arrowstyle='-|>', mutation_scale=12, lw=4,alpha=1)
  ax.add_patch(arrow)

  arrow = mpl.patches.FancyArrowPatch((-25, 12), (-59, 12), color='white',arrowstyle='-|>', mutation_scale=12, lw=1,alpha=1)
  plt.text(-28, 10, 'Nº of passes', va='center', fontfamily="Liberation Sans Narrow", fontsize=12,fontweight='bold',color='white')
  ax.add_patch(arrow)

  # plot title
  plt.title(f'Pass network {team} against {team_against}',loc='center', fontweight='bold',color='white')
  plt.text(78, -5,f'*minimum 5 passes to be included', fontsize=12, ha='left', va='center',color='white',fontfamily="Liberation Sans Narrow")
  average_locations.reset_index(inplace=True)

  # Plot images
  ax3 = add_image(team_img, fig, left=0.64, bottom=0.75, width=0.075, interpolation='hanning')

  # plot player names
  for index, row in average_locations.iterrows():
    words = row.passer.split()
    if len(words)>1:
        first_letters = ''.join(word[0] for word in words[:-1])
        row.passer= f"{first_letters}.{words[-1]}"
    if row.x > np.mean(average_locations['x']):
     pitch.annotate(row.passer, xy=(row.x+4,row.y), c='#EEE9DF',zorder=4,
                    va='center', ha='center', size=9,ax=ax, fontweight= 'bold')
    else:
     pitch.annotate(row.passer, xy=(row.x-4,row.y), c='#EEE9DF',zorder=4,
                    va='center', ha='center', size=9,ax=ax, fontweight= 'bold')

  return fig



##### PLAYERS INFO
def search_players(team,season):
    conn = create_connection() 
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT DISTINCT players.name FROM match_event
    JOIN players ON match_event.player_id = players.player_id
    JOIN matches ON match_event.match_id = matches.match_id
    JOIN teams ON match_event.team_id = teams.team_id
    WHERE teams.name = '{team}' AND matches.season = '{season}'
    """)
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    return df['name'].to_list()