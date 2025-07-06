import streamlit as st
import pandas as pd
import requests
from team_name_mapping import team_name_mapping

picture_to_full_name = {
    v["picture_code"]: v["full_name"]
    for v in team_name_mapping.values()
}

st.set_page_config(page_title="ELF Fantasy Spieler", layout="wide")
st.title("🏈 European League Fantasy Spielerübersicht")

@st.cache_data(ttl=300)
def load_data():
    url = "https://fantasy.europeanleague.football/api/getMainPlayerData"
    r = requests.get(url)
    return r.json()

raw_data = load_data()

# Daten extrahieren
records = []
for player in raw_data["data"]:
    base = {
        "Name": player.get("cbsname"),
        "Position": player.get("pos_short"),
        "Team": picture_to_full_name.get(player.get("teamshort"), None),
        "Wert (GC)": player.get("value"),
        "Prediction": player.get("ff_pred"),
        "Status": player.get("status"),
        "#": player.get("uni"),
        "Byeweeks": ", ".join(str(x) for x in player.get("byeweek", []))
    }
    ff_scores = player.get("data", {})
    for season, season_data in ff_scores.items():
        for phase in ["RS", "PO"]:  # Regular Season und Playoffs
            weeks = season_data.get(phase, {})
            for week, stats in weeks.items():
                base[f"{season} {phase} Week {week}"] = stats.get("ff_score", 0)
    
    for season, season_data in ff_scores.items():
        season_total = 0  # Score-Summe für die gesamte Season (RS + PO)
        for phase in ["RS", "PO"]:
            weeks = season_data.get(phase, {})
            for week, stats in weeks.items():
                score = stats.get("ff_score", 0)
                base[f"{season} {phase} Week {week}"] = score
                season_total += score

        base[f"Season {season} total"] = season_total

    records.append(base)

df = pd.DataFrame(records)

# Filter
with st.sidebar:
    st.header("🔎 Filter")
    positions = df["Position"].dropna().unique().tolist()
    teams = df["Team"].dropna().unique().tolist()

    pos_filter = st.multiselect("Position", options=positions, default=positions)
    team_filter = st.multiselect("Team", options=teams, default=teams)

df_filtered = df[df["Position"].isin(pos_filter) & df["Team"].isin(team_filter)]

# Übersicht
st.subheader("📊 Spieler-Statistiken")
st.dataframe(df_filtered.sort_values(by="Wert (GC)", ascending=False), use_container_width=True, hide_index=True)

# Top-Woche-Spieler (z. B. Woche 5)
select_season = st.number_input("Wähle die Saison", step=1, min_value=2021, max_value=2025)
select_phase = st.selectbox("Wähle Regular (RS)/Playoffs (PO)", ["RS", "PO"])
# Filter auf den DataFrame anwenden
df_filtered_season_phase = df_filtered[
    (df_filtered["season"] == select_season) & 
    (df_filtered["phase"] == select_phase)
]

# Eindeutige Wochen extrahieren und sortieren
get_possible_weeks = sorted(df_filtered_season_phase["week"].unique())

# Falls keine Wochen vorhanden sind
if not get_possible_weeks:
    st.warning("Keine Wochen gefunden für diese Auswahl.")
    select_week = None
else:
    select_week = st.selectbox("Wähle die Woche", get_possible_weeks)

st.subheader(f"🔥 Top Spieler in Woche {select_week} (Saison {select_season}, {select_phase})")
week_to_show = f"{select_season} {select_phase} Week {select_week}"
top_week = df_filtered[["Name", "Position", "Team", week_to_show]].dropna().sort_values(week_to_show, ascending=False).head(5)
st.dataframe(top_week, hide_index=True, column_config={week_to_show : "Fantasypoints"})