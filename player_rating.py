import pandas as pd
import sklearn
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import xgboost as xgb
import joblib

def generate_df():
  std_df = pd.read_csv(f'data/Big5Leagues_Players_Standard_Stats.csv')
  shoot_df = pd.read_csv(f'data/Big5Leagues_Players_shooting_Stats.csv')
  gca_df = pd.read_csv(f'data/Big5Leagues_Players_gca_Stats.csv')
  passing_df = pd.read_csv(f'data/Big5Leagues_Players_passing_Stats.csv')
  defense_df = pd.read_csv(f'data/Big5Leagues_Players_defense_Stats.csv')
  possession_df = pd.read_csv(f'data/Big5Leagues_Players_possession_Stats.csv')
  miscellaneous_df = pd.read_csv(f'data/Big5Leagues_Players_misc_Stats.csv')

  combined_df = std_df[['player','position','team','games','minutes','goals_per90','assists_per90','xg_per90','cards_yellow',
                    'cards_red','progressive_carries','progressive_passes','progressive_passes_received']]

  combined_df = combined_df[combined_df['position']!='GK']
  gca_selected = ['player','team','sca','gca']
  combined_df = pd.merge(combined_df, gca_df[gca_selected], on=['player', 'team'])
  # Passing Stats
  passing_selected = ['player','team','passes_completed','passes_pct','assisted_shots','passes_into_final_third','passes_into_penalty_area']
  combined_df = pd.merge(combined_df, passing_df[passing_selected], on=['player', 'team'])
  # Possession Stats
  possession_selected = ['player','team','take_ons_won','take_ons_won_pct','take_ons_tackled']
  combined_df = pd.merge(combined_df, possession_df[possession_selected], on=['player', 'team'])
  # Defense Stats
  defense_selected = ['player','team','tackles_won','tackles','blocked_shots','blocked_passes','interceptions','clearances','errors']
  combined_df = pd.merge(combined_df, defense_df[defense_selected], on=['player', 'team'])

  # Miscellaneos Stats
  misc_selected = ['player','team','ball_recoveries','aerials_won','aerials_won_pct']
  combined_df = pd.merge(combined_df, miscellaneous_df[misc_selected], on=['player', 'team'])
  combined_df['minutes_per_game'] = combined_df['minutes']/combined_df['games']
  selected_columns =['cards_yellow','cards_red','progressive_carries','progressive_passes','progressive_passes_received',
                    'sca','gca','passes_completed','assisted_shots','passes_into_final_third','passes_into_penalty_area',
                    'take_ons_won','take_ons_tackled','tackles_won','tackles','blocked_shots','blocked_passes','interceptions','clearances',
                    'errors','ball_recoveries','aerials_won']

  for column in selected_columns:
    combined_df[column]= (combined_df[column]/combined_df['minutes'])*90
  
  performance_df = combined_df[['player','position','team','minutes_per_game','goals_per90','assists_per90','xg_per90',
                           'take_ons_won_pct','passes_pct','aerials_won_pct']+selected_columns]
  
  return performance_df


def get_rating(df,player_name,team):
  encoder = OneHotEncoder()
  loaded_model = xgb.Booster()
  loaded_model.load_model('XGBoost/xgb_model.json')
  loaded_encoder = joblib.load('XGBoost/encoder.joblib')

  performance_player = df.loc[(df['player']==player_name) & (df['team']==team)]
  single_instance_df = performance_player
  single_instance_df.drop(columns=['player', 'team'],inplace=True)
  
  # Codificar la columna 'position' de la instancia
  position_encoded_single = loaded_encoder.transform(single_instance_df[['position']]).toarray()
  position_encoded_single_df = pd.DataFrame(position_encoded_single, columns=loaded_encoder.get_feature_names_out(['position']))
  
  # Concatenar las variables codificadas con el resto de las variables de la instancia
  single_instance_df = single_instance_df.drop(columns=['position'])
  single_instance_df = pd.concat([single_instance_df.reset_index(drop=True), position_encoded_single_df], axis=1)

  # Convertir la instancia a DMatrix
  dsingle = xgb.DMatrix(single_instance_df)

  # Hacer la predicción
  predicted_rating = loaded_model.predict(dsingle)

  return predicted_rating