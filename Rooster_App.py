# Sla dit bestand op als Rooster_App.py

import streamlit as st
import datetime
import uuid
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
    page_title="Invoeren Rooster",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ Invoeren Rooster")

# Roosterstatus sectie
st.header("Roosterstatus")
vastgestelde_maanden = [maand for maand, is_vastgesteld in st.session_state.rooster_vastgesteld.items() if is_vastgesteld]
if vastgestelde_maanden:
    laatst_vastgesteld = max(vastgestelde_maanden)
    maand_obj = datetime.datetime.strptime(laatst_vastgesteld, "%Y-%m")
    st.success(f"✅ Laatst vastgestelde rooster: **{maand_obj.strftime('%B %Y')}**")
else:
    st.info("ℹ️ Er zijn momenteel geen roosters vastgesteld.")

st.divider()

# Invoertools sectie met aangepaste volgorde
st.header("Invoertools")

with st.expander("⚙️ Werkpatronen instellen en toepassen", expanded=True):
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

with st.expander("✍️ Individuele Dag Invoeren"):
    col1_form, col2_form, col3_form = st.columns(3)
    medewerker_invoer = col1_form.selectbox("Medewerker", st.session_state.MEDEWERKERS, key="invoer_medewerker")
    datum_invoer = col2_form.date_input("Datum", datetime.date.today(), key="invoer_datum")
    werkplek_invoer = col3_form.selectbox("Werkplek", st.session_state.WERKPLEK_NAMEN, key="invoer_werkplek")
    
    maand_key_invoer = datum_invoer.strftime("%Y-%m")
    is_vastgesteld_invoer = st.session_state.rooster_vastgesteld.get(maand_key_invoer, False)
    
    if is_vastgesteld_invoer:
        st.warning("Let op: het rooster voor deze maand is vastgesteld. Een wijziging indienen leidt tot een verzoek.")
    
    if st.button("💾 Opslaan of Aanvragen"):
        if not is_vastgesteld_invoer:
            update_rooster_entry(datum_invoer, medewerker_invoer, werkplek_invoer)
            save_all_data()
            st.success(f"Rooster bijgewerkt voor {medewerker_invoer} op {datum_invoer.strftime('%d-%m-%Y')}!")
        else:
            verzoek_id = str(uuid.uuid4())
            if maand_key_invoer not in st.session_state.wijzigingsverzoeken:
                st.session_state.wijzigingsverzoeken[maand_key_invoer] = []
            
            st.session_state.wijzigingsverzoeken[maand_key_invoer].append({
                "id": verzoek_id,
                "medewerker": medewerker_invoer, 
                "datum": datum_invoer.strftime("%Y-%m-%d"),
                "werkplek": werkplek_invoer
            })
            save_all_data()
            st.success("Wijzigingsverzoek ingediend ter goedkeuring!")
            st.info("De teamleider kan het verzoek goedkeuren onder 'Teamleiderbeheer'.")
        st.rerun()

with st.expander("🧑‍🎓 Disciplinebeheer (Stel hier de vaardigheden per medewerker in)"):
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

st.divider()

with st.expander("👑 Teamleiderbeheer", expanded=False):
    maand_opties = [(datetime.date(datetime.date.today().year, m, 1)) for m in range(1, 13)]
    geselecteerde_datum = st.selectbox("Selecteer een maand voor beheer:", options=maand_opties, format_func=lambda date: date.strftime('%B %Y'), index=datetime.date.today().month - 1)
    maand_key_beheer = geselecteerde_datum.strftime("%Y-%m")
    tab1, tab2 = st.tabs(["Voortgang & Vaststellen", "Wijzigingsverzoeken"])
    with tab1:
        st.subheader(f"Status voor {geselecteerde_datum.strftime('%B %Y')}")
        year = geselecteerde_datum.year
        month_num = geselecteerde_datum.month
        compleetheid, onvolledig_ingepland = get_maand_voltooiing_percentage(year, month_num)
        st.progress(compleetheid / 100, text=f"Rooster is voor {compleetheid:.1f}% gevuld.")
        if onvolledig_ingepland["Medewerker"]:
            with st.container(border=True):
                st.warning("De volgende medewerkers zijn nog niet volledig ingepland:")
                st.dataframe(onvolledig_ingepland, hide_index=True)
        st.divider()
        is_vastgesteld = st.session_state.rooster_vastgesteld.get(maand_key_beheer, False)
        if is_vastgesteld:
            st.success("✅ Rooster is vastgesteld.")
            if st.button(f"🔓 Rooster voor {geselecteerde_datum.strftime('%B')} vrijgeven"):
                st.session_state.rooster_vastgesteld[maand_key_beheer] = False
                save_all_data()
                st.rerun()
        else:
            st.warning("⚠️ Rooster nog niet vastgesteld.")
            if st.button(f"🔒 Rooster voor {geselecteerde_datum.strftime('%B')} vaststellen"):
                st.session_state.rooster_vastgesteld[maand_key_beheer] = True
                save_all_data()
                st.rerun()
    with tab2:
        st.subheader(f"Openstaande verzoeken voor {geselecteerde_datum.strftime('%B %Y')}")
        verzoeken = st.session_state.wijzigingsverzoeken.get(maand_key_beheer, [])
        if not verzoeken:
            st.info("Geen openstaande wijzigingsverzoeken voor deze maand.")
        else:
            for verzoek in verzoeken:
                with st.container(border=True):
                    col1_req, col2_req = st.columns([3, 1])
                    with col1_req:
                        st.write(f"**{verzoek['medewerker']}** wil op **{verzoek['datum']}** naar **{verzoek['werkplek']}**")
                    with col2_req:
                        sub_col1, sub_col2 = st.columns(2)
                        if sub_col1.button("✅", key=f"goed_{verzoek['id']}", help="Goedkeuren"):
                            verzoek_datum = datetime.datetime.strptime(verzoek["datum"], "%Y-%m-%d").date()
                            update_rooster_entry(verzoek_datum, verzoek["medewerker"], verzoek["werkplek"])
                            st.session_state.wijzigingsverzoeken[maand_key_beheer] = [v for v in verzoeken if v['id'] != verzoek['id']]
                            save_all_data()
                            st.success("Verzoek goedgekeurd en rooster bijgewerkt.")
                            st.rerun()
                        if sub_col2.button("❌", key=f"af_{verzoek['id']}", help="Afwijzen"):
                            st.session_state.wijzigingsverzoeken[maand_key_beheer] = [v for v in verzoeken if v['id'] != verzoek['id']]
                            save_all_data()
                            st.warning("Verzoek afgewezen.")
                            st.rerun()

