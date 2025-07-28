# Sla dit bestand op als Rooster_App.py

import streamlit as st
import datetime
import calendar as py_cal
import random

# Importeer alle logica uit het utils.py bestand
from utils import (
    initialize_session_state,
    update_rooster_entry,
    save_all_data,
    get_maand_voltooiing_percentage
)

# Initialiseer de app en laad de data
initialize_session_state()

# --- HOOFDPAGINA CONTENT ---
st.set_page_config(
    page_title="Rooster App - Controlepaneel",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Controlepaneel Rooster App")
st.markdown("Gebruik de beheertools hieronder om het rooster handmatig te vullen en disciplines toe te wijzen.")
st.divider()

st.header("1. Roosterbeheer")
col1, col2 = st.columns([1, 1.5])
with col1:
    if st.button("🗑️ Verwijder Alle Roosterdata", type="primary"):
        st.session_state.rooster_data = {}
        st.session_state.beschikbaarheid_data = {}
        st.session_state.notes_data = {}
        save_all_data()
        st.success("Alle roosterdata en notities zijn verwijderd.")
        st.rerun()

with col2:
    with st.expander("Optioneel: Genereer demo-data"):
        if st.button("✨ Genereer Fictieve Data 2025"):
            # --- AANGEPAST: Slimmere logica voor data generatie ---
            # Reset eerst alle data
            st.session_state.rooster_data = {}
            st.session_state.beschikbaarheid_data = {}
            st.session_state.notes_data = {}
            st.session_state.medewerker_skills = {}

            # 1. Wijs eerst vaste skills toe aan medewerkers
            for medewerker in st.session_state.MEDEWERKERS:
                num_skills = random.randint(1, 2)
                toegekende_skills = random.sample(st.session_state.SKILLS_BEREIKBAARHEID, num_skills)
                st.session_state.medewerker_skills[medewerker] = {s: (s in toegekende_skills) for s in st.session_state.SKILLS_BEREIKBAARHEID}

            # 2. Loop door de dagen en plan volgens de nieuwe regels
            start_datum = datetime.date(2025, 1, 1)
            eind_datum = datetime.date(2025, 12, 31)
            totaal_dagen = (eind_datum - start_datum).days + 1
            progress_bar = st.progress(0, text="Slim rooster genereren...")

            for i in range(totaal_dagen):
                huidige_dag = start_datum + datetime.timedelta(days=i)
                dag_index = huidige_dag.weekday()  # Maandag=0, Zondag=6
                
                # Bepaal het doel voor kantoorbezetting op basis van de dag
                if dag_index in [1, 2, 3]:  # Di, Wo, Do
                    kantoor_doel = 15
                elif dag_index == 0:  # Ma
                    kantoor_doel = 8
                else:  # Vr, Za, Zo
                    kantoor_doel = 0

                # Shuffle de medewerkers voor willekeur
                beschikbare_medewerkers = st.session_state.MEDEWERKERS.copy()
                random.shuffle(beschikbare_medewerkers)
                
                # Wijs kantoorplekken toe
                kantoor_medewerkers = []
                if kantoor_doel > 0:
                    kantoor_medewerkers = beschikbare_medewerkers[:kantoor_doel]
                    for medewerker in kantoor_medewerkers:
                        update_rooster_entry(huidige_dag, medewerker, "Kantoor")

                # Verwerk de overige medewerkers
                overige_medewerkers = [m for m in beschikbare_medewerkers if m not in kantoor_medewerkers]
                for medewerker in overige_medewerkers:
                    werkplek = "Niet aan het werk"
                    
                    # Logica voor weekenden
                    if dag_index >= 5: # Za of Zo
                        if random.random() < 0.05: # Zeer kleine kans om in het weekend te werken
                           werkplek = random.choice(["Aan het werk", "Actiedag"])
                    
                    # Logica voor weekdagen
                    else:
                        is_vakantie = (huidige_dag.month in [7, 8] and random.random() < 0.25) or (huidige_dag.month not in [7, 8] and random.random() < 0.07)
                        if is_vakantie:
                            werkplek = "Vakantie"
                        elif random.random() > 0.15: # 85% kans om wel iets te doen
                            werkplek_opties = [w['naam'] for w in st.session_state.WERKPLEKKEN_CONFIG if w['naam'] not in ["Kantoor"] + st.session_state.NIET_WERKEND_STATUS]
                            werkplek = random.choice(werkplek_opties)
                    
                    if werkplek != "Niet aan het werk":
                         update_rooster_entry(huidige_dag, medewerker, werkplek)

                progress_bar.progress((i + 1) / totaal_dagen, text=f"Rooster voor {huidige_dag.strftime('%d-%m-%Y')} gevuld...")

            save_all_data()
            progress_bar.empty()
            st.success("Fictieve data volgens de nieuwe bezettingsregels is gegenereerd!")
            st.rerun()


st.divider()
st.header("2. Invoertools")

with st.expander("🧑‍🎓 Disciplinebeheer (Stel hier de vaardigheden per medewerker in)", expanded=True):
    gekozen_medewerker = st.selectbox("Selecteer medewerker om disciplines te beheren:", st.session_state.MEDEWERKERS, key="skill_medewerker")

    if gekozen_medewerker:
        with st.form(key=f"skill_form_{gekozen_medewerker}"):
            st.write(f"Vink de disciplines aan die **{gekozen_medewerker}** beheerst:")
            
            huidige_skills = st.session_state.medewerker_skills.get(gekozen_medewerker, {})
            nieuwe_skills = {}
            
            form_cols = st.columns(len(st.session_state.SKILLS_BEREIKBAARHEID))
            for i, skill in enumerate(st.session_state.SKILLS_BEREIKBAARHEID):
                with form_cols[i]:
                    nieuwe_skills[skill] = st.checkbox(skill, value=huidige_skills.get(skill, False), key=f"{gekozen_medewerker}_{skill}")
            
            if st.form_submit_button("💾 Sla disciplines op"):
                st.session_state.medewerker_skills[gekozen_medewerker] = nieuwe_skills
                save_all_data()
                st.success(f"Disciplines voor {gekozen_medewerker} opgeslagen!")

with st.expander("⚙️ Werkpatronen instellen en toepassen"):
    with st.form(key="pattern_form"):
        medewerker_patroon = st.selectbox("Selecteer medewerker:", st.session_state.MEDEWERKERS, key="patroon_medewerker")
        huidig_patroon = st.session_state.user_patterns.get(medewerker_patroon, {})
        
        st.write(f"**Weekpatroon voor {medewerker_patroon}:**")
        cols = st.columns(7)
        nieuw_patroon = {}
        for i, dag in enumerate(["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]):
            with cols[i]:
                default = huidig_patroon.get(i, "Niet aan het werk")
                index = st.session_state.WERKPLEK_NAMEN.index(default)
                nieuw_patroon[i] = st.selectbox(dag, st.session_state.WERKPLEK_NAMEN, index=index, key=f"patroon_{medewerker_patroon}_{i}")
        
        c1_form, c2_form = st.columns(2)
        save_pattern = c1_form.form_submit_button("💾 Sla patroon op")
        apply_pattern = c2_form.form_submit_button("📆 Pas patroon toe op huidige maand")

        if save_pattern:
            st.session_state.user_patterns[medewerker_patroon] = nieuw_patroon
            save_all_data()
            st.success(f"Patroon opgeslagen voor {medewerker_patroon}.")

        if apply_pattern:
            patroon = st.session_state.user_patterns.get(medewerker_patroon)
            if not patroon:
                 st.warning(f"Sla eerst een patroon op voor {medewerker_patroon}.")
            else:
                vandaag = datetime.date.today()
                _, dagen_in_maand = py_cal.monthrange(vandaag.year, vandaag.month)
                for dag_nummer in range(1, dagen_in_maand + 1):
                    datum = datetime.date(vandaag.year, vandaag.month, dag_nummer)
                    werkplek = patroon.get(datum.weekday(), "Niet aan het werk")
                    update_rooster_entry(datum, medewerker_patroon, werkplek)
                save_all_data()
                st.success(f"Patroon van {medewerker_patroon} toegepast op {vandaag.strftime('%B %Y')}.")

with st.expander("✍️ Individuele Dag Aanpassen"):
    col1, col2, col3 = st.columns(3)
    medewerker_invoer = col1.selectbox("Medewerker", st.session_state.MEDEWERKERS, key="invoer_medewerker")
    datum_invoer = col2.date_input("Datum", datetime.date.today(), key="invoer_datum")
    werkplek_invoer = col3.selectbox("Werkplek", st.session_state.WERKPLEK_NAMEN, key="invoer_werkplek")
    
    if st.button("💾 Opslaan"):
        update_rooster_entry(datum_invoer, medewerker_invoer, werkplek_invoer)
        save_all_data()
        st.success(f"Rooster bijgewerkt voor {medewerker_invoer} op {datum_invoer.strftime('%d-%m-%Y')}!")

st.divider()

with st.expander("👑 Teamleiderbeheer"):
    st.subheader("Voortgang Rooster Invoer")
    maand_keuze = st.selectbox(
        "Selecteer een maand om de voortgang te bekijken:",
        options=[(datetime.date(datetime.date.today().year, m, 1)).strftime('%B %Y') for m in range(1, 13)],
        index=datetime.date.today().month - 1
    )
    
    if maand_keuze:
        year = int(maand_keuze.split(' ')[1])
        month_name = maand_keuze.split(' ')[0]
        # A little hack to get month number from Dutch month name
        maand_namen_nl = ["", "Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"]
        month_num = maand_namen_nl.index(month_name) if month_name in maand_namen_nl else list(py_cal.month_name).index(month_name)
        
        compleetheid, onvolledig_ingepland = get_maand_voltooiing_percentage(year, month_num)
        
        st.progress(compleetheid / 100, text=f"Rooster voor {maand_keuze} is voor {compleetheid:.1f}% gevuld.")
        
        if onvolledig_ingepland["Medewerker"]:
            with st.container(border=True):
                st.warning("De volgende medewerkers zijn nog niet volledig ingepland voor deze maand (minder dan 70% van de werkdagen):")
                st.dataframe(onvolledig_ingepland, hide_index=True)
        else:
            st.success("Alle medewerkers lijken volledig ingepland voor deze maand.")
