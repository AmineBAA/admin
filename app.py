import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Test Authentification", page_icon="🔒", layout="centered")

# --- INITIALISATION DES VARIABLES DE SESSION ---
# Permet de garder en mémoire si l'utilisateur est connecté et de stocker les "comptes" créés
if "connected" not in st.session_state:
    st.session_state.connected = False
if "users_db" not in st.session_state:
    # Un petit dictionnaire pour simuler une base de données (Format: {"email": "mot_de_passe"})
    st.session_state.users_db = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- FONCTIONS LOGIQUE ---
def logout():
    st.session_state.connected = False
    st.session_state.current_user = None
    st.rerun()

# --- ESPACE MEMBRE (PAGE VIDE) ---
if st.session_state.connected:
    # Barre latérale pour se déconnecter
    with st.sidebar:
        st.write(f"👤 Connecté en tant que : **{st.session_state.current_user}**")
        if st.button("Se déconnecter", use_container_width=True):
            logout()
    
    # Contenu de la plateforme vide
    st.title("Mon Application Sécurisée")
    st.subheader("Bienvenue sur votre espace !")
    
    st.info("Cette page est actuellement vide. Le concept d'authentification fonctionne ! 🚀")
    
    # Tu peux ajouter ton futur contenu ici...

# --- PAGE D'AUTHENTIFICATION (CONNEXION / INSCRIPTION) ---
else:
    st.title("🔐 Accès à la Plateforme")
    
    # Création de deux onglets : Connexion et Inscription
    tab_login, tab_register = st.tabs(["Se connecter", "S'inscrire"])
    
    # --- ONGLET : CONNEXION ---
    with tab_login:
        st.subheader("Connexion")
        login_email = st.text_input("Adresse Email", key="login_email")
        login_password = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Connexion", type="primary", use_container_width=True):
            # Vérification si l'email existe et si le mot de passe correspond
            if login_email in st.session_state.users_db and st.session_state.users_db[login_email] == login_password:
                st.session_state.connected = True
                st.session_state.current_user = login_email
                st.success("Connexion réussie ! Redirection...")
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
            elif reg_email in st.session_state.users_db:
                st.error("Cet email est déjà enregistré.")
            else:
                # Ajout de l'utilisateur dans notre "base de données" en mémoire
                st.session_state.users_db[reg_email] = reg_password
                st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")