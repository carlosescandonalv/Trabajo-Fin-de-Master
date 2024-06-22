import requests
import pandas as pd
import os
from bs4 import BeautifulSoup, Comment
import re

url = "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
response = requests.get(url,
                        headers={"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
url2 = "https://fbref.com/en/comps/23/stats/Eredivisie-Stats"
response2 = requests.get(url2,
                        headers={"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
url3= "https://fbref.com/en/comps/32/stats/Primeira-Liga-Stats"
response3 = requests.get(url3,
                        headers={"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})


soup = BeautifulSoup(response.text, 'html.parser')
soup2= BeautifulSoup(response2.text,'html.parser')
soup3 = BeautifulSoup(response3.text,'html.parser')

# Find all <tr> elements within the <tbody>
rows = soup.find('tbody').find_all('tr')


data = []

header_row = rows[0]
header_cells = header_row.find_all('td', {'data-stat': True})
column_names = [cell['data-stat'] for cell in header_cells]


for row in rows:
    cells = row.find_all('td', {'data-stat': True})
    row_data = {}
    for cell in cells:
        row_data[cell['data-stat']] = cell.get_text(strip=True)
    data.append(row_data)

df = pd.DataFrame(data, columns=column_names)

# Find all HTML comments
comments = soup2.find_all(text=lambda text: isinstance(text, Comment))

# Parse and extract the HTML content within the comments
comment_html_list = []

for comment in comments:
    comment_soup = BeautifulSoup(comment, 'html.parser')
    comment_html = comment_soup.prettify()
    comment_html_list.append(comment_html)
# Define a list to store the filtered HTML content
filtered_html_list = []

for comment_html in comment_html_list:
    comment_soup = BeautifulSoup(comment_html, 'html.parser')
    target_element = comment_soup.find('div', {'class': 'table_container', 'id': 'div_stats_standard'})

    if target_element:
        # If the element is found, add its HTML content to the filtered list
        filtered_html_list.append(target_element.prettify())

soup = BeautifulSoup(filtered_html_list[0], 'html.parser')
stats = soup.find('tbody')
rows = stats.find_all('tr')
#print(tbody_content)

data = []

for row in rows:
    cells = row.find_all('td', {'data-stat': True})
    row_data = {}
    for cell in cells:
        row_data[cell['data-stat']] = cell.get_text(strip=True)
    data.append(row_data)

df2 = pd.DataFrame(data, columns=column_names)
df2['comp_level'] = 'Eredivisie'



######################################## Primeira Liga ####################################################3
comments = soup3.find_all(text=lambda text: isinstance(text, Comment))

# Parse and extract the HTML content within the comments
comment_html_list = []

for comment in comments:
    comment_soup = BeautifulSoup(comment, 'html.parser')
    comment_html = comment_soup.prettify()
    comment_html_list.append(comment_html)
# Define a list to store the filtered HTML content
filtered_html_list = []

for comment_html in comment_html_list:
    comment_soup = BeautifulSoup(comment_html, 'html.parser')
    target_element = comment_soup.find('div', {'class': 'table_container', 'id': 'div_stats_standard'})

    if target_element:
        # If the element is found, add its HTML content to the filtered list
        filtered_html_list.append(target_element.prettify())

soup = BeautifulSoup(filtered_html_list[0], 'html.parser')
stats = soup.find('tbody')
rows = stats.find_all('tr')
#print(tbody_content)

data = []

for row in rows:
    cells = row.find_all('td', {'data-stat': True})
    row_data = {}
    for cell in cells:
        row_data[cell['data-stat']] = cell.get_text(strip=True)
    data.append(row_data)

df3 = pd.DataFrame(data, columns=column_names)
df3['comp_level'] = 'Primeira Liga'

# Combine all dataframes
combined_df = pd.concat([df, df2,df3],ignore_index=True)

df = combined_df
# Extract only the last three characters from the "nationality" column
df['nationality'] = df['nationality'].str[-3:]
df.drop(columns=['matches'],inplace=True)
df= df.dropna()
df = df[df['age'] != '']
df['age'] = df['age'].str[:2].astype(int)
df['comp_level'] = df['comp_level'].apply(lambda x: re.sub(r'^[^A-Z]*', '', x))
# Minutes comma removal
df['minutes'] = df['minutes'].str.replace(",","")
df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')

excluded_columns = ['player', 'nationality', 'position','team','birth_year','comp_level']
columns_to_process = [col for col in df.columns if col not in excluded_columns]
df[columns_to_process] = df[columns_to_process].apply(lambda col: pd.to_numeric(col, errors='coerce'))

df['xg'] = pd.to_numeric(df['xg'], errors='coerce')

df.fillna(0,inplace=True)


path = "data"
csv_file_name = f'Big5Leagues_Players_Standard_Stats.csv'
file_path = os.path.join(path, csv_file_name)
if os.path.exists(file_path):
      # If it exists, delete it
      os.remove(file_path)
df.to_csv(file_path, index=False)





## Function to 
Stat_type = ['passing','shooting','passing_types','gca','defense','possession','misc']

def extraction_allstats(Stat_type):
  for stat in Stat_type:
      url = f'https://fbref.com/en/comps/Big5/{stat}/players/Big-5-European-Leagues-Stats'
      response = requests.get(url,headers={"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
      response.status_code
      soup = BeautifulSoup(response.text, 'html.parser')
      #rows = soup.find('tbody').find_all('tr')
      stats = soup.find('tbody')
      rows = stats.find_all('tr')
      data=[]
      for tr in rows:
        row_data = {}
        player_name = tr.find('th', {'data-stat': 'player'})
        player_country = tr.find('th', {'data-stat': 'nationality'})
        player_team = tr.find('th', {'data-stat': 'team'})
        if player_name:
          player_name_a = player_name.find('a')
          if player_name_a:
            row_data['player'] = player_name_a.get_text(strip=True)
        if player_country:
          player_country_a = player_country.find('a')
          if player_country_a:
            row_data['nationality'] = player_country_a.get_text(strip=True)
        if player_team:
          player_team_a = player_team.find('a')
          if player_team_a:
            row_data['team'] = player_team_a.get_text(strip=True)

        cells = tr.find_all('td')  # Extract <td> elements within the row
        for cell in cells:
          data_stat = cell.get('data-stat', '')  # Get the data-stat attribute as column name
          value = cell.get_text(strip=True)  # Get the text content within the <td> element
          row_data[data_stat] = value  # Add data to the row_data dictionary

        data.append(row_data)  # Add the row_data dictionary to the data list

      df = pd.DataFrame(data)

      leagues = ['Eredivisie','Primeira Liga']
      for league in leagues:
        if league=='Eredivisie':
          url2=f'https://fbref.com/en/comps/23/{stat}/Eredivisie-Stats'
        else:
          url2=f'https://fbref.com/en/comps/32/{stat}/Primeira-Liga-Stats'
        response2 = requests.get(url2,headers={"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'})
        soup2 = BeautifulSoup(response2.text,'html.parser')
        # Find all HTML comments
        comments = soup2.find_all(text=lambda text: isinstance(text, Comment))

        # Parse and extract the HTML content within the comments
        comment_html_list = []

        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            comment_html = comment_soup.prettify()
            comment_html_list.append(comment_html)
        # Define a list to store the filtered HTML content
        filtered_html_list = []

        for comment_html in comment_html_list:
            comment_soup = BeautifulSoup(comment_html, 'html.parser')
            target_element = comment_soup.find('div', {'class': 'table_container', 'id': f'div_stats_{stat}'})

            if target_element:
                # If the element is found, add its HTML content to the filtered list
                filtered_html_list.append(target_element.prettify())

        soup = BeautifulSoup(filtered_html_list[0], 'html.parser')
        stats = soup.find('tbody')
        rows = stats.find_all('tr')
        #print(tbody_content)

        data = []

        for row in rows:
            cells = row.find_all('td', {'data-stat': True})
            row_data = {}
            for cell in cells:
                row_data[cell['data-stat']] = cell.get_text(strip=True)
            data.append(row_data)
        header_row = rows[0]
        header_cells = header_row.find_all('td', {'data-stat': True})
        column_names = [cell['data-stat'] for cell in header_cells]
        df2 = pd.DataFrame(data, columns=column_names)
        df2['comp_level'] = league
        df = pd.concat([df,df2],ignore_index=True)


      #Final Preprocess
      # Extract only the last three characters from the "nationality" column
      df['nationality'] = df['nationality'].str[-3:]
      df.drop(columns=['matches'],inplace=True)
      df= df.dropna()
      df = df[df['age'] != '']
      df['age'] = df['age'].str[:2].astype(int)
      df['comp_level'] = df['comp_level'].apply(lambda x: re.sub(r'^[^A-Z]*', '', x))
      # Minutes comma removal
      excluded_columns = ['player', 'nationality', 'position','team','birth_year','comp_level']
      columns_to_process = [col for col in df.columns if col not in excluded_columns]
      df[columns_to_process] = df[columns_to_process].apply(lambda col: pd.to_numeric(col, errors='coerce'))

      df = df.fillna(0)

      path = "data"
      csv_file_name = f'Big5Leagues_Players_{stat}_Stats.csv'
      file_path = os.path.join(path, csv_file_name)
      # Check if the file exists
      if os.path.exists(file_path):
          # If it exists, delete it
          os.remove(file_path)
      df.to_csv(file_path, index=False)


extraction_allstats(Stat_type)
