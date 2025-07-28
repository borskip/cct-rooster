# Sla dit bestand op in de 'pages' map als 1_🗓️_Dagoverzicht.py

import streamlit as st
import datetime

st.set_page_config(page_title="Dagoverzicht", layout="wide")
st.title("🗓️ Dagoverzicht")

if not st.session_state.get('rooster_data'):
    st.info("Er is nog geen roosterdata. Ga naar de hoofdpagina 'Rooster_App' om data te genereren.")
    st.stop()

WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
SKILLS_BEREIKBAARHEID = st.session_state.SKILLS_BEREIKBAARHEID
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS

def format_medewerker_display(medewerker, werkplek_info):
    """Maakt een HTML-blokje voor een medewerker met kleur en afkorting."""
    bg_color = werkplek_info.get('kleur', '#f0f2f6')
    text_color = werkplek_info.get('tekstkleur', '#000000')
    afkorting = werkplek_info.get('afkorting', '???')

    display_html = f"""
    <div style='margin-bottom: 5px; padding: 5px; border-left: 5px solid {bg_color};'>
        <span style='background-color: {bg_color}; color: {text_color}; padding: 3px 6px; border-radius: 5px; font-weight: bold; font-family: monospace;'>
            {afkorting}
        </span>
        <strong style='margin-left: 10px;'>{medewerker}</strong>
    </div>
    """
    return display_html

# UI Logica
start_datum = st.date_input("Selecteer startdatum", datetime.date.today())
st.divider()

for i in range(7):
    huidige_dag = start_datum + datetime.timedelta(days=i)
    datum_str = huidige_dag.strftime("%Y-%m-%d")
    dag_naam = huidige_dag.strftime("%A").capitalize()

    st.subheader(f"{dag_naam} {huidige_dag.strftime('%d-%m-%Y')}")

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
        
        # --- AANGEPAST: Logica voor drie kolommen ---
        col1, col2, col3 = st.columns(3)
        
        n = len(sorted_medewerkers)
        base_size = n // 3
        remainder = n % 3
        
        p1 = base_size + (1 if remainder > 0 else 0)
        p2 = p1 + base_size + (1 if remainder > 1 else 0)

        with col1:
            for medewerker, werkplek in sorted_medewerkers[:p1]:
                werkplek_info = WERKPLEK_MAP.get(werkplek, {})
                st.markdown(format_medewerker_display(medewerker, werkplek_info), unsafe_allow_html=True)

        with col2:
            for medewerker, werkplek in sorted_medewerkers[p1:p2]:
                werkplek_info = WERKPLEK_MAP.get(werkplek, {})
                st.markdown(format_medewerker_display(medewerker, werkplek_info), unsafe_allow_html=True)

        with col3:
            for medewerker, werkplek in sorted_medewerkers[p2:]:
                werkplek_info = WERKPLEK_MAP.get(werkplek, {})
                st.markdown(format_medewerker_display(medewerker, werkplek_info), unsafe_allow_html=True)

    st.divider()
