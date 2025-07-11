import streamlit as st
from streamlit_calendar import calendar
import json
from pathlib import Path
import datetime

# =========================================================================
#                   CONFIGURATIE & CONSTANTEN
# =========================================================================

st.set_page_config(page_title="Maandoverzicht", layout="wide")
st.title("📅 Maandoverzicht")

DATA_FILE = Path("rooster_app_data.json")
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

MEDEWERKERS = sorted([
    "Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob",
    "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"
])

DISCIPLINES = {
    "digi": ["Jan", "Emma", "Sophie", "Tom"],
    "intel": ["Lisa", "Daan", "Eva"],
    "leiding": ["Milan", "Laura", "Rob"],
    "tactiek": ["Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars"]
}

# =========================================================================
#                   DATA LADEN
# =========================================================================

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
    except (json.JSONDecodeError, FileNotFoundError):
        st.error("Kon roosterdata niet laden.")
        return {"rooster_data": {}, "bereikbaarheden": {}}

data = load_data()
rooster_data = data.get("rooster_data", {})
bereikbaarheden = data.get("bereikbaarheden", {})

# =========================================================================
#                   EVENTS BOUWEN
# =========================================================================

events = []

for datum_key, dag_info in rooster_data.items():
    for medewerker, werkplek in dag_info.items():
        # Kleur bepalen
        if werkplek == "Kantoor":
            kleur = "#28A745"  # Groen
        elif werkplek == "Vakantie/Verlof":
            kleur = "#FFC107"  # Geel
        elif werkplek == "Niet ingepland":
            kleur = "#495057"  # Grijs
        else:
            kleur = "#007BFF"  # Blauw (voor alle overige werkplekken)

        info = WERKPLEK_MAP.get(werkplek, WERKPLEK_MAP[DEFAULT_WERKPLEK])
        events.append({
            "title": f"{info['emoji']} {medewerker}",
            "start": datum_key,
            "allDay": True,
            "backgroundColor": kleur,
            "textColor": "#FFFFFF"
        })

# Bereikbaarheid indicatoren per dag
for datum_key in set(rooster_data.keys()).union(bereikbaarheden.keys()):
    dag_bereikbaar = bereikbaarheden.get(datum_key, {})
    indicatoren = ""

    for disc, letter in zip(["digi", "intel", "leiding", "tactiek"], ["D", "I", "L", "T"]):
        persoon = dag_bereikbaar.get(disc)
        if persoon:
            indicatoren += f"✅{letter} "
        else:
            indicatoren += f"❌{letter} "

    events.append({
        "title": indicatoren.strip(),
        "start": datum_key,
        "allDay": True,
        "backgroundColor": "transparent",
        "textColor": "#FFFFFF"
    })

# =========================================================================
#                   KALENDER WEERGAVE
# =========================================================================

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "nl",
    "height": 800,
    "eventDisplay": 'block'
}

calendar(events=events, options=calendar_options, key="maandoverzicht")
