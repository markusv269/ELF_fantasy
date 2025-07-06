import requests
import xmltodict
import json
from pathlib import Path

# 1. XML von URL laden
url = "https://europeanleague.football/api/game/hdmb2507/xml"
response = requests.get(url)
xml_content = response.content
json_str = xml_content.decode("utf-8")
data_dict = json.loads(json_str)
# Auf fbgame > team zugreifen (Liste von Teams: Heim & Auswärts)
teams = data_dict['fbgame']['team']

# Beispiel: Teams in vereinfachter Form extrahieren
simplified_teams = []
for team in teams:
    team_info = team['_attributes']
    linescore = team.get('linescore', {}).get('_attributes', {})
    totals = team.get('totals', {}).get('_attributes', {})

    simplified_teams.append({
        'team_id': team_info.get('id'),
        'team_name': team_info.get('name'),
        'vh': team_info.get('vh'),
        'score': linescore.get('score'),
        'plays': totals.get('totoff_plays'),
        'yards': totals.get('totoff_yards'),
        'avg': totals.get('totoff_avg'),
    })

# Spieler extrahieren (nur für ein Team als Beispiel)
players1 = teams[0].get('player', [])
players2 = teams[1].get('player', [])

simplified_players = []
for p in players1 + players2:
    player_data = p['_attributes']
    player_entry = {
        'id': player_data['id'],
        'name': player_data['name'],
        'uni': player_data['uni'],
        'gp': player_data.get('gp'),
    }

    # Beispiel: Defense-Stats, falls vorhanden
    if 'defense' in p:
        defense_stats = p['defense']['_attributes']
        player_entry.update({f"def_{k}": v for k, v in defense_stats.items()})

    # Beispiel: Receiving-Stats, falls vorhanden
    if 'rcv' in p:
        rcv_stats = p['rcv']['_attributes']
        player_entry.update({f"rcv_{k}": v for k, v in rcv_stats.items()})

    simplified_players.append(player_entry)

# Ergebnis z. B. als JSON-Dateien speichern
Path("output").mkdir(exist_ok=True)

with open("output/teams.json", "w", encoding="utf-8") as f:
    json.dump(simplified_teams, f, indent=2, ensure_ascii=False)

with open("output/players.json", "w", encoding="utf-8") as f:
    json.dump(simplified_players, f, indent=2, ensure_ascii=False)

