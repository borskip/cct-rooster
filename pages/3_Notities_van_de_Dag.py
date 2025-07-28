# Sla dit bestand op in de 'pages' map, bv. 4_Notities.py

import streamlit as st
import datetime
import uuid
from utils import initialize_session_state, save_all_data

initialize_session_state()

st.set_page_config(page_title="Notities van de Dag", layout="centered")
st.title("📝 Notities van de Dag")

# Haal constanten uit session_state
NOTE_CATEGORIES = st.session_state.NOTE_CATEGORIES
NOTE_AUTHORS = st.session_state.NOTE_AUTHORS

# --- Functie om notities voor een specifieke dag te tonen ---
def display_notes_for_day(date_obj, title_suffix=""):
    """Toont de notities en delete-knoppen voor een gegeven datum."""
    datum_str = date_obj.strftime("%Y-%m-%d")
    dag_naam = date_obj.strftime("%A").capitalize()
    
    st.subheader(f"{dag_naam} {date_obj.strftime('%d-%m-%Y')} {title_suffix}")
    
    notes_on_day = st.session_state.notes_data.get(datum_str)

    if not notes_on_day:
        st.info(f"Geen notities voor deze dag.")
        return

    for note in notes_on_day:
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        with col1:
            emoji = NOTE_CATEGORIES.get(note['category'], '📝')
            st.markdown(f"<h3 style='text-align: center;'>{emoji}</h3>", unsafe_allow_html=True)

        with col2:
            author_text = f"<span style='font-size: 0.8em; color: grey;'>gepost door: <strong>{note['author']}</strong></span>" if note.get('author') else ""
            
            if note['category'] == "Belangrijk":
                st.warning(f"**{note['category']}**: {note['text']}")
            else:
                st.info(f"**{note['category']}**: {note['text']}")
            
            if author_text:
                st.markdown(author_text, unsafe_allow_html=True)
        
        with col3:
            st.write("")
            if st.button("❌", key=note['id'], help="Verwijder notitie"):
                st.session_state.notes_data[datum_str] = [n for n in notes_on_day if n['id'] != note['id']]
                if not st.session_state.notes_data[datum_str]:
                    del st.session_state.notes_data[datum_str]
                save_all_data()
                st.rerun()
        st.markdown("---")

# --- Hoofdweergave ---
vandaag = datetime.date.today()

# Sectie voor VANDAAG
display_notes_for_day(vandaag, title_suffix="(Vandaag)")

st.divider()

# Sectie voor het bekijken van ANDERE DAGEN
st.header("Bekijk een andere dag")
selected_date = st.date_input("Kies een datum", value=vandaag, key="note_date_picker")

if selected_date != vandaag:
    display_notes_for_day(selected_date)

st.divider()

# --- Notitie Toevoegen Formulier (ingeklapt) ---
with st.expander("➕ Nieuwe notitie toevoegen", expanded=False):
    with st.form("new_note_form", clear_on_submit=True):
        # Datum staat standaard op de geselecteerde datum
        note_date = st.date_input("Datum", value=selected_date, key="note_date_input")
        
        col1, col2 = st.columns(2)
        with col1:
            note_author = st.selectbox("Auteur", NOTE_AUTHORS, key="note_author")
        with col2:
            note_category = st.selectbox("Categorie", list(NOTE_CATEGORIES.keys()))
        
        note_text = st.text_area("Notitie")
        submitted = st.form_submit_button("Voeg notitie toe")
        
        if submitted and note_text:
            datum_str = note_date.strftime("%Y-%m-%d")
            author_to_save = note_author if note_author != "-- Algemene Notitie --" else None
            
            new_note = {
                "id": str(uuid.uuid4()),
                "category": note_category,
                "text": note_text,
                "author": author_to_save 
            }
            if datum_str not in st.session_state.notes_data:
                st.session_state.notes_data[datum_str] = []
            st.session_state.notes_data[datum_str].append(new_note)
            save_all_data()
            st.success("Notitie toegevoegd!")
            st.rerun() # Rerun om de notitie direct te tonen in de lijst
        elif submitted and not note_text:
            st.warning("Vul een notitietekst in.")
