# Sla dit bestand op in de 'pages' map, bv. 3_📝_Notities_van_de_Dag.py

import streamlit as st
import datetime
import uuid
from utils import initialize_session_state, save_all_data, add_note_for_day

initialize_session_state()

st.set_page_config(page_title="Notities van de Dag", layout="centered")
st.title("📝 Notities van de Dag")

# Haal constanten uit session_state
NOTE_CATEGORIES = st.session_state.NOTE_CATEGORIES
ingelogde_gebruiker = st.session_state.logged_in_user

# --- Functie om notities voor een specifieke dag te tonen ---
def display_notes_for_day(date_obj, title_suffix=""):
    """Toont de notities en delete-knoppen voor een gegeven datum."""
    datum_str = date_obj.strftime("%Y-%m-%d")
    
    # Verbeterde, robuuste datumnotatie
    st.subheader(f"{date_obj.strftime('%A %d %B %Y')} {title_suffix}")
    
    notes_on_day = st.session_state.notes_data.get(datum_str, [])

    if not notes_on_day:
        st.info(f"Geen notities voor deze dag.")
        return

    for note in notes_on_day:
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        with col1:
            # --- FIX 1: Gebruik 'categorie' (NL) i.p.v. 'category' (EN) ---
            emoji = NOTE_CATEGORIES.get(note['categorie'], '📝')
            st.markdown(f"<h3 style='text-align: center;'>{emoji}</h3>", unsafe_allow_html=True)

        with col2:
            # --- FIX 2: Gebruik 'auteur' (NL) i.p.v. 'author' (EN) ---
            auteur_info = note.get('auteur', 'Algemeen')
            author_text = f"<span style='font-size: 0.8em; color: grey;'>gepost door: <strong>{auteur_info}</strong></span>"
            
            if note['categorie'] == "Belangrijk":
                st.warning(f"**{note['categorie']}**: {note['tekst']}")
            else:
                st.info(f"**{note['categorie']}**: {note['tekst']}")
            
            st.markdown(author_text, unsafe_allow_html=True)
        
        with col3:
            st.write("")
            # Alleen de auteur (of iedereen bij algemene notitie) kan verwijderen
            if ingelogde_gebruiker == note.get('auteur') or not note.get('auteur'):
                if st.button("❌", key=note['id'], help="Verwijder notitie"):
                    st.session_state.notes_data[datum_str] = [n for n in notes_on_day if n['id'] != note['id']]
                    if not st.session_state.notes_data[datum_str]:
                        del st.session_state.notes_data[datum_str]
                    save_all_data()
                    st.rerun()
        st.markdown("---")

# --- Hoofdweergave (uw originele structuur) ---
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

# --- Notitie Toevoegen Formulier (nu consistent) ---
with st.expander("➕ Nieuwe notitie toevoegen", expanded=False):
    with st.form("new_note_form", clear_on_submit=True):
        note_date = st.date_input("Datum", value=selected_date, key="note_date_input")
        note_category = st.selectbox("Categorie", list(NOTE_CATEGORIES.keys()))
        note_text = st.text_area("Notitie")
        submitted = st.form_submit_button("Voeg notitie toe")
        
        if submitted and note_text:
            # --- FIX 3: Gebruik de centrale functie voor consistente data ---
            add_note_for_day(note_date, ingelogde_gebruiker, note_category, note_text)
            st.success("Notitie toegevoegd!")
            st.rerun()
        elif submitted and not note_text:
            st.warning("Vul een notitietekst in.")
