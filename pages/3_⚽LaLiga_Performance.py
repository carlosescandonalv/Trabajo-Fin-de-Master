import streamlit as st
import database_access as db
from streamlit_extras.add_vertical_space import add_vertical_space


st.set_page_config(page_title='La Liga Performance', page_icon=':soccer')

st.title("Database Access")

teams_list = db.team_list()
teams_list.insert(0,"")
team = st.selectbox("Search a player", teams_list)

add_vertical_space(2)

if team:
    col1,col2,col3 =st.columns([0.2,0.4,0.4],gap='small')
    with col1:
        team_img,c1,c2 = db.get_team_info(team)
        st.image(team_img)
    with col2:
        st.header(team)
        df = db.get_team_event_xi(team)
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
    goals_fig,goals_scored,goals_conceded = db.goals_development(team)

    with col2:
        st.metric("Goals scored",goals_scored)
    with col3:
        st.metric("Goals conceded",goals_conceded)

    st.plotly_chart(goals_fig)



    points_fig = db.pass_development(team)
    st.plotly_chart(points_fig)