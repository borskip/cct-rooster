# Sla dit bestand op als Rooster_App.py

import streamlit as st
import datetime
import uuid
import calendar as py_cal
import random

# --- PAGINA CONFIGURATIE EN CONSTANTEN ---
st.set_page_config(
    page_title="Rooster App - Controlepaneel",
    page_icon="🛠️",
    layout="wide"
)

def setup_constants():
    """Initialiseert alle constanten en slaat ze op in de session_state."""
    if 'constants_set' not in st.session_state:
        st.session_state.MEDEWERKERS = ["Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"]
        st.session_state.WERKPLEKKEN_CONFIG = [
            {"naam": "Kantoor", "emoji": "🏤", "afkorting": "KNT", "display_group": "Kantoor", "kleur": "#28a745", "tekstkleur": "#ffffff"},
            {"naam": "Aan het werk", "emoji": "💼", "afkorting": "WRK", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
            {"naam": "Opleiding/cursus", "emoji": "🧑‍🏫", "afkorting": "OPL", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
            {"naam": "IBT", "emoji": "💪", "afkorting": "IBT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
            {"naam": "Actiedag", "emoji": "🦺", "afkorting": "ACT", "display_group": "Werkend_Anders", "kleur": "#6c757d", "tekstkleur": "#ffffff"},
            {"naam": "Vakantie", "emoji": "🏖️", "afkorting": "VAK", "display_group": "Niet_Werkend", "kleur": None},
            {"naam": "Niet aan het werk", "emoji": "❌", "afkorting": "---", "display_group": "Niet_Werkend", "kleur": None},
        ]
        st.session_state.WERKPLEK_MAP = {w["naam"]: w for w in st.session_state.WERKPLEKKEN_CONFIG}
        st.session_state.WERKPLEK_NAMEN = [w["naam"] for w in st.session_state.WERKPLEKKEN_CONFIG]
        st.session_state.SKILLS_BEREIKBAARHEID = ["Digi", "Intel", "Leiding", "Tactiek"]
        st.session_state.NIET_WERKEND_STATUS = ["Vakantie", "Niet aan het werk"]
        st.session_state.BESCHIKBAAR_VOOR_DIENST = ["Kantoor", "Aan het werk"]
        st.session_state.constants_set = True

setup_constants()

def initialize_session_state():
    """Start de app altijd met een lege staat bij een nieuwe sessie."""
    if 'app_initialized' not in st.session_state:
        st.session_state.rooster_data = {}
        st.session_state.beschikbaarheid_data = {}
        st.session_state.user_patterns = {}
        st.session_state.rooster_vastgesteld = {}
        st.session_state.wijzigingsverzoeken = {}
        st.session_state.pending_change = None
        st.session_state.medewerker_skills = {}
        st.session_state.app_initialized = True

def update_rooster_entry(datum, medewerker, werkplek):
    """Berekent beschikbaarheid o.b.v. VASTE disciplines en werkplek."""
    datum_str = datum.strftime("%Y-%m-%d")
    st.session_state.rooster_data.setdefault(datum_str, {})
    st.session_state.beschikbaarheid_data.setdefault(datum_str, {})

    if werkplek == "Niet aan het werk":
        st.session_state.rooster_data[datum_str].pop(medewerker, None)
    else:
        st.session_state.rooster_data[datum_str][medewerker] = werkplek

    persoonlijke_skills = st.session_state.medewerker_skills.get(medewerker, {})
    is_beschikbaar_voor_dienst = werkplek in st.session_state.BESCHIKBAAR_VOOR_DIENST

    if is_beschikbaar_voor_dienst:
        bereikbaarheid_details = {"status": "Bereikbaar"}
        for skill in st.session_state.SKILLS_BEREIKBAARHEID:
            heeft_skill = persoonlijke_skills.get(skill, False)
            bereikbaarheid_details[skill] = heeft_skill
        st.session_state.beschikbaarheid_data[datum_str][medewerker] = bereikbaarheid_details
    else:
        st.session_state.beschikbaarheid_data[datum_str].pop(medewerker, None)

initialize_session_state()

# --- HOOFDPAGINA CONTENT ---
st.title("🛠️ Controlepaneel Rooster App")
st.markdown("Gebruik de beheertools hieronder om het rooster handmatig te vullen en disciplines toe te wijzen.")
st.divider()

st.header("1. Roosterbeheer")
col1, col2 = st.columns([1, 1.5])
with col1:
    if st.button("🗑️ Verwijder Alle Roosterdata", type="primary"):
        st.session_state.rooster_data = {}
        st.session_state.beschikbaarheid_data = {}
        st.success("Alle roosterdata is verwijderd.")
        st.rerun()
with col2:
    with st.expander("Optioneel: Genereer demo-data"):
        if st.button("✨ Genereer Fictieve Data 2025"):
            st.session_state.medewerker_skills = {}
            for medewerker in st.session_state.MEDEWERKERS:
                num_skills = random.randint(1, 2)
                toegekende_skills = random.sample(st.session_state.SKILLS_BEREIKBAARHEID, num_skills)
                st.session_state.medewerker_skills[medewerker] = {s: (s in toegekende_skills) for s in st.session_state.SKILLS_BEREIKBAARHEID}
            
            for key in ['rooster_data', 'beschikbaarheid_data', 'rooster_vastgesteld', 'wijzigingsverzoeken']:
                st.session_state[key] = {}
            
            start_datum = datetime.date(2025, 1, 1)
            eind_datum = datetime.date(2025, 12, 31)
            totaal_dagen = (eind_datum - start_datum).days + 1

            progress_bar = st.progress(0, text="Data genereren...")
            for i in range(totaal_dagen):
                huidige_dag = start_datum + datetime.timedelta(days=i)
                for medewerker in st.session_state.MEDEWERKERS:
                    if random.random() < 0.20: continue
                    is_vakantie = (huidige_dag.month in [7, 8] and random.random() < 0.25) or (huidige_dag.month not in [7, 8] and random.random() < 0.07)
                    werkplek = "Vakantie" if is_vakantie else random.choice([w['naam'] for w in st.session_state.WERKPLEKKEN_CONFIG if w['naam'] not in st.session_state.NIET_WERKEND_STATUS])
                    update_rooster_entry(huidige_dag, medewerker, werkplek)
                progress_bar.progress((i + 1) / totaal_dagen, text=f"Datum: {huidige_dag.strftime('%d-%m-%Y')}")
            
            progress_bar.empty()
            st.success("Fictieve data en disciplines gegenereerd!")
            st.info("👈 Bekijk de resultaten op de overzichtspagina's in de zijbalk.")
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
                st.success(f"Disciplines voor {gekozen_medewerker} opgeslagen!")
                st.rerun()

with st.expander("⚙️ Werkpatronen instellen en toepassen"):
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
    
    if st.button("💾 Sla patroon op"):
        st.session_state.user_patterns[medewerker_patroon] = nieuw_patroon
        st.success(f"Patroon opgeslagen voor {medewerker_patroon}.")

    if st.button("📆 Pas patroon toe op huidige maand"):
        patroon = st.session_state.user_patterns.get(medewerker_patroon)
        if not patroon:
             st.warning(f"Er is geen patroon opgeslagen voor {medewerker_patroon}.")
        else:
            vandaag = datetime.date.today()
            _, dagen_in_maand = py_cal.monthrange(vandaag.year, vandaag.month)
            for dag_nummer in range(1, dagen_in_maand + 1):
                datum = datetime.date(vandaag.year, vandaag.month, dag_nummer)
                werkplek = patroon.get(datum.weekday(), "Niet aan het werk")
                update_rooster_entry(datum, medewerker_patroon, werkplek)
            st.success(f"Patroon van {medewerker_patroon} toegepast op {vandaag.strftime('%B %Y')}.")
            st.rerun()

with st.expander("✍️ Individuele Dag Aanpassen"):
    col1, col2, col3 = st.columns(3)
    medewerker_invoer = col1.selectbox("Medewerker", st.session_state.MEDEWERKERS, key="invoer_medewerker")
    datum_invoer = col2.date_input("Datum", datetime.date.today(), key="invoer_datum")
    werkplek_invoer = col3.selectbox("Werkplek", st.session_state.WERKPLEK_NAMEN, key="invoer_werkplek")
    
    maand_key_invoer = datum_invoer.strftime("%Y-%m")
    is_vastgesteld_invoer = st.session_state.rooster_vastgesteld.get(maand_key_invoer, False)
    if is_vastgesteld_invoer:
        st.warning("Let op: het rooster voor deze maand is vastgesteld. Wijziging wordt een verzoek.")
    
    if st.button("💾 Opslaan of Aanvragen"):
        if not is_vastgesteld_invoer:
            update_rooster_entry(datum_invoer, medewerker_invoer, werkplek_invoer)
            st.success(f"Rooster bijgewerkt voor {medewerker_invoer} op {datum_invoer.strftime('%d-%m-%Y')}!")
            st.rerun()
        else:
            st.session_state.pending_change = {
                "medewerker": medewerker_invoer, "datum": datum_invoer.strftime("%Y-%m-%d"), 
                "maand": maand_key_invoer, "werkplek": werkplek_invoer
            }
            st.rerun()

    if st.session_state.pending_change:
        pc = st.session_state.pending_change
        with st.form("verzoek_bevestiging"):
            st.warning(f"Verzoek voor {pc['medewerker']} op {pc['datum']} → {pc['werkplek']}")
            akkoord = st.checkbox("Ik begrijp dat dit een verzoek is")
            if st.form_submit_button("✅ Indienen"):
                if akkoord:
                    verzoeken = st.session_state.wijzigingsverzoeken.setdefault(pc["maand"], [])
                    pc["id"] = str(uuid.uuid4())
                    verzoeken.append(pc)
                    st.session_state.pending_change = None
                    st.success("Verzoek ingediend!")
                    st.rerun()
                else:
                    st.error("Bevestig je verzoek via de checkbox.")

with st.expander("👑 Teamleiderbeheer"):
    vandaag = datetime.date.today()
    maand_opties = [(vandaag.replace(month=m)).strftime("%Y-%m") for m in range(1, 13)]
    maand_key_beheer = st.selectbox("Selecteer maand voor beheer:", maand_opties, index=vandaag.month - 1)
    
    vastgesteld_beheer = st.session_state.rooster_vastgesteld.get(maand_key_beheer, False)
    st.subheader(f"Status maand {maand_key_beheer}")
    if vastgesteld_beheer:
        st.success("✅ Rooster is vastgesteld.")
        if st.button(f"🔓 Rooster voor {maand_key_beheer} vrijgeven"):
            st.session_state.rooster_vastgesteld[maand_key_beheer] = False
            st.rerun()
    else:
        st.warning("⚠️ Rooster nog niet vastgesteld.")
        if st.button(f"🔒 Rooster voor {maand_key_beheer} vaststellen"):
            st.session_state.rooster_vastgesteld[maand_key_beheer] = True
            st.rerun()

    st.divider()
    st.subheader(f"📬 Wijzigingsverzoeken voor {maand_key_beheer}")
    verzoeken_beheer = st.session_state.wijzigingsverzoeken.get(maand_key_beheer, [])
    if not verzoeken_beheer:
        st.info("Geen openstaande verzoeken voor deze maand.")
    else:
        for verzoek in verzoeken_beheer:
            with st.container(border=True):
                st.write(f"**{verzoek['medewerker']}** – {verzoek['datum']} → **{verzoek['werkplek']}**")
                c1, c2, _ = st.columns([1, 1, 4])
                if c1.button("✅ Goedkeuren", key=f"goed_{verzoek['id']}"):
                    verzoek_datum = datetime.datetime.strptime(verzoek["datum"], "%Y-%m-%d").date()
                    update_rooster_entry(verzoek_datum, verzoek["medewerker"], verzoek["werkplek"])
                    st.session_state.wijzigingsverzoeken[maand_key_beheer] = [v for v in verzoeken_beheer if v["id"] != verzoek["id"]]
                    st.success("Verzoek goedgekeurd.")
                    st.rerun()
                if c2.button("❌ Afwijzen", key=f"af_{verzoek['id']}"):
                    st.session_state.wijzigingsverzoeken[maand_key_beheer] = [v for v in verzoeken_beheer if v["id"] != verzoek["id"]]
                    st.warning("Verzoek afgewezen.")
                    st.rerun()
