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
    ff_scores = player.get("data", {}).get("2025", {}).get("RS", {})
    for week, stats in ff_scores.items():
        base[f"Week {week}"] = stats.get("ff_score", 0)
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
st.dataframe(df_filtered.sort_values(by="Wert (GC)", ascending=False), use_container_width=True)

# Top-Woche-Spieler (z. B. Woche 5)
if "Week 5" in df.columns:
    st.subheader("🔥 Top Spieler in Woche 5")
    top_week = df_filtered[["Name", "Position", "Team", "Week 5"]].dropna().sort_values("Week 5", ascending=False).head(5)
    st.table(top_week)

# Optional: CSV Export
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ CSV exportieren", csv, file_name="elf_fantasy_players.csv")
