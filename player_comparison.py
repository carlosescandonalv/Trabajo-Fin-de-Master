#from soccerplots.radar_chart import Radar
from radar_plot.function_radar import Radar
from radar_plot.utils import add_image
#from soccerplots.utils import add_image
import pandas as pd
import matplotlib.pyplot as plt
import os


std_df = pd.read_csv(f'data/Big5Leagues_Players_Standard_Stats.csv')
shoot_df = pd.read_csv(f'data/Big5Leagues_Players_shooting_Stats.csv')
gca_df = pd.read_csv(f'data/Big5Leagues_Players_gca_Stats.csv')
passing_df = pd.read_csv(f'data/Big5Leagues_Players_passing_Stats.csv')
defense_df = pd.read_csv(f'data/Big5Leagues_Players_defense_Stats.csv')
possession_df = pd.read_csv(f'data/Big5Leagues_Players_possession_Stats.csv')
miscellaneous_df = pd.read_csv(f'data/Big5Leagues_Players_misc_Stats.csv')


def forward_vs_mean(player,modo,team,match_th):
    global std_df,shoot_df,gca_df,passing_df,possession_df,miscellaneous_df
    liga = "Big7 leagues"

     # Modify possession dataframe to add a column named takons per game (equal to take_ons_won/matches)
    possession_df['take_ons_won_per90'] = possession_df['take_ons_won'] / possession_df['minutes_90s']
    possession_df['progressive_carries_per90'] = possession_df['progressive_carries'] / possession_df['minutes_90s']

    passing_df['key_passes_per90'] = passing_df['assisted_shots'] / passing_df['minutes_90s']
    miscellaneous_df['offsides_per90'] = miscellaneous_df['offsides'] / miscellaneous_df['minutes_90s']
    # FILTRAR POR DELANTEROS
    std = std_df
    shoot = shoot_df
    gca = gca_df
    passing = passing_df
    possession = possession_df
    miscellaneous = miscellaneous_df
    
    if modo == "Liga":
        player_row = std_df[(std_df['player'] == player) & (std_df['team'] == team)]
        liga = player_row['comp_level'].iloc[0]
        std = std[std['comp_level'] == liga]
        shoot = shoot[shoot['comp_level'] == liga]
        gca = gca[gca['comp_level'] == liga]
        passing = passing[passing['comp_level'] == liga]
        possession = possession[possession['comp_level'] == liga]
        miscellaneous = miscellaneous[miscellaneous['comp_level'] == liga]
    
   
    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0 = '#6CABDD'
    color1= '#00F0B5'
    std_data0 = std[(std['player'] == player) & (std['team'] == team)]
    shoot_data0 = shoot[(shoot['player'] == player) & (shoot['team'] == team)] 
    gca_data0 = gca[(gca['player'] == player) & (gca['team'] == team)]
    pass_data0 = passing[(passing['player'] == player) & (gca['team'] == team)]
    possession_data0 = possession[(possession['player'] == player )& (possession['team'] == team)]
    miscellaneous_data0 = miscellaneous[(miscellaneous['player'] == player) & (miscellaneous['team'] == team)]

    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Goals per90','XG per90','Assists per90','XA per90','Shots',
                'Shots on goal','Goals/shot on goal','SCA','GCA',
                'Pass %','Key passes','Progressive carries','Takeons',
                'Aerial duel%','Offsides']


    values = [
        std_data0['goals_per90'].mean(),
        std_data0['xg_per90'].mean(),
        std_data0['assists_per90'].mean(),
        std_data0['xg_assist_per90'].mean(),
        shoot_data0['shots_per90'].mean(),
        shoot_data0['shots_on_target_per90'].mean(),
        shoot_data0['goals_per_shot_on_target'].mean(),
        gca_data0['sca_per90'].mean(),
        gca_data0['gca_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
        possession_data0['take_ons_won_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['offsides_per90'].mean(),
    ]

    std = std_df[(std_df['position'].notna() & std_df['position'].str.contains('FW')) & (std_df['minutes_90s']>match_th)]
    shoot = shoot_df[(shoot_df['position'].notna() & shoot_df['position'].str.contains('FW')) & (shoot_df['minutes_90s']>match_th)]
    gca = gca_df[(gca_df['position'].notna() & gca_df['position'].str.contains('FW')) & (gca_df['minutes_90s']>match_th)]
    passing = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('FW')) & (passing_df['minutes_90s']>match_th)]
    possession = possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('FW')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('FW')&(miscellaneous_df['minutes_90s']>match_th)]
    
    values1 = [
        std['goals_per90'].mean(),
        std['xg_per90'].mean(),
        std['assists_per90'].mean(),
        std['xg_assist_per90'].mean(),
        shoot['shots_per90'].mean(),
        shoot['shots_on_target_per90'].mean(),
        shoot['goals_per_shot_on_target'].mean(),
        gca['sca_per90'].mean(),
        gca['gca_per90'].mean(),
        passing['passes_pct'].mean(),
        passing['key_passes_per90'].mean(),
        possession['progressive_carries_per90'].mean(),
        possession['take_ons_won_per90'].mean(),
        miscellaneous['aerials_won_pct'].mean(),
        miscellaneous['offsides_per90'].mean(),
    ]

    # Define ranges for scaling the values
    value_ranges = [
        (std['goals_per90'].min(), std['goals_per90'].max()),    # Goals per90
        (std['xg_per90'].min(), std['xg_per90'].max()),    # xG per90
        (std['assists_per90'].min(), std['assists_per90'].max()),    # Assists per90
        (std['xg_assist_per90'].min(),std['xg_assist_per90'].max()),    # xAssist per90
        (shoot['shots_per90'].min(), shoot['shots_per90'].max()),  # Shots per 90
        (shoot['shots_on_target_per90'].min(), shoot['shots_per90'].max()),  # Shots on target per 90
        (shoot['goals_per_shot_on_target'].min(), shoot['goals_per_shot_on_target'].max()), # Goals per shot on target
        (gca['sca_per90'].min(),gca['sca_per90'].max()), # SCA per 90
        (gca['gca_per90'].min(), gca['gca_per90'].max()), # GCA per 90
        (passing['passes_pct'].min(),passing['passes_pct'].max()), # Passing pct
        (passing['key_passes_per90'].min(),passing['key_passes_per90'].max()), # Key Passes per 90
        (possession['progressive_carries_per90'].min(), possession['progressive_carries_per90'].max()), # Progressive carries per 90
        (possession['take_ons_won_per90'].min(),  possession['take_ons_won_per90'].max()), # Take ons percentage
        (miscellaneous['aerials_won_pct'].min(), miscellaneous['aerials_won_pct'].max()), # Aerial percentage
        (miscellaneous['offsides_per90'].min(), miscellaneous['offsides_per90'].max()) # Offsides
    ]

    values= [values,values1]
    
    radar = Radar(patch_color="#2C3B4D",label_fontsize=10,
              background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
              range_fontsize=8) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'vs Forward average in {liga}',
        title_color_2 = color1,
        subtitle_name_2 = f'>{match_th*90} min played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 15,
        subtitle_fontsize=5,
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color0, color1], alphas=[.7,.6],
                            title=title, endnote=None,end_color="white", dpi=600,filename="a",
                            compare=True)

    return fig,ax


def midfielder_vs_mean(player,modo,team,match_th):
    
    global std_df,shoot_df,gca_df,passing_df,possession_df,defense_df, miscellaneous_df
    liga = "Big7 leagues"

    # FILTRAR POR MEDIOCAMPISTAS
    std = std_df
    shoot = shoot_df
    gca = gca_df
    passing = passing_df
    defense = defense_df
    possession = possession_df
    miscellaneous = miscellaneous_df

    possession['take_ons_won_per90'] = possession['take_ons_won'] / possession['minutes_90s']
    possession['progressive_carries_per90'] = possession['progressive_carries'] / possession['minutes_90s']
    passing['pass_xa_per90'] = passing['pass_xa'] / passing['minutes_90s']
    passing['progressive_passes_per90'] = passing['progressive_passes'] / passing['minutes_90s']  
    passing['key_passes_per90'] = passing['assisted_shots'] / passing['minutes_90s']
    miscellaneous['ball_recoveries_per90'] = miscellaneous['ball_recoveries'] / miscellaneous['minutes_90s']     #Ball Recoveries 90
    miscellaneous['fouls_per90'] = miscellaneous['fouls'] / miscellaneous['minutes_90s']     #Ball Recoveries 90
    defense['tackles_interceptions_per90'] = defense['tackles_interceptions'] / defense_df['minutes_90s']     #Ball Recoveries 90

    if modo == "Liga":
        player_row = std_df[(std_df['player'] == player) & (std_df['team'] == team)]
        liga = player_row['comp_level'].iloc[0]

        std = std[std['comp_level'] == liga]
        shoot = shoot[shoot['comp_level'] == liga]
        defense = defense[defense['comp_level'] == liga]
        gca = gca[gca['comp_level'] == liga]
        passing = passing[passing['comp_level'] == liga]
        possession = possession[possession['comp_level'] == liga]
        miscellaneous = miscellaneous[miscellaneous['comp_level'] == liga]
    
   
    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0 = '#6CABDD'
    color1= '#00F0B5'
    std_data0 = std[(std['player'] == player) & (std['team'] == team)]
    shoot_data0 = shoot[(shoot['player'] == player) & (shoot['team'] == team)]
    gca_data0 = gca[(gca['player'] == player) & (gca['team'] == team)]
    pass_data0 = passing[(passing['player'] == player) & (passing['team'] == team)]
    defense_data0 =  defense[(defense['player'] == player) & (defense['team'] == team)]
    possession_data0 = possession[(possession['player'] == player) & (possession['team'] == team)]
    miscellaneous_data0 = miscellaneous[(miscellaneous['player'] == player) & (miscellaneous['team'] == team)]
    
    
    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Goals','Assists','XAssists','Pass%','Key passes',
                'Long Pass %','Prog. passes','Takeons','Shots on target','SCA',
                'GCA','Prog. carries','Tackles+int','Aerial Duels %',
                'Ball Recoveries','Fouls']
    
    values = [
        std_data0['goals_per90'].mean(),
        std_data0['assists_per90'].mean(),
        pass_data0['pass_xa_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        pass_data0['passes_pct_long'].mean(),
        pass_data0['progressive_passes_per90'].mean(),
        possession_data0['take_ons_won_per90'].mean(),
        shoot_data0['shots_on_target_per90'].mean(),
        gca_data0['sca_per90'].mean(),
        gca_data0['gca_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
        defense_data0['tackles_interceptions_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['ball_recoveries_per90'].mean(),
        miscellaneous_data0['fouls_per90'].mean(),
    ]
    std = std_df[(std_df['position'].notna() & std_df['position'].str.contains('MF')) & (std_df['minutes_90s']>match_th)]
    shoot = shoot_df[(shoot_df['position'].notna() & shoot_df['position'].str.contains('MF')) & (shoot_df['minutes_90s']>match_th)]
    gca = gca_df[(gca_df['position'].notna() & gca_df['position'].str.contains('MF')) & (gca_df['minutes_90s']>match_th)]
    passing = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('MF')) & (passing_df['minutes_90s']>match_th)]
    defense = defense_df[(defense_df['position'].notna() & defense_df['position'].str.contains('MF')) & (defense_df['minutes_90s']>match_th)]
    possession = possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('MF')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('MF')& (miscellaneous_df['minutes_90s']>match_th)]

    values1 = [
        std['goals_per90'].mean(),
        std['assists_per90'].mean(),
        passing['pass_xa_per90'].mean(),
        passing['passes_pct'].mean(),
        passing['key_passes_per90'].mean(),
        passing['passes_pct_long'].mean(),
        passing['progressive_passes_per90'].mean(),
        possession['take_ons_won_per90'].mean(),
        shoot['shots_on_target_per90'].mean(),
        gca['sca_per90'].mean(),
        gca['gca_per90'].mean(),
        possession['progressive_carries_per90'].mean(),
        defense['tackles_interceptions_per90'].mean(),
        miscellaneous['aerials_won_pct'].mean(),
        miscellaneous['ball_recoveries_per90'].mean(),
        miscellaneous['fouls_per90'].mean(),
    ]
    # Define ranges for scaling the values
    value_ranges = [
        (std['goals_per90'].min(), std['goals_per90'].max()),    # Goals
        (std['assists_per90'].min(), std['assists_per90'].max()),    # Assists
        (passing['pass_xa_per90'].min(), passing['pass_xa_per90'].max()),    # xA
        (passing['passes_pct'].min(), passing['passes_pct'].max()),    # Percentage of Passes
        (passing['key_passes_per90'].min(), passing['key_passes_per90'].max()),    # Key passes per 90
        (passing['passes_pct_long'].min(), passing['passes_pct_long'].max()),    # Percentage long passes
        (passing['progressive_passes_per90'].min(), passing['progressive_passes_per90'].max()),    # Progressive passes
        (possession['take_ons_won_per90'].min(),  possession['take_ons_won_per90'].max()), # Take ons percentage
        (shoot['shots_on_target_per90'].min(), shoot['shots_per90'].max()),  # Shots on target per 90
        (gca['sca_per90'].min(),gca['sca_per90'].max()), # SCA per 90
        (gca['gca_per90'].min(),gca['gca_per90'].max()), # GCA per 90
        (possession['progressive_carries_per90'].min(), possession['progressive_carries_per90'].max()), # Progressive carries per 90
        (defense['tackles_interceptions_per90'].min(), defense['tackles_interceptions_per90'].max()),  # Tackles percentages
        (miscellaneous['aerials_won_pct'].min(), miscellaneous['aerials_won_pct'].max()), # Aerial percentage
        (miscellaneous['ball_recoveries_per90'].min(),miscellaneous['ball_recoveries_per90'].max()),  # Ball recoveries
        (miscellaneous['fouls_per90'].min(), miscellaneous['fouls_per90'].max()) # Interceptions
    ]
    values= [values,values1]
    
    radar = Radar(patch_color="#2C3B4D",label_fontsize=10,
                background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
                range_fontsize=8) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'vs Midfielder average in {liga}',
        title_color_2 = color1,
        subtitle_name_2 = f'>{match_th*90} min played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 15,
        subtitle_fontsize=5,
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color0, color1], alphas=[.7,.6],
                            title=title, endnote=None,end_color="white", dpi=600,filename="a",
                            compare=True)

    return fig,ax


def defender_vs_mean(player,modo,team,match_th):
    
    global std_df,shoot_df,passing_df,possession_df,defense_df, miscellaneous_df
    liga = "Big7 leagues"

    # FILTRAR POR DEFENSAS
    std= std_df
    passing= passing_df
    defense= defense_df
    possession= possession_df
    miscellaneous= miscellaneous_df

    possession['progressive_carries_per90'] = possession['progressive_carries'] / possession['minutes_90s']   # Progressive carries per 90

    passing['key_passes_per90'] = passing['assisted_shots'] / passing['minutes_90s']      # Key passes per 90
    passing['progressive_passes_per90'] = passing['progressive_passes'] / passing['minutes_90s']      # Progressive passes per 90
    passing['passes_completed_long_per90'] = passing['passes_completed_long'] / passing['minutes_90s']   # Passes long per 90
    passing['passes_per90'] = passing['passes_completed'] / passing['minutes_90s']    # Passes per 90

    
    miscellaneous['ball_recoveries_per90'] = miscellaneous['ball_recoveries'] / miscellaneous['minutes_90s']     #Ball Recoveries 90
    miscellaneous['fouls_per90'] = miscellaneous['fouls'] / miscellaneous['minutes_90s']     #Fouls per 90
    miscellaneous['aerials_won_per90'] = miscellaneous['aerials_won'] / miscellaneous['minutes_90s']     #Aerial wins per 90

    
    defense['tackles_won_per90'] = defense['tackles_won'] / defense['minutes_90s']     #Tackles Won per90
    defense['tackles_won_pct'] = (defense['tackles_won'] / defense['tackles'])*100 # Tackles pct
    defense['blocks_per90'] = defense['blocks'] / defense['minutes_90s']     #Tackles per90
    defense['interceptions_per90'] = defense['interceptions'] / defense['minutes_90s']     #Tackles per90
    
    if modo == "Liga":
        player_row = std_df[(std_df['player'] == player) & (std_df['team']==team)]
        liga = player_row['comp_level'].iloc[0]
        std = std[std['comp_level'] == liga]
        defense = defense[defense['comp_level'] == liga]
        passing = passing[passing['comp_level'] == liga]
        possession = possession[possession['comp_level'] == liga]
        miscellaneous = miscellaneous[miscellaneous['comp_level'] == liga]
    
   
    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0 = '#6CABDD'
    color1= '#6DECAF'
    std_data0 = std[(std['player'] == player) & (std['team'] ==team)]
    pass_data0 = passing[(passing['player'] == player) & (passing['team'] == team)]
    defense_data0 =  defense[(defense['player'] == player) & (defense['team'] == team)]
    possession_data0 = possession[(possession['player'] == player) & (possession['team'] == team)]
    miscellaneous_data0 = miscellaneous[(miscellaneous['player'] == player) & (miscellaneous['team'] == team)]
    
    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Tackles Won','Tackles won %','Blocks','Interceptions','Aerial wins',
                  'Aerial win %','Ball recoveries','Fouls','Passes completed','Pass %',
                  'Key passes','Acc. Long balls','Long pass %','Progr. passes','Progr. carries']
    
    values = [
        defense_data0['tackles_won_per90'].mean(),
        defense_data0['tackles_won_pct'].mean(),
        defense_data0['blocks_per90'].mean(),
        defense_data0['interceptions_per90'].mean(),
        miscellaneous_data0['aerials_won_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['ball_recoveries_per90'].mean(),
        miscellaneous_data0['fouls_per90'].mean(),
        pass_data0['passes_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        pass_data0['passes_completed_long_per90'].mean(),
        pass_data0['passes_pct_long'].mean(),
        pass_data0['progressive_passes_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
    ]

    std= std_df[(std_df['position'].notna() & std_df['position'].str.contains('DF')) & (std_df['minutes_90s']>match_th)]
    passing= passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('DF')) & (passing_df['minutes_90s']>match_th)]
    defense= defense_df[(defense_df['position'].notna() & defense_df['position'].str.contains('DF')) & (defense_df['minutes_90s']>match_th)]
    possession= possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('DF')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous= miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('DF')& (miscellaneous_df['minutes_90s']>match_th)]

    values1 = [
        defense['tackles_won_per90'].mean(),
        defense['tackles_won_pct'].mean(),
        defense['blocks_per90'].mean(),
        defense['interceptions_per90'].mean(),
        miscellaneous['aerials_won_per90'].mean(),
        miscellaneous['aerials_won_pct'].mean(),
        miscellaneous['ball_recoveries_per90'].mean(),
        miscellaneous['fouls_per90'].mean(),
        passing['passes_per90'].mean(),
        passing['passes_pct'].mean(),
        passing['key_passes_per90'].mean(),
        passing['passes_completed_long_per90'].mean(),
        passing['passes_pct_long'].mean(),
        passing['progressive_passes_per90'].mean(),
        possession['progressive_carries_per90'].mean(),
    ]
    # Define ranges for scaling the values
    value_ranges = [
        (defense['tackles_won_per90'].min(),defense['tackles_won_per90'].max()),    # Tackles
        (defense['tackles_won_pct'].min(),defense['tackles_won_pct'].max()),    # Tackles won %
        (defense['blocks_per90'].min(),defense['blocks_per90'].max()),    # Blocks
        (defense['interceptions_per90'].min(),defense['interceptions_per90'].max()),    # Interceptions
        (miscellaneous['aerials_won_per90'].min(),miscellaneous['aerials_won_per90'].max()),    # Aerial wins
        (miscellaneous['aerials_won_pct'].min(),miscellaneous['aerials_won_pct'].max()),    # Aerial sin %
        (miscellaneous['ball_recoveries_per90'].min(),miscellaneous['ball_recoveries_per90'].max()),    # Ball recoveries
        (miscellaneous['fouls_per90'].min(),miscellaneous['fouls_per90'].max()),  # Fouls per 90
        (passing['passes_per90'].min(),passing['passes_per90'].max()), # Passes per 90
        (passing['passes_pct'].min(),passing['passes_pct'].max()),  # Passes pct
        (passing['key_passes_per90'].min(),passing['key_passes_per90'].max() ), # Key passes
        (passing['passes_completed_long_per90'].min(),passing['passes_completed_long_per90'].max()),  # Long passes completed
        (passing['passes_pct_long'].min(),passing['passes_pct_long'].max()), # Long passes %
        (passing['progressive_passes_per90'].min(),passing['progressive_passes_per90'].max()), # Progressive passes
        (possession['progressive_carries_per90'].min(),possession['progressive_carries_per90'].max()) #Progressive carries
    ]

    values= [values,values1]
    
    radar = Radar(patch_color="#2C3B4D",label_fontsize=10,
                background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
                range_fontsize=8) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'vs Defenders average in {liga}',
        title_color_2 = color1,
        subtitle_name_2 = f'>{match_th*90} min played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 15,
        subtitle_fontsize=5,
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color0, color1], alphas=[.7,.6],
                            title=title, endnote=None,end_color="white", dpi=600,filename="a",
                            compare=True)

    return fig,ax




