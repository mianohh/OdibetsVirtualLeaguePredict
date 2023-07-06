import requests
from bs4 import BeautifulSoup
from math import exp
from scipy.special import factorial
import datetime
import time

# function to calculate poisson probability
def poisson_probability(k, lam):
    return (lam ** k) * exp(-lam) / factorial(k)

# function to scrape odibets league A
def scrape_odibets_league_A():
    url = 'https://odibets.com/league?br=1&tab=results'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    team_performance = {}

    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')
        if home_team not in team_performance:
            team_performance[home_team] = {'matches': []}
        team_performance[home_team]['matches'].append({'home': True, 'scored': int(home_score), 'conceded': int(away_score)})

        if away_team not in team_performance:
            team_performance[away_team] = {'matches': []}
        team_performance[away_team]['matches'].append({'home': False, 'scored': int(away_score), 'conceded': int(home_score)})

    for team, performance in team_performance.items():
        games_with_goals = 0
        gg = 0
        for match in performance['matches']:
            if match['scored'] > 0 and match['conceded'] > 0:
                gg += 1
            if match['scored'] > 0 or match['conceded'] > 0:
                games_with_goals += 1
        if games_with_goals > 0:
            gg_probability = gg / games_with_goals
            performance['gg_probability'] = gg_probability

    sorted_teams_A = sorted(team_performance.items(), key=lambda x: x[1]['gg_probability'], reverse=True)

    return sorted_teams_A

# function to scrape odibets league B
def scrape_odibets_league_B():
    url = 'https://odibets.com/league?br=1&tab=results'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    team_performance = {}

    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')

        if home_team not in team_performance:
            team_performance[home_team] = {'matches': []}
        team_performance[home_team]['matches'].append({'home': True, 'scored': int(home_score), 'conceded': int(away_score)})

        if away_team not in team_performance:
            team_performance[away_team] = {'matches': []}
        team_performance[away_team]['matches'].append({'home': False, 'scored': int(away_score), 'conceded': int(home_score)})

    for team, performance in team_performance.items():
        games_with_goals = 0
        gg = 0
        goals_scored = sum([match['scored'] for match in performance['matches']])
        goals_conceded = sum([match['conceded'] for match in performance['matches']])
        expected_goals_scored = goals_scored / len(performance['matches'])
        expected_goals_conceded = goals_conceded / len(performance['matches'])

        poisson_scored = [poisson_probability(k, expected_goals_scored) for k in range(1, 10)]
        poisson_conceded = [poisson_probability(k, expected_goals_conceded) for k in range(1, 10)]

        gg_probability = sum([poisson_scored[k-1] * poisson_conceded[k-1] for k in range(1, 10)])
        performance['gg_probability'] = gg_probability

    sorted_teams_B = sorted(team_performance.items(), key=lambda x: x[1]['gg_probability'], reverse=True)

    return sorted_teams_B

# function to scrape odibets script C
def scrape_odibets_script_C():
    url = 'https://odibets.com/league?br=1&tab=results'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    team_performance = {}
    probabilities = []

    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')
        home_score, away_score = int(home_score), int(away_score)

        if home_team not in team_performance:
            team_performance[home_team] = {'games_played': 0, 'goals_scored': 0, 'goals_conceded': 0}
        team_performance[home_team]['games_played'] += 1
        team_performance[home_team]['goals_scored'] += home_score
        team_performance[home_team]['goals_conceded'] += away_score

        if away_team not in team_performance:
            team_performance[away_team] = {'games_played': 0, 'goals_scored': 0, 'goals_conceded': 0}
        team_performance[away_team]['games_played'] += 1
        team_performance[away_team]['goals_scored'] += away_score
        team_performance[away_team]['goals_conceded'] += home_score

    for team, performance in team_performance.items():
        goal_scored = performance['goals_scored']
        goal_conceded = performance['goals_conceded']
        if goal_conceded > 0:
            probability_both_scored = goal_scored / performance['games_played'] * goal_conceded / performance['games_played']
            probabilities.append({'team': team, 'probability_both_scored': probability_both_scored,
                                  'total_games': performance['games_played'], 'total_goals_scored': goal_scored,
                                  'total_goals_conceded': goal_conceded})

    sorted_probabilities_C = sorted(probabilities, key=lambda x: x['probability_both_scored'], reverse=True)

    return sorted_probabilities_C

