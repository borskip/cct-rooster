# Sla dit bestand op in de 'pages' map als 5_👤_Mijn_Rooster.py

import streamlit as st
import datetime
from utils import initialize_session_state
from collections import defaultdict

initialize_session_state()

st.set_page_config(page_title="Mijn Rooster", layout="wide")
st.title("👤 Mijn Rooster")

# --- LOGIN CHECK ---
if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de 'Invoeren Rooster' pagina om in te loggen.")
    st.stop()

# Gebruik direct de ingelogde gebruiker
geselecteerde_medewerker = st.session_state.logged_in_user
st.header(f"Planning voor {geselecteerde_medewerker}")
st.divider()


if geselecteerde_medewerker:
    # Bepaal de periode: huidige en volgende maand
    vandaag = datetime.date.today()
    start_periode = vandaag.replace(day=1)
    
    # Bereken de start van de maand na de volgende maand
    volgende_maand_maand = (vandaag.month % 12) + 1
    volgende_maand_jaar = vandaag.year if vandaag.month < 12 else vandaag.year + 1
    
    maand_daarna_maand = (volgende_maand_maand % 12) + 1
    maand_daarna_jaar = volgende_maand_jaar if volgende_maand_maand < 12 else volgende_maand_jaar + 1
    
    eind_periode = datetime.date(maand_daarna_jaar, maand_daarna_maand, 1)

    # Verzamel de planning voor de geselecteerde medewerker en groepeer per week
    planning_per_week = defaultdict(list)
    huidige_dag = start_periode
    while huidige_dag < eind_periode:
        datum_str = huidige_dag.strftime("%Y-%m-%d")
        werkplek = st.session_state.rooster_data.get(datum_str, {}).get(geselecteerde_medewerker)
        
        if werkplek and werkplek not in NIET_WERKEND_STATUS:
            # Gebruik ISO weeknummer om correct te groeperen
            weeknummer = huidige_dag.isocalendar()[1]
            planning_per_week[weeknummer].append((huidige_dag, werkplek))
        
        huidige_dag += datetime.timedelta(days=1)
        
    if not planning_per_week:
        st.info(f"Geen werkdagen gevonden voor {geselecteerde_medewerker} in de komende periode.")
    else:
        st.header(f"Planning voor {geselecteerde_medewerker}")
        
        # Sorteer de weken op weeknummer
        for week, planning in sorted(planning_per_week.items()):
            # Toon de week als header
            start_week_datum = planning[0][0]
            st.subheader(f"Week {week} (vanaf {start_week_datum.strftime('%d %B')})")
            
            # --- Logica voor 2 kolommen ---
            col1, col2 = st.columns(2)
            
            for datum_obj, werkplek in sorted(planning):
                dag_naam = datum_obj.strftime("%A")
                werkplek_info = WERKPLEK_MAP[werkplek]
                color = werkplek_info.get('kleur', '#f0f2f6')
                text_color = werkplek_info.get('tekstkleur', '#000000')

                # --- AANGEPAST: `background-color: #f8f9fa;` is verwijderd ---
                display_html = f"""
                <div style='display: flex; align-items: center; margin-bottom: 8px; padding: 8px; border-radius: 5px;'>
                    <div style='width: 120px; color: #333; font-weight: bold;'>{dag_naam} {datum_obj.day}</div>
                    <div style='background-color: {color}; color: {text_color}; padding: 4px 8px; border-radius: 5px; font-weight: bold;'>
                        {werkplek_info['naam']}
                    </div>
                </div>
                """
                
                # Verdeel over kolommen op basis van de dag van de week (Ma, Di, Wo links | Do, Vr rechts)
                if datum_obj.weekday() < 3: # Maandag, Dinsdag, Woensdag
                    with col1:
                        st.markdown(display_html, unsafe_allow_html=True)
                else: # Donderdag, Vrijdag (en weekend, indien van toepassing)
                    with col2:
                        st.markdown(display_html, unsafe_allow_html=True)

            # --- Duidelijke scheiding tussen weken ---
            st.divider()
