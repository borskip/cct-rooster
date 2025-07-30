# Sla dit bestand op als utils.py

import streamlit as st
import json
import os
import datetime
import calendar as py_cal
import uuid
import holidays  # Vereist: pip install holidays

DATA_FILE = "data.json"

# --- HELPER FUNCTIE VOOR KLEURCONTRAST ---
def get_text_color(hex_bg_color):
    """Bepaalt of tekst wit of zwart moet zijn op basis van de achtergrondkleur voor leesbaarheid."""
    if not hex_bg_color: # Valideer of er een kleur is
        return "#ffffff" # Default voor transparant of geen kleur
        
    hex_color = hex_bg_color.lstrip('#')
    if len(hex_color) != 6:
        return "#ffffff" # Fallback voor ongeldige hex code

    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Formule voor het berekenen van de 'luminance' (helderheid)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#ffffff" if luminance < 0.5 else "#000000"
    except (ValueError, IndexError):
        return "#ffffff" # Fallback voor onverwachte fouten

# --- FEESTDAGEN FUNCTIE ---
def get_dutch_holiday_name(datum):
    """Geeft de naam van de Nederlandse feestdag terug als de datum een feestdag is, anders None."""
    nl_holidays = holidays.Netherlands()
    return nl_holidays.get(datum)

# --- INSTELLINGEN & DATA BEHEER ---
def setup_constants():
    """Initialiseert alle vaste configuraties van de app."""
    
    # --- KLEURENPALET ---
    # Centraal beheer van zachte, goed leesbare kleuren voor een donkere achtergrond.
    KLEUREN_PALET = {
        "kantoor": "#2E7D32",         # Helder groen voor Kantoor
        "werkend_blauw": "#5B84B1",   # Zacht blauw voor algemeen werk
        "opleiding_groen": "#63B4B8", # Zacht groen voor opleiding/IBT
        "actie_roze": "#D0A9A4",      # Zacht roze voor actiedagen
        "piket_paars": "#8e5a9a",     # Gedempt paars voor piketdiensten
        "neutraal_grijs": "#6c757d",  # Grijs voor niet-werkende statussen
        "transparant": None,         # Geen kleur voor 'Niet aan het werk'
    }

    # --- WERKPLEK CONFIGURATIE ---
    # Alle diensten en hun eigenschappen worden hier gedefinieerd.
    st.session_state.WERKPLEKKEN_CONFIG = [
        # Groep: Kantoor
        {"naam": "Kantoor", "afkorting": "KNT", "display_group": "Kantoor", "kleur": KLEUREN_PALET["kantoor"], "tekstkleur": get_text_color(KLEUREN_PALET["kantoor"])},
        
        # Groep: Werkend_Anders
        {"naam": "Aan het werk", "afkorting": "WRK", "display_group": "Werkend_Anders", "kleur": KLEUREN_PALET["werkend_blauw"], "tekstkleur": get_text_color(KLEUREN_PALET["werkend_blauw"])},
        {"naam": "Opleiding/cursus", "afkorting": "OPL", "display_group": "Werkend_Anders", "kleur": KLEUREN_PALET["opleiding_groen"], "tekstkleur": get_text_color(KLEUREN_PALET["opleiding_groen"])},
        {"naam": "IBT", "afkorting": "IBT", "display_group": "Werkend_Anders", "kleur": KLEUREN_PALET["opleiding_groen"], "tekstkleur": get_text_color(KLEUREN_PALET["opleiding_groen"])},
        {"naam": "Actiedag", "afkorting": "ACT", "display_group": "Werkend_Anders", "kleur": KLEUREN_PALET["actie_roze"], "tekstkleur": get_text_color(KLEUREN_PALET["actie_roze"])},

        # Groep: Piket
        {"naam": "HOvJ", "afkorting": "HOvJ", "display_group": "Piket", "kleur": KLEUREN_PALET["piket_paars"], "tekstkleur": get_text_color(KLEUREN_PALET["piket_paars"])},
        {"naam": "HOvJ (laat)", "afkorting": "HOvJ-L", "display_group": "Piket", "kleur": KLEUREN_PALET["piket_paars"], "tekstkleur": get_text_color(KLEUREN_PALET["piket_paars"])},
        {"naam": "TGO Piket", "afkorting": "TGO", "display_group": "Piket", "kleur": KLEUREN_PALET["piket_paars"], "tekstkleur": get_text_color(KLEUREN_PALET["piket_paars"])},
        
        # Groep: Niet_Werkend
        {"naam": "Vakantie", "afkorting": "VAK", "display_group": "Niet_Werkend", "kleur": KLEUREN_PALET["neutraal_grijs"], "tekstkleur": get_text_color(KLEUREN_PALET["neutraal_grijs"])},
        {"naam": "Niet aan het werk", "afkorting": "---", "display_group": "Niet_Werkend", "kleur": KLEUREN_PALET["transparant"], "tekstkleur": "#ffffff"},
    ]
    
    # Afgeleide constanten
    st.session_state.WERKPLEK_MAP = {w["naam"]: w for w in st.session_state.WERKPLEKKEN_CONFIG}
    st.session_state.WERKPLEK_NAMEN = [w["naam"] for w in st.session_state.WERKPLEKKEN_CONFIG]
    st.session_state.NIET_WERKEND_STATUS = [w["naam"] for w in st.session_state.WERKPLEKKEN_CONFIG if w["display_group"] == "Niet_Werkend"]
    
    # Overige constanten
    st.session_state.MEDEWERKERS = ["Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"]
    st.session_state.TEAMLEIDERS = ["Emma", "Tom"]
    st.session_state.PASSWORD = "1234"
    st.session_state.SKILLS_BEREIKBAARHEID = ["Digi", "Intel", "Leiding", "Tactiek"]
    st.session_state.BESCHIKBAAR_VOOR_DIENST = ["Kantoor", "Aan het werk"]
    st.session_state.NOTE_CATEGORIES = {"Info": "ℹ️", "Belangrijk": "⚠️", "Laat": "🏃"}
    st.session_state.NOTE_AUTHORS = ["-- Algemene Notitie --"] + st.session_state.MEDEWERKERS

