# --- VOLLEDIGE CODE VOOR: pages/7_📅_Team_Momenten.py ---
# Sla dit bestand op in de 'pages' map

import streamlit as st
import datetime
import uuid
from utils import save_all_data

# BELANGRIJK: De volgende twee functies horen alleen in het hoofdbestand (Rooster_App.py)
# en zijn daarom hier verwijderd voor een correcte werking:
# - initialize_session_state()
# - st.set_page_config(...)

st.title("📅 Team Momenten Beheren")

# Controleer of de gebruiker is ingelogd
if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'✍️ Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

# --- Nieuw team moment toevoegen ---
with st.expander("➕ Nieuw team moment toevoegen", expanded=True):
    with st.form("new_event_form", clear_on_submit=True):
        event_beschrijving = st.text_input("Beschrijving van het moment", placeholder="Bijv: Teamdag, Kwartaalmeeting, BBQ")
        event_datum = st.date_input("Datum", min_value=datetime.date.today())
        
        # UI-verbetering: primaire knop voor de hoofdactie
        submitted = st.form_submit_button("💾 Plan Moment", type="primary")
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
# Filtert op alle events die vandaag of in de toekomst plaatsvinden
geplande_events = [event for event in st.session_state.get("team_events", []) if event.get('datum') >= vandaag_str]

if not geplande_events:
    st.info("Er zijn geen toekomstige team momenten gepland.")
else:
    # Sorteer op datum voor een logisch overzicht
    for event in sorted(geplande_events, key=lambda x: x.get('datum', '')):
        datum_obj = datetime.datetime.strptime(event['datum'], "%Y-%m-%d").date()
        dag_naam = datum_obj.strftime("%A").capitalize()
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(event.get('beschrijving', 'Onbekend evenement'))
                maker = event.get('maker', 'Onbekend') # .get() is veiliger dan directe toegang
                st.caption(f"{dag_naam} {datum_obj.strftime('%d-%m-%Y')} | Ingepland door: {maker}")
            
            with col2:
                # FUNCTIONELE VERBETERING: Zowel de maker als een Teamleider kan verwijderen
                is_maker = (maker == st.session_state.logged_in_user)
                is_teamleider = (st.session_state.user_role == 'Teamleider')

                if is_maker or is_teamleider:
                    if st.button(
                        "🗑️", 
                        key=f"del_{event.get('id', '')}", 
                        help="Verwijder dit moment", 
                        type="secondary", # UI: Maakt de knop minder agressief
                        use_container_width=True # UI: Maakt de knop makkelijker te klikken
                    ):
                        st.session_state.team_events = [e for e in st.session_state.team_events if e.get('id') != event.get('id')]
                        save_all_data()
                        st.rerun()
