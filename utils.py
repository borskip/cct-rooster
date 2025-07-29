# Sla dit bestand op als utils.py

import streamlit as st
import json
import os
import datetime
import calendar as py_cal

DATA_FILE = "data.json"

def setup_constants():
    st.session_state.MEDEWERKERS = ["Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"]
    st.session_state.TEAMLEIDERS = ["Emma", "Tom"]
    st.session_state.PASSWORD = "1234"
    st.session_state.WERKPLEKKEN_CONFIG = [
        {"naam": "Kantoor", "afkorting": "KNT", "display_group": "Kantoor", "kleur": "#28a745", "tekstkleur": "#ffffff"},
        {"naam": "Aan het werk", "afkorting": "WRK", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "Opleiding/cursus", "afkorting": "OPL", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "IBT", "afkorting": "IBT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "Actiedag", "afkorting": "ACT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
        {"naam": "HOvJ", "afkorting": "HOvJ", "display_group": "Piket", "kleur": "#6f42c1", "tekstkleur": "#ffffff"},
        {"naam": "HOvJ (laat)", "afkorting": "HOvJ-L", "display_group": "Piket", "kleur": "#6f42c1", "tekstkleur": "#ffffff"},
        {"naam": "TGO Piket", "afkorting": "TGO", "display_group": "Piket", "kleur": "#6f42c1", "tekstkleur": "#ffffff"},
        {"naam": "Vakantie", "afkorting": "VAK", "display_group": "Niet_Werkend", "kleur": None},
        {"naam": "Niet aan het werk", "afkorting": "---", "display_group": "Niet_Werkend", "kleur": None},
    ]
    st.session_state.WERKPLEK_MAP = {w["naam"]: w for w in st.session_state.WERKPLEKKEN_CONFIG}
    st.session_state.WERKPLEK_NAMEN = [w["naam"] for w in st.session_state.WERKPLEKKEN_CONFIG]
    st.session_state.SKILLS_BEREIKBAARHEID = ["Digi", "Intel", "Leiding", "Tactiek"]
    st.session_state.NIET_WERKEND_STATUS = ["Vakantie", "Niet aan het werk"]
    st.session_state.BESCHIKBAAR_VOOR_DIENST = ["Kantoor", "Aan het werk"]
    st.session_state.NOTE_CATEGORIES = {"Info": "ℹ️", "Belangrijk": "⚠️", "Laat": "🏃"}
    st.session_state.NOTE_AUTHORS = ["-- Algemene Notitie --"] + st.session_state.MEDEWERKERS

def save_all_data():
    data_to_save = {
        "rooster_data": st.session_state.rooster_data,
        "beschikbaarheid_data": st.session_state.beschikbaarheid_data,
        "user_patterns": st.session_state.user_patterns,
        "medewerker_skills": st.session_state.medewerker_skills,
        "notes_data": st.session_state.notes_data,
        "rooster_vastgesteld": st.session_state.rooster_vastgesteld,
        "wijzigingsverzoeken": st.session_state.wijzigingsverzoeken
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def initialize_session_state():
    if 'app_initialized' not in st.session_state:
        setup_constants()
        loaded_data = load_all_data()
        st.session_state.rooster_data = loaded_data.get("rooster_data", {})
        st.session_state.beschikbaarheid_data = loaded_data.get("beschikbaarheid_data", {})
        st.session_state.user_patterns = loaded_data.get("user_patterns", {})
        st.session_state.medewerker_skills = loaded_data.get("medewerker_skills", {})
        st.session_state.notes_data = loaded_data.get("notes_data", {})
        st.session_state.rooster_vastgesteld = loaded_data.get("rooster_vastgesteld", {})
        st.session_state.wijzigingsverzoeken = loaded_data.get("wijzigingsverzoeken", {})
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.session_state.app_initialized = True

def update_rooster_entry(datum, medewerker, werkplek):
    datum_str = datum.strftime("%Y-%m-%d") if isinstance(datum, datetime.date) else datum
    st.session_state.rooster_data.setdefault(datum_str, {})
    st.session_state.beschikbaarheid_data.setdefault(datum_str, {})
    if werkplek == "Niet aan het werk": st.session_state.rooster_data[datum_str].pop(medewerker, None)
    else: st.session_state.rooster_data[datum_str][medewerker] = werkplek
    persoonlijke_skills = st.session_state.medewerker_skills.get(medewerker, {})
    is_beschikbaar_voor_dienst = werkplek in st.session_state.BESCHIKBAAR_VOOR_DIENST
    if is_beschikbaar_voor_dienst:
        bereikbaarheid_details = {"status": "Bereikbaar"}
        for skill in st.session_state.SKILLS_BEREIKBAARHEID:
            bereikbaarheid_details[skill] = persoonlijke_skills.get(skill, False)
        st.session_state.beschikbaarheid_data[datum_str][medewerker] = bereikbaarheid_details
    else:
        st.session_state.beschikbaarheid_data[datum_str].pop(medewerker, None)

def get_maand_voltooiing_percentage(year, month):
    _, num_days = py_cal.monthrange(year, month)
    werkdagen, totaal_ingepland = 0, 0
    medewerker_planning = {m: 0 for m in st.session_state.MEDEWERKERS}
    for day in range(1, num_days + 1):
        datum = datetime.date(year, month, day)
        if datum.weekday() < 5:
            werkdagen += 1
            datum_str = datum.strftime("%Y-%m-%d")
            dag_rooster = st.session_state.rooster_data.get(datum_str, {})
            for m in st.session_state.MEDEWERKERS:
                if m in dag_rooster and dag_rooster[m] not in st.session_state.NIET_WERKEND_STATUS:
                    totaal_ingepland += 1
                    medewerker_planning[m] += 1
    max_planning = werkdagen * len(st.session_state.MEDEWERKERS) if werkdagen > 0 else 1
    percentage = (totaal_ingepland / max_planning) * 100 if max_planning > 0 else 0
    onvolledig = {"Medewerker": [], "Ingeplande Dagen": []}
    for m, d in medewerker_planning.items():
        if werkdagen > 0 and d < werkdagen * 0.7:
            onvolledig["Medewerker"].append(m)
            onvolledig["Ingeplande Dagen"].append(f"{d} / {werkdagen}")
    return percentage, onvolledig
