import requests
import json
from pathlib import Path
from datetime import datetime
from team_name_mapping import team_name_mapping

schedule_url = "https://europeanleague.football/api/scoreboard"

def fetch_schedule():
    response = requests.get(schedule_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching schedule: {response.status_code}")
        return None
schedule_list = fetch_schedule()

for game in schedule_list:
    id = game['statcrewID']
    hometeam = id[:2]
    if hometeam in team_name_mapping:
        hometeam = team_name_mapping[hometeam]["full_name"]
    homescore = game['homeScore']
    awayteam = id[2:4]
    if awayteam in team_name_mapping:
        awayteam = team_name_mapping[awayteam]["full_name"]
    awayscore = game['awayScore']
    week = int(id[-2:])
    print(f"Game ID: {id}, Week: {week}, Home: {hometeam} ({homescore}), Away: {awayteam} ({awayscore})")
    