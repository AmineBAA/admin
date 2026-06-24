import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Saham Bank - Néo Points", page_icon="🧡", layout="wide", initial_sidebar_state="collapsed")

# --- VARIABLES DE SESSION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # 'login' ou 'register'

# --- CONFIGURATION ADMIN ---
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# --- STYLE CSS INJECTÉ (Pour correspondre aux Mockups) ---
st.markdown("""
<style>
    /* Global Background Color based on Page 1 & 2 */
    .stApp {
        background-color: #162E28;
        color: #FFFFFF;
    }
    
    /* Input field styling */
    .stTextInput div div input {
        background-color: #1C3A32 !important;
        color: #FFFFFF !important;
        border: 1px solid #2D5248 !important;
        border-radius: 8px !important;
        height: 45px;
    }
    
    /* Primary Buttons (Orange Saham) */
    .stButton>button[kind="primary"] {
        background-color: #E6673D !important;
        border-color: #E6673D !important;
        color: white !important;
        border-radius: 10px !important;
        height: 50px;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
    }
    
    /* Secondary Action Links */
    .link-style {
        color: #E6673D;
        text-decoration: none;
        font-weight: bold;
        cursor: pointer;
    }
    
    /* Card Styles for Welcome Page (Page 3.png) */
    .welcome-bg {
        background-color: #F4F6F6 !important;
        padding: 30px;
        border-radius: 20px;
    }
    .main-card {
        background: linear-gradient(135deg, #162E28 0%, #1C3A32 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    .sub-card {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        color: #162E28;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid transparent;
    }
    .sub-card:hover {
        border-left: 5px solid #E6673D;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES SQLite ---
def init_db():
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, prenom TEXT, nom TEXT)")
    conn.commit()
    conn.close()

init_db()

def ajouter_utilisateur(email, password, prenom, nom):
    try:
        conn = sqlite3.connect("utilisateurs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password, prenom, nom) VALUES (?, ?, ?, ?)", (email, password, prenom, nom))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verifier_utilisateur(email, password):
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return "admin"
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT prenom FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return ("user", user[0]) if user else None

def recuperer_tous_les_inscrits():
    conn = sqlite3.connect("utilisateurs.db")
    df = pd.read_sql_query("SELECT id, prenom, nom, email FROM users", conn)
    conn.close()
    return df

# --- ZONE CONNECTÉE (Page 3.png) ---
if st.session_state.connected:
    
    # --- VUE ADMIN ---
    if st.session_state.role == "admin":
        st.title("🛠️ Administration Centralisée")
        df_inscrits = recuperer_tous_les_inscrits()
        st.dataframe(df_inscrits, use_container_width=True)
        csv = df_inscrits.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter la liste des clients (CSV)", data=csv, file_name="clients_centralises.csv", mime="text/csv")
        if st.button("Se déconnecter"):
            st.session_state.connected = False
            st.rerun()

    # --- VUE CLIENT (Page 3.png) ---
    else:
        # Forcer un fond clair uniquement sur l'espace client pour matcher le mockup Page 3
        st.markdown("<style>.stApp { background-color: #F8F9FA !important; color: #333333 !important; }</style>", unsafe_allow_html=True)
        
        # En-tête Dynamique
        st.markdown(f"""
            <h1 style='color: #162E28; font-family: serif; margin-bottom:0;'>Bonjour {st.session_state.current_user}</h1>
            <p style='color: #666666; margin-top:0; margin-bottom:30px;'>Ravi de vous revoir</p>
        """, unsafe_allow_html=True)
        
        # Layout principal centré comme sur l'image
        col_center, _ = st.columns([2, 1])
        
        with col_center:
            # Grande Carte Verte "SAHAM LOYALTY PROGRAM"
            st.markdown("""
                <div class="main-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; opacity: 0.8; font-size: 13px; font-weight: bold; letter-spacing: 1px;">
                        <span>SAHAM LOYALTY PROGRAM</span>
                        <span style="font-size: 20px;">☆</span>
                    </div>
                    <div style="margin-top: 30px;">
                        <span style="font-size: 12px; opacity: 0.7; font-weight: bold;">POINTS DISPONIBLES</span>
                        <div style="font-size: 64px; font-weight: bold; font-family: serif; line-height: 1;">
                            125 <span style="font-size: 24px; color: #E6673D; font-family: sans-serif;">pts</span>
                        </div>
                    </div>
                    <div style="margin-top: 35px; border-top: 1px solid rgba(25px,255,255,0.1); padding-top: 15px;">
                        <span style="font-size: 11px; opacity: 0.6; font-weight: bold;">VALABLE JUSQU'AU</span><br>
                        <span style="font-size: 15px; font-weight: bold;">31/12/2027</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Liste des options cliquables simulées
            options = [
                ("💳", "Historique paiements"),
                ("🕒", "Historique points"),
                ("🎁", "Catalogue cadeaux")
            ]
            
            for icon, text in options:
                st.markdown(f"""
                    <div class="sub-card">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span style="background-color: #F4F6F6; padding: 10px 14px; border-radius: 10px; font-size: 18px;">{icon}</span>
                            <span style="font-weight: 500; font-size: 16px; color: #162E28;">{text}</span>
                        </div>
                        <span style="color: #666666; font-weight: bold;">→</span>
                    </div>
                """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("Quitter la session", type="secondary"):
            st.session_state.connected = False
            st.rerun()

# --- ZONE AUTHENTIFICATION (Page 1.jpg & Page 2.jpg) ---
else:
    # Division 50/50 pour le visuel à gauche et les formulaires à droite
    col_visuel, col_form = st.columns([1, 1], gap="large")
    
    # --- COLONNE GAUCHE : MOCKUP STATIQUE VISUEL ---
    with col_visuel:
        st.write("")
        st.markdown("<p style='font-weight: bold; letter-spacing: 1px; opacity: 0.8;'>🦅 SAHAM BANK</p>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        st.markdown("<p style='color: #E6673D; font-weight: bold; font-size: 14px; letter-spacing: 1px;'>— SAHAM LOYALTY PROGRAM</p>", unsafe_allow_html=True)
        
        st.markdown("""
            <h1 style='font-family: serif; font-size: 52px; font-style: italic; line-height: 1.1; margin-bottom: 20px;'>
                Accélérateur de <br>vos ambitions.
            </h1>
            <p style='opacity: 0.7; font-size: 16px; max-width: 400px;'>
                Connectez-vous pour suivre les récompenses que vous avez gagnées.
            </p>
        """, unsafe_allow_html=True)
        
        st.write("")
        # Petit encadré des points cumulés globaux du mockup
        st.markdown("""
            <div style="background-color: rgba(28, 58, 50, 0.5); border: 1px solid #2D5248; border-radius: 15px; padding: 15px 20px; display: flex; align-items: center; gap: 15px; max-width: 300px;">
                <span style="background-color: #E6673D; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%;">★</span>
                <div>
                    <div style="font-weight: bold; font-size: 16px;">12 480 pts</div>
                    <div style="font-size: 12px; opacity: 0.6;">Solde Récompenses Saham</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- COLONNE DROITE : FORMULAIRES INTERACTIFS ---
    with col_form:
        st.markdown("<p style='text-align: right; opacity: 0.5; font-size: 12px;'>Sécurisé 256 bits</p>", unsafe_allow_html=True)
        
        # --- MODE : CONNEXION (Page 1.jpg) ---
        if st.session_state.auth_mode == "login":
            st.markdown("<h2 style='font-family: serif; font-size: 40px; margin-bottom:0;'>Néo Points</h2>", unsafe_allow_html=True)
            
            # Switch vers inscription
            if st.button("Nouveau chez Saham Loyalty Program ? Ouvrir un compte", key="go_reg", type="secondary"):
                st.session_state.auth_mode = "register"
                st.rerun()
                
            login_email = st.text_input("E-mail ou identifiant client", placeholder="vous@exemple.com")
            login_password = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.checkbox("Rester connecté", value=True)
            
            if st.button("Se connecter", type="primary", use_container_width=True):
                res = verifier_utilisateur(login_email, login_password)
                if res == "admin":
                    st.session_state.connected = True
                    st.session_state.role = "admin"
                    st.session_state.current_user = "Admin"
                    st.rerun()
                elif res and res[0] == "user":
                    st.session_state.connected = True
                    st.session_state.role = "user"
                    st.session_state.current_user = res[1] # On prend le Prénom enregistré
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

        # --- MODE : INSCRIPTION (Page 2.jpg) ---
        else:
            st.markdown("<h2 style='font-family: serif; font-size: 40px; margin-bottom:0;'>Néo Points</h2>", unsafe_allow_html=True)
            
            # Switch vers connexion
            if st.button("Déjà inscrit au programme ? Se connecter", key="go_log", type="secondary"):
                st.session_state.auth_mode = "login"
                st.rerun()
                
            col_p, col_n = st.columns(2)
            with col_p:
                prenom = st.text_input("Prénom", placeholder="Ex: Karim")
            with col_n:
                nom = st.text_input("Nom", placeholder="Ex: Alami")
                
            reg_email = st.text_input("E-mail", placeholder="vous@exemple.com")
            reg_password = st.text_input("Mot de passe", type="password", placeholder="••••••••••••")
            
            st.markdown("<p style='font-size: 12px; opacity:0.6;'>En créant un compte, vous acceptez nos Conditions d'utilisation.</p>", unsafe_allow_html=True)
            
            if st.button("Créer mon compte Néo Points", type="primary", use_container_width=True):
                if reg_email and reg_password and prenom:
                    if ajouter_utilisateur(reg_email, reg_password, prenom, nom):
                        st.success("Compte créé ! Connectez-vous.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error("Cet e-mail existe déjà.")
                else:
                    st.warning("Veuillez remplir les champs obligatoires (Prénom, Email, Passe).")
