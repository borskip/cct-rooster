# Sla dit bestand op als Rooster_App.py

import streamlit as st
import datetime
import uuid
import calendar as py_cal
import random

from utils import (
    initialize_session_state,
    update_rooster_entry,
    save_all_data,
    get_maand_voltooiing_percentage
)

initialize_session_state()

st.set_page_config(page_title="Invoeren Rooster", page_icon="✍️", layout="wide")

# --- AUTHENTICATIE LOGICA ---
if not st.session_state.get('logged_in_user'):
    st.title("🔒 Inloggen Rooster App")
    st.write("Selecteer je naam en voer het wachtwoord in om verder te gaan.")

    medewerker_login = st.selectbox("Kies je naam:", options=st.session_state.MEDEWERKERS, index=None, placeholder="Selecteer je naam...")
    password_login = st.text_input("Wachtwoord:", type="password")

    if st.button("Inloggen"):
        if medewerker_login and password_login == st.session_state.PASSWORD:
            st.session_state.logged_in_user = medewerker_login
            if medewerker_login in st.session_state.TEAMLEIDERS:
                st.session_state.user_role = "Teamleider"
            else:
                st.session_state.user_role = "Medewerker"
            st.rerun()
        else:
            st.error("Naam en/of wachtwoord is incorrect.")
else:
    # --- HOOFDPAGINA CONTENT (ALS INGELOGD) ---
    st.sidebar.success(f"Ingelogd als: **{st.session_state.logged_in_user}**")
    if st.sidebar.button("Uitloggen"):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()

    st.title("✍️ Invoeren Rooster")
    st.header("Roosterstatus")
    vastgestelde_maanden = [maand for maand, is_vastgesteld in st.session_state.rooster_vastgesteld.items() if is_vastgesteld]
    if vastgestelde_maanden:
        laatst_vastgesteld = max(vastgestelde_maanden)
        maand_obj = datetime.datetime.strptime(laatst_vastgesteld, "%Y-%m")
        st.success(f"✅ Laatst vastgestelde rooster: **{maand_obj.strftime('%B %Y')}**")
    else:
        st.info("ℹ️ Er zijn momenteel geen roosters vastgesteld.")

    st.divider()
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

    with st.expander("🧑‍🎓 Jouw Disciplines Beheren"):
        with st.form(key=f"skill_form_{st.session_state.logged_in_user}"):
            st.write(f"Vink de disciplines aan die jij beheerst, **{st.session_state.logged_in_user}**:")
            huidige_skills = st.session_state.medewerker_skills.get(st.session_state.logged_in_user, {})
            nieuwe_skills = {}
            form_cols = st.columns(len(st.session_state.SKILLS_BEREIKBAARHEID))
            for i, skill in enumerate(st.session_state.SKILLS_BEREIKBAARHEID):
                with form_cols[i]:
                    nieuwe_skills[skill] = st.checkbox(skill, value=huidige_skills.get(skill, False), key=f"{st.session_state.logged_in_user}_{skill}")
            if st.form_submit_button("💾 Mijn disciplines opslaan"):
                st.session_state.medewerker_skills[st.session_state.logged_in_user] = nieuwe_skills
                save_all_data()
                st.success(f"Jouw disciplines zijn opgeslagen!")

    st.divider()

    if st.session_state.user_role == 'Teamleider':
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
            # Code voor demo-data generatie is hier weggelaten voor duidelijkheid
            pass
