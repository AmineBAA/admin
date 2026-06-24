import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Plateforme Sécurisée", page_icon="🔒", layout="centered")

# --- CONFIGURATION DU COMPTE ADMIN ---
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- FONCTIONS SQLITE ---
def ajouter_utilisateur(email, password):
    try:
        conn = sqlite3.connect("utilisateurs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verifier_utilisateur(email, password):
    # Vérification d'abord si c'est l'admin
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return "admin"
    
    # Sinon vérification dans la base des utilisateurs
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user is not None:
        return "user"
    return None

def recuperer_tous_les_inscrits():
    conn = sqlite3.connect("utilisateurs.db")
    df = pd.read_sql_query("SELECT id, email FROM users", conn)
    conn.close()
    return df

# --- VARIABLES DE SESSION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "role" not in st.session_state:
    st.session_state.role = None

def logout():
    st.session_state.connected = False
    st.session_state.current_user = None
    st.session_state.role = None
    st.rerun()

# --- ZONE CONNECTÉE ---
if st.session_state.connected:
    
    # --- CAS 1 : VUE ADMINISTRATEUR ---
    if st.session_state.role == "admin":
        with st.sidebar:
            st.subheader("🛠️ Panneau Admin")
            st.write(f"Connecté : **{st.session_state.current_user}**")
            
            st.divider()
            # Récupération et téléchargement de la liste centralisée
            df_inscrits = recuperer_tous_les_inscrits()
            csv = df_inscrits.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter la liste (CSV)",
                data=csv,
                file_name="liste_centralisee_clients.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.divider()
            if st.button("Se déconnecter", use_container_width=True):
                logout()
        
        st.title("Tableau de Bord Administrateur")
        st.subheader("Gestion centralisée des inscriptions")
        st.info("Ce panneau et la barre latérale ne sont visibles que par vous.")
        
        # Affichage de la liste cumulée directement à l'écran pour l'admin
        st.dataframe(df_inscrits, use_container_width=True)

    # --- CAS 2 : VUE UTILISATEUR STANDARD (PAGE VIDE) ---
    else:
        # On peut laisser un bouton de déconnexion discret en haut ou dans le sidebar vide
        with st.sidebar:
            st.write(f"👤 Compte : {st.session_state.current_user}")
            if st.button("Se déconnecter", use_container_width=True):
                logout()
        
        # La plateforme principale pour l'utilisateur (complètement vide/neutre)
        st.title("Application")
        # st.write("Espace utilisateur vide...") 

# --- ZONE D'AUTHENTIFICATION ---
else:
    st.title("🔐 Accès Plateforme")
    tab_login, tab_register = st.tabs(["Se connecter", "S'inscrire"])
    
    with tab_login:
        st.subheader("Connexion")
        login_email = st.text_input("Adresse Email", key="login_email")
        login_password = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Connexion", type="primary", use_container_width=True):
            role_detecte = verifier_utilisateur(login_email, login_password)
            if role_detecte:
                st.session_state.connected = True
                st.session_state.current_user = login_email
                st.session_state.role = role_detecte
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
                
    with tab_register:
        st.subheader("Créer un compte")
        reg_email = st.text_input("Choisir une adresse Email", key="reg_email")
        reg_password = st.text_input("Choisir un mot de passe", type="password", key="reg_password")
        
        if st.button("S'inscrire", use_container_width=True):
            if reg_email == "" or reg_password == "":
                st.warning("Veuillez remplir tous les champs.")
            elif reg_email == ADMIN_EMAIL:
                st.error("Cet identifiant est réservé.")
            else:
                succes = ajouter_utilisateur(reg_email, reg_password)
                if succes:
                    st.success("Inscription validée ! Vous pouvez maintenant vous connecter.")
                else:
                    st.error("Cet email est déjà utilisé.")
