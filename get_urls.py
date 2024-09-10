import requests
import pandas as pd
from bs4 import BeautifulSoup

base_url = "https://www.transfermarkt.com"
league_url = f"{base_url}/premier-league/startseite/wettbewerb/GB1"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}

leagues_urls = ['https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1',
                'https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1',
                'https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1',
                'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1',
                'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1']

def get_team_urls(leagues_urls):
    team_urls = []
    for league_url in leagues_urls:
        html = requests.get(league_url, headers=headers)
        soup = BeautifulSoup(html.content, 'html.parser')
        teams_table = soup.find('table', class_='items')
        for row in teams_table.find_all('tr')[1:]:
            # Find the cell with the class 'hauptlink no-border-links' which contains the team name
            team_cell = row.find('td', class_='hauptlink no-border-links')
            # Check if the cell is found
            if team_cell:
                # Find the anchor tag within this cell
                link_tag = team_cell.find('a', href=True)
                # Extract the team name from the text of the anchor tag
                if link_tag:
                    team_url = base_url + link_tag['href']
                    team_urls.append(team_url)
    return team_urls


def get_player_urls(team_urls):
    players_urls = []
    valid_positions = ['Attacking Midfield', 'Left Winger', 'Right Winger', 'Center-Forward']
    for team_url in team_urls:
        html = requests.get(team_url, headers=headers)
        soup = BeautifulSoup(html.content, 'html.parser')
        players_table = soup.find('table', class_='items')
        count = 0
        for row in players_table.find_all('tr')[1:]:
            count += 1
            player_cell = row.find('td', class_='hauptlink')
            if count == 3:
                player_name = row.text.replace('\n', '').strip()
                if player_name not in valid_positions:
                    players_urls.pop()
                    count = 0
            if player_cell:
                link_tag = player_cell.find('a', href=True)
                # Extract the team name from the text of the anchor tag
                if link_tag:
                    player_url = base_url + link_tag['href']
                    if player_url not in players_urls:
                        players_urls.append(player_url)
    return players_urls


team_urls = get_team_urls(leagues_urls)
print(team_urls)
print(len(team_urls))
players_urls = get_player_urls(team_urls)
print(players_urls)
print(len(players_urls))
# Create a DataFrame from the player URLs
df = pd.DataFrame(players_urls, columns=['Player URL'])

# Display the DataFrame
print(df)

# Save the DataFrame to a CSV file
df.to_csv('players_urls.csv', index=False)

