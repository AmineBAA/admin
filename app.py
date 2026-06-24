import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Test Authentification + DB", page_icon="🔐", layout="centered")

# --- INITIALISATION DE LA BASE DE DONNÉES LOCALES (SQLite) ---
def init_db():
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    # Création de la table si elle n'existe pas encore
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

# --- FONCTIONS DE GESTION DES UTILISATEURS ---
def ajouter_utilisateur(email, password):
    try:
        conn = sqlite3.connect("utilisateurs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Gère le cas où l'email existe déjà (contrainte UNIQUE)
        return False

def verifier_utilisateur(email, password):
    conn = sqlite3.connect("utilisateurs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def recuperer_tous_les_inscrits():
    conn = sqlite3.connect("utilisateurs.db")
    # Pandas permet de lire directement une requête SQL et d'en faire un DataFrame
    df = pd.read_sql_query("SELECT id, email FROM users", conn)
    conn.close()
    return df

# --- INITIALISATION DES VARIABLES DE SESSION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.connected = False
    st.session_state.current_user = None
    st.rerun()

# --- ESPACE MEMBRE (PAGE VIDE) ---
if st.session_state.connected:
    # Barre latérale
    with st.sidebar:
        st.write(f"👤 Connecté en tant que : **{st.session_state.current_user}**")
        
        st.divider()
        st.subheader("📊 Administration (Test)")
        
        # Récupération de la liste des inscrits via la DB
        df_inscrits = recuperer_tous_les_inscrits()
        
        # Bouton pour télécharger la liste en CSV
        csv = df_inscrits.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger la liste des inscrits",
            data=csv,
            file_name="liste_inscrits.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        if st.button("Se déconnecter", use_container_width=True, type="secondary"):
            logout()
    
    # Contenu de l'application
    st.title("Mon Application Sécurisée")
    st.subheader("Bienvenue sur votre espace !")
    
    st.info("Cette page est vide. Les utilisateurs sont maintenant persistés dans la base de données locale `utilisateurs.db`.")
    
    # Optionnel : Afficher la liste directement à l'écran pour ton test
    with st.expander("👀 Voir la liste des inscrits en base (visible pour le test)"):
        st.dataframe(df_inscrits, use_container_width=True)

# --- PAGE D'AUTHENTIFICATION (CONNEXION / INSCRIPTION) ---
else:
    st.title("🔐 Accès à la Plateforme")
    
    tab_login, tab_register = st.tabs(["Se connecter", "S'inscrire"])
    
    # --- ONGLET : CONNEXION ---
    with tab_login:
        st.subheader("Connexion")
        login_email = st.text_input("Adresse Email", key="login_email")
        login_password = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Connexion", type="primary", use_container_width=True):
            # Vérification dans la base SQLite
            if verifier_utilisateur(login_email, login_password):
                st.session_state.connected = True
                st.session_state.current_user = login_email
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
                
    # --- ONGLET : INSCRIPTION ---
    with tab_register:
        st.subheader("Créer un compte")
        reg_email = st.text_input("Choisir une adresse Email", key="reg_email")
        reg_password = st.text_input("Choisir un mot de passe", type="password", key="reg_password")
        
        if st.button("S'inscrire", use_container_width=True):
            if reg_email == "" or reg_password == "":
                st.warning("Veuillez remplir tous les champs.")
            else:
                # Tentative d'ajout dans la base SQLite
                succes = ajouter_utilisateur(reg_email, reg_password)
                if succes:
                    st.success("Compte créé avec succès en base de données ! Passez à l'onglet Connexion.")
                else:
                    st.error("Cet email est déjà enregistré dans la base de données.")