# function to scrape odibets script D
def scrape_odibets_script_D():
    url = 'https://odibets.com/league?br=1&tab=results'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    team_performance = {}
    probabilities = []

    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')
        home_score, away_score = int(home_score), int(away_score)

        if home_team not in team_performance:
            team_performance[home_team] = {'games_played': 0, 'both_scored': 0, 'no_goal': 0}
        team_performance[home_team]['games_played'] += 1
        if home_score > 0 and away_score > 0:
            team_performance[home_team]['both_scored'] += 1
        else:
            team_performance[home_team]['no_goal'] += 1

        if away_team not in team_performance:
            team_performance[away_team] = {'games_played': 0, 'both_scored': 0, 'no_goal': 0}
        team_performance[away_team]['games_played'] += 1
        if home_score > 0 and away_score > 0:
            team_performance[away_team]['both_scored'] += 1
        else:
            team_performance[away_team]['no_goal'] += 1

    for team, performance in team_performance.items():
        total_games = performance['games_played']
        total_both_scored = performance['both_scored']
        total_no_goal = performance['no_goal']
        if total_games > 0:
            probability_both_scored = total_both_scored / total_games
            probabilities.append({'team': team, 'probability_both_scored': probability_both_scored,
                                  'total_games': total_games, 'total_both_scored': total_both_scored,
                                  'total_no_goal': total_no_goal})

    sorted_probabilities_D = sorted(probabilities, key=lambda x: x['probability_both_scored'], reverse=True)

    return sorted_probabilities_D

# function to scrape odibets script E
def scrape_odibets_script_E():
    url = 'https://odibets.com/league?br=1&tab=results'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    team_performance = {}
    for row in soup.select('tr.results-body'):
        home_team, home_score, away_score, away_team = row.get_text(strip=True, separator='|').split('|')
        if home_team not in team_performance:
            team_performance[home_team] = {'matches': []}
        team_performance[home_team]['matches'].append({'home': True, 'scored': int(home_score), 'conceded': int(away_score)})
        if away_team not in team_performance:
            team_performance[away_team] = {'matches': []}
        team_performance[away_team]['matches'].append({'home': False, 'scored': int(away_score), 'conceded': int(home_score)})
    for team, performance in team_performance.items():
        games_with_goals = 0
        over_2_5 = 0
        gg = 0
        btts_over_2_5 = 0
        for match in performance['matches']:
            if match['scored'] + match['conceded'] > 2:
                over_2_5 += 1
                if match['scored'] > 1 and match['conceded'] > 1:
                    btts_over_2_5 += 1
            if match['scored'] > 0 and match['conceded'] > 0:
                gg += 1
                if match['scored'] > 1 and match['conceded'] > 1:
                    btts_over_2_5 += 1
            games_with_goals += 1
        if games_with_goals > 0:
            over_2_5_probability = over_2_5 / games_with_goals
            gg_probability = gg / games_with_goals
            btts_over_2_5_probability = btts_over_2_5 / games_with_goals
            performance.update({'over_2_5_probability': over_2_5_probability,
                                'gg_probability': gg_probability,
                                'btts_over_2_5_probability': btts_over_2_5_probability})
    sorted_teams = sorted(team_performance.items(), key=lambda x: x[1]['over_2_5_probability'], reverse=True)
    most_probable_team_over_2_5, info1 = max(team_performance.items(), key=lambda x: x[1]['over_2_5_probability'])
    most_probable_team_gg, info2 = max(team_performance.items(), key=lambda x: x[1]['gg_probability'])
    most_probable_team_btts_over_2_5, info3 = max(team_performance.items(), key=lambda x: x[1]['btts_over_2_5_probability'])

    return {'most_probable_team_over_2_5': most_probable_team_over_2_5,
            'most_probable_team_gg': most_probable_team_gg,
            'most_probable_team_btts_over_2_5': most_probable_team_btts_over_2_5}

# loop to run scrape functions and predict outcomes
while True:
    # run all the scrape functions to get latest data
    sorted_teams_A = scrape_odibets_league_A()
    most_probable_team_A, _ = sorted_teams_A[0]

    sorted_teams_B = scrape_odibets_league_B()
    most_probable_team_B, _ = sorted_teams_B[0]

    sorted_probabilities_C = scrape_odibets_script_C()
    most_probable_team_C = sorted_probabilities_C[0]['team']

    sorted_probabilities_D = scrape_odibets_script_D()
    most_probable_team_D = sorted_probabilities_D[0]['team']

    script_E_predictions = scrape_odibets_script_E()

    # print the predictions
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"At {current_time}:")
    print(f"The most probable team for a GG result from script A is {most_probable_team_A}.")
    print(f"The most probable team for a GG result from script B is {most_probable_team_B}.")
    print(f"The most probable team for a GG result from Script C is {most_probable_team_C}.")
    print(f"The most probable team for a GG result from Script D is {most_probable_team_D}.")
    print(f"The most probable team for over 2.5 goals result from script E is {script_E_predictions['most_probable_team_over_2_5']}.")
    print(f"The most probable team for GG result from script E is {script_E_predictions['most_probable_team_gg']}.")
    print(f"The most probable team for both teams to score and over 2.5 goals result from script E is {script_E_predictions['most_probable_team_btts_over_2_5']}.")
    print("=" * 50)
    time.sleep(117)   # wait for 2 minutes before running the next iteration