def compare_attackers(player,player1,match_th):
    global std_df,shoot_df,passing_df,possession_df,defense_df, miscellaneous_df

    # FILTRAR POR DELANTEROS
    std = std_df
    shoot = shoot_df
    gca= gca_df
    passing = passing_df
    possession= possession_df
    miscellaneous = miscellaneous_df

    # Modify possession dataframe to add a column named takons per game (equal to take_ons_won/matches)
    possession['take_ons_won_per90'] = possession['take_ons_won'] / possession['minutes_90s']
    possession['progressive_carries_per90'] = possession['progressive_carries'] / possession['minutes_90s']

    passing['key_passes_per90'] = passing['assisted_shots'] / passing['minutes_90s']

    miscellaneous['offsides_per90'] = miscellaneous['offsides'] / miscellaneous['minutes_90s']

    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0 = '#7C85CB'
    std_data0 = std_df[std_df['player'] == player]
    shoot_data0 = shoot_df[shoot_df['player'] == player]
    gca_data0 = gca_df[gca_df['player'] == player]
    pass_data0 = passing_df[passing_df['player'] == player]
    possession_data0 = possession_df[possession_df['player'] == player]
    miscellaneous_data0 = miscellaneous_df[miscellaneous_df['player'] == player]

    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]

    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color1 = '#A50044'
    std_data1 = std_df[std_df['player'] == player1]
    shoot_data1 = shoot_df[shoot_df['player'] == player1]
    gca_data1 = gca_df[gca_df['player'] == player1]
    pass_data1 = passing_df[passing_df['player'] == player1]
    possession_data1 = possession_df[possession_df['player'] == player1]
    miscellaneous_data1 = miscellaneous_df[miscellaneous_df['player'] == player1]

    age1 = std_data1["age"].values[0]
    minutes_played1 = std_data1["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Goals','XG','Assists','XA','Shots',
                'Shots on goal','Goals/Shot \n on target','SCA','GCA',
                'Pass %','Key passes','Prog. carries','Takeons','Aerial Duels%',
                'Offsides']


    values = [
        std_data0['goals_per90'].mean(),
        std_data0['xg_per90'].mean(),
        std_data0['assists_per90'].mean(),
        std_data0['xg_assist_per90'].mean(),
        shoot_data0['shots_per90'].mean(),
        shoot_data0['shots_on_target_per90'].mean(),
        shoot_data0['goals_per_shot_on_target'].mean(),
        gca_data0['sca_per90'].mean(),
        gca_data0['gca_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
        possession_data0['take_ons_won_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['offsides_per90'].mean(),
    ]

    values1 = [
        std_data1['goals_per90'].mean(),
        std_data1['xg_per90'].mean(),
        std_data1['assists_per90'].mean(),
        std_data1['xg_assist_per90'].mean(),
        shoot_data1['shots_per90'].mean(),
        shoot_data1['shots_on_target_per90'].mean(),
        shoot_data1['goals_per_shot_on_target'].mean(),
        gca_data1['sca_per90'].mean(),
        gca_data1['gca_per90'].mean(),
        pass_data1['passes_pct'].mean(),
        pass_data1['key_passes_per90'].mean(),
        possession_data1['progressive_carries_per90'].mean(),
        possession_data1['take_ons_won_per90'].mean(),
        miscellaneous_data1['aerials_won_pct'].mean(),
        miscellaneous_data1['offsides_per90'].mean(),
    ]

    std = std_df[(std_df['position'].notna() & std_df['position'].str.contains('FW')) & (std_df['minutes_90s']>match_th)]
    shoot = shoot_df[(shoot_df['position'].notna() & shoot_df['position'].str.contains('FW')) & (shoot_df['minutes_90s']>match_th)]
    gca= gca_df[(gca_df['position'].notna() & gca_df['position'].str.contains('FW')) & (gca_df['minutes_90s']>match_th)]
    passing = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('FW')) & (passing_df['minutes_90s']>match_th)]
    possession= possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('FW')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('FW')&(miscellaneous_df['minutes_90s']>match_th)]

    # Define ranges for scaling the values
    value_ranges = [
        (std['goals_per90'].min(), std['goals_per90'].max()),    # Goals per90
        (std['xg_per90'].min(), std['xg_per90'].max()),    # xG per90
        (std['assists_per90'].min(), std['assists_per90'].max()),    # Assists per90
        (std['xg_assist_per90'].min(),std['xg_assist_per90'].max()),    # xAssist per90
        (shoot['shots_per90'].min(), shoot['shots_per90'].max()),  # Shots per 90
        (shoot['shots_on_target_per90'].min(), shoot['shots_per90'].max()),  # Shots on target per 90
        (shoot['goals_per_shot_on_target'].min(), shoot['goals_per_shot_on_target'].max()), # Goals per shot on target
        (gca['sca_per90'].min(),gca['sca_per90'].max()), # SCA per 90
        (gca['gca_per90'].min(), gca['gca_per90'].max()), # GCA per 90
        (passing['passes_pct'].min(),passing['passes_pct'].max()), # Passing pct
        (passing['key_passes_per90'].min(),passing['key_passes_per90'].max()), # Key Passes per 90
        (possession['progressive_carries_per90'].min(), possession['progressive_carries_per90'].max()), # Progressive carries per 90
        (possession['take_ons_won_per90'].min(),  possession['take_ons_won_per90'].max()), # Take ons percentage
        (miscellaneous['aerials_won_pct'].min(), miscellaneous['aerials_won_pct'].max()), # Aerial percentage
        (miscellaneous['offsides_per90'].min(), miscellaneous['offsides_per90'].max()) # Offsides
    ]

    values= [values,values1]
    radar = Radar(patch_color="#2C3B4D",label_fontsize=12,
                background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
                range_fontsize=9) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'{player1}',
        title_color_2 = color1,
        subtitle_name_2 = f'{age1} years/ {minutes_played1} mins played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 15,
        subtitle_fontsize=5
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color0, color1], alphas=[.8,.7],
                            title=title, endnote=None,end_color="white", dpi=600,filename="b",
                            compare=True)

    return fig,ax

