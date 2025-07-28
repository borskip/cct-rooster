# Sla dit bestand op in de 'pages' map als 2_📊_Weekoverzicht.py

import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="Weekoverzicht", layout="wide")
st.title("📊 Weekoverzicht")

if not st.session_state.get('rooster_data'):
    st.info("Er is nog geen roosterdata. Ga naar de hoofdpagina 'Rooster_App' om data te genereren.")
    st.stop()

WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
MEDEWERKERS = st.session_state.MEDEWERKERS
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS

def style_rooster(val):
    """Past kleur toe op basis van de werkplek-afkorting."""
    werkplek_info = next((info for info in WERKPLEK_MAP.values() if info['afkorting'] == val), None)
    if werkplek_info and werkplek_info['kleur']:
        return f'background-color: {werkplek_info["kleur"]}; color: {werkplek_info["tekstkleur"]}; font-weight: bold;'
    return ''

# UI Logica
selected_date = st.date_input("Selecteer een datum om de week te tonen", datetime.date.today())
start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
dagen_van_de_week = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
dagen_namen = [dag.strftime("%a %d-%m") for dag in dagen_van_de_week]

st.header(f"Week van {start_of_week.strftime('%d-%m-%Y')}")

data = []
for medewerker in MEDEWERKERS:
    row = {}
    is_working_this_week = False
    for i, dag in enumerate(dagen_van_de_week):
        datum_str = dag.strftime("%Y-%m-%d")
        werkplek = st.session_state.rooster_data.get(datum_str, {}).get(medewerker)
        
        if werkplek and werkplek not in NIET_WERKEND_STATUS:
            row[dagen_namen[i]] = WERKPLEK_MAP.get(werkplek, {}).get('afkorting', '???')
            is_working_this_week = True
        else:
            row[dagen_namen[i]] = ""
    
    if is_working_this_week:
        row['Medewerker'] = medewerker
        data.append(row)

if not data:
    st.info("Geen medewerkers ingeroosterd om te tonen voor deze week.")
else:
    df = pd.DataFrame(data).set_index('Medewerker')
    df_styled = df.style.applymap(style_rooster)
    st.dataframe(df_styled, use_container_width=True)
