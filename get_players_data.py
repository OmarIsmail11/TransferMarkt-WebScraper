import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://www.transfermarkt.com"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}
players_urls = []

with open('players_urls.csv', 'r') as file:
    next(file)
    reader = csv.reader(file)
    for row in reader:
        players_urls.append(row[0])

leagues_rank = {'Premier League': 1, 'LaLiga': 2, 'Bundesliga': 3, 'Serie A': 4, 'Ligue 1': 5,
                'Premier League 2': 150, 'Primera Federación - Gr. II': 106, 'Primera Federación - Gr. I': 22,
                'Segunda Federación - Gr. III': 183 , 'Segunda Federación - Gr. II': 53,
                'Segunda Federación - Gr. I': 120, 'U19 Nachwuchsliga - Gr. B': 250,
                'Regionalliga Südwest': 350}

Leagues_urls = ['https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1',
                'https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1',
                'https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1',
                'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1',
                'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1']

def extract_age(text):
    start = text.find('(')
    end = text.find(')')
    age = text[start+1:end]
    return int(age)

def extract_market_value(text):
    start = text.find('€')
    if 'm' in text:
        end = text.find('m')
        market_value = int(float(text[start + 1:end]) * 1000000.00)
    else:
        end = text.find('k')
        market_value = int(float(text[start + 1:end]) * 1000.00)
    return market_value


def extract_minutes_per_goal(text):
    text = text.replace('.0', '')
    text = text.replace('.', '')
    return int(text)


def extract_contact_expires(text):
    if '-' in text:
        text = text.replace('-', '2030')
        return int(text)
    date = text.strip().split(',')
    return int(date[-1])


def extract_trophie(text):
    end = text.find('x')
    return int(text[:end])

def extract_name(text):
    parts = text.strip().split()
    number = parts[0].lstrip('#')
    name = ' '.join(parts[1:])
    return name

def extract_height(text):
    text = text.replace('m', '').replace(',', '.').strip()
    return float(text)

def get_players_data(players_urls):
    players_data = []
    count = 0
    for player_url in players_urls:
        print(f'Processing Player {count} ...')
        count += 1
        html = requests.get(player_url, headers=headers)
        soup = BeautifulSoup(html.content, 'html.parser')
        name = extract_name(soup.find('h1', class_='data-header__headline-wrapper').text)
        age = extract_age(soup.find('li', class_='data-header__label').find('span', class_='data-header__content').text)
        club = soup.find('div', class_='data-header__club-info').find('span', class_ = 'data-header__club').text.strip()
        league = soup.find('div', class_='data-header__club-info').find('span', class_='data-header__league').text.strip()
        league_rank = leagues_rank[league]
        international_stats = soup.find('div', class_='data-header__info-box').find_all('ul', class_='data-header__items')
        trophies_url = soup.find('div', class_='data-header__badge-container')
        if not trophies_url:
            trophies = 0
        else:
            trophies_url = trophies_url.find('a', href=True)['href']
            trophies_url = base_url + trophies_url
            trophies_html = requests.get(trophies_url, headers=headers)
            trophies_soup = BeautifulSoup(trophies_html.content, 'html.parser')
            trophies_block = trophies_soup.find('div', class_='large-8 columns').find_all('div', class_='row')
            trophies = 0
            for row in trophies_block:
                columns = row.find_all('h2', class_='content-box-headline')
                for column in columns:
                    trophie = extract_trophie(column.text.strip())
                    trophies += trophie
        if not international_stats[2].find('li',class_='data-header__label'):
            is_international = False
            international_caps = 0
            international_goals = 0
        else:
            is_international = True
            international_caps = int(international_stats[2].find_all('li', class_='data-header__label')[1].find_all('a')[0].text)
            international_goals = int(international_stats[2].find_all('li', class_='data-header__label')[1].find_all('a')[1].text)
        height = extract_height(soup.find('div', class_ = 'data-header__details').find_all('ul', class_='data-header__items')[1].find('li',class_='data-header__label').find('span', class_ = 'data-header__content').text)
        foot_contract_block = soup.find('div', class_='large-6 large-pull-6 small-12 columns spielerdatenundfakten').find_all('span')[13:]
        for i in range(len(foot_contract_block)):
            if foot_contract_block[i].text.strip() == 'left' or foot_contract_block[i].text.strip() == 'right':
                foot = foot_contract_block[i].text.strip()
            if foot_contract_block[i].text.strip() == 'Contract expires:':
                contract_expires = extract_contact_expires(foot_contract_block[i+1].text)
                break
        position = soup.find('div', class_ = 'data-header__details').find_all('ul', class_ = 'data-header__items')[1].find_all('li', class_ = 'data-header__label')[1].find('span', class_ = 'data-header__content').text.strip()
        nationality_block = soup.find('div', class_ = 'data-header__details').find_all('ul', class_ = 'data-header__items')[0].find_all('li', class_ = 'data-header__label')
        if len(nationality_block) == 3:
            nationality = nationality_block[2].find('span', class_='data-header__content').text.strip()
        else:
            nationality = nationality_block[1].find('span', class_ = 'data-header__content').text.strip()
        market_value = extract_market_value(soup.find('div', class_='data-header__box--small').find('a').text)
        statistics = soup.find('table', class_='items').find('tfoot').find('tr').find_all('td')
        matches_played = int(statistics[2].text.replace('-', '0').replace("'", ""))
        goals = int(statistics[3].text.replace('-', '0').replace("'", ""))
        assists = int(statistics[4].text.replace('-', '0').replace("'", ""))
        minutes_per_goals = extract_minutes_per_goal(statistics[5].text.replace('-', '0').replace("'", ""))
        minutes_played = int(statistics[6].text.replace('.', '').replace('-', '0').replace("'", ""))
        player_data = {'name': name, 'club': club, 'age': age, 'height': height, 'foot': foot, 'position': position,
                       'nationality': nationality, 'league': league, 'league_rank': league_rank, 'contract_expires': contract_expires,
                       'matches_played': matches_played, 'goals': goals, 'assists': assists,'is_international': is_international,
                       'international_caps': international_caps, 'international_goals': international_goals,
                       'trophies': trophies, 'minutes_played': minutes_played, 'minutes_per_goals': minutes_per_goals,
                       'market_value': market_value}
        players_data.append(player_data)
    return players_data

data = get_players_data(players_urls)
df = pd.DataFrame(data)
df.to_csv('players_data.csv', index=False)