def compare_midfielders(player,player1,match_th):
    global std_df,shoot_df,passing_df,possession_df,defense_df, miscellaneous_df

    # FILTRAR POR DELANTEROS
    std = std_df
    shoot = shoot_df
    gca= gca_df
    passing = passing_df
    possession= possession_df
    defense = defense_df
    miscellaneous = miscellaneous_df

    # Modify possession dataframe to add a column named takons per game (equal to take_ons_won/matches)
    possession_df = possession_df.merge(std_df[['player', 'games']], on='player', how='left')
    possession_df['take_ons_won_per90'] = possession_df['take_ons_won'] / possession_df['minutes_90s']     #Take ons won per 90
    possession_df['progressive_carries_per90'] = possession_df['progressive_carries'] / possession_df['minutes_90s']   # Progressive carries per 90

    passing_df['key_passes_per90'] = passing_df['assisted_shots'] / passing_df['minutes_90s']      # Key passes per 90
    passing_df['progressive_passes_per90'] = passing_df['progressive_passes'] / passing_df['minutes_90s']      # Progressive passes per 90
    passing_df['pass_xa_per90'] = passing_df['pass_xa'] / passing_df['minutes_90s']

    miscellaneous_df['ball_recoveries_per90'] = miscellaneous_df['ball_recoveries'] / miscellaneous_df['minutes_90s']     #Ball Recoveries 90
    miscellaneous_df['fouls_per90'] = miscellaneous_df['fouls'] / miscellaneous_df['minutes_90s']     #Ball Recoveries 90

    defense_df['tackles_interceptions_per90'] = defense_df['tackles_interceptions'] / defense_df['minutes_90s']     #Ball Recoveries 90


    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0= '#E32221'
    std_data0 = std_df[std_df['player'] == player]
    shoot_data0 = shoot_df[shoot_df['player'] == player]
    gca_data0 = gca_df[gca_df['player'] == player]
    pass_data0 = passing_df[passing_df['player'] == player]
    defense_data0 =  defense_df[defense_df['player'] == player]
    possession_data0 = possession_df[possession_df['player'] == player]
    miscellaneous_data0 = miscellaneous_df[miscellaneous_df['player'] == player]


    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]

    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color1 = '#2D5CAE'
    std_data1 = std_df[std_df['player'] == player1]
    shoot_data1 = shoot_df[shoot_df['player'] == player1]
    gca_data1 = gca_df[gca_df['player'] == player1]
    pass_data1 = passing_df[passing_df['player'] == player1]
    defense_data1 = defense_df[defense_df['player'] == player1]
    possession_data1 = possession_df[possession_df['player'] == player1]
    miscellaneous_data1 = miscellaneous_df[miscellaneous_df['player'] == player1]


    age1 = std_data1["age"].values[0]
    minutes_played1 = std_data1["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Goals','Assists','XAssists','Pass%','Key passes',
              '% Long Passes','Progressive passes','Takeons','Shots on target','SCA',
              'GCA','Progressive carries','Tackles+Int.','Aerial Duels %',
              'Ball Rec.','Fouls']


    values = [
        std_data0['goals_per90'].mean(),
        std_data0['assists_per90'].mean(),
        pass_data0['pass_xa_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        pass_data0['passes_pct_long'].mean(),
        pass_data0['progressive_passes_per90'].mean(),
        possession_data0['take_ons_won_per90'].mean(),
        shoot_data0['shots_on_target_per90'].mean(),
        gca_data0['sca_per90'].mean(),
        gca_data0['gca_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
        defense_data0['tackles_interceptions_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['ball_recoveries_per90'].mean(),
        miscellaneous_data0['fouls_per90'].mean(),
    ]

    values1 = [
        std_data1['goals_per90'].mean(),
        std_data1['assists_per90'].mean(),
        pass_data1['pass_xa_per90'].mean(),
        pass_data1['passes_pct'].mean(),
        pass_data1['key_passes_per90'].mean(),
        pass_data1['passes_pct_long'].mean(),
        pass_data1['progressive_passes_per90'].mean(),
        possession_data1['take_ons_won_per90'].mean(),
        shoot_data1['shots_on_target_per90'].mean(),
        gca_data1['sca_per90'].mean(),
        gca_data1['gca_per90'].mean(),
        possession_data1['progressive_carries_per90'].mean(),
        defense_data1['tackles_interceptions_per90'].mean(),
        miscellaneous_data1['aerials_won_pct'].mean(),
        miscellaneous_data1['ball_recoveries_per90'].mean(),
        miscellaneous_data1['fouls_per90'].mean(),
    ]

    std= std_df[(std_df['position'].notna() & std_df['position'].str.contains('MF')) & (std_df['minutes_90s']>match_th)]
    shoot = shoot_df[(shoot_df['position'].notna() & shoot_df['position'].str.contains('MF')) & (shoot_df['minutes_90s']>match_th)]
    gca = gca_df[(gca_df['position'].notna() & gca_df['position'].str.contains('MF')) & (gca_df['minutes_90s']>match_th)]
    passing = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('MF')) & (passing_df['minutes_90s']>match_th)]
    defense = defense_df[(defense_df['position'].notna() & defense_df['position'].str.contains('MF')) & (defense_df['minutes_90s']>match_th)]
    possession = possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('MF')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('MF')& (miscellaneous_df['minutes_90s']>match_th)]

    # Define ranges for scaling the values
    value_ranges = [
        (std['goals_per90'].min(), std['goals_per90'].max()),    # Goals
        (std['assists_per90'].min(), std['assists_per90'].max()),    # Assists
        (passing['pass_xa_per90'].min(), passing['pass_xa_per90'].max()),    # xA
        (passing['passes_pct'].min(), passing['passes_pct'].max()),    # Percentage of Passes
        (passing['key_passes_per90'].min(), passing['key_passes_per90'].max()),    # Key passes per 90
        (passing['passes_pct_long'].min(), passing['passes_pct_long'].max()),    # Percentage long passes
        (passing['progressive_passes_per90'].min(), passing['progressive_passes_per90'].max()),    # Progressive passes
        (possession['take_ons_won_per90'].min(),  possession['take_ons_won_per90'].max()), # Take ons percentage
        (shoot['shots_on_target_per90'].min(), shoot['shots_per90'].max()),  # Shots on target per 90
        (gca['sca_per90'].min(),gca['sca_per90'].max()), # SCA per 90
        (gca['gca_per90'].min(),gca['gca_per90'].max()), # GCA per 90
        (possession['progressive_carries_per90'].min(), possession['progressive_carries_per90'].max()), # Progressive carries per 90
        (defense['tackles_interceptions_per90'].min(), defense['tackles_interceptions_per90'].max()),  # Tackles percentages
        (miscellaneous['aerials_won_pct'].min(), miscellaneous['aerials_won_pct'].max()), # Aerial percentage
        (miscellaneous['ball_recoveries_per90'].min(),miscellaneous['ball_recoveries_per90'].max()),  # Ball recoveries
        (miscellaneous['fouls_per90'].min(), miscellaneous['fouls_per90'].max()) # Interceptions
    ]

    values= [values1,values]
    radar = Radar(patch_color="#2C3B4D",label_fontsize=12,
                background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
                range_fontsize=9) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'{player1}',
        title_color_2 = color1,
        subtitle_name_2 = f'{age1} years/ {minutes_played1} mins played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 18,
        subtitle_fontsize=15
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color1, color0], alphas=[.8,.8],
                            title=title, endnote=None,end_color="white", dpi=600,filename="b",
                            compare=True)

    return fig,ax




