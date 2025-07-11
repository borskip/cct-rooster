import streamlit as st
import datetime
import locale
from pathlib import Path
import json

DATA_FILE = Path("rooster_app_data.json")
MEDEWERKERS = sorted([
    "Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan",
    "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars",
    "Puck", "Bas", "Vera", "Nina"
])
WERKPLEKKEN_CONFIG = [
    {"naam": "Niet ingepland", "emoji": "❌"},
    {"naam": "Kantoor", "emoji": "🏤"},
    {"naam": "Thuiswerk", "emoji": "🏠"},
    {"naam": "Opleiding", "emoji": "🧑‍🏫"},
    {"naam": "IBT", "emoji": "💪"},
    {"naam": "Vakantie/Verlof", "emoji": "🏖️"},
]
WERKPLEK_MAP = {item["naam"]: item for item in WERKPLEKKEN_CONFIG}
DEFAULT_WERKPLEK = "Niet ingepland"

DISCIPLINES = {
    "digi": ["Jan", "Emma", "Sophie", "Tom"],
    "intel": ["Lisa", "Daan", "Eva"],
    "leiding": ["Milan", "Laura", "Rob"],
    "tactiek": ["Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars"]
}

def load_data():
    if not DATA_FILE.exists():
        return {"rooster_data": {}, "bereikbaarheden": {}}
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return {
                "rooster_data": data.get("rooster_data", {}),
                "bereikbaarheden": data.get("bereikbaarheden", {})
            }
    except:
        return {"rooster_data": {}, "bereikbaarheden": {}}

st.set_page_config(page_title="Dagoverzicht", layout="wide")
st.title("📄 Dagoverzicht")

data = load_data()
rooster_data = data["rooster_data"]
bereikbaarheden = data["bereikbaarheden"]

locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
today = datetime.date.today()
dagen = [today, today + datetime.timedelta(days=1), today + datetime.timedelta(days=2)]

for dag in dagen:
    dag_str = dag.strftime("%Y-%m-%d")
    st.subheader(f"{dag.strftime('%A')} {dag.strftime('%d-%m-%Y')}")

    dag_bereikbaar = bereikbaarheden.get(dag_str, {})
    niet_beschikbaar = []

    st.markdown("**Bereikbaarheid per discipline:**")
    for disc in ["digi", "intel", "leiding", "tactiek"]:
        persoon = dag_bereikbaar.get(disc)
        if persoon:
            st.write(f"✅ {disc.capitalize()}: {persoon}")
        else:
            niet_beschikbaar.append(disc.capitalize())

    if niet_beschikbaar:
        disciplines_str = ", ".join(niet_beschikbaar)
        st.error(f"❌ Geen bereikbare medewerker voor: {disciplines_str}")

    st.divider()

    dag_data = rooster_data.get(dag_str, {})
    if dag_data:
        medewerkers = sorted(dag_data.keys())
        aantal_per_rij = 4
        rijtjes = [medewerkers[i:i+aantal_per_rij] for i in range(0, len(medewerkers), aantal_per_rij)]

        for rij in rijtjes:
            cols = st.columns(len(rij))
            for i, medewerker in enumerate(rij):
                werkplek = dag_data.get(medewerker, DEFAULT_WERKPLEK)
                emoji = WERKPLEK_MAP.get(werkplek, WERKPLEK_MAP[DEFAULT_WERKPLEK])["emoji"]

                bereikbaar_disc = None
                for disc, names in DISCIPLINES.items():
                    if dag_bereikbaar.get(disc) == medewerker:
                        bereikbaar_disc = disc.capitalize()
                        break

                tekst = f"{emoji} **{medewerker}**"
                if bereikbaar_disc:
                    tekst += f" ✅ ({bereikbaar_disc})"

                with cols[i]:
                    st.write(tekst)
    else:
        st.write("Geen planning.")