with st.expander("🗑️ Roosterbeheer"):
    st.warning("Let op: het verwijderen van alle roosterdata kan niet ongedaan worden gemaakt.")
    col1_del, col2_del = st.columns(2)
    with col1_del:
        if st.button("Verwijder definitief Alle Roosterdata", type="primary"):
            st.session_state.rooster_data = {}
            st.session_state.beschikbaarheid_data = {}
            st.session_state.notes_data = {}
            st.session_state.wijzigingsverzoeken = {}
            st.session_state.rooster_vastgesteld = {}
            save_all_data()
            st.success("Alle roosterdata, notities en verzoeken zijn verwijderd.")
            st.rerun()
    with col2_del:
        if st.button("Optioneel: Genereer demo-data"):
            # --- VOLLEDIGE CODE VOOR DEMO DATA ---
            st.session_state.rooster_data = {}
            st.session_state.beschikbaarheid_data = {}
            st.session_state.notes_data = {}
            st.session_state.medewerker_skills = {}

            for medewerker in st.session_state.MEDEWERKERS:
                num_skills = random.randint(1, 2)
                toegekende_skills = random.sample(st.session_state.SKILLS_BEREIKBAARHEID, num_skills)
                st.session_state.medewerker_skills[medewerker] = {s: (s in toegekende_skills) for s in st.session_state.SKILLS_BEREIKBAARHEID}

            start_datum = datetime.date(2025, 1, 1)
            eind_datum = datetime.date(2025, 12, 31)
            totaal_dagen = (eind_datum - start_datum).days + 1
            progress_bar = st.progress(0, text="Slim rooster genereren...")

            for i in range(totaal_dagen):
                huidige_dag = start_datum + datetime.timedelta(days=i)
                dag_index = huidige_dag.weekday()
                kantoor_doel = 0
                if dag_index in [1, 2, 3]: kantoor_doel = 15
                elif dag_index == 0: kantoor_doel = 8

                beschikbare_medewerkers = st.session_state.MEDEWERKERS.copy()
                random.shuffle(beschikbare_medewerkers)
                
                kantoor_medewerkers = []
                if kantoor_doel > 0:
                    kantoor_medewerkers = beschikbare_medewerkers[:kantoor_doel]
                    for medewerker in kantoor_medewerkers:
                        update_rooster_entry(huidige_dag, medewerker, "Kantoor")

                overige_medewerkers = [m for m in beschikbare_medewerkers if m not in kantoor_medewerkers]
                for medewerker in overige_medewerkers:
                    werkplek = "Niet aan het werk"
                    if dag_index >= 5:
                        if random.random() < 0.05:
                           werkplek = random.choice(["Aan het werk", "Actiedag"])
                    else:
                        is_vakantie = (huidige_dag.month in [7, 8] and random.random() < 0.25) or (huidige_dag.month not in [7, 8] and random.random() < 0.07)
                        if is_vakantie: werkplek = "Vakantie"
                        elif random.random() > 0.15:
                            werkplek_opties = [w['naam'] for w in st.session_state.WERKPLEKKEN_CONFIG if w['naam'] not in ["Kantoor"] + st.session_state.NIET_WERKEND_STATUS]
                            werkplek = random.choice(werkplek_opties)
                    if werkplek != "Niet aan het werk":
                         update_rooster_entry(huidige_dag, medewerker, werkplek)
                progress_bar.progress((i + 1) / totaal_dagen, text=f"Rooster voor {huidige_dag.strftime('%d-%m-%Y')} gevuld...")

            save_all_data()
            progress_bar.empty()
            st.success("Fictieve data volgens de nieuwe bezettingsregels is gegenereerd!")
            st.rerun()
