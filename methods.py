import streamlit as st
import requests
import json
import pandas as pd

@st.cache_data(ttl=300)
def load_json_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def load_elf_game_from_xml(game_id):
    """
    Lädt ein ELF-Spiel im JSON-Format (als XML deklariert) von der European League of Football API.

    Args:
        game_id (str): Die Game-ID, z.B. "hdmb2507"

    Returns:
        dict: Das Spiel als Python-Dictionary (JSON)

    Raises:
        requests.HTTPError: Wenn ein HTTP-Fehler auftritt
        json.JSONDecodeError: Wenn die Antwort kein gültiges JSON ist
    """
    url = f"https://europeanleague.football/api/game/{game_id}/xml"
    response = requests.get(url)
    response.raise_for_status()  # wirft Fehler bei 4xx/5xx

    try:
        json_str = response.content.decode("utf-8")
        data_dict = json.loads(json_str)
        fbgame = data_dict.get('fbgame', {})
        if not fbgame:
            raise ValueError("Keine gültigen Spieldaten gefunden in der Antwort.")
        return fbgame["_attributes"], fbgame["venue"], fbgame["team"],# fbgame["scores"], fbgame["drives"], fbgame["plays"]
    except json.JSONDecodeError as e:
        raise ValueError(f"Antwort konnte nicht als JSON geparst werden: {e}")

def ensure_dict(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return {}
    return {}

cookie_token = st.secrets["fantasy"]["api_token"]
@st.cache_data(ttl=300)
def get_leaderboard(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie_token,  # Gültigen Token einfügen
    }

    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        leaderboard = data.get("pageProps", {}).get("serverData", {})
        leaderboard_df = pd.DataFrame(leaderboard)
        leaderboard_df.index = leaderboard_df.index + 1  # Index anpassen, damit er bei 1 beginnt
        leaderboard_df.columns = ["Player", "Total Points"]
        leaderboard_df = leaderboard_df.reset_index().rename(columns={"index": "Place"})
        leaderboard_df["Place"] = leaderboard_df["Place"].astype(int)  # Stelle als Integer
        leaderboard_df = leaderboard_df[leaderboard_df["Total Points"] > 0]  # Nur Teams mit Punkten anzeigen
        return leaderboard_df
    except Exception as e:
        st.write("Fehler beim Parsen der JSON-Antwort:", e)
        st.write("Antwortinhalt:", response.text[:500])
        return {}

def get_team(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie_token,  # Gültigen Token einfügen
    }

    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        team_data = data.get("pageProps", {}).get("initialTeam", {})
        team_data_df = pd.read_json(json.dumps(team_data), orient="index")
        return team_data_df
    except Exception as e:
        st.write("Fehler beim Parsen der JSON-Antwort:", e)
        st.write("Antwortinhalt:", response.text[:500])
        return {}