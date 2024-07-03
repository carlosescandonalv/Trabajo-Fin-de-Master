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

def create_connection():
    conn = psycopg2.connect(
            user = "postgres.ztcwzgcdqaecducpznat",
            password= 'PTNRNRWooVK0bmvr',
            host="aws-0-eu-west-2.pooler.supabase.com",
            port="6543",
            database ="postgres"
        )
    return conn

def team_list():
    conn = create_connection() 
    cursor = conn.cursor()
    cursor.execute("""
       SELECT name FROM teams
        """)
    records = cursor.fetchall()
    team_names = [team[0] for team in records]
    return team_names


def goals_development(team):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT * from matches
       WHERE matches.home = '{team}' OR matches.away = '{team}'
             
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
        
def pass_development(team):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT match_event.*, teams.name AS team_name,matches.match_date AS match_date, 
       matches.home AS home_team, matches.away AS away_team, matches.goals_h AS goals_home, matches.goals_a AS goals_away
       FROM match_event
       JOIN teams ON match_event.team_id = teams.team_id
       JOIN matches ON match_event.match_id = matches.match_id
       WHERE teams.name = '{team}' AND type = 'Pass'
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
    {'Team': 'Almeria', 'Crest': 'Almeria.png', 'Color': '#ee1119','Color2':'white'},
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

def get_team_event_xi(team):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
       SELECT match_event.*, players.name AS player_name, players.shirt_no AS number,teams.name AS team_name FROM match_event
        JOIN players ON match_event.player_id = players.player_id
        JOIN teams ON match_event.team_id = teams.team_id
        JOIN matches ON match_event.match_id = matches.match_id
        WHERE teams.name = '{team}'
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