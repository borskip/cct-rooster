# Sla dit bestand op in de 'pages' map als 1_🗓️_Weekoverzicht.py
# Dit was voorheen het Dagoverzicht

import streamlit as st
import datetime
from utils import initialize_session_state

initialize_session_state()

st.set_page_config(page_title="Weekoverzicht", layout="wide")
st.title("🗓️ Weekoverzicht")

if not st.session_state.rooster_data:
    st.info("Er is nog geen roosterdata. Ga naar het 'Controlepaneel' om het rooster te vullen.")
    st.stop()

WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
SKILLS_BEREIKBAARHEID = st.session_state.SKILLS_BEREIKBAARHEID
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS

def format_medewerker_display(medewerker, werkplek_info):
    bg_color = werkplek_info.get('kleur', '#f0f2f6')
    text_color = werkplek_info.get('tekstkleur', '#000000')
    afkorting = werkplek_info.get('afkorting', '???')
    return f"""
    <div style='margin-bottom: 5px; padding: 5px; border-left: 5px solid {bg_color};'>
        <span style='background-color: {bg_color}; color: {text_color}; padding: 3px 6px; border-radius: 5px; font-weight: bold; font-family: monospace;'>{afkorting}</span>
        <strong style='margin-left: 10px;'>{medewerker}</strong>
    </div>
    """

start_datum = st.date_input("Selecteer startdatum", datetime.date.today())
st.divider()

for i in range(7):
    huidige_dag = start_datum + datetime.timedelta(days=i)
    datum_str = huidige_dag.strftime("%Y-%m-%d")
    dag_naam = huidige_dag.strftime("%A").capitalize()

    with st.expander(f"**{dag_naam} {huidige_dag.strftime('%d-%m-%Y')}**", expanded=True):
        dag_rooster = st.session_state.rooster_data.get(datum_str, {})
        dag_beschikbaarheid = st.session_state.beschikbaarheid_data.get(datum_str, {})

        onbemande_skills = [s for s in SKILLS_BEREIKBAARHEID if not any(d.get(s, False) for d in dag_beschikbaarheid.values())]
        if onbemande_skills:
            st.error(f"❌ Geen bereikbare medewerker voor: **{', '.join(onbemande_skills)}**")
        else:
            st.success("✅ Alle disciplines zijn gedekt.")
        
        st.write("**Ingeplande medewerkers:**")
        
        werkende_medewerkers = {m: w for m, w in dag_rooster.items() if w not in NIET_WERKEND_STATUS}
        
        if not werkende_medewerkers:
            st.write("Niemand ingeroosterd.")
        else:
            sorted_medewerkers = sorted(werkende_medewerkers.items(), key=lambda item: (WERKPLEK_MAP[item[1]]['display_group'], item[0]))
            
            cols = st.columns(3)
            for idx, (medewerker, werkplek) in enumerate(sorted_medewerkers):
                with cols[idx % 3]:
                    werkplek_info = WERKPLEK_MAP.get(werkplek, {})
                    st.markdown(format_medewerker_display(medewerker, werkplek_info), unsafe_allow_html=True)
