import streamlit as st
import pandas as pd
import json
import requests
from methods import load_json_data, ensure_dict, load_elf_game_from_xml, get_leaderboard, get_team
from team_name_mapping import team_name_mapping
from parse_elf_game import get_game_stats

team_name_from_code = {team_name_mapping['picture_code']: team_name_mapping['full_name'] for team_name_mapping in team_name_mapping.values()}

st.set_page_config(page_title="ELF Fantasy Spieler")
st.title("🏈 European League Fantasy Spielerübersicht")

# Daten laden
fantasyplayer_url = "https://fantasy.europeanleague.football/api/getMainPlayerData"
mainplayerdata = load_json_data(fantasyplayer_url)

# DataFrame bauen
df = pd.DataFrame(mainplayerdata["data"])

# Falls Spalten fehlen, nicht umbenennen, Pandas zieht es automatisch
# Falls nötig, kannst du hier prüfen:
# st.write(df.columns)

# "data" als dict parsen, falls es ein String ist
def parse_data(val):
    if isinstance(val, str):
        return json.loads(val)
    if isinstance(val, dict):
        return val
    return {}

df["data_json"] = df["data"].apply(parse_data)

# Auflösen in flache Struktur mit MultiIndex
records = []
for _, row in df.iterrows():
    player_info = {k: v for k, v in row.items() if k not in ["data", "data_json"]}
    data_json = row["data_json"]

    for year, seasons_raw in data_json.items():
        seasons = ensure_dict(seasons_raw)
        for season, weeks_raw in seasons.items():
            weeks = ensure_dict(weeks_raw)
            for week, stats in weeks.items():
                records.append({
                    "player_id": row["_id"],
                    "year": year,
                    "season": season,
                    "week": int(week),
                    **player_info,
                    **stats
                })

df_expanded = pd.DataFrame(records)
df_expanded.set_index(["player_id", "year", "season", "week"], inplace=True)
df_expanded['teamshort'] = df_expanded['teamshort'].map(team_name_from_code)
df_expanded["headshot"] = f"https://storage.googleapis.com/leaguetool-dfc3d.appspot.com/Images/Player/cropped/thumbs/" + df_expanded['id'].astype(str) + "_200x200.png"

# Ausgabe: die ersten 50 Zeilen des aufgelösten DataFrames anzeigen
show_week = st.checkbox("Zeige nur die aktuelle Woche", value=True)
current_week = 8
current_year = 2025
current_season = "RS"

top_players = {"QB" : 12,"RB" : 24,  "WR" : 24, "TE" : 12, "K" : 12, "D/ST" : 12}

select_week = st.selectbox(
    "Wähle eine Woche aus:",
    options=[f"Aktuelle Woche ({current_week})"] + [f"Woche {i}" for i in range(1, 11)],
    index=0
)
if select_week == f"Aktuelle Woche ({current_week})":
    selected_week = current_week
else:
    selected_week = int(select_week.split(" ")[-1])

if show_week:
    filtered_df = df_expanded[
        (df_expanded.index.get_level_values("year") == str(current_year)) &
        (df_expanded.index.get_level_values("season") == current_season) &
        (df_expanded.index.get_level_values("week") == selected_week)
    ]
    # st.dataframe(filtered_df)
    st.write("Top Spieler je Position in der aktuellen Woche:")
    positions = filtered_df["pos_short"].unique()
    for pos, number in top_players.items():
        if pos in positions:
            top_players_pos = filtered_df[filtered_df["pos_short"] == pos].nlargest(number, "ff_score")
            st.write(f"**Top {number} {pos}**:")
            st.dataframe(top_players_pos[["cbsname", 'headshot', "ff_score", "teamshort", "value"]],
                        column_config={"headshot": st.column_config.ImageColumn("Bild")},
                        hide_index=True)
else:
    st.dataframe(df_expanded)

st.subheader("Top Fantasy Spieler der Saison")
df_expanded_season = df_expanded[
    (df_expanded.index.get_level_values("year") == str(current_year)) &
    (df_expanded.index.get_level_values("season") == current_season)
]
df_expanded_season = df_expanded_season.groupby(['_id', 'cbsname', 'pos_short', 'headshot', 'teamshort', 'value'])['ff_score'].sum().reset_index()
st.dataframe(df_expanded_season.nlargest(50, "ff_score")[["cbsname", 'headshot', 'pos_short', "ff_score", "teamshort", "value"]],
             column_config={"headshot": st.column_config.ImageColumn("Bild")},
             hide_index=True)

base_url = st.secrets["elf"]["base_url"]
# cookie = st.secrets["elf"]["api_token"]
leaderboard_url = base_url.format("league")
team_url = base_url.format("team")