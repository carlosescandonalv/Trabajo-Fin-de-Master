import streamlit as st
import numpy as np
import pandas as pd
#import altair as alt
import subprocess
import os
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_option_menu import option_menu
from player_percentiles import percentile_plot, highlight_value
from image_extraction import clear_directory, image_extraction, find_first_valid_image
from player_comparison import forward_vs_mean, midfielder_vs_mean, defender_vs_mean
from player_comparison import compare_attackers, compare_midfielders, compare_defenders
from player_recomendation import *
from player_report_llm import llm_call_up
from player_rating import generate_df, get_rating
import re

#@st.cache_data    Nada más se enciende la pagina descargar (demasiado tiempo)
#def run_script_and_load_data():
    # Run the external script
#    script_path = 'Data_extraction.py'
#    subprocess.run(['python', script_path], check=True)


st.title('Player Analysis')


def load_data():
    csv_path = os.path.join('data', 'Big5Leagues_Players_Standard_Stats.csv')
    df = pd.read_csv(csv_path)
    return df


with open('style/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

# Find Players
players = load_data()
players_field = players[players['position']!='GK']
#players_list = players_field['player'].tolist()
players_list = [f"{row['player']} ({row['team']})" for index, row in players_field.iterrows()]
players_list.insert(0,"")
player = st.selectbox("Search a player", players_list)
if player:
    team = re.findall(r'\(.*?\)', player)[0].strip("()")
    player = player.split(" (")[0]
else:
    player = ""

if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = ""

def select_mode(mode):
    st.session_state.selected_mode = mode

# Botones para seleccionar
col1, col2 = st.columns(2,gap="small")
with col1:
    if st.button('League', key='League', help='Compare with same ligue players', args=('Big7',)):
        select_mode("Liga")

with col2:
    if st.button('Big7', key='Big7', help='Compare with Big7 Leagues players', args=('Ligue')):
        select_mode("Big5") 

add_vertical_space(2)

# Comprueba que se introduce nombre y el modo de la sesión
if player and st.session_state.selected_mode:
        col1,col2,col3 = st.columns([0.4,0.4,0.2],gap="small")
        with col1:
            image_extraction(f' {player} {team}')
            pth = find_first_valid_image("images")
            st.image(pth, width=200)
        # Rating extraction
        with col2: 
            st.subheader(f"{player}",divider="gray")
            position = (players[players['player']==player])['position'].values[0]
            print(position)
            st.write(f"Position: {position}")
            nationality = (players[players['player']==player])['nationality'].values[0]
            st.write(f"Nationality: {nationality}")
            
            st.write(f"Team: {team}")
        with col3: 
            performance = generate_df()
            rating = float(get_rating(performance,player,team))
            rating = min(round(rating, 2), 10)
            st.metric("Rating",rating)
        
        
        # Check player position
        age =  (players[players['player']==player])['age'].values[0]
        if position not in ['DF', 'MF', 'FW']:
            pos1, pos2 = position.split(',')
            st.write(f"Player {player} can be compared to two positions: {pos1} and {pos2}")
            selected_position = st.selectbox("Select the position", [pos1, pos2])
        else:
            selected_position = position
        
        fig, results = percentile_plot(player,st.session_state.selected_mode,team,selected_position)
        
        # Dataframe a la izq e imagen a la derecha
        col1, col2 = st.columns([0.4,0.7])
        with col1:
            styled_results = results.style.applymap(highlight_value, subset=['Percentile']).format({'Value':'{:.2f}'})
            st.dataframe(styled_results,height=500)
        with col2:
            st.pyplot(fig)
        
        player_row = players[players['player'] == player]
        col1,col2,col3,col4= st.columns(4)
        col1.metric("Goals",player_row['goals'].values[0])
        col2.metric("Assists",player_row['assists'].values[0])
        col3.metric("xG",player_row['xg'].values[0],(player_row['goals'].values[0]-player_row['xg'].values[0]).round(2))
        col4.metric("xG difference", (player_row['goals'].values[0]-player_row['xg'].values[0]).round(2))

        col1,col2,col3,col4 = st.columns(4)
        passing = pd.read_csv("data/Big5Leagues_Players_passing_Stats.csv")
        col1.metric("Passing %",passing[passing['player'] == player]['passes_pct'].values[0])
        defense = pd.read_csv("data/Big5Leagues_Players_defense_Stats.csv")
        col2.metric("Ground Duels %",defense[defense['player'] == player]['challenge_tackles_pct'].values[0])
        misc = pd.read_csv("data/Big5Leagues_Players_misc_Stats.csv")
        col3.metric("Aerial Duels %",misc[misc['player'] == player]['aerials_won_pct'].values[0])
        
        st.title('Player Stat Comparison')
        
        col1, col2 = st.columns([0.5,0.5])
        with col1:
            value = int(player_row['minutes_90s'].values[0])
            value_max = int(players['minutes_90s'].max())
            threshold = st.number_input("Select Match Threshold",value=value,min_value=1, max_value=value_max)
            if selected_position =='FW':
                comp = forward_vs_mean(player,st.session_state.selected_mode,team,threshold)
                st.image("a.png")
            elif selected_position == 'MF':
                comp = midfielder_vs_mean(player,st.session_state.selected_mode,team,threshold)
                st.image("a.png")
            elif selected_position == 'DF':
                comp = defender_vs_mean(player,st.session_state.selected_mode,team,threshold)
                st.image("a.png")
        with col2:
            min_threshold_mean = int(players['minutes_90s'].mean())
            list_comparison = players_field[players_field['position']==selected_position]['player'].tolist()
            list_comparison.insert(0,"")
            comp_player=st.selectbox(f"Compare with another {selected_position}",list_comparison)
            if comp_player:
                if selected_position == 'FW':
                    compare_attackers(player,comp_player,min_threshold_mean)
                    st.image("b.png")
                elif selected_position == 'MF':
                    compare_midfielders(player,comp_player,min_threshold_mean)
                    st.image("b.png")
                elif selected_position == 'DF':
                    compare_defenders(player,comp_player,min_threshold_mean)
                    st.image("b.png")


        #### Player Recommender
        st.title('Player Recommender')
        test_df = create_test_df(player,selected_position,team,st.session_state.selected_mode)
        test_df.fillna(0,inplace=True)

        number_of_sim= st.slider("Select a number from 1 to 10", min_value=1, max_value=10, value=5)
        similar_players, similarity_scores=recommend_similar_players(test_df,player,team,number_of_sim)
        
        similar_players = preprocess_df(similar_players,selected_position)
        
        new_index = similar_players.index[1:]
        sim_df = pd.DataFrame({'Similarity Score %': similarity_scores}, index=new_index)
        sim_df['Similarity Score %'] = (sim_df['Similarity Score %'] * 100)
        sim_df['Team'] = similar_players.loc[new_index, 'team'].values
        sim_df = sim_df[['Team', 'Similarity Score %']]
        
        
        st.table(sim_df)
        
        sim_table= make_plottable_table(similar_players)
        st.pyplot(sim_table)
        
        similar_recommend_list = sim_df.index.insert(0,"")
        sim_play=st.selectbox("Compare with any recommended players",similar_recommend_list)
        
        if sim_play:
            left_co, cent_co,last_co = st.columns([0.1,0.6,0.3])
            with cent_co:
                if selected_position == 'FW':
                    compare_attackers(player,sim_play,min_threshold_mean)
                    st.image("b.png",width=500)
                elif selected_position == 'MF':
                    compare_midfielders(player,sim_play,min_threshold_mean)
                    st.image("b.png",width=500)
                elif selected_position == 'DF':
                    compare_defenders(player,sim_play,min_threshold_mean)
                    st.image("b.png",width=500)

        #### Player Report
        st.title('Player Report')

        image_extraction(player)
        pth = find_first_valid_image("images")
        st.image(pth, width=200)

        if selected_position == "FW":
            position = "Forward"
        elif selected_position =="MF":
            position = "Midfielder"
        elif selected_position =="DF":
            position = "Defender"

        if st.session_state.selected_mode == "Liga":
            modo = "against same League"
        elif st.session_state.selected_mode == "Big5":
            modo = "against European Big 5 Leagues"
        report = llm_call_up(player,age,team,position,modo,results)
        st.write(report)



#def main():
    #with st.spinner('Running script and downloading CSV...'):
    #    run_script_and_load_data()

    #st.success('Script executed and download complete!')


#if __name__ == '__main__':
#    main()