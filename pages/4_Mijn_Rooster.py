# Sla dit bestand op in de 'pages' map, bv. 4_Mijn_Rooster.py

import streamlit as st
import datetime
from utils import initialize_session_state, get_team_event_for_date, add_note_for_day # <-- Nieuwe functie importeren
from collections import defaultdict

initialize_session_state()

st.set_page_config(page_title="Mijn Rooster", layout="wide")
st.title("👤 Mijn Rooster")

if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

# Haal constanten en data op
ingelogde_gebruiker = st.session_state.logged_in_user
WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS
NOTE_CATEGORIES = st.session_state.NOTE_CATEGORIES

st.header(f"Planning voor {ingelogde_gebruiker}")
st.divider()

# Bepaal de periode
vandaag = datetime.date.today()
start_periode = vandaag.replace(day=1)
volgende_maand_maand = (vandaag.month % 12) + 1
volgende_maand_jaar = vandaag.year if vandaag.month < 12 else vandaag.year + 1
maand_daarna_maand = (volgende_maand_maand % 12) + 1
maand_daarna_jaar = volgende_maand_jaar if volgende_maand_maand < 12 else volgende_maand_jaar + 1
eind_periode = datetime.date(maand_daarna_jaar, maand_daarna_maand, 1)

# Verzamel de planning
planning_per_week = defaultdict(list)
huidige_dag = start_periode
while huidige_dag < eind_periode:
    datum_str = huidige_dag.strftime("%Y-%m-%d")
    werkplek = st.session_state.rooster_data.get(datum_str, {}).get(ingelogde_gebruiker)
    
    if werkplek and werkplek not in NIET_WERKEND_STATUS:
        weeknummer = huidige_dag.isocalendar()[1]
        planning_per_week[weeknummer].append((huidige_dag, werkplek))
    
    huidige_dag += datetime.timedelta(days=1)
    
if not planning_per_week:
    st.info(f"Geen werkdagen gevonden voor {ingelogde_gebruiker} in de komende periode.")
else:
    for week, planning in sorted(planning_per_week.items()):
        start_week_datum = planning[0][0]
        st.subheader(f"Week {week} (vanaf {start_week_datum.strftime('%d %B')})")
        
        col1, col2 = st.columns(2)
        
        for i, (datum_obj, werkplek) in enumerate(sorted(planning)):
            werkplek_info = WERKPLEK_MAP[werkplek]
            
            # De robuuste kolomverdeling
            target_col = col1 if i % 2 == 0 else col2

            with target_col:
                with st.container(border=True):
                    # Toon team event indien aanwezig
                    team_event = get_team_event_for_date(datum_obj)
                    if team_event:
                        st.markdown(f"<div style='background-color: #e8dff5; color: #6f42c1; border-radius: 5px; padding: 6px 8px; margin-bottom: 8px; font-weight: bold; font-size: 0.9em;'>🗓️ {team_event}</div>", unsafe_allow_html=True)
                    
                    # Layout voor de dag-info en de notitie-knop
                    c1_dag, c2_dag = st.columns([4, 1])
                    
                    with c1_dag:
                        datum_display = f"{datum_obj.strftime('%A')} {datum_obj.strftime('%d %B')}"
                        st.markdown(f"**{datum_display}**")
                        st.markdown(f"<span style='background-color: {werkplek_info['kleur']}; color: {werkplek_info['tekstkleur']}; padding: 4px 8px; border-radius: 5px; font-weight: bold;'>{werkplek_info['naam']}</span>", unsafe_allow_html=True)
                    
                    with c2_dag:
                        with st.popover("📝", use_container_width=True):
                            with st.form(f"note_form_{datum_obj.isoformat()}", clear_on_submit=True):
                                st.write(f"**Notitie voor {datum_obj.strftime('%d-%m-%Y')}**")
                                categorie = st.selectbox("Categorie", options=list(NOTE_CATEGORIES.keys()))
                                tekst = st.text_area("Jouw notitie")
                                if st.form_submit_button("Opslaan", type="primary"):
                                    if tekst:
                                        add_note_for_day(datum_obj, ingelogde_gebruiker, categorie, tekst)
                                        st.success("Notitie opgeslagen!")
                                    else:
                                        st.warning("Tekst is verplicht.")

        # Scheiding tussen de weken
        st.divider()
