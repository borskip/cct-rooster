# Sla dit bestand op in de 'pages' map als 4_📝_Notities_van_de_Dag.py

import streamlit as st
import datetime
import uuid
from utils import initialize_session_state, save_all_data

initialize_session_state()

st.set_page_config(page_title="Notities van de Dag", layout="centered")
st.title("📝 Notities van de Dag")

NOTE_CATEGORIES = st.session_state.NOTE_CATEGORIES

# --- Notitie Toevoegen ---
with st.expander("➕ Nieuwe notitie toevoegen", expanded=True):
    with st.form("new_note_form", clear_on_submit=True):
        note_date = st.date_input("Datum", datetime.date.today())
        note_category = st.selectbox("Categorie", list(NOTE_CATEGORIES.keys()))
        note_text = st.text_area("Notitie")
        submitted = st.form_submit_button("Voeg notitie toe")
        
        if submitted and note_text:
            datum_str = note_date.strftime("%Y-%m-%d")
            new_note = {
                "id": str(uuid.uuid4()),
                "category": note_category,
                "text": note_text,
                "author": "Gebruiker" # Kan worden uitgebreid met authenticatie
            }
            if datum_str not in st.session_state.notes_data:
                st.session_state.notes_data[datum_str] = []
            st.session_state.notes_data[datum_str].append(new_note)
            save_all_data()
            st.success("Notitie toegevoegd!")
        elif submitted and not note_text:
            st.warning("Vul een notitietekst in.")

st.divider()

# --- Bestaande Notities Weergeven ---
st.header("Bestaande Notities")

if not st.session_state.notes_data:
    st.info("Er zijn nog geen notities.")
else:
    # Sorteer datums, meest recente eerst
    sorted_dates = sorted(st.session_state.notes_data.keys(), reverse=True)
    
    for datum_str in sorted_dates:
        notes_on_day = st.session_state.notes_data[datum_str]
        if not notes_on_day: continue # Sla lege dagen over
        
        display_date = datetime.datetime.strptime(datum_str, "%Y-%m-%d").strftime("%A %d-%m-%Y")
        st.subheader(display_date)
        
        for note in notes_on_day:
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                emoji = NOTE_CATEGORIES.get(note['category'], '📝')
                if note['category'] == "Belangrijk":
                    st.warning(f"**{emoji} {note['category']}**: {note['text']}")
                else:
                    st.info(f"**{emoji} {note['category']}**: {note['text']}")
            
            with col2:
                if st.button("❌", key=note['id'], help="Verwijder notitie"):
                    # Verwijder de notitie uit de lijst
                    st.session_state.notes_data[datum_str] = [n for n in st.session_state.notes_data[datum_str] if n['id'] != note['id']]
                    # Als de dag leeg is, verwijder de hele key
                    if not st.session_state.notes_data[datum_str]:
                        del st.session_state.notes_data[datum_str]
                    save_all_data()
                    st.rerun()
