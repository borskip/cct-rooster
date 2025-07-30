# Sla dit bestand op in de 'pages' map als 2_🧑‍🤝‍🧑_Medewerkersoverzicht.py
import streamlit as st
import datetime
import pandas as pd
from utils import initialize_session_state, get_team_event_for_date, get_dutch_holiday_name

initialize_session_state()
if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

st.set_page_config(page_title="Medewerkersoverzicht", layout="wide")
st.title("🧑‍🤝‍🧑 Medewerkersoverzicht")

if not st.session_state.rooster_data:
    st.info("Er is nog geen roosterdata.")
    st.stop()

WERKPLEK_MAP = st.session_state.WERKPLEK_MAP
MEDEWERKERS = st.session_state.MEDEWERKERS
NIET_WERKEND_STATUS = st.session_state.NIET_WERKEND_STATUS

# --- Styling Functies ---
def style_special_day_border(column):
    style = [''] * len(column)
    col_name = column.name
    if "🎉" in col_name or "🗓️" in col_name:
        border_color = '#198754' if "🎉" in col_name else '#6f42c1'
        style = [f'border-left: 2px solid {border_color}; border-right: 2px solid {border_color};'] * len(column)
    return style

def style_rooster_cell(val):
    werkplek_info = next((info for info in WERKPLEK_MAP.values() if info['afkorting'] == val), None)
    if werkplek_info and werkplek_info['kleur']:
        return f'background-color: {werkplek_info["kleur"]}; color: {werkplek_info["tekstkleur"]}; font-weight: bold;'
    return ''

# --- Hoofdlogica ---
selected_date = st.date_input("Selecteer een datum om de week te tonen", datetime.date.today())
start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
st.header(f"Week van {start_of_week.strftime('%d %B %Y')}")
dagen_van_de_week = [start_of_week + datetime.timedelta(days=i) for i in range(7)]

# --- DE NIEUWE OPLOSSING: Visuele Legenda Boven de Tabel ---
st.markdown("**Speciale Dagen in deze Week:**")
legend_cols = st.columns(7)
dagen_namen_voor_tabel = []

for i, dag in enumerate(dagen_van_de_week):
    dag_naam_str = dag.strftime("%a %d-%m")
    holiday_name = get_dutch_holiday_name(dag)
    team_event = get_team_event_for_date(dag)
    
    prefix_tabel = ""
    with legend_cols[i]:
        if holiday_name:
            prefix_tabel = "🎉 "
            st.markdown(f"<div style='background-color:#198754; color:white; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9em;'><b>{dag_naam_str}</b><br>{holiday_name}</div>", unsafe_allow_html=True)
        elif team_event:
            prefix_tabel = "🗓️ "
            st.markdown(f"<div style='background-color:#6f42c1; color:white; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9em;'><b>{dag_naam_str}</b><br>{team_event}</div>", unsafe_allow_html=True)
        else:
            # Maak een lege placeholder om de uitlijning te behouden
            st.markdown(f"<div style='text-align: center; padding: 5px; font-size: 0.9em;'><b>{dag_naam_str}</b><br> </div>", unsafe_allow_html=True)

    dagen_namen_voor_tabel.append(f"{prefix_tabel}{dag_naam_str}")
st.markdown("---") # Scheiding tussen legenda en tabel

# Data voor de tabel voorbereiden
data = []
for medewerker in MEDEWERKERS:
    row = {}
    is_working_this_week = False
    for i, dag in enumerate(dagen_van_de_week):
        datum_str = dag.strftime("%Y-%m-%d")
        werkplek = st.session_state.rooster_data.get(datum_str, {}).get(medewerker)
        if werkplek and werkplek not in NIET_WERKEND_STATUS:
            row[dagen_namen_voor_tabel[i]] = WERKPLEK_MAP.get(werkplek, {}).get('afkorting', '???')
            is_working_this_week = True
        else:
            row[dagen_namen_voor_tabel[i]] = ""
    if is_working_this_week:
        row['Medewerker'] = medewerker
        data.append(row)

# Tabel tonen met de werkende styling
if not data:
    st.info("Geen medewerkers ingeroosterd om te tonen voor deze week.")
else:
    df = pd.DataFrame(data).set_index('Medewerker')
    df = df[dagen_namen_voor_tabel]
    
    df_styled = (
        df.style
        .apply(style_special_day_border, axis=0)
        .applymap(style_rooster_cell)
    )
    
    st.dataframe(df_styled, use_container_width=True)
