import streamlit as st
import database_access as db
from streamlit_extras.add_vertical_space import add_vertical_space


st.set_page_config(page_title='La Liga Performance', page_icon=':soccer')

st.title("Database Access")
seasons = db.season_list()
season = st.selectbox("Select Season",seasons)
col1, col2 = st.columns([0.3,0.7])
with col1:
    table_df = db.table_extraction(season)
    
    table_ind = table_df.rename(columns={'team':'Team','matches_won': 'W', 'matches_drawn': 'D','matches_lost': 'L',
                              'goals_scored': 'G','goals_received': 'GA',
                              'points': 'Pts'})
   
    table_ind = table_ind.sort_values(by='Pts', ascending=False).reset_index(drop=True)
    table_ind.index = table_ind.index + 1

    st.dataframe(table_ind.style.apply(db.color_rows, axis=1))
with col2:
    points_dev = db.table_plot(table_df)
    st.plotly_chart(points_dev)

# Matches
st.subheader("Match overview")
col1, col2 = st.columns([0.5,0.5])
teams = db.team_list(season)
teams.insert(0,"")
with col1: 
    home = st.selectbox("Select Home Team",teams)
    
with col2: 
    away = st.selectbox("Select Away Team",teams)
    
if home and away:
    if home == away:
        st.write("Home and Away team can't be equal")    
    else:
        home_img,h1,h2 = db.get_team_info(home)
        away_img,a1,a2 = db.get_team_info(away)
        pass_data_home, pass_data_away,df_pass = db.match_info(home,away,season)
        col1, col2 = st.columns([0.5,0.5])
        with col1: 
            match_network = db.pass_network(pass_data_home,df_pass,home,away,5,h1,h2,home_img)
            st.pyplot(match_network)
        with col2: 
            match_network = db.pass_network(pass_data_away,df_pass,away,home,5,a1,a2,away_img)
            st.pyplot(match_network)


st.subheader("Team overview")
teams_list = db.team_list(season)

teams_list.insert(0,"")
team = st.selectbox("Search a team", teams_list)

add_vertical_space(2)

if team:
    col1,col2,col3 =st.columns([0.2,0.4,0.4],gap='small')
    with col1:
        team_img,c1,c2 = db.get_team_info(team)
        st.image(team_img)
    with col2:
        st.header(team)
        df = db.get_team_event_xi(team,season)
        xi_df, full_squad = db.get_xi(df)
        full_squad.rename(columns={'player_name':'Name','player_number': 'ShirtN', 'total_minutes_played': 'Minutes'}, inplace=True)
        full_squad.set_index('Name', inplace=True)
        st.dataframe(full_squad,height=320,width=400)
    with col3:
        df_pass = df[(df['type'].isin(['Pass','BallTouch'])) & (df['outcome'] == 'Successful')]
        average_locations = df_pass.groupby('player_name').agg({'x':['mean'],'y':['mean']})
        average_locations.reset_index(inplace=True)
        for i,player in xi_df.iterrows():
            player = player['player_name']
            pos_row = average_locations[average_locations['player_name']==player]
            xi_df.at[i, 'x'] = pos_row['x'].values[0]
            xi_df.at[i, 'y'] = pos_row['y'].values[0]

        initial_xi =db.draw_initial_xi(xi_df,team,c1,c2)
        st.pyplot(initial_xi)




    # Section passes and goals development
    col1,col2,col3,col4 =st.columns([0.3,0.2,0.2,0.3],vertical_alignment='center')
    goals_fig,goals_scored,goals_conceded = db.goals_development(team,season)

    with col2:
        st.metric("Goals scored",goals_scored)
    with col3:
        st.metric("Goals conceded",goals_conceded)

    st.plotly_chart(goals_fig)



    points_fig = db.pass_development(team,season)
    st.plotly_chart(points_fig)

    st.subheader("Player overview")
    player_names = db.search_players(team,season)
    player_names.insert(0,"")
    player = st.selectbox(f"Select a player from {team}",player_names)
    if player:
        col1,col2 = st.columns([0.5,0.5])
        with col1:
            heatmap = db.player_heatmap(player,season)
            st.pyplot(heatmap)
        