# Sla dit bestand op in de 'pages' map als 5_📢_Bijzondere_Inzet.py

import streamlit as st
import datetime
from utils import initialize_session_state, update_rooster_entry, save_all_data

initialize_session_state()

st.set_page_config(page_title="Bijzondere Inzet", layout="wide")
st.title("📢 Openstaande Inzetten")

if not st.session_state.get('logged_in_user'):
    st.warning("U moet ingelogd zijn om deze pagina te bekijken.")
    st.info("Ga naar de **'Invoeren Rooster'** pagina om in te loggen.")
    st.stop()

ingelogde_gebruiker = st.session_state.logged_in_user
user_skills = st.session_state.medewerker_skills.get(ingelogde_gebruiker, {})
vandaag_str = datetime.date.today().strftime("%Y-%m-%d")

# Jouw originele, robuuste filterlogica
open_inzetten_raw = [
    inzet for inzet in st.session_state.open_diensten 
    if inzet.get('datum', '1970-01-01') >= vandaag_str
]

if not open_inzetten_raw:
    st.success("✅ Er zijn momenteel geen openstaande oproepen voor bijzondere inzet.")
    st.stop()

st.info("Hieronder zie je oproepen die nog ingevuld moeten worden. Meld je aan voor een discipline die je beheerst.")
st.divider()

# Jouw originele sortering
gefilterde_en_gesorteerde_inzetten = sorted(open_inzetten_raw, key=lambda x: x.get('datum', '1970-01-01'))

aantal_getoonde_inzetten = 0
for inzet in gefilterde_en_gesorteerde_inzetten:
    if 'maker' not in inzet or 'behoefte' not in inzet or inzet.get('status') == 'gesloten':
        continue
    
    aantal_getoonde_inzetten += 1
    datum_obj = datetime.datetime.strptime(inzet['datum'], "%Y-%m-%d").date()
    dag_naam = datum_obj.strftime("%A").capitalize()
    
    with st.container(border=True):
        st.subheader(f"{inzet['werkplek']}")
        st.caption(f"Datum: **{dag_naam} {datum_obj.strftime('%d-%m-%Y')}** | Georganiseerd door: **{inzet['maker']}**")

        st.markdown("**Voortgang & Aanmelden:**")
        
        is_al_aangemeld_voor_inzet = any(ingelogde_gebruiker in aanmeldingen for aanmeldingen in inzet['aanmeldingen'].values())
        is_al_ingepland_op_dag = ingelogde_gebruiker in st.session_state.rooster_data.get(inzet['datum'], {})

        if is_al_aangemeld_voor_inzet:
            st.success("✔️ Je bent al aangemeld voor deze inzet.")
        # --- DE AANGEPASTE LOGICA ---
        # Jouw originele, slimme check wordt behouden en uitgebreid
        elif is_al_ingepland_op_dag:
            huidige_plek = st.session_state.rooster_data[inzet['datum']][ingelogde_gebruiker]
            if inzet['werkplek'] not in huidige_plek:
                 st.warning(f"Let op: je bent al ingepland voor '{huidige_plek}'. Aanmelden zal dit overschrijven.", icon="⚠️")
        # --- EINDE AANPASSING ---

        progress_cols = st.columns(len(inzet['behoefte']))
        
        for i, (skill, benodigd) in enumerate(inzet['behoefte'].items()):
            with progress_cols[i]:
                aanmeldingen = inzet['aanmeldingen'].get(skill, [])
                aangemeld_count = len(aanmeldingen)
                
                if aangemeld_count >= benodigd:
                    st.markdown(f"**{skill}**")
                    st.progress(1.0, text=f"✅ {aangemeld_count} / {benodigd} (Vol)")
                else:
                    st.markdown(f"**{skill}**")
                    st.progress(aangemeld_count / benodigd, text=f"⏳ {aangemeld_count} / {benodigd}")

                # --- DE AANGEPASTE KNOPLOGICA ---
                # Toon alleen de aanmeldopties als je je nog niet voor deze inzet hebt aangemeld
                if not is_al_aangemeld_voor_inzet:
                    plek_vrij = aangemeld_count < benodigd
                    heeft_skill = user_skills.get(skill, False)
                    
                    # De knop wordt niet meer gedisabled door `is_al_ingepland_op_dag`
                    button_text = "Toch aanmelden" if is_al_ingepland_op_dag else f"Aanmelden {skill}"
                    
                    if st.button(button_text, key=f"meld_{inzet['id']}_{skill}", disabled=not (plek_vrij and heeft_skill), type="primary"):
                        # Actie is altijd: update de planning (overschrijft de oude)
                        inzet['aanmeldingen'][skill].append(ingelogde_gebruiker)
                        rooster_tekst = f"{inzet['werkplek']} ({skill})"
                        update_rooster_entry(datum_obj, ingelogde_gebruiker, rooster_tekst)
                        save_all_data()
                        st.success(f"Top! Je bent aangemeld voor {skill}. Je oude planning is overschreven.")
                        st.rerun()
                    
                    # Hulpteksten blijven
                    if not heeft_skill:
                        st.caption("Jij beheerst dit niet")
                    if not plek_vrij and heeft_skill:
                        st.caption("Deze rol is vol")
                # --- EINDE AANGEPASTE KNOPLOGICA ---
        
        with st.expander("Wie hebben zich al aangemeld?"):
            any_signups = any(inzet['aanmeldingen'].values())
            if not any_signups:
                st.write("Nog geen aanmeldingen.")
            else:
                for skill, aangemeld_list in inzet['aanmeldingen'].items():
                    if aangemeld_list:
                        st.markdown(f"**{skill}**: {', '.join(aangemeld_list)}")

        if ingelogde_gebruiker == inzet['maker']:
            st.divider()
            if st.button("Sluit deze oproep", key=f"sluit_{inzet['id']}", type="primary"):
                inzet['status'] = 'gesloten'
                save_all_data()
                st.rerun()

# Jouw originele, robuuste eind-check
if aantal_getoonde_inzetten == 0:
    st.success("✅ Er zijn momenteel geen openstaande oproepen voor bijzondere inzet.")
