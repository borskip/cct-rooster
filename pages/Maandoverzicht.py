# Sla dit bestand op in de 'pages' map als 3_📅_Maandoverzicht.py

import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(page_title="Maandoverzicht", layout="wide")
st.title("📅 Maandoverzicht (Kalender)")

if not st.session_state.get('rooster_data'):
    st.info("Er is nog geen roosterdata. Ga naar de hoofdpagina 'Rooster_App' om data te genereren.")
    st.stop()

WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
SKILLS_BEREIKBAARHEID = st.session_state.SKILLS_BEREIKBAARHEID
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS

def build_events_list():
    events = []
    all_dates = sorted(list(set(st.session_state.rooster_data.keys()) | set(st.session_state.beschikbaarheid_data.keys())))

    for datum_key in all_dates:
        dag_beschikbaarheid = st.session_state.beschikbaarheid_data.get(datum_key, {})
        onbemande_skills = [s for s in SKILLS_BEREIKBAARHEID if not any(d.get(s) for d in dag_beschikbaarheid.values())]
        if onbemande_skills:
            events.append({
                "title": f"⚠️ Geen: {', '.join(onbemande_skills)}",
                "start": datum_key, "allDay": True,
                "backgroundColor": "#dc3545", "textColor": "#ffffff", "borderColor": "#dc3545",
            })

        dag_info = st.session_state.rooster_data.get(datum_key, {})
        for medewerker, werkplek in dag_info.items():
            if werkplek not in NIET_WERKEND_STATUS:
                werkplek_info = WERKPLEK_MAP[werkplek]
                
                # --- AANGEPAST: Voeg een sorteerveld toe aan het event-object ---
                # Dit veld wordt gebruikt door de 'eventOrder' optie van de kalender.
                sort_priority = 0 if werkplek_info['display_group'] == 'Kantoor' else 1
                
                event = {
                    "title": f"[{werkplek_info['afkorting']}] {medewerker}",
                    "start": datum_key,
                    "allDay": True,
                    "backgroundColor": werkplek_info['kleur'],
                    "textColor": werkplek_info['tekstkleur'],
                    "borderColor": werkplek_info['kleur'],
                    "sort_priority": sort_priority, # BELANGRIJK: dit veld wordt nu meegegeven!
                }
                events.append(event)
    return events

calendar(
    events=build_events_list(),
    options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "initialView": "dayGridMonth",
        "locale": "nl", "height": 800,
        "eventDisplay": 'block',
        
        # --- DE FIX: Vertel de kalender hoe hij events moet sorteren ---
        # Sorteer eerst op ons eigen 'sort_priority' veld, en daarna alfabetisch op titel.
        "eventOrder": "sort_priority, title"
    }
)
