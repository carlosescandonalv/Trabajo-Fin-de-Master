import database_access as db
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
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap


def match_report(home,away,season,home_img,away_img,color_home,color_away):
    conn = db.create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT match_event.*, players.name AS player_name, teams.name AS team_name,
        home AS team_home, away AS team_away, goals_h AS goals_home, goals_a AS goals_away,
        match_date AS date
        FROM match_event
        JOIN matches ON match_event.match_id = matches.match_id
        JOIN players ON match_event.player_id = players.player_id
        JOIN teams ON match_event.team_id = teams.team_id
        WHERE matches.home = '{home}' AND matches.away = '{away}'
        AND matches.season = '{season}'
    """)
    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])

    def make_html(fontname):
        return "<p>{font}: <span style='font-family:{font}; font-size: 24px;'>{font}</p>".format(font=fontname)

    code = "\n".join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])

    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/montserratalternates/MontserratAlternates-SemiBold.ttf')

    pitch = Pitch(pitch_type='opta',half=False, line_color='#EEE9DF',pitch_color='#182632', goal_type='box', linewidth=0.5)
                        #axis=True, label=True, tick=True)
    fig, ax = pitch.draw(figsize=(10, 5.5))
    fig.set_facecolor('#182632')

    team_home = df.team_home.unique()[0]
    team_away = df.team_away.unique()[0]

    shots = df[df['is_shot']==True]
    home_shots = shots[(shots['team_name'] == shots['team_home'])]
    away_shots = shots[(shots['team_name'] == shots['team_away'])]

    for index,row in home_shots.iterrows():
        color_choice = 'red'
        size_c = 50
        alpha_c = 0.5
        edge_c = 'none'
        if row['type'] == 'Goal':
            color_choice = '#7AF47A'
            size_c= 90
            alpha_c = 0.9
            edge_c = '#7AF47A'
            plt.plot([100-row['x'], 0], [100-row['y'],100-row['goal_mouth_y']], color='#EEE9DF', linestyle='--', linewidth=0.3, zorder=3)
            #plt.plot([row['y'], row['goal_mouth_y']], [row['x'],100], color='#EEE9DF', linestyle='--', linewidth=0.3, zorder=1)
        plt.scatter(100-row['x'],100-row['y'],color = color_choice,s=size_c,edgecolor=edge_c,alpha=alpha_c,zorder=4)


    for index,row in away_shots.iterrows():
        color_choice = 'red'
        size_c = 50
        alpha_c = 0.5
        edge_c = 'none'
        if row['type'] == 'Goal':
            color_choice = '#7AF47A'
            size_c= 90
            alpha_c = 0.9
            edge_c = '#7AF47A'
            plt.plot([row['x'], 100], [row['y'],row['goal_mouth_y']], color='#EEE9DF', linestyle='--', linewidth=0.3, zorder=3)

        plt.scatter(row['x'],row['y'],color = color_choice,s=size_c,edgecolor=edge_c,alpha=alpha_c,zorder=4)



    # Plot images
    date = df.date.unique()[0].strftime('%Y-%m-%d')
    ax3 = add_image(home_img, fig, left=0.16, bottom=0.85, width=0.075, interpolation='hanning',zorder=2)
    ax4 = add_image(away_img, fig, left=0.77, bottom=0.85, width=0.075, interpolation='hanning',zorder=2)
    plt.text(-550,110,f"La Liga | {date}", va='center', ha='center', fontsize=14,color='#C9C1B1',fontfamily="Liberation Sans Narrow")
    title = fig.suptitle(f"{team_home} vs {team_away}", x=0.5, y=0.93, va='center', ha='center', fontsize=22,fontweight='bold',fontfamily="Liberation Sans Narrow",color='#EEE9DF')


    home_on_target = shots[(shots['team_name'] == shots['team_home']) & 
                        (shots['type'].isin(['SavedShot', 'Goal']))]


    away_on_target = shots[(shots['team_name'] == shots['team_away']) & 
                        (shots['type'].isin(['SavedShot', 'Goal']))]

    passes = df[df['type']=='Pass']
    home_passes = passes[(passes['team_name'] == passes['team_home'])]
    home_successful_passes = home_passes[home_passes['outcome'] == 'Successful'].shape[0]
    home_total_passes = home_passes.shape[0]
    home_pass_accuracy = round((home_successful_passes / home_total_passes) * 100,1) if home_total_passes > 0 else 0

    away_passes = passes[(passes['team_name'] == passes['team_away'])]
    away_successful_passes = away_passes[away_passes['outcome'] == 'Successful'].shape[0]
    away_total_passes = away_passes.shape[0]
    away_pass_accuracy = round((away_successful_passes / away_total_passes) * 100,1) if away_total_passes > 0 else 0

    home_df = df[df['team_name']==team_home]
    home_bc = 0
    for qualifiers in home_df['qualifiers']:
        if any(qualifier.get('type', {}).get('displayName') == 'BigChance' for qualifier in qualifiers):
            home_bc += 1

    away_df = df[df['team_name']==team_away]
    away_bc = 0
    for qualifiers in away_df['qualifiers']:
        if any(qualifier.get('type', {}).get('displayName') == 'BigChance' for qualifier in qualifiers):
            away_bc += 1

    cards = df[df['type']=='Card']
    home_cards = cards[cards['team_name'] == team_home]
    away_cards = cards[cards['team_name'] == team_away]


    # DATA HOME
    goals_h = df.goals_home.unique()[0]
    shot_h = home_shots.shape[0]
    on_target_h = home_on_target.shape[0]
    passes_h = f"{home_successful_passes} ({home_pass_accuracy}%)"
    big_chances_h = home_bc
    cards_h = home_cards.shape[0]

    # DATA AWAY
    goals_a = df.goals_away.unique()[0]
    shot_a = away_shots.shape[0]
    on_target_a = away_on_target.shape[0]
    passes_a = f"{away_successful_passes} ({away_pass_accuracy}%)"
    big_chances_a = away_bc
    cards_a = away_cards.shape[0]

    color_select= color_home
    color_select1= color_away


    name_color = 'black'
    plt.text(-810, 325,f'{goals_h}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-300, 325,f'{goals_a}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-600, 325,'Goals ', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 411,f'{big_chances_h}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-300, 411,f'{big_chances_a}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-630, 411,f'Big Chances', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 496,f'{shot_h}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-320, 496,f'{shot_a}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-600, 496,f'Shots', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 576,f'{on_target_h}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-320, 576,f'{on_target_a}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-620, 576,f'On Target', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 652,f'{home_successful_passes}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-380, 652,f'{away_successful_passes}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-600, 652,f'Passes', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 732,f'{home_pass_accuracy}%', fontsize=18, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-380, 732,f'{away_pass_accuracy}%', fontsize=18, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-635, 732,f'Pass Accuracy', fontsize=16, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)

    plt.text(-810, 812,f'{cards_h}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-300, 812,f'{cards_a}', fontsize=20, ha='left', va='center',fontproperties=fm_rubik.prop,color='white')
    plt.text(-590, 812,f'Cards', fontsize=18, ha='left', va='center',fontfamily="Liberation Sans Narrow",color=name_color)


    total_g= goals_h+goals_a
    length_h = (goals_h/total_g)*42
    rec1 = mpl.patches.Rectangle((28,76),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec2 = mpl.patches.Rectangle((28+length_h,76), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec1)
    ax.add_patch(rec2)

    total_bc= big_chances_h+big_chances_a
    length_h = (big_chances_h/total_bc)*40
    rec3 = mpl.patches.Rectangle((28,66.5),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec4 = mpl.patches.Rectangle((28+length_h,66.5), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec3)
    ax.add_patch(rec4)

    total_against= shot_h+shot_a
    length_h = (shot_h/total_against)*40
    rec5 = mpl.patches.Rectangle((28,57),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec6 = mpl.patches.Rectangle((28+length_h,57), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec5)
    ax.add_patch(rec6)

    total_against= on_target_h+on_target_a
    length_h = (on_target_h/total_against)*40
    rec7 = mpl.patches.Rectangle((28,48),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec8 = mpl.patches.Rectangle((28+length_h,48), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec7)
    ax.add_patch(rec8)

    total_against= home_successful_passes+away_successful_passes
    length_h = (home_successful_passes/total_against)*40
    rec9 = mpl.patches.Rectangle((28,39),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec10 = mpl.patches.Rectangle((28+length_h,39), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec9)
    ax.add_patch(rec10)

    total_against= home_pass_accuracy+away_pass_accuracy
    length_h = (home_pass_accuracy/total_against)*40
    rec11 = mpl.patches.Rectangle((28,30),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec12 = mpl.patches.Rectangle((28+length_h,30), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec11)
    ax.add_patch(rec12)

    total_against= cards_h+cards_a
    length_h = (cards_h/total_against)*40
    rec13 = mpl.patches.Rectangle((28,21),length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select, alpha=1, capstyle='round',joinstyle='round')
    rec14 = mpl.patches.Rectangle((28+length_h,21), 44-length_h, 6.5, linewidth=1, edgecolor='none', facecolor=color_select1, alpha=1, capstyle='round',joinstyle='round')
    ax.add_patch(rec13)
    ax.add_patch(rec14)

    return fig



def penalties_player(player,season):
    conn = db.create_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
                me.*,p.name,m.home,m.away
        FROM
                match_event me
        JOIN
                players p ON me.player_id = p.player_id
        JOIN
                matches m ON me.match_id = m.match_id
        WHERE
                me.is_shot = True AND p.name = '{player}' AND m.season = '{season}' ;
            """)

    records = cursor.fetchall()
    df = pd.DataFrame(records, columns = [desc[0] for desc in cursor.description])
    is_penalty = lambda x: any(qualifier.get('type', {}).get('displayName') == 'Penalty' for qualifier in x)
    df['is_penalty'] = df['qualifiers'].apply(is_penalty)
    penalty_rows = df[df['is_penalty']]
    df = df.loc[df['is_penalty'] == True]
    df['goal_mouth_z'] = (df['goal_mouth_z']*2.4)/39.6
    df['goal_mouth_y'] = ((df['goal_mouth_y'] - 45) / (55 - 45)) * (7.2 - 0) + 0
    # Load the image
    image_path = 'imgs_app/porteria.png'
    image = plt.imread(image_path)

    x_min, x_max, y_min, y_max = 0, 7.5, 0, 2.45
    fig, ax = plt.subplots(figsize=(32,6))

    aspect_ratio = (x_max - x_min) / (y_max - y_min)
    ax.imshow(image, extent=(x_min, x_max, y_min, y_max), aspect=aspect_ratio, alpha=0.8)


    plt.gca().invert_xaxis()
    for index,row in df.iterrows():
        color_shot = 'red'
        alpha_c=0.6
        if row['type'] =='Goal':
            color_shot = '#53FF45'
            alpha_c=0.8
        ax.scatter(row['goal_mouth_y'], row['goal_mouth_z'], marker='o', color=color_shot,s=250, label='Goals',alpha=alpha_c,edgecolor='black')

    ax.set_xlim(10, -3)
    ax.set_ylim(-0.2, 4)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    return fig