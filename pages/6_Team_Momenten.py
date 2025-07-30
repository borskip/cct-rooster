# Sla dit bestand op in de 'pages' map als 7_📅_Team_Momenten.py

import streamlit as st
import datetime
import uuid
from utils import initialize_session_state, save_all_data

initialize_session_state()

st.set_page_config(page_title="Team Momenten", page_icon="📅", layout="wide")
st.title("📅 Team Momenten")

if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

# --- Nieuw team moment toevoegen ---
with st.expander("➕ Nieuw team moment toevoegen"):
    with st.form("new_event_form", clear_on_submit=True):
        event_beschrijving = st.text_input("Beschrijving van het moment", placeholder="Bijv: Teamdag, Kwartaalmeeting, BBQ")
        event_datum = st.date_input("Datum", min_value=datetime.date.today())
        
        submitted = st.form_submit_button("💾 Opslaan")
        if submitted:
            if event_beschrijving:
                nieuw_event = {
                    "id": str(uuid.uuid4()),
                    "datum": event_datum.strftime("%Y-%m-%d"),
                    "beschrijving": event_beschrijving,
                    "maker": st.session_state.logged_in_user
                }
                st.session_state.team_events.append(nieuw_event)
                save_all_data()
                st.success(f"Moment '{event_beschrijving}' opgeslagen!")
                st.rerun()
            else:
                st.error("Een beschrijving is verplicht.")

st.divider()

# --- Overzicht van geplande momenten ---
st.header("🗓️ Geplande Momenten")

vandaag_str = datetime.date.today().strftime("%Y-%m-%d")
geplande_events = [event for event in st.session_state.team_events if event['datum'] >= vandaag_str]

if not geplande_events:
    st.info("Er zijn geen toekomstige team momenten gepland.")
else:
    # Sorteer op datum
    for event in sorted(geplande_events, key=lambda x: x['datum']):
        datum_obj = datetime.datetime.strptime(event['datum'], "%Y-%m-%d").date()
        dag_naam = datum_obj.strftime("%A").capitalize()
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(event['beschrijving'])
                st.caption(f"{dag_naam} {datum_obj.strftime('%d-%m-%Y')} | Ingepland door: {event['maker']}")
            
            with col2:
                # Alleen de maker kan het event verwijderen
                if event['maker'] == st.session_state.logged_in_user:
                    if st.button("🗑️", key=f"del_{event['id']}", help="Verwijder dit moment"):
                        st.session_state.team_events = [e for e in st.session_state.team_events if e['id'] != event['id']]
                        save_all_data()
                        st.rerun()