def compare_defenders(player,player1,match_th):
    global std_df,shoot_df,passing_df,possession_df,defense_df, miscellaneous_df

    # FILTRAR POR DELANTEROS
    std = std_df
    passing = passing_df
    possession= possession_df
    defense = defense_df
    miscellaneous = miscellaneous_df

    # Modify possession dataframe to add a column named takons per game (equal to take_ons_won/matches)
    possession['progressive_carries_per90'] = possession['progressive_carries'] / possession['minutes_90s']   # Progressive carries per 90

    passing['key_passes_per90'] = passing['assisted_shots'] / passing['minutes_90s']      # Key passes per 90
    passing['progressive_passes_per90'] = passing['progressive_passes'] / passing['minutes_90s']      # Progressive passes per 90
    passing['passes_completed_long_per90'] = passing['passes_completed_long'] / passing['minutes_90s']   # Passes long per 90
    passing['passes_per90'] = passing['passes_completed'] / passing['minutes_90s']    # Passes per 90

    miscellaneous['ball_recoveries_per90'] = miscellaneous['ball_recoveries'] / miscellaneous['minutes_90s']     #Ball Recoveries 90
    miscellaneous['fouls_per90'] = miscellaneous['fouls'] / miscellaneous['minutes_90s']     #Fouls per 90
    miscellaneous['aerials_won_per90'] = miscellaneous['aerials_won'] / miscellaneous['minutes_90s']     #Aerial wins per 90

    defense['tackles_per90'] = defense['tackles'] / defense['minutes_90s']     #Tackles per90
    defense['tackles_won_pct'] = (defense['tackles_won'] / defense['tackles'])*100 # Tackles pct
    defense['blocks_per90'] = defense['blocks'] / defense['minutes_90s']     #Tackles per90
    defense['interceptions_per90'] = defense['interceptions'] / defense['minutes_90s']     #Tackles per90


    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color0= '#E32221'
    std_data0 = std_df[std_df['player'] == player]
    pass_data0 = passing_df[passing_df['player'] == player]
    defense_data0 =  defense_df[defense_df['player'] == player]
    possession_data0 = possession_df[possession_df['player'] == player]
    miscellaneous_data0 = miscellaneous_df[miscellaneous_df['player'] == player]

    age = std_data0["age"].values[0]
    minutes_played0 = std_data0["minutes"].values[0]

    # Filter data for a specific team (replace 'your_team' with your desired team name)
    color1 = '#2D5CAE'
    std_data1 = std_df[std_df['player'] == player1]
    pass_data1 = passing_df[passing_df['player'] == player1]
    defense_data1 = defense_df[defense_df['player'] == player1]
    possession_data1 = possession_df[possession_df['player'] == player1]
    miscellaneous_data1 = miscellaneous_df[miscellaneous_df['player'] == player1]


    age1 = std_data1["age"].values[0]
    minutes_played1 = std_data1["minutes"].values[0]


    # Define the radar pie chart categories and values
    categories = ['Tackles','Tackles won %','Blocks','Interceptions','Aerial wins','Aerial win %','Ball recoveries',
                'Fouls','Passes completed','Pass %','Key passes','Accurate Long balls','Long pass %','Progressive passes',
                'Progressive carries']

    values = [
        defense_data0['tackles_per90'].mean(),
        defense_data0['tackles_won_pct'].mean(),
        defense_data0['blocks_per90'].mean(),
        defense_data0['interceptions_per90'].mean(),
        miscellaneous_data0['aerials_won_per90'].mean(),
        miscellaneous_data0['aerials_won_pct'].mean(),
        miscellaneous_data0['ball_recoveries_per90'].mean(),
        miscellaneous_data0['fouls_per90'].mean(),
        pass_data0['passes_per90'].mean(),
        pass_data0['passes_pct'].mean(),
        pass_data0['key_passes_per90'].mean(),
        pass_data0['passes_completed_long_per90'].mean(),
        pass_data0['passes_pct_long'].mean(),
        pass_data0['progressive_passes_per90'].mean(),
        possession_data0['progressive_carries_per90'].mean(),
    ]

    values1 = [
        defense_data1['tackles_per90'].mean(),
        defense_data1['tackles_won_pct'].mean(),
        defense_data1['blocks_per90'].mean(),
        defense_data1['interceptions_per90'].mean(),
        miscellaneous_data1['aerials_won_per90'].mean(),
        miscellaneous_data1['aerials_won_pct'].mean(),
        miscellaneous_data1['ball_recoveries_per90'].mean(),
        miscellaneous_data1['fouls_per90'].mean(),
        pass_data1['passes_per90'].mean(),
        pass_data1['passes_pct'].mean(),
        pass_data1['key_passes_per90'].mean(),
        pass_data1['passes_completed_long_per90'].mean(),
        pass_data1['passes_pct_long'].mean(),
        pass_data1['progressive_passes_per90'].mean(),
        possession_data1['progressive_carries_per90'].mean(),
    ]


    std = std_df[(std_df['position'].notna() & std_df['position'].str.contains('DF')) & (std_df['minutes_90s']>match_th)]
    passing = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains('DF')) & (passing_df['minutes_90s']>match_th)]
    defense = defense_df[(defense_df['position'].notna() & defense_df['position'].str.contains('DF')) & (defense_df['minutes_90s']>match_th)]
    possession = possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains('DF')) & (possession_df['minutes_90s']>match_th)]
    miscellaneous = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains('DF')& (miscellaneous_df['minutes_90s']>match_th)]

    # Define ranges for scaling the values
    value_ranges = [
        (defense['tackles_per90'].min(),defense['tackles_per90'].max()),    # Tackles
        (defense['tackles_won_pct'].min(),defense['tackles_won_pct'].max()),    # Tackles won %
        (defense['blocks_per90'].min(),defense['blocks_per90'].max()),    # Blocks
        (defense['interceptions_per90'].min(),defense['interceptions_per90'].max()),    # Interceptions
        (miscellaneous['aerials_won_per90'].min(),miscellaneous['aerials_won_per90'].max()),    # Aerial wins
        (miscellaneous['aerials_won_pct'].min(),miscellaneous['aerials_won_pct'].max()),    # Aerial sin %
        (miscellaneous['ball_recoveries_per90'].min(),miscellaneous['ball_recoveries_per90'].max()),    # Ball recoveries
        (miscellaneous['fouls_per90'].min(),miscellaneous['fouls_per90'].max()),  # Fouls per 90
        (passing['passes_per90'].min(),passing['passes_per90'].max()), # Passes per 90
        (passing['passes_pct'].min(),passing['passes_pct'].max()),  # Passes pct
        (passing['key_passes_per90'].min(),passing['key_passes_per90'].max() ), # Key passes
        (passing['passes_completed_long_per90'].min(),passing['passes_completed_long_per90'].max()),  # Long passes completed
        (passing['passes_pct_long'].min(),passing['passes_pct_long'].max()), # Long passes %
        (passing['progressive_passes_per90'].min(),passing['progressive_passes_per90'].max()), # Progressive passes
        (possession['progressive_carries_per90'].min(),possession['progressive_carries_per90'].max()) #Progressive carries
    ]

    values= [values,values1]
    radar = Radar(patch_color="#2C3B4D",label_fontsize=12,
                background_color='#1B2632',label_color='#EEE9DF',range_color="#C9C1B1",
                range_fontsize=9) # Initialize the object
    title = dict(
        title_name=f'{player}',
        title_color = color0,
        subtitle_name = f'{age} years/ {minutes_played0} mins played',
        subtitle_color = '#EEE9DF',
        title_name_2=f'{player1}',
        title_color_2 = color1,
        subtitle_name_2 = f'{age1} years/ {minutes_played1} mins played',
        subtitle_color_2 = '#EEE9DF',
        title_fontsize = 18,
        subtitle_fontsize=5
    )


    fig,ax = radar.plot_radar(ranges=value_ranges, params=categories,values=values,
                            radar_color = [color0, color1], alphas=[.7,.6],
                            title=title, endnote=None,end_color="white", dpi=600,filename="b",
                            compare=True)

    return fig,ax