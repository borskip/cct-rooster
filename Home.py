import streamlit as st
from streamlit_calendar import calendar
import datetime
import uuid
import calendar as py_cal
import json
from pathlib import Path

# =========================================================================
#                   1. CONFIGURATIE & CONSTANTEN
# =========================================================================

st.set_page_config(page_title="Rooster", layout="wide")
st.title("🗓️ Teamrooster")

st.markdown("""
    <style>
    .fc-license-message { display: none !important; }
    .st-expander > summary > .st-emotion-cache-1f1p6pr { font-size: 1.1rem; }
    .fc-event { border-radius: 4px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; font-weight: 500 !important; padding: 2px 4px !important; }
    .fc-event-main-frame { font-size: 12px !important; line-height: 1.3 !important; }
    .fc-event-main-frame .fc-event-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    div[data-baseweb="radio"] > label { background-color: #31333F; padding: 5px 10px; border-radius: 5px; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = Path("rooster_app_data.json")
TEAMLEIDERS = ["Jan", "Emma"]
MEDEWERKERS = sorted(["Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob", "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"])
WERKPLEKKEN_CONFIG = [{"naam": "Niet ingepland", "afkorting": "N.v.t.", "emoji": "❌", "kleur": "#495057", "tekst": "#F8F9FA"}, {"naam": "Kantoor", "afkorting": "Kan", "emoji": "🏤", "kleur": "#28A745", "tekst": "#FFFFFF"}, {"naam": "Thuiswerk", "afkorting": "Thuis", "emoji": "🏠", "kleur": "#17A2B8", "tekst": "#FFFFFF"}, {"naam": "Opleiding", "afkorting": "Opl", "emoji": "🧑‍🏫", "kleur": "#FFC107", "tekst": "#212529"}, {"naam": "IBT", "afkorting": "IBT", "emoji": "💪", "kleur": "#6F42C1", "tekst": "#FFFFFF"}, {"naam": "Vakantie/Verlof", "afkorting": "Vak", "emoji": "🏖️", "kleur": "#DC3545", "tekst": "#FFFFFF"}]
WERKPLEK_MAP = {item["naam"]: item for item in WERKPLEKKEN_CONFIG}
WERKPLEK_NAMEN = [item["naam"] for item in WERKPLEKKEN_CONFIG]
DEFAULT_WERKPLEK = "Niet ingepland"
DAGEN_VD_WEEK = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
ROLES = {"TEAMLEIDER": "Teamleider", "MEDEWERKER": "Medewerker"}

# Discipline toewijzing
DISCIPLINES = {
    "digi": ["Jan", "Emma", "Sophie", "Tom"],
    "intel": ["Lisa", "Daan", "Eva"],
    "leiding": ["Milan", "Laura", "Rob"],
    "tactiek": ["Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars"]
}

# =========================================================================
#                   2. DATA MANAGEMENT
# =========================================================================
def get_default_data():
    return {"rooster_data": {}, "rooster_vastgesteld": {}, "wijzigingsverzoeken": {}, "user_patterns": {}, "bereikbaarheden": {}}

def load_data():
    if not DATA_FILE.exists():
        save_data(get_default_data()); return get_default_data()
    try:
        with open(DATA_FILE, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        st.error("Corrupt databestand. Backup gemaakt, nieuw bestand gestart.")
        DATA_FILE.rename(f"{DATA_FILE}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        save_data(get_default_data()); return get_default_data()

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    st.toast("Wijzigingen opgeslagen!", icon="💾")

# =========================================================================
#                   3. STATE & LOGICA
# =========================================================================
def init_state():
    if 'data_loaded' not in st.session_state:
        data = load_data()
        st.session_state.update(data)
        st.session_state.data_loaded = True
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.session_state.pending_change = None
        st.session_state.calendar_start_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # ✅ Nieuw: initializeer bereikbaarheden
        if "bereikbaarheden" not in st.session_state:
            st.session_state["bereikbaarheden"] = {}

def get_current_data_payload():
    return {
        "rooster_data": st.session_state.rooster_data,
        "rooster_vastgesteld": st.session_state.rooster_vastgesteld,
        "wijzigingsverzoeken": st.session_state.wijzigingsverzoeken,
        "user_patterns": st.session_state.user_patterns,
        "bereikbaarheden": st.session_state.bereikbaarheden
    }

def build_events_for_timeline():
    events = []
    for datum_key, dag_info in st.session_state.rooster_data.items():
        for medewerker, werkplek in dag_info.items():
            if medewerker in MEDEWERKERS:
                # Kleur bepalen
                if werkplek == "Kantoor":
                    kleur = "#28A745"
                elif werkplek == "Vakantie/Verlof":
                    kleur = "#FFC107"
                elif werkplek == "Niet ingepland":
                    kleur = "#495057"
                else:
                    kleur = "#007BFF"

                info = WERKPLEK_MAP.get(werkplek, WERKPLEK_MAP[DEFAULT_WERKPLEK])
                events.append({
                    "title": f"{info['emoji']} {info['afkorting']}",
                    "start": datum_key,
                    "resourceId": medewerker,
                    "allDay": True,
                    "backgroundColor": kleur,
                    "textColor": "#FFFFFF"
                })
    for maand, verzoeken in st.session_state.wijzigingsverzoeken.items():
        for verzoek in verzoeken:
            info = WERKPLEK_MAP[verzoek['werkplek']]
            events.append({
                "title": f"❓➡️ {info['emoji']}",
                "start": verzoek['datum'],
                "resourceId": verzoek['medewerker'],
                "allDay": True,
                "backgroundColor": "#FFC107",
                "textColor": "#000000"
            })
    return events


def build_events_for_grid():
    events = []
    for datum_key, dag_info in st.session_state.rooster_data.items():
        for medewerker, werkplek in dag_info.items():
            if medewerker in MEDEWERKERS:
                # Kleur bepalen
                if werkplek == "Kantoor":
                    kleur = "#28A745"
                elif werkplek == "Vakantie/Verlof":
                    kleur = "#FFC107"
                elif werkplek == "Niet ingepland":
                    kleur = "#495057"
                else:
                    kleur = "#007BFF"

                info = WERKPLEK_MAP.get(werkplek, WERKPLEK_MAP[DEFAULT_WERKPLEK])
                events.append({
                    "title": f"{info['emoji']} {medewerker}",
                    "start": datum_key,
                    "allDay": True,
                    "backgroundColor": kleur,
                    "textColor": "#FFFFFF"
                })
    for maand, verzoeken in st.session_state.wijzigingsverzoeken.items():
        for verzoek in verzoeken:
            info = WERKPLEK_MAP[verzoek['werkplek']]
            events.append({
                "title": f"❓ {verzoek['medewerker']}",
                "start": verzoek['datum'],
                "allDay": True,
                "backgroundColor": "#FFC107",
                "textColor": "#000000"
            })
    return events

# =========================================================================
#                   4. UI COMPONENTEN
# =========================================================================
def render_login():
    st.header("Login")
    st.info("Selecteer je naam om door te gaan.")
    display_namen = [f"{m} (Beheer)" if m in TEAMLEIDERS else m for m in MEDEWERKERS]
    user_display = st.selectbox("Selecteer gebruiker", display_namen, index=None, placeholder="Kies je naam...")
    if st.button("Login", disabled=not user_display, use_container_width=True):
        user_clean = user_display.split(" ")[0]
        st.session_state.logged_in_user = user_clean
        st.session_state.user_role = ROLES["TEAMLEIDER"] if user_clean in TEAMLEIDERS else ROLES["MEDEWERKER"]
        st.rerun()

def render_individual_edit():
    with st.expander("✍️ **Individuele Dag Aanpassen**"):
        invoer_cols = st.columns(3)
        gekozen_datum = invoer_cols[0].date_input("Datum", datetime.datetime.strptime(st.session_state.calendar_start_date, "%Y-%m-%d"), key="invoer_dat")
        gekozen_werkplek = invoer_cols[1].selectbox("Nieuwe Werkplek", WERKPLEK_NAMEN, key="invoer_wp", index=1)
        
        # Extra invoer voor bereikbaarheid
        medewerker = st.session_state.logged_in_user
        disciplines = {
            "digi": ["Jan", "Emma", "Sophie", "Tom"],
            "intel": ["Lisa", "Daan", "Eva"],
            "leiding": ["Milan", "Laura", "Rob"],
            "tactiek": ["Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars"]
        }
        discipline_van_medewerker = None
        for disc, names in disciplines.items():
            if medewerker in names:
                discipline_van_medewerker = disc
                break

        bereikbaar = False
        if discipline_van_medewerker:
            bereikbaar = st.checkbox("Ik ben deze dag bereikbaar", key="bereikbaar_checkbox")

        if invoer_cols[2].button("💾 Wijziging Doorvoeren", use_container_width=True):
            datum_key = gekozen_datum.strftime("%Y-%m-%d")
            maand_key = gekozen_datum.strftime("%Y-%m")
            is_vastgesteld = st.session_state.rooster_vastgesteld.get(maand_key, False)
            st.session_state.calendar_start_date = datum_key
            st.session_state.pending_change = None 

            if not is_vastgesteld:
                # Werkplek aanpassen
                rooster_dag = st.session_state.rooster_data.setdefault(datum_key, {})
                if gekozen_werkplek == DEFAULT_WERKPLEK:
                    rooster_dag.pop(medewerker, None)
                else:
                    rooster_dag[medewerker] = gekozen_werkplek

                # Bereikbaarheid opslaan
                bereikbaarheid_dag = st.session_state.get("bereikbaarheden", {}).setdefault(datum_key, {})
                if discipline_van_medewerker:
                    if bereikbaar:
                        bereikbaarheid_dag[discipline_van_medewerker] = medewerker
                    else:
                        bereikbaarheid_dag.pop(discipline_van_medewerker, None)

                # Update session_state
                st.session_state["bereikbaarheden"][datum_key] = bereikbaarheid_dag

                save_data(get_current_data_payload())
                st.success("Rooster en bereikbaarheid bijgewerkt!")
                st.rerun()
            else:
                st.session_state.pending_change = {
                    "medewerker": medewerker,
                    "datum": datum_key,
                    "maand": maand_key,
                    "werkplek": gekozen_werkplek
                }
                st.rerun()

        if st.session_state.pending_change:
            pc = st.session_state.pending_change
            st.warning(f"**Let op:** Het rooster voor {pc['maand']} is vastgesteld. Je staat op het punt een wijzigingsverzoek in te dienen.")
            st.write(f"**Verzoek:** `{pc['medewerker']}` naar `{pc['werkplek']}` op `{pc['datum']}`")
            if st.button("✅ Verzoek Indienen", type="primary"):
                verzoeken = st.session_state.wijzigingsverzoeken.setdefault(pc['maand'], [])
                pc['id'] = str(uuid.uuid4())
                verzoeken.append(pc)
                save_data(get_current_data_payload())
                st.success("Verzoek succesvol ingediend.")
                st.session_state.pending_change = None 
                st.rerun()

def render_pattern_manager():
    with st.expander("⚙️ **Werkpatronen Instellen en Toepassen**"):
        is_teamleider = st.session_state.user_role == ROLES["TEAMLEIDER"]
        if is_teamleider:
            patroon_medewerker = st.selectbox("Selecteer medewerker voor patroonbeheer:", MEDEWERKERS, index=MEDEWERKERS.index(st.session_state.logged_in_user))
        else:
            patroon_medewerker = st.session_state.logged_in_user
        st.write(f"**Huidig patroon voor {patroon_medewerker}:**")
        huidig_patroon = st.session_state.user_patterns.get(patroon_medewerker, {})
        cols = st.columns(7)
        nieuw_patroon = {}
        for i, dag in enumerate(DAGEN_VD_WEEK):
            with cols[i]:
                default = huidig_patroon.get(str(i), DEFAULT_WERKPLEK)
                index = WERKPLEK_NAMEN.index(default) if default in WERKPLEK_NAMEN else 0
                nieuw_patroon[i] = st.selectbox(dag, WERKPLEK_NAMEN, index=index, key=f"pattern_{patroon_medewerker}_{i}")

        if st.button(f"Sla patroon op voor {patroon_medewerker}"):
            st.session_state.user_patterns[patroon_medewerker] = {str(k): v for k, v in nieuw_patroon.items()}
            save_data(get_current_data_payload())
            st.success(f"Patroon voor {patroon_medewerker} opgeslagen!")
            st.rerun()

        st.divider()
        st.write(f"**Pas patroon toe voor {patroon_medewerker}:**")
        apply_cols = st.columns(3)
        sel_maand = apply_cols[0].selectbox("Maand", range(1, 13), index=datetime.date.today().month - 1, key="apply_month")
        sel_jaar = apply_cols[1].number_input("Jaar", value=datetime.date.today().year, key="apply_year")
        
        if apply_cols[2].button("Vul rooster in"):
            maand_key_check = f"{sel_jaar}-{sel_maand:02d}"
            if st.session_state.rooster_vastgesteld.get(maand_key_check, False):
                st.error(f"Het rooster voor {maand_key_check} is vastgesteld. Gebruik 'Individuele Dag Aanpassen' om een verzoek in te dienen.")
            else:
                patroon = st.session_state.user_patterns.get(patroon_medewerker)
                if not patroon:
                    st.error("Geen patroon gevonden. Sla eerst een patroon op.")
                else:
                    _, num_days = py_cal.monthrange(sel_jaar, sel_maand)
                    for dag_nummer in range(1, num_days + 1):
                        dt = datetime.date(sel_jaar, sel_maand, dag_nummer)
                        index = str(dt.weekday())
                        wp = patroon.get(index, DEFAULT_WERKPLEK)
                        key = dt.strftime("%Y-%m-%d")
                        dag_data = st.session_state.rooster_data.setdefault(key, {})
                        if wp == DEFAULT_WERKPLEK:
                            dag_data.pop(patroon_medewerker, None)
                        else:
                            dag_data[patroon_medewerker] = wp
                    st.session_state.calendar_start_date = f"{sel_jaar}-{sel_maand:02d}-01"
                    save_data(get_current_data_payload())
                    st.success(f"Rooster gevuld voor {py_cal.month_name[sel_maand]} {sel_jaar}.")
                    st.rerun()

def render_admin_panel():
    with st.expander("👑 **Beheer (voor Teamleiders)**", expanded=False):
        st.subheader("Rooster Status Beheren")
        admin_cols = st.columns(2)
        sel_maand_admin = admin_cols[0].selectbox("Maand", range(1, 13), index=datetime.date.today().month - 1, key="admin_maand")
        sel_jaar_admin = admin_cols[1].number_input("Jaar", value=datetime.date.today().year, key="admin_jaar")
        
        beheer_maand_key = f"{sel_jaar_admin}-{sel_maand_admin:02d}"
        is_maand_vastgesteld = st.session_state.rooster_vastgesteld.get(beheer_maand_key, False)

        if is_maand_vastgesteld:
            st.success(f"✅ Rooster voor {beheer_maand_key} is VASTGESTELD.")
            if st.button(f"Rooster voor {beheer_maand_key} VRIJGEVEN"):
                st.session_state.rooster_vastgesteld[beheer_maand_key] = False
                save_data(get_current_data_payload()); st.rerun()
        else:
            st.warning(f"⚠️ Rooster voor {beheer_maand_key} is CONCEPT.")
            if st.button(f"Rooster voor {beheer_maand_key} VASTSTELLEN"):
                st.session_state.rooster_vastgesteld[beheer_maand_key] = True
                save_data(get_current_data_payload()); st.rerun()

        st.divider()
        st.subheader("Inkomende Wijzigingsverzoeken")
        alle_verzoeken = st.session_state.wijzigingsverzoeken
        if not any(alle_verzoeken.values()):
            st.info("Geen openstaande verzoeken.")
        else:
            for maand_key, verzoeken in alle_verzoeken.items():
                if verzoeken:
                    st.write(f"**Verzoeken voor {maand_key}**")
                    for verzoek in verzoeken:
                        with st.container(border=True):
                            emoji = WERKPLEK_MAP[verzoek['werkplek']]['emoji']
                            st.write(f"**{verzoek['medewerker']}** | Datum: **{verzoek['datum']}** | Nieuw: **{emoji} {verzoek['werkplek']}**")
                            col1, col2, _ = st.columns([1, 1, 4])
                            if col1.button("👍 Goedkeuren", key=f"goed_{verzoek['id']}"):
                                st.session_state.rooster_data.setdefault(verzoek['datum'], {})[verzoek['medewerker']] = verzoek['werkplek']
                                st.session_state.wijzigingsverzoeken[maand_key] = [v for v in verzoeken if v['id'] != verzoek['id']]
                                save_data(get_current_data_payload()); st.rerun()
                            if col2.button("👎 Afwijzen", key=f"af_{verzoek['id']}"):
                                st.session_state.wijzigingsverzoeken[maand_key] = [v for v in verzoeken if v['id'] != verzoek['id']]
                                save_data(get_current_data_payload()); st.rerun()


# =========================================================================
#                   5. HOOFDPAGINA
# =========================================================================
init_state()

if not st.session_state.get("logged_in_user"):
    render_login()
else:
    col1, col2 = st.columns([0.8, 0.2])
    with col1: st.subheader(f"Welkom, {st.session_state.logged_in_user} ({st.session_state.user_role})")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in_user = None; st.session_state.user_role = None; st.rerun()

    render_individual_edit()
    render_pattern_manager()
    if st.session_state.user_role == ROLES["TEAMLEIDER"]:
        render_admin_panel()

    st.divider(); st.header("📅 Kalenderoverzicht")
    view_choice = st.radio("Kies een weergave:", ["Timeline", "Maandoverzicht"], horizontal=True, label_visibility="collapsed")
    calendar_options = {"headerToolbar": {"left": "prev,next today", "center": "title", "right": ""}, "locale": "nl", "height": 800, "initialDate": st.session_state.calendar_start_date}

    if view_choice == "Timeline":
        events = build_events_for_timeline()
        calendar_options.update({"initialView": "resourceTimelineMonth", "resources": [{"id": med, "title": med} for med in MEDEWERKERS], "resourceAreaHeaderContent": "Medewerkers"})
        kalender_key = "finale_kalender_timeline"
    else:
        events = build_events_for_grid()
        calendar_options.update({"initialView": "dayGridMonth", "eventDisplay": 'block'})
        kalender_key = "finale_kalender_grid"

    calendar(events=events, options=calendar_options, key=kalender_key)

    if st.button("🔄 Ververs roosterweergave", use_container_width=True):
        st.rerun()
