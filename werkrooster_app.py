import streamlit as st
from streamlit_calendar import calendar
import datetime
import uuid
import calendar as py_cal # Alias om conflict met de component te vermijden

# --- CONFIGURATIE ---
st.set_page_config(page_title="Rooster V12 - Patronen", layout="wide")
st.title("🗓️ Teamrooster met Patroonbeheer")

# --- CSS INJECTIE ---
st.markdown("""
    <style>
    .monospace-event .fc-event-title {font-family: 'Courier New', monospace !important; white-space: pre !important; font-size: 12px;}
    .monospace-event {margin: 1px 0 !important; padding: 0 !important;}
    .st-expander > summary > .st-emotion-cache-1f1p6pr { font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTEN ---
medewerkers = [
    "Jan", "Emma", "Sophie", "Tom", "Lisa", "Daan", "Eva", "Milan", "Laura", "Rob",
    "Julia", "Sam", "Sanne", "Thijs", "Noa", "Lars", "Puck", "Bas", "Vera", "Nina"
]
WERKPLEKKEN_CONFIG = [
    {"naam": "Niet aan het werk", "emoji": "❌", "kleur": None},
    {"naam": "Kantoor", "emoji": "🏤", "kleur": "#D4EDDA"},
    {"naam": "Aan het werk", "emoji": "💼", "kleur": None},
    {"naam": "Opleiding/cursus", "emoji": "🧑‍🏫", "kleur": None},
    {"naam": "IBT", "emoji": "💪", "kleur": None},
    {"naam": "Actiedag", "emoji": "🦺", "kleur": None},
    {"naam": "Vakantie", "emoji": "🏖️", "kleur": None},
]
werkplek_map = {item["naam"]: item for item in WERKPLEKKEN_CONFIG}
werkplek_namen = [item["naam"] for item in WERKPLEKKEN_CONFIG]
DAGEN_VD_WEEK = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]

# --- STATE MANAGEMENT INITIALISATIE ---
def init_state():
    if "rooster_data" not in st.session_state: st.session_state.rooster_data = {}
    if "rooster_vastgesteld" not in st.session_state: st.session_state.rooster_vastgesteld = {}
    if "wijzigingsverzoeken" not in st.session_state: st.session_state.wijzigingsverzoeken = {}
    if 'pending_change' not in st.session_state: st.session_state.pending_change = None
    # NIEUW: State voor gebruikerspatronen
    if 'user_patterns' not in st.session_state: st.session_state.user_patterns = {}
init_state()

# --- CENTRALE FUNCTIE OM EVENTS TE BOUWEN (ongewijzigd) ---
def build_events_list():
    # Deze functie blijft exact hetzelfde, wat de kracht van de architectuur toont.
    # ... (code is identiek aan de vorige versie, hier ingekort voor leesbaarheid)
    events = []
    max_len = max(len(m) for m in medewerkers) + 2
    for datum_key, dag_info in st.session_state.rooster_data.items():
        werkplek_groepen = {}
        for medewerker, werkplek in dag_info.items():
            werkplek_groepen.setdefault(werkplek, []).append(medewerker)
        for werkplek, medewerkers_in_groep in werkplek_groepen.items():
            werkplek_info = werkplek_map[werkplek]
            sorted_meds = sorted(medewerkers_in_groep)
            kolom_grootte = (len(sorted_meds) + 1) // 2
            kolom1, kolom2 = sorted_meds[:kolom_grootte], sorted_meds[kolom_grootte:]
            for i in range(kolom_grootte):
                naam1_raw = f"{werkplek_info['emoji']} {kolom1[i]}"
                naam2_raw = f"{werkplek_info['emoji']} {kolom2[i]}" if i < len(kolom2) else ""
                gecombineerde_titel = f"{naam1_raw.ljust(max_len, ' ')}  {naam2_raw}"
                event = {"title": gecombineerde_titel, "start": datum_key, "end": datum_key, "allDay": True, "className": "monospace-event"}
                if werkplek_info["kleur"]: event.update({"backgroundColor": werkplek_info["kleur"], "textColor": "#000000", "borderColor": werkplek_info["kleur"]})
                events.append(event)
    for maand, verzoeken in st.session_state.wijzigingsverzoeken.items():
        for verzoek in verzoeken:
            events.append({"title": f"❓ Verzoek: {verzoek['medewerker']} -> {werkplek_map[verzoek['werkplek']]['emoji']}", "start": verzoek['datum'], "end": verzoek['datum'], "allDay": True, "backgroundColor": "#FFC107", "textColor": "#000000", "borderColor": "#FFC107"})
    return events


# =========================================================================
#                   PAGINA OPBOUW
# =========================================================================

# --- NIEUW: PATROONBEHEER IN UITKLAPMENU ---
with st.expander("⚙️ **Werkpatronen Instellen en Toepassen**"):
    st.info("Stel hier je standaard weekpatroon in. Pas het daarna toe om snel de hele maand te vullen.")
    
    patroon_medewerker = st.selectbox("Selecteer medewerker voor patroonbeheer:", medewerkers)
    
    # Haal het huidige patroon op, of maak een leeg patroon
    huidig_patroon = st.session_state.user_patterns.get(patroon_medewerker, {})
    
    st.write(f"**Patroon voor {patroon_medewerker}:**")
    patroon_cols = st.columns(7)
    nieuw_patroon = {}
    for i, dag_naam in enumerate(DAGEN_VD_WEEK):
        with patroon_cols[i]:
            # Gebruik de weekdag index (0=Maandag) als key
            default_werkplek = huidig_patroon.get(i, "Niet aan het werk")
            index = werkplek_namen.index(default_werkplek) if default_werkplek in werkplek_namen else 0
            nieuw_patroon[i] = st.selectbox(dag_naam, werkplek_namen, index=index, key=f"pattern_{patroon_medewerker}_{i}")
            
    if st.button(f"Sla patroon voor {patroon_medewerker} op"):
        st.session_state.user_patterns[patroon_medewerker] = nieuw_patroon
        st.success(f"Patroon voor {patroon_medewerker} opgeslagen!")
        
    st.divider()

    st.write(f"**Pas patroon toe voor {patroon_medewerker}:**")
    # Voor nu passen we het toe op de huidige maand.
    huidige_maand_dt = datetime.date.today()
    maand_naam = huidige_maand_dt.strftime("%B %Y")
    
    if st.button(f"Vul {maand_naam} met het patroon van {patroon_medewerker}"):
        # Haal het opgeslagen patroon op
        toe_te_passen_patroon = st.session_state.user_patterns.get(patroon_medewerker)
        if not toe_te_passen_patroon:
            st.error(f"Er is geen patroon opgeslagen voor {patroon_medewerker}. Stel eerst een patroon in en sla het op.")
        else:
            # Bereken alle dagen in de maand
            _, num_days = py_cal.monthrange(huidige_maand_dt.year, huidige_maand_dt.month)
            for dag_nummer in range(1, num_days + 1):
                huidige_dag = datetime.date(huidige_maand_dt.year, huidige_maand_dt.month, dag_nummer)
                dag_vd_week_index = huidige_dag.weekday() # Maandag=0, Zondag=6
                
                # Zoek de werkplek uit het patroon
                werkplek_van_patroon = toe_te_passen_patroon.get(dag_vd_week_index, "Niet aan het werk")
                
                # Pas de wijziging toe in de rooster data
                datum_key = huidige_dag.strftime("%Y-%m-%d")
                
                if werkplek_van_patroon == "Niet aan het werk":
                    st.session_state.rooster_data.get(datum_key, {}).pop(patroon_medewerker, None)
                else:
                    st.session_state.rooster_data.setdefault(datum_key, {})[patroon_medewerker] = werkplek_van_patroon
            
            st.success(f"Rooster voor {maand_naam} succesvol gevuld met het patroon van {patroon_medewerker}!")
            st.rerun()


# --- INVOER EN BEHEER (NU INGEKLAPT) ---
with st.expander("✍️ **Individuele Dag Aanpassen**"):
    # Deze code is exact hetzelfde als in de vorige versie
    key_maand = datetime.date.today().strftime("%Y-%m")
    is_vastgesteld = st.session_state.rooster_vastgesteld.get(key_maand, False)
    if is_vastgesteld: st.warning("Let op: Het rooster voor deze maand is vastgesteld. Wijzigingen vereisen goedkeuring.")
    # ... etc. de rest van de invoerlogica ...
    invoer_cols = st.columns(3)
    gekozen_medewerker = invoer_cols[0].selectbox("Medewerker", medewerkers, key="invoer_med")
    gekozen_datum = invoer_cols[1].date_input("Datum", datetime.date.today(), key="invoer_dat")
    gekozen_werkplek = invoer_cols[2].selectbox("Werkplek", werkplek_namen, key="invoer_wp")
    if st.button("💾 Wijziging Opslaan/Aanvragen"):
        datum_key, maand_key = gekozen_datum.strftime("%Y-%m-%d"), gekozen_datum.strftime("%Y-%m")
        change_data = {"medewerker": gekozen_medewerker, "datum": datum_key, "maand": maand_key, "werkplek": gekozen_werkplek}
        if not st.session_state.rooster_vastgesteld.get(maand_key, False):
            if gekozen_werkplek == "Niet aan het werk": st.session_state.rooster_data.get(datum_key, {}).pop(gekozen_medewerker, None)
            else: st.session_state.rooster_data.setdefault(datum_key, {})[gekozen_medewerker] = gekozen_werkplek
            st.success("Rooster direct bijgewerkt!"); st.rerun()
        else: st.session_state.pending_change = change_data; st.rerun()
    if st.session_state.pending_change:
        with st.form("bevestig_wijziging_form"):
            pc = st.session_state.pending_change
            st.warning(f"**Bevestig je aanvraag:**\n- **Wie:** {pc['medewerker']}\n- **Wanneer:** {pc['datum']}\n- **Nieuwe status:** {pc['werkplek']}")
            akkoord = st.checkbox("Ik begrijp dat dit rooster is vastgesteld en dat mijn wijziging goedkeuring vereist.")
            if st.form_submit_button("✅ Verzoek Indienen"):
                if akkoord:
                    verzoeken = st.session_state.wijzigingsverzoeken.setdefault(pc['maand'], [])
                    pc['id'] = str(uuid.uuid4())
                    verzoeken.append(pc)
                    st.success("Verzoek ingediend."); st.session_state.pending_change = None; st.rerun()
                else: st.error("Vink de checkbox aan om in te dienen.")


with st.expander("👑 **Beheer (voor Teamleiders)**"):
    # Deze code is ook exact hetzelfde
    beheer_maand_key = datetime.date.today().strftime("%Y-%m")
    is_maand_vastgesteld = st.session_state.rooster_vastgesteld.get(beheer_maand_key, False)
    # ... etc. de rest van de beheerlogica ...
    st.subheader(f"Status voor {beheer_maand_key}")
    if is_maand_vastgesteld:
        st.success("✅ Dit rooster is vastgesteld.")
        if st.button(f"Rooster vrijgeven"): st.session_state.rooster_vastgesteld[beheer_maand_key] = False; st.rerun()
    else:
        st.warning("⚠️ Dit rooster is nog niet vastgesteld.")
        if st.button(f"Rooster vaststellen"): st.session_state.rooster_vastgesteld[beheer_maand_key] = True; st.rerun()
    st.divider()
    st.subheader("Inkomende Wijzigingsverzoeken")
    verzoeken = st.session_state.wijzigingsverzoeken.get(beheer_maand_key, [])
    if not verzoeken: st.info("Geen openstaande verzoeken.")
    else:
        for verzoek in verzoeken:
            with st.container(border=True):
                st.write(f"**Verzoek van {verzoek['medewerker']}** | Datum: **{verzoek['datum']}** | Nieuwe status: **{werkplek_map[verzoek['werkplek']]['emoji']} {verzoek['werkplek']}**")
                col1, col2, _ = st.columns([1,1,4])
                if col1.button("👍 Goedkeuren", key=f"goed_{verzoek['id']}"):
                    st.session_state.rooster_data.setdefault(verzoek['datum'], {})[verzoek['medewerker']] = verzoek['werkplek']
                    st.session_state.wijzigingsverzoeken[beheer_maand_key] = [v for v in verzoeken if v['id'] != verzoek['id']]
                    st.rerun()
                if col2.button("👎 Afwijzen", key=f"af_{verzoek['id']}"):
                    st.session_state.wijzigingsverzoeken[beheer_maand_key] = [v for v in verzoeken if v['id'] != verzoek['id']]
                    st.rerun()

# --- ALTIJD ZICHTBARE KALENDER ---
st.divider()
st.header("📅 Kalenderoverzicht")
events_to_display = build_events_list()
calendar(events=events_to_display, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": ""}, "initialView": "dayGridMonth", "locale": "nl", "eventDisplay": 'block', "height": 800})