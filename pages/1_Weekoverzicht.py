# Sla dit bestand op in de 'pages' map als 1_🗓️_Weekoverzicht.py

import streamlit as st
import datetime
from utils import initialize_session_state

initialize_session_state()
# Voeg dit toe aan de top van ELK bestand in de 'pages' map
if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

st.set_page_config(page_title="Weekoverzicht", layout="wide")
st.title("🗓️ Weekoverzicht")

if not st.session_state.rooster_data and not st.session_state.notes_data:
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
maand_key = start_datum.strftime("%Y-%m")
if st.session_state.rooster_vastgesteld.get(maand_key, False):
    st.warning(f"🔒 **Rooster Vastgesteld** voor {start_datum.strftime('%B %Y')}")
st.divider()

for i in range(7):
    huidige_dag = start_datum + datetime.timedelta(days=i)
    datum_str = huidige_dag.strftime("%Y-%m-%d")
    dag_naam = huidige_dag.strftime("%A").capitalize()

    with st.expander(f"**{dag_naam} {huidige_dag.strftime('%d-%m-%Y')}**", expanded=True):
        dag_beschikbaarheid = st.session_state.beschikbaarheid_data.get(datum_str, {})
        
        if huidige_dag.weekday() < 5:
            onbemande_skills = [s for s in SKILLS_BEREIKBAARHEID if not any(d.get(s, False) for d in dag_beschikbaarheid.values())]
            if onbemande_skills:
                st.error(f"❌ Geen bereikbare medewerker voor: **{', '.join(onbemande_skills)}**")
            else:
                st.success("✅ Alle disciplines zijn gedekt.")
        
        st.write("**Ingeplande medewerkers:**")
        
        dag_rooster = st.session_state.rooster_data.get(datum_str, {})
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
