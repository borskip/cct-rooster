# Sla dit bestand op als Rooster_App.py

import streamlit as st
import datetime
import uuid
import calendar as py_cal
import random

# Probeer pandas te importeren, geef een foutmelding als het niet lukt
try:
    import pandas as pd
except ImportError:
    st.error("De 'pandas' library is niet geïnstalleerd. Installeer deze a.u.b. met het commando: pip install pandas")
    st.stop()

from utils import (
    initialize_session_state,
    update_rooster_entry,
    save_all_data,
    get_maand_voltooiing_percentage,
    get_day_stats,
    get_team_event_for_date
)

initialize_session_state()

st.set_page_config(page_title="Invoeren Rooster", page_icon="✍️", layout="wide")

# --- AUTHENTICATIE LOGICA ---
# Als er niemand is ingelogd, toon het login scherm
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
# ALS ER WEL IEMAND IS INGELOGD, TOON DE APP
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
    
    # --- EXPANDER 1: JOUW DAG INPLANNEN ---
    with st.expander("✍️ Jouw Dag Inplannen", expanded=True):
        medewerker_invoer = st.session_state.logged_in_user
        
        col1_form, col2_form = st.columns(2)
        with col1_form:
            datum_invoer = st.date_input("Kies een datum", datetime.date.today(), key="invoer_datum")
        with col2_form:
            werkplek_invoer = st.selectbox("Kies je werkplek/dienst", st.session_state.WERKPLEK_NAMEN, key="invoer_werkplek")

        if datum_invoer:
            team_event = get_team_event_for_date(datum_invoer)
            if team_event:
                st.info(f"🗓️ **Team Moment:** Op deze dag is '{team_event}' gepland!", icon="❗")

            with st.container(border=True):
                kantoor_count, gedekte_skills = get_day_stats(datum_invoer)
                status_cols = st.columns(len(st.session_state.SKILLS_BEREIKBAARHEID) + 1)
                with status_cols[0]:
                    st.markdown(f"**👥 Kantoor: {kantoor_count}**")
                for i, skill in enumerate(st.session_state.SKILLS_BEREIKBAARHEID):
                    with status_cols[i+1]:
                        emoji = "✅" if gedekte_skills[skill] else "❌"
                        st.markdown(f"{emoji} {skill}")

        maand_key_invoer = datum_invoer.strftime("%Y-%m")
        is_vastgesteld_invoer = st.session_state.rooster_vastgesteld.get(maand_key_invoer, False)
        
        if is_vastgesteld_invoer:
            st.warning("Let op: het rooster voor deze maand is vastgesteld. Een wijziging indienen leidt tot een verzoek.")
        
        col_plan, col_view = st.columns(2)
        with col_plan:
            if st.button("💾 Plan mij in", type="primary"):
                if not is_vastgesteld_invoer:
                    update_rooster_entry(datum_invoer, medewerker_invoer, werkplek_invoer)
                    save_all_data()
                    st.success(f"Je bent ingepland voor {werkplek_invoer} op {datum_invoer.strftime('%d-%m-%Y')}!")
                else:
                    verzoek_id = str(uuid.uuid4())
                    if maand_key_invoer not in st.session_state.wijzigingsverzoeken:
                        st.session_state.wijzigingsverzoeken[maand_key_invoer] = []
                    st.session_state.wijzigingsverzoeken[maand_key_invoer].append({
                        "id": verzoek_id, "medewerker": medewerker_invoer, 
                        "datum": datum_invoer.strftime("%Y-%m-%d"), "werkplek": werkplek_invoer
                    })
                    save_all_data()
                    st.success("Wijzigingsverzoek ingediend!")
                st.rerun()

        with col_view:
            with st.popover("👀 Wie is er dan?"):
                team_event_popover = get_team_event_for_date(datum_invoer)
                if team_event_popover:
                    st.markdown(f"🗓️ **Team Moment: {team_event_popover}**")
                    st.divider()
                
                datum_str = datum_invoer.strftime("%Y-%m-%d")
                dag_rooster = st.session_state.rooster_data.get(datum_str, {})
                werkende_collegas = {m: w for m, w in dag_rooster.items() if w not in st.session_state.NIET_WERKEND_STATUS}

                if not werkende_collegas:
                    st.info("Nog niemand ingepland op deze dag.")
                else:
                    st.markdown(f"**Aanwezig op {datum_invoer.strftime('%d-%m-%Y')}:**")
                    for medewerker, werkplek in sorted(werkende_collegas.items()):
                        werkplek_info = st.session_state.WERKPLEK_MAP.get(werkplek, {
                            "kleur": "#6c757d", "tekstkleur": "#ffffff", "afkorting": "AANW"
                        })
                        st.markdown(f"""
                        <div style='display: flex; align-items: center; margin-bottom: 5px;'>
                            <span style='background-color: {werkplek_info["kleur"]}; color: {werkplek_info["tekstkleur"]}; padding: 2px 5px; border-radius: 4px; font-weight: bold; font-family: monospace; margin-right: 8px;'>
                                {werkplek_info["afkorting"]}
                            </span>
                            <span>{medewerker} ({werkplek})</span>
                        </div>
                        """, unsafe_allow_html=True)

    # --- EXPANDER 2: WERKPATROON INSTELLEN (NIEUWE CODE) ---
    with st.expander("⚙️ Jouw Werkpatroon instellen en toepassen"):
        medewerker_patroon = st.session_state.logged_in_user

        with st.form(key="pattern_save_form"):
            st.write(f"**Stap 1: Stel hier jouw standaard weekpatroon in, {medewerker_patroon}.**")
            huidig_patroon = st.session_state.user_patterns.get(medewerker_patroon, {})
            
            cols = st.columns(7)
            nieuw_patroon = {}
            dagen_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
            
            for i, dag_naam in enumerate(dagen_namen):
                with cols[i]:
                    default_werkplek = huidig_patroon.get(str(i), "Niet aan het werk")
                    try:
                        index = st.session_state.WERKPLEK_NAMEN.index(default_werkplek)
                    except ValueError:
                        index = st.session_state.WERKPLEK_NAMEN.index("Niet aan het werk")
                    
                    nieuw_patroon[str(i)] = st.selectbox(dag_naam[:2], st.session_state.WERKPLEK_NAMEN, index=index, key=f"patroon_{medewerker_patroon}_{i}")

            if st.form_submit_button("💾 Sla mijn patroon op", type="primary"):
                st.session_state.user_patterns[medewerker_patroon] = nieuw_patroon
                save_all_data()
                st.success(f"Jouw patroon is opgeslagen, {medewerker_patroon}.")
                st.rerun()

        st.divider()

        st.write(f"**Stap 2: Pas je opgeslagen patroon toe op het rooster.**")
        
        patroon = st.session_state.user_patterns.get(medewerker_patroon)

        if not patroon:
            st.warning("Je hebt nog geen patroon opgeslagen. Doe dat eerst hierboven.")
        else:
            st.write("Jouw huidige opgeslagen patroon:")
            patroon_cols = st.columns(7)
            for i, dag_naam in enumerate(dagen_namen):
                werkplek = patroon.get(str(i), "N.v.t.")
                patroon_cols[i].metric(label=dag_naam, value=werkplek)

            today = datetime.date.today()
            six_months_later = today + datetime.timedelta(days=182)
            
            col_start, col_end = st.columns(2)
            with col_start:
                start_datum = st.date_input("Startdatum", value=today)
            with col_end:
                eind_datum = st.date_input("Einddatum", value=six_months_later)
            
            if start_datum > eind_datum:
                st.error("De startdatum kan niet na de einddatum liggen.")
            elif st.button("📆 Pas patroon toe op geselecteerde periode", type="primary"):
                datums_in_periode = pd.date_range(start_datum, eind_datum)
                updates_gedaan = 0
                
                progress_text = "Patroon wordt toegepast op het rooster..."
                my_bar = st.progress(0, text=progress_text)

                for i, dag in enumerate(datums_in_periode):
                    weekdag_nummer = str(dag.weekday())
                    werkplek = patroon.get(weekdag_nummer, "Niet aan het werk")
                    datum_voor_update = dag.date()
                    
                    update_rooster_entry(datum_voor_update, medewerker_patroon, werkplek)
                    updates_gedaan += 1
                    
                    my_bar.progress((i + 1) / len(datums_in_periode), text=f"{progress_text} ({dag.strftime('%d-%m-%Y')})")
                
                save_all_data()
                
                my_bar.empty()
                st.success(f"✅ Jouw patroon is succesvol toegepast op **{updates_gedaan} dagen** in de periode van {start_datum.strftime('%d-%m-%Y')} tot {eind_datum.strftime('%d-%m-%Y')}.")
                st.rerun()

    # --- EXPANDER 3: JOUW DISCIPLINES BEHEREN ---
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

    # --- EXPANDER 4: TEAM INZET ORGANISEREN ---
    with st.expander("🤝 Team Inzet Organiseren"):
        st.info("Creëer een oproep voor een bijzondere inzet. Je collega's kunnen zich vervolgens aanmelden voor de disciplines die jij nodig hebt.")
        
        with st.form("bijzondere_inzet_form", clear_on_submit=True):
            inzet_maker = st.session_state.logged_in_user
            inzet_beschrijving = st.text_input("Beschrijving van de inzet", placeholder="Bijv: Ondersteuning ME locatie X, Spoedklus Y")
            
            c1_form, c2_form = st.columns(2)
            with c1_form:
                inzet_datum = st.date_input("Datum van de inzet", min_value=datetime.date.today())
            with c2_form:
                st.write("**Hoeveel mensen heb je nodig per discipline?** (Laat op 0 als niet van toepassing)")

            behoefte = {}
            skill_cols = st.columns(len(st.session_state.SKILLS_BEREIKBAARHEID))
            for i, skill in enumerate(st.session_state.SKILLS_BEREIKBAARHEID):
                with skill_cols[i]:
                    behoefte[skill] = st.number_input(skill, min_value=0, value=0, step=1, key=f"need_{skill}")

            if st.form_submit_button("📢 Plaats Oproep", type="primary"):
                if not inzet_beschrijving:
                    st.warning("Geef een beschrijving van de inzet op.")
                elif sum(behoefte.values()) == 0:
                    st.warning("Geef aan hoeveel mensen je nodig hebt voor minstens één discipline.")
                else:
                    gefilterde_behoefte = {s: v for s, v in behoefte.items() if v > 0}
                    
                    nieuwe_inzet = {
                        "id": str(uuid.uuid4()),
                        "maker": inzet_maker,
                        "datum": inzet_datum.strftime("%Y-%m-%d"),
                        "werkplek": inzet_beschrijving,
                        "behoefte": gefilterde_behoefte,
                        "aanmeldingen": {skill: [] for skill in gefilterde_behoefte},
                        "status": "open"
                    }
                    st.session_state.open_diensten.append(nieuwe_inzet)
                    save_all_data()
                    st.success(f"Oproep geplaatst voor {inzet_beschrijving} op {inzet_datum.strftime('%d-%m-%Y')}.")
                    st.rerun()
                    
    # --- EXPANDER 5: TEAMLEIDERBEHEER (ALLEEN VOOR TEAMLEIDERS) ---
    if st.session_state.user_role == 'Teamleider':
        with st.expander("👑 Teamleiderbeheer", expanded=False):
            maand_opties = [(datetime.date(datetime.date.today().year, m, 1)) for m in range(1, 13)]
            geselecteerde_datum = st.selectbox(
                "Selecteer een maand voor beheer:", 
                options=maand_opties, 
                format_func=lambda date: date.strftime('%B %Y'), 
                index=datetime.date.today().month - 1,
                key="teamleider_maand_select"
            )
            maand_key_beheer = geselecteerde_datum.strftime("%Y-%m")
            
            tab1, tab2 = st.tabs(["Voortgang & Vaststellen", "Wijzigingsverzoeken"])

            with tab1:
                st.subheader(f"Status voor {geselecteerde_datum.strftime('%B %Y')}")
                year, month_num = geselecteerde_datum.year, geselecteerde_datum.month
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

    # --- EXPANDER 6: ROOSTERBEHEER (DATA RESET) ---
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
                st.session_state.open_diensten = []
                st.session_state.team_events = []
                save_all_data()
                st.success("Alle roosterdata, notities en verzoeken zijn verwijderd.")
                st.rerun()
        with col2_del:
            if st.button("Optioneel: Genereer demo-data"):
                # Code voor demo-data generatie is hier ongewijzigd gelaten
                st.session_state.rooster_data = {}
                st.session_state.beschikbaarheid_data = {}
                st.session_state.notes_data = {}
                st.session_state.medewerker_skills = {}
                st.session_state.open_diensten = []
                st.session_state.team_events = []
                for medewerker in st.session_state.MEDEWERKERS:
                    num_skills = random.randint(1, 2)
                    toegekende_skills = random.sample(st.session_state.SKILLS_BEREIKBAARHEID, num_skills)
                    st.session_state.medewerker_skills[medewerker] = {s: (s in toegekende_skills) for s in st.session_state.SKILLS_BEREIKBAARHEID}
                start_datum = datetime.date.today() - datetime.timedelta(days=90)
                eind_datum = datetime.date.today() + datetime.timedelta(days=90)
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
                st.success("Fictieve data is gegenereerd!")
                st.rerun()
