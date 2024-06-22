from mplsoccer import PyPizza, add_image, FontManager
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy import stats
def percentile_plot(name,mode,team,position):
    if mode == "Liga":
        std_df = pd.read_csv(f'data/Big5Leagues_Players_Standard_Stats.csv')
        player_row = std_df[(std_df['player'] == name) & (std_df['team'] == team)]
        liga = player_row['comp_level'].iloc[0]

        shoot_df = pd.read_csv(f'data/Big5Leagues_Players_shooting_Stats.csv')
        gca_df = pd.read_csv(f'data/Big5Leagues_Players_gca_Stats.csv')
        passing_df = pd.read_csv(f'data/Big5Leagues_Players_passing_Stats.csv')
        defense_df = pd.read_csv(f'data/Big5Leagues_Players_defense_Stats.csv')
        possession_df = pd.read_csv(f'data/Big5Leagues_Players_possession_Stats.csv')
        miscellaneous_df = pd.read_csv(f'data/Big5Leagues_Players_misc_Stats.csv')

        std_df = std_df[std_df['comp_level'] == liga]
        shoot_df = shoot_df[shoot_df['comp_level'] == liga]
        gca_df = gca_df[gca_df['comp_level'] == liga]
        defense_df = defense_df[defense_df['comp_level'] == liga]
        possession_df = possession_df[possession_df['comp_level'] == liga]
        miscellaneous_df = miscellaneous_df[miscellaneous_df['comp_level'] == liga]

    elif mode == "Big5":
        liga = "Big 7 Leagues"
        std_df = pd.read_csv(f'data/Big5Leagues_Players_Standard_Stats.csv')
        shoot_df = pd.read_csv(f'data/Big5Leagues_Players_shooting_Stats.csv')
        gca_df = pd.read_csv(f'data/Big5Leagues_Players_gca_Stats.csv')
        passing_df = pd.read_csv(f'data/Big5Leagues_Players_passing_Stats.csv')
        defense_df = pd.read_csv(f'data/Big5Leagues_Players_defense_Stats.csv')
        possession_df = pd.read_csv(f'data/Big5Leagues_Players_possession_Stats.csv')
        miscellaneous_df = pd.read_csv(f'data/Big5Leagues_Players_misc_Stats.csv')

    
    

    std_df = std_df[(std_df['position'].notna() & std_df['position'].str.contains(position)) & (std_df['minutes_90s']>1)]
    shoot_df = shoot_df[(shoot_df['position'].notna() & shoot_df['position'].str.contains(position)) & (shoot_df['minutes_90s']>1)]
    gca_df = gca_df[(gca_df['position'].notna() & gca_df['position'].str.contains(position)) & (gca_df['minutes_90s']>1)]
    passing_df = passing_df[(passing_df['position'].notna() & passing_df['position'].str.contains(position)) & (passing_df['minutes_90s']>1)]
    defense_df = defense_df[(defense_df['position'].notna() & defense_df['position'].str.contains(position)) & (defense_df['minutes_90s']>1)]
    possession_df = possession_df[(possession_df['position'].notna() & possession_df['position'].str.contains(position)) & (possession_df['minutes_90s']>1)]
    miscellaneous_df = miscellaneous_df[miscellaneous_df['position'].notna() & miscellaneous_df['position'].str.contains(position)& (miscellaneous_df['minutes_90s']>1)]

    passing_df['passes_attempted_per90'] = passing_df['passes_completed']/passing_df['minutes_90s']
    passing_df['progressive_passes_per90'] = passing_df['progressive_passes'] / passing_df['minutes_90s']      # Progressive passes per 90
    passing_df['key_passes_per90'] = passing_df['assisted_shots'] / passing_df['minutes_90s']      # Key passes per 90
    passing_df['passes_into_finalthird_per90'] = passing_df['passes_into_final_third'] / passing_df['minutes_90s']

    possession_df['take_ons_won_per90'] = possession_df['take_ons_won'] / possession_df['minutes_90s']
    possession_df['progressive_carries_per90'] = possession_df['progressive_carries'] / possession_df['minutes_90s']
    possession_df['touches_att_pen_area_per90'] = possession_df['touches_att_pen_area'] / possession_df['minutes_90s']

    defense_df['tackles_won_per90'] = defense_df['tackles_won'] / defense_df['minutes_90s']
    defense_df['blocks_per90'] = defense_df['blocks'] / defense_df['minutes_90s']
    defense_df['interceptions_per90'] = defense_df['interceptions'] / defense_df['minutes_90s']

    miscellaneous_df['ball_recoveries_per90'] = miscellaneous_df['ball_recoveries'] / miscellaneous_df['minutes_90s']     #Ball Recoveries 90
    miscellaneous_df['fouls_per90'] = miscellaneous_df['fouls'] / miscellaneous_df['minutes_90s']     #Fouls per 90
    miscellaneous_df['aerials_won_per90'] = miscellaneous_df['aerials_won'] / miscellaneous_df['minutes_90s']     #Aerial wins per 90

    std_cat = ["goals_per90","xg_per90","assists_per90","xg_assist_per90"]
    sc_cat = ["sca_per90","gca_per90"]
    pass_cat = ["passes_attempted_per90","passes_pct","progressive_passes_per90","key_passes_per90","passes_into_finalthird_per90"]
    possession_cat = ["take_ons_won_per90","progressive_carries_per90","touches_att_pen_area_per90"]
    defense_cat = ["tackles_won_per90","blocks_per90","interceptions_per90"]
    misc_cat =["ball_recoveries_per90","fouls_per90","aerials_won_per90"]

    data_to_concat = []
    result_df = pd.DataFrame(columns=['Category', 'Value', 'Percentile'])

    # Loop through each category and its corresponding dataset
    for category_name, category_values in zip(['Standard','GCA','Passing','Possession','Defense','Miscellaneous'],
                                            [std_cat,sc_cat,pass_cat, possession_cat, defense_cat,misc_cat]):
        if category_name == 'Standard':
            dataset = std_df
        elif category_name == 'GCA':
            dataset = gca_df
        elif category_name == 'Passing':
            dataset = passing_df
        elif category_name == 'Possession':
            dataset = possession_df
        elif category_name == 'Defense':
            dataset = defense_df
        elif category_name == 'Miscellaneous':
            dataset = miscellaneous_df

        for feature in category_values:
            player_data = dataset.loc[(dataset['player'] == name) & (dataset['team'] == team)] 
            player_value = player_data[feature].values[0]
            percentile0 = int(stats.percentileofscore(dataset[feature], player_value, kind='rank'))
            data_to_concat.append(pd.DataFrame({'Category': [feature],
                                                'Value': [player_value.round(2)],
                                                'Percentile': [percentile0]}))
        result_df = pd.concat(data_to_concat, ignore_index=True)


    # Rename the categories for a smoother visualization
    category_mapping = {
        'goals_per90': 'Goals',
        'xg_per90': 'xG',
        'assists_per90': 'Assists',
        'xg_assist_per90': 'XA',
        'sca_per90': 'SCA',
        'gca_per90': 'GCA',
        'passes_attempted_per90': 'Passes',
        'passes_pct': 'Pass\n completion %',
        'progressive_passes_per90': 'Progr.\n Passes',
        'key_passes_per90': 'Key Passes',
        'passes_into_finalthird_per90': 'Passes\n final1/3',
        'take_ons_won_per90': 'Takeons won',
        'progressive_carries_per90': 'Progr.\n Carries',
        'touches_att_pen_area_per90': 'Touches\n att area',
        'tackles_won_per90': 'Tackles won',
        'blocks_per90': 'Blocks',
        'interceptions_per90': 'Interceptions',
        'ball_recoveries_per90': 'Ball\n Recoveries',
        'fouls_per90': 'Fouls',
        'aerials_won_per90': 'Aerials won'
    }
    # Replace the categories' names
    result_df['Category'] = result_df['Category'].replace(category_mapping)
    # Replace the categories' names
    result_df['Category'] = result_df['Category'].replace(category_mapping)
    values = result_df['Percentile']
    slice_colors = ["#449DD1"] * 6 + ["#C2ED81"] * 5 + ["#6F2DBD"] * 3 + ['#F55D3E'] *6

    baker = PyPizza(
        params=result_df['Category'],                  # list of parameters
        background_color="#1B2632",     # background color
        straight_line_color="#1B2632",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=0,               # linewidth of last circle
        other_circle_lw=0,              # linewidth for other circles
        inner_circle_size=20            # size of inner circle
    )

    fig, ax = baker.make_pizza(
        values,                          # list of values
        figsize=(8, 8.5),                # adjust figsize according to your need
        color_blank_space="same",        # use same color to fill blank space
        slice_colors=slice_colors,       # color for individual slices
        #value_colors=text_colors,        # color for the value-text
        value_bck_colors=slice_colors,   # color for the blank spaces
        blank_alpha=0.4,                 # alpha for blank-space colors
        kwargs_slices=dict(
            edgecolor="white", zorder=2, linewidth=1
        ),                               # values to be used when plotting slices
        kwargs_params=dict(
            color="#EEE9DF", fontsize=11, va="center"
        ),                               # values to be used when adding parameter
        kwargs_values=dict(
            color="#1B2632", fontsize=11, zorder=3,
            bbox=dict(
                edgecolor="#1B2632", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        )                                # values to be used when adding parameter-values
    )

    # add title
    fig.text(
        0.515, 0.975, f"{name}-{team}", size=16,
        ha="center", color="#EEE9DF",fontweight='bold'
    )

    # add subtitle
    fig.text(
        0.515, 0.953,
        f"Percentile Rank against {liga} {position} per 90 min | Season 2023-24",
        size=13,
        ha="center",color="#EEE9DF"
    )

    # add text
    fig.text(
        0.25, 0.925, "Attacking        Passing       Possession      Defending", size=12,
        color="#EEE9DF"
    )
    # add rectangles
    fig.patches.extend([
        plt.Rectangle(
            (0.22, 0.9225), 0.025, 0.021, fill=True, color="#449DD1",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.37, 0.9225), 0.025, 0.021, fill=True, color="#C2ED81",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.495, 0.9225), 0.025, 0.021, fill=True, color="#6F2DBD",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.647, 0.9225), 0.025, 0.021, fill=True, color="#F55D3E",
            transform=fig.transFigure, figure=fig
        ),
    ])
   
    #ax_image = add_image(
    #    fdj_cropped, fig, left=0.425, bottom=0.443, width=0.17, height=0.115
    #)   # these values might differ when you are plotting


    # edit result_df
    result_df.set_index('Category',inplace=True)
    result_df['Value'] = result_df['Value'].round(2)
    return fig,result_df




def highlight_value(value):
    if value >=90:
        color = "#13A658"
    elif value >=80:
        color= "#40E14E"
    elif value >=70:
        color="#79FA48"
    elif value >=50:
        color= "#EBF559"
    elif value >=25:
        color= "#FA6666"
    else: 
        color = "red"
    return f'color: {color}'