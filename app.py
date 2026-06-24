import streamlit as st
import sqlite3
import pandas as pd
import base64
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Saham Bank - Néo Points", page_icon="🧡", layout="wide", initial_sidebar_state="collapsed")

# --- VARIABLES DE SESSION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_prenom" not in st.session_state:
    st.session_state.user_prenom = None
if "user_points" not in st.session_state:
    st.session_state.user_points = 0
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# --- CONFIGURATION ADMIN ---
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# --- FONCTION POUR ENCODER LE LOGO LOCAL EN BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

LOGO_PATH = "logo-Saham Bank.jfif"
logo_base64 = get_image_base64(LOGO_PATH)

# --- FONCTION DE MATCHING AVEC LE FICHIER CSV ---
def recuperer_points_utilisateur(email):
    csv_path = "data_test.csv"
    if os.path.exists(csv_path):
        try:
            # Lecture du fichier CSV
            df_points = pd.read_csv(csv_path)
            
            # Nettoyage simple des colonnes pour éviter les espaces en trop
            df_points.columns = df_points.columns.str.strip()
            
            # Recherche de l'email (en minuscules pour éviter les erreurs de casse)
            row = df_points[df_points['email'].str.strip().str.lower() == email.strip().lower()]
            
            if not row.empty:
                # Retourne la valeur de la colonne 'points'
                return int(row.iloc[0]['points'])
        except Exception as e:
            print(f"Erreur lors de la lecture du CSV : {e}")
    return 0 # Retourne 0 points par défaut si l'email n'est pas trouvé ou s'il y a un problème

# --- STYLE CSS INJECTÉ ---
st.markdown("""
<style>
    .stApp {
        background-color: #162E28;
        color: #FFFFFF;
    }
    .stTextInput div div input {
        background-color: #1C3A32 !important;
        color: #FFFFFF !important;
        border: 1px solid #2D5248 !important;
        border-radius: 8px !important;
        height: 45px;
    }
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
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .logo-img {
        height: 35px;
        object-fit: contain;
    }
    .logo-text {
        font-weight: bold; 
        letter-spacing: 1px; 
        opacity: 0.9;
        font-size: 16px;
        margin: 0;
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
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN prenom TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN nom TEXT")
    except sqlite3.OperationalError:
        pass
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

# --- ZONE CONNECTÉE ---
if st.session_state.connected:
    
    if st.session_state.role == "admin":
        st.title("🛠️ Administration Centralisée")
        df_inscrits = recuperer_tous_les_inscrits()
        st.dataframe(df_inscrits, use_container_width=True)
        csv = df_inscrits.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter la liste (CSV)", data=csv, file_name="clients.csv", mime="text/csv")
        if st.button("Se déconnecter"):
            st.session_state.connected = False
            st.rerun()

    else:
        # Style clair pour l'espace membre (Mockup Page 3)
        st.markdown("<style>.stApp { background-color: #F8F9FA !important; color: #333333 !important; }</style>", unsafe_allow_html=True)
        
        # En-tête avec le prénom dynamique
        st.markdown(f"""
            <h1 style='color: #162E28; font-family: serif; margin-bottom:0;'>Bonjour {st.session_state.user_prenom}</h1>
            <p style='color: #666666; margin-top:0; margin-bottom:30px;'>Ravi de vous revoir</p>
        """, unsafe_allow_html=True)
        
        col_center, _ = st.columns([2, 1])
        with col_center:
            # Grande Carte Verte avec les POINTS DYNAMIQUES tirés du CSV
            st.markdown(f"""
                <div class="main-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; opacity: 0.8; font-size: 13px; font-weight: bold; letter-spacing: 1px;">
                        <span>SAHAM LOYALTY PROGRAM</span>
                        <span style="font-size: 20px;">☆</span>
                    </div>
                    <div style="margin-top: 30px;">
                        <span style="font-size: 12px; opacity: 0.7; font-weight: bold;">POINTS DISPONIBLES</span>
                        <div style="font-size: 64px; font-weight: bold; font-family: serif; line-height: 1;">
                            {st.session_state.user_points:,} <span style="font-size: 24px; color: #E6673D; font-family: sans-serif;">pts</span>
                        </div>
                    </div>
                    <div style="margin-top: 35px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                        <span style="font-size: 11px; opacity: 0.6; font-weight: bold;">VALABLE JUSQU'AU</span><br>
                        <span style="font-size: 15px; font-weight: bold;">31/12/2027</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
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

# --- ZONE AUTHENTIFICATION ---
else:
    col_visuel, col_form = st.columns([1, 1], gap="large")
    
    with col_visuel:
        st.write("")
        if logo_base64:
            st.markdown(f"""
                <div class="logo-container">
                    <img class="logo-img" src="data:image/jfif;base64,{logo_base64}">
                    <span class="logo-text">SAHAM BANK</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-weight: bold; letter-spacing: 1px; opacity: 0.8;'>SAHAM BANK</p>", unsafe_allow_html=True)
            
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
        st.markdown("""
            <div style="background-color: rgba(28, 58, 50, 0.5); border: 1px solid #2D5248; border-radius: 15px; padding: 15px 20px; display: flex; align-items: center; gap: 15px; max-width: 300px;">
                <span style="background-color: #E6673D; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 50%;">★</span>
                <div>
                    <div style="font-weight: bold; font-size: 16px;">12 480 pts</div>
                    <div style="font-size: 12px; opacity: 0.6;">Solde Récompenses Saham</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("<p style='text-align: right; opacity: 0.5; font-size: 12px;'>Sécurisé 256 bits</p>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "login":
            st.markdown("<h2 style='font-family: serif; font-size: 40px; margin-bottom:0;'>Néo Points</h2>", unsafe_allow_html=True)
            
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
                    st.session_state.current_user = login_email
                    st.session_state.user_prenom = res[1]
                    
                    # --- CRUCIAL : MATCHING ET REQUISITION DES POINTS DYNAMIQUES ---
                    st.session_state.user_points = recuperer_points_utilisateur(login_email)
                    
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

        else:
            st.markdown("<h2 style='font-family: serif; font-size: 40px; margin-bottom:0;'>Néo Points</h2>", unsafe_allow_html=True)
            
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
                    st.warning("Veuillez remplir les champs obligatoires.")
