import streamlit as st # type: ignore
import requests

# Titre et description de l'application
st.title("Gestion des Utilisateurs et Prédictions")
st.write("""
Cette application permet de gérer les utilisateurs et les prédictions à travers une interface intuitive.
""")

# Section pour l'inscription d'un nouvel utilisateur
st.header("Inscription d'un nouvel utilisateur")

# Champs de saisie pour les détails de l'utilisateur
name = st.text_input("Nom")
email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")
read_rights = st.text_input("Droits de lecture")
write_rights = st.text_input("Droits d'écriture")

# Bouton pour soumettre l'inscription
if st.button("S'inscrire"):
    if name and email and password:
        # Envoyer une requête POST pour créer un nouvel utilisateur
        response = requests.post("http://app:8000/api/user/register", json={
            "name": name,
            "email": email,
            "password": password,
            "read_rights": read_rights,
            "write_rights": write_rights
        })
        # Afficher le résultat de la requête
        if response.status_code == 200:
            st.success("Utilisateur enregistré avec succès!")
        else:
            st.error(f"Erreur: {response.text}")
    else:
        st.warning("Veuillez remplir tous les champs.")

# Section pour afficher la liste des utilisateurs
st.header("Liste des utilisateurs")

# Bouton pour charger les utilisateurs
if st.button("Charger les utilisateurs"):
    token = st.text_input("Token d'authentification", type="password")
    if token:
        # Envoyer une requête GET pour obtenir la liste des utilisateurs
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://app:8000/api/admin/users", headers=headers)
        # Afficher les utilisateurs ou une erreur
        if response.status_code == 200:
            users = response.json()
            st.write(users)
        else:
            st.error(f"Erreur: {response.text}")
    else:
        st.warning("Veuillez fournir un token d'authentification.")
