#Author : Alex Miano
#Date : 2023-05-28
#Description : This is a script that scrapes the odibets website and predicts the next possible outcome for a team
#Version : 1.0
#Usage : python3 goal.py
#Dependencies : BeautifulSoup, requests, time, datetime

#============================================================
#  link with the Author in Github  _Mianohh                 #
#============================================================

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

def countdown(seconds):
    for i in reversed(range(seconds + 1)):
        minutes = i // 60
        seconds_left = i % 60
        print(f"{minutes:02d}:{seconds_left:02d}", end="\r")
        time.sleep(1)
    print()

def get_next_game_teams():
    # Send a GET request to the specified URL
    url = "https://odibets.com/league"
    response = requests.get(url)

    # Create a BeautifulSoup object and parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the game containers in the content
    game_containers = soup.find_all('div', {'class': 'event'})

    if not game_containers:
        # If there are no game containers, wait for 10 seconds and retry
        print('Error: No games found. Retrying in 10 seconds...')
        time.sleep(10)
        return get_next_game_teams()

    # Get the teams for the next game
    game = game_containers[0]
    home_team = game.find('div', {'class': 'team'}).text.strip()
    away_team = game.find_all('div', {'class': 'team'})[1].text.strip()

    return home_team, away_team

while True:
    # Get the teams playing in the next game
    next_game_home_team, next_game_away_team = get_next_game_teams()

    # Create a URL to scrape the data from
    url = f'https://odibets.com/league?br=1&tab=results&h2h={next_game_home_team}&h2h={next_game_away_team}'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    team_details = {}
    max_points = 0

    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')
        if home_team not in team_details:
            team_details[home_team] = []
        team_details[home_team].append({'scored': home_score, 'conceded': away_score, 'opponent': away_team})

        if away_team not in team_details:
            team_details[away_team] = []
        team_details[away_team].append({'scored': away_score, 'conceded': home_score, 'opponent': home_team})

    # Define a function to compute goal stats
    def compute_goal_stats(details):
        total_scored = 0
        total_conceded = 0
        games_over_2_5 = 0
        games_both_scored = 0
        for r in details:
            total_scored += int(r['scored'])
            total_conceded += int(r['conceded'])
            if int(r['scored']) + int(r['conceded']) > 2:
                games_over_2_5 += 1
            if int(r['scored']) > 0 and int(r['conceded']) > 0:
                games_both_scored += 1
        avg_scored = total_scored / len(details)
        avg_conceded = total_conceded / len(details)
        return {'avg_scored': avg_scored, 'avg_conceded': avg_conceded, 'games_over_2_5': games_over_2_5, 'games_both_scored': games_both_scored}

    # Define a function to get the rank of each team
    def get_team_rank(teams):
        team_rank = sorted(teams, key=lambda x: x['points'], reverse=True)
        for i in range(0, 4):
            team_rank[i]['position'] = i + 1
            team_rank[i]['color'] = 'GREEN'
        for i in range(-4, 0):
            team_rank[i]['position'] = len(team_rank) + i + 1
            team_rank[i]['color'] = 'RED'
        for i in range(4, len(team_rank)-4):
            team_rank[i]['position'] = i + 1
            team_rank[i]['color'] = 'WHITE'
        return sorted(team_rank, key=lambda x: x['position'])

    # Perform analysis for each team
    teams = []
    for team, details in team_details.items():
        goal_stats = compute_goal_stats(details)
        last_4_games = details[-4:]
        team_points = 0
        for r in last_4_games:
            if int(r['scored']) > int(r['conceded']):
                team_points += 3
            elif int(r['scored']) == int(r['conceded']):
                team_points += 1
        teams.append({'team_name': team, 'points': team_points, 'goal_stats': goal_stats})
        if team_points > max_points:
            max_points = team_points

    # Rank the teams based on points scored
    ranked_teams = get_team_rank(teams)

    # Predictions for top 3 teams
    for team in ranked_teams[0:3]:
        print(f"\n{team['team_name']} - Points: {team['points']}")
        if team['goal_stats']['games_over_2_5'] > len(team_details[team['team_name']])/2:
            print(f"Prediction 1: {team['team_name']} and their opponent are likely to have over 2.5 goals in the next game")
        elif team['goal_stats']['games_over_2_5'] == len(team_details[team['team_name']])/2:
            print(f"Prediction 1: There is a balanced chance that {team['team_name']} and their opponent will have over 2.5 goals in the next game")
        else:
            print(f"Prediction 1: It is unlikely that {team['team_name']} and their opponent will have over 2.5 goals in the next game")

        if team['goal_stats']['games_both_scored'] > len(team_details[team['team_name']])/2:
            print(f"Prediction 2: Both teams are likely to score in the next game involving {team['team_name']}")
        elif team['goal_stats']['games_both_scored'] == len(team_details[team['team_name']])/2:
            print(f"Prediction 2: There is a balanced chance that both teams will score in the next game involving {team['team_name']}")
        else:
            print(f"Prediction 2: It is unlikely that both teams will score in the next game involving {team['team_name']}")

        next_game_opponent = team_details[team['team_name']][-1]['opponent'] # get the team playing against the top team in their next game
        if next_game_opponent.lower() == next_game_home_team.lower() or next_game_opponent.lower() == next_game_away_team.lower():
            if max_points - team['points'] <= 3:
                if max_points - team['points'] == 3:
                    print(f"Prediction 3: {team['team_name']} is likely to win the next game against {next_game_opponent} by 3 or more goals")
                elif max_points - team['points'] == 2:
                    print(f"Prediction 3: {team['team_name']} is likely to win the next game against {next_game_opponent} by 2 or more goals")
                elif max_points - team['points'] == 1:
                    print(f"Prediction 3: {team['team_name']} is likely to win the next game against {next_game_opponent} by 1 goal")
                elif max_points - team['points'] == 0:
                    print(f"Prediction 3: {team['team_name']} and {next_game_opponent} are likely to draw in the next game")
            else:
                print(f"Prediction 3: {next_game_opponent} is likely to win the next game against {team['team_name']}")
    # Wait for 120 seconds before making the next request
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('=' * 100)
    countdown(117)
 #======================================================================
#   WARNING: This script is for educational purposes only and should    #
#   Betting can lead to financial loss and addiction.                   #
#   Please bet responsibly and seek help if needed                      #
#======================================================================


#Success is not final; failure is not fatal: It is the courage to continue that counts.