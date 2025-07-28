# Sla dit bestand op als utils.py

import streamlit as st
import json
import os
import datetime
import calendar as py_cal

DATA_FILE = "data.json"

# --- CONSTANTEN DEFINITIES ---
# Deze worden één keer gedefinieerd en in de session state geplaatst.
def setup_constants():
    st.session_state.MEDEWERKERS = ["Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"]
    st.session_state.WERKPLEKKEN_CONFIG = [
        {"naam": "Kantoor", "afkorting": "KNT", "display_group": "Kantoor", "kleur": "#28a745", "tekstkleur": "#ffffff"},
        {"naam": "Aan het werk", "afkorting": "WRK", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "Opleiding/cursus", "afkorting": "OPL", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "IBT", "afkorting": "IBT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "Actiedag", "afkorting": "ACT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "Vakantie", "afkorting": "VAK", "display_group": "Niet_Werkend", "kleur": None},
        {"naam": "Niet aan het werk", "afkorting": "---", "display_group": "Niet_Werkend", "kleur": None},
    ]
    st.session_state.WERKPLEK_MAP = {w["naam"]: w for w in st.session_state.WERKPLEKKEN_CONFIG}
    st.session_state.WERKPLEK_NAMEN = [w["naam"] for w in st.session_state.WERKPLEKKEN_CONFIG]
    st.session_state.SKILLS_BEREIKBAARHEID = ["Digi", "Intel", "Leiding", "Tactiek"]
    st.session_state.NIET_WERKEND_STATUS = ["Vakantie", "Niet aan het werk"]
    st.session_state.BESCHIKBAAR_VOOR_DIENST = ["Kantoor", "Aan het werk"]
    st.session_state.NOTE_CATEGORIES = {
        "Info": "ℹ️",
        "Belangrijk": "⚠️",
        "Laat": "🏃"
    }

# --- DATA PERSISTENTIE ---
def save_all_data():
    """Slaat alle relevante data uit de session state op naar een JSON-bestand."""
    data_to_save = {
        "rooster_data": st.session_state.rooster_data,
        "beschikbaarheid_data": st.session_state.beschikbaarheid_data,
        "user_patterns": st.session_state.user_patterns,
        "medewerker_skills": st.session_state.medewerker_skills,
        "notes_data": st.session_state.notes_data
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

def load_all_data():
    """Laadt data uit het JSON-bestand als het bestaat."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def initialize_session_state():
    """Wordt één keer uitgevoerd bij de start van de app."""
    if 'app_initialized' not in st.session_state:
        setup_constants()
        
        loaded_data = load_all_data()
        st.session_state.rooster_data = loaded_data.get("rooster_data", {})
        st.session_state.beschikbaarheid_data = loaded_data.get("beschikbaarheid_data", {})
        st.session_state.user_patterns = loaded_data.get("user_patterns", {})
        st.session_state.medewerker_skills = loaded_data.get("medewerker_skills", {})
        st.session_state.notes_data = loaded_data.get("notes_data", {})
        
        st.session_state.app_initialized = True

# --- KERNLOGICA ---
def update_rooster_entry(datum, medewerker, werkplek):
    """Berekent beschikbaarheid o.b.v. VASTE disciplines en werkplek."""
    datum_str = datum.strftime("%Y-%m-%d") if isinstance(datum, datetime.date) else datum
    
    st.session_state.rooster_data.setdefault(datum_str, {})
    st.session_state.beschikbaarheid_data.setdefault(datum_str, {})

    if werkplek == "Niet aan het werk":
        st.session_state.rooster_data[datum_str].pop(medewerker, None)
    else:
        st.session_state.rooster_data[datum_str][medewerker] = werkplek

    persoonlijke_skills = st.session_state.medewerker_skills.get(medewerker, {})
    is_beschikbaar_voor_dienst = werkplek in st.session_state.BESCHIKBAAR_VOOR_DIENST

    if is_beschikbaar_voor_dienst:
        bereikbaarheid_details = {"status": "Bereikbaar"}
        for skill in st.session_state.SKILLS_BEREIKBAARHEID:
            heeft_skill = persoonlijke_skills.get(skill, False)
            bereikbaarheid_details[skill] = heeft_skill
        st.session_state.beschikbaarheid_data[datum_str][medewerker] = bereikbaarheid_details
    else:
        st.session_state.beschikbaarheid_data[datum_str].pop(medewerker, None)

def get_maand_voltooiing_percentage(year, month):
    """Berekent hoe compleet het rooster is voor een gegeven maand."""
    _, num_days = py_cal.monthrange(year, month)
    werkdagen = 0
    totaal_ingepland = 0
    medewerker_planning = {m: 0 for m in st.session_state.MEDEWERKERS}

    for day in range(1, num_days + 1):
        datum = datetime.date(year, month, day)
        if datum.weekday() < 5:  # Ma-Vr
            werkdagen += 1
            datum_str = datum.strftime("%Y-%m-%d")
            dag_rooster = st.session_state.rooster_data.get(datum_str, {})
            for medewerker in st.session_state.MEDEWERKERS:
                if medewerker in dag_rooster and dag_rooster[medewerker] not in st.session_state.NIET_WERKEND_STATUS:
                    totaal_ingepland += 1
                    medewerker_planning[medewerker] += 1
    
    max_planning = werkdagen * len(st.session_state.MEDEWERKERS)
    percentage = (totaal_ingepland / max_planning) * 100 if max_planning > 0 else 0
    
    onvolledig = {
        "Medewerker": [],
        "Ingeplande Dagen": []
    }
    for medewerker, dagen in medewerker_planning.items():
        if dagen < werkdagen * 0.7:  # drempel van 70%
            onvolledig["Medewerker"].append(medewerker)
            onvolledig["Ingeplande Dagen"].append(f"{dagen} / {werkdagen}")

    return percentage, onvolledig
