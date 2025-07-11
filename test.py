import requests

url = "https://europeanleague.football/api/scoreboard"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "br",  # Brotli erlaubt, automatisch entpackt
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://europeanleague.football/games/scoreboard",
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()  # keine manuelle Brotli-Verarbeitung nötig
except Exception as e:
    print(f"Fehler beim Abrufen oder Parsen der Daten: {e}")
    data = []

statcrewIDs = []

# Sicherstellen, dass es eine Liste von Spielen ist
if isinstance(data, list):
    for game in data:
        if isinstance(game, dict) and 'statcrewID' in game:
            statcrewID = game['statcrewID']
            if statcrewID not in statcrewIDs:
                statcrewIDs.append(statcrewID)
else:
    print("Antwort ist kein Spiele-Array:")
    print(data)

print(data)