def save_all_data():
    """Slaat de volledige session state op in een JSON-bestand."""
    data_to_save = {
        key: st.session_state[key] for key in [
            "rooster_data", "beschikbaarheid_data", "user_patterns", 
            "medewerker_skills", "notes_data", "rooster_vastgesteld", 
            "wijzigingsverzoeken", "open_diensten", "team_events"
        ]
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4, default=str) # default=str om datetime objecten te kunnen verwerken

def load_all_data():
    """Laadt data uit het JSON-bestand. Geeft een lege dict terug als het bestand niet bestaat of corrupt is."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def initialize_session_state():
    """Initialiseert de app state, laadt data en zet de basisvariabelen."""
    if 'app_initialized' not in st.session_state:
        setup_constants()
        loaded_data = load_all_data()
        
        # Zet alle data-gerelateerde state variabelen
        data_keys = ["rooster_data", "beschikbaarheid_data", "user_patterns", "medewerker_skills", 
                     "notes_data", "rooster_vastgesteld", "wijzigingsverzoeken"]
        for key in data_keys:
            st.session_state[key] = loaded_data.get(key, {})
            
        list_keys = ["open_diensten", "team_events"]
        for key in list_keys:
            st.session_state[key] = loaded_data.get(key, [])
            
        # Zet sessie-specifieke variabelen
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.session_state.app_initialized = True

# --- FUNCTIES VOOR DE APP LOGICA ---

def get_team_event_for_date(datum):
    datum_str = datum.strftime("%Y-%m-%d")
    for event in st.session_state.get('team_events', []):
        if event['datum'] == datum_str:
            return event['beschrijving']
    return None

def update_rooster_entry(datum, medewerker, werkplek):
    datum_str = datum.strftime("%Y-%m-%d") if isinstance(datum, datetime.date) else datum
    
    st.session_state.rooster_data.setdefault(datum_str, {})
    if werkplek == "Niet aan het werk":
        st.session_state.rooster_data[datum_str].pop(medewerker, None)
    else:
        st.session_state.rooster_data[datum_str][medewerker] = werkplek

    st.session_state.beschikbaarheid_data.setdefault(datum_str, {})
    persoonlijke_skills = st.session_state.medewerker_skills.get(medewerker, {})
    is_beschikbaar = werkplek in st.session_state.BESCHIKBAAR_VOOR_DIENST
    if is_beschikbaar:
        bereikbaarheid_details = {"status": "Bereikbaar", **{s: p for s, p in persoonlijke_skills.items()}}
        st.session_state.beschikbaarheid_data[datum_str][medewerker] = bereikbaarheid_details
    else:
        st.session_state.beschikbaarheid_data[datum_str].pop(medewerker, None)

def add_note_for_day(datum, auteur, categorie, tekst):
    datum_str = datum.strftime("%Y-%m-%d")
    st.session_state.notes_data.setdefault(datum_str, [])
    nieuwe_notitie = {
        "id": str(uuid.uuid4()), 
        "auteur": auteur, 
        "categorie": categorie, 
        "tekst": tekst,
        "timestamp": datetime.datetime.now().isoformat()
    }
    st.session_state.notes_data[datum_str].append(nieuwe_notitie)
    save_all_data()

def get_maand_voltooiing_percentage(year, month):
    _, num_days = py_cal.monthrange(year, month)
    werkdagen = sum(1 for d in range(1, num_days + 1) if datetime.date(year, month, d).weekday() < 5)
    
    totaal_ingepland = 0
    medewerker_planning = {m: 0 for m in st.session_state.MEDEWERKERS}
    
    for day in range(1, num_days + 1):
        datum_str = datetime.date(year, month, day).strftime("%Y-%m-%d")
        dag_rooster = st.session_state.rooster_data.get(datum_str, {})
        for m, w in dag_rooster.items():
            if w not in st.session_state.NIET_WERKEND_STATUS:
                totaal_ingepland += 1
                if m in medewerker_planning:
                    medewerker_planning[m] += 1
                    
    max_planning = werkdagen * len(st.session_state.MEDEWERKERS)
    percentage = (totaal_ingepland / max_planning) * 100 if max_planning > 0 else 0
    
    onvolledig = {"Medewerker": [], "Ingeplande Dagen": []}
    for m, d in medewerker_planning.items():
        if werkdagen > 0 and d < werkdagen * 0.7:
            onvolledig["Medewerker"].append(m)
            onvolledig["Ingeplande Dagen"].append(f"{d} / {werkdagen}")
            
    return percentage, onvolledig

def get_day_stats(datum):
    datum_str = datum.strftime("%Y-%m-%d")
    dag_rooster = st.session_state.rooster_data.get(datum_str, {})
    dag_beschikbaarheid = st.session_state.beschikbaarheid_data.get(datum_str, {})
    
    kantoor_count = sum(1 for werkplek in dag_rooster.values() if werkplek == "Kantoor")
    
    gedekte_skills = {skill: False for skill in st.session_state.SKILLS_BEREIKBAARHEID}
    for details in dag_beschikbaarheid.values():
        for skill, is_actief in details.items():
            if skill in gedekte_skills and is_actief:
                gedekte_skills[skill] = True
                
    return kantoor_count, gedekte_skills
