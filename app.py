import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Créer une connexion à la base de données SQLite
conn = sqlite3.connect('ma_base_de_donnees.db')
c = conn.cursor()

# Créer la table si elle n'existe pas
c.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        prenom TEXT,
        mail TEXT,
        nb_connexions INTEGER DEFAULT 0,
        date_heure_connexion TEXT
    )
''')
conn.commit()

# Fonction pour insérer un utilisateur dans la base de données
def inserer_utilisateur(nom, prenom, mail):
    date_heure_connexion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO utilisateurs (nom, prenom, mail, nb_connexions, date_heure_connexion) VALUES (?, ?, ?, 0, ?)', (nom, prenom, mail, date_heure_connexion))
    conn.commit()

# Fonction pour vérifier si un utilisateur existe et incrémenter le nombre de connexions
def utilisateur_existe(nom, prenom, mail):
    c.execute('SELECT * FROM utilisateurs WHERE nom=? AND prenom=? AND mail=?', (nom, prenom, mail))
    utilisateur = c.fetchone()
    
    if utilisateur is not None:
        # Utilisateur existant, incrémenter le nombre de connexions
        count = utilisateur_count_connections(nom, prenom, mail)
        count += 1
        date_heure_connexion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('UPDATE utilisateurs SET nb_connexions=?, date_heure_connexion=? WHERE nom=? AND prenom=? AND mail=?', (count, date_heure_connexion, nom, prenom, mail))
        conn.commit()
        
        # Récupérer les informations de l'utilisateur
        id_utilisateur = utilisateur[0]
        nom_utilisateur = utilisateur[1]
        prenom_utilisateur = utilisateur[2]
        mail_utilisateur = utilisateur[3]
        
        # Afficher un message de bienvenue avec les informations de l'utilisateur
        st.success(f'Bienvenue, {prenom_utilisateur} {nom_utilisateur} ({mail_utilisateur})! Vous êtes maintenant connecté avec l\'ID {id_utilisateur}.')
        return True
    else:
        return False
    
# Fonction pour compter le nombre de connexions pour un utilisateur donné
def utilisateur_count_connections(nom, prenom, mail):
    c.execute('SELECT nb_connexions FROM utilisateurs WHERE nom=? AND prenom=? AND mail=?', (nom, prenom, mail))
    count = c.fetchone()[0]
    return count

# Fonction pour récupérer tous les utilisateurs de la base de données
def get_utilisateurs():
    st.cache_data.clear()
    c.execute('SELECT id, nom, prenom, mail, nb_connexions, date_heure_connexion FROM utilisateurs')
    utilisateurs = c.fetchall()
    return utilisateurs

# Fonction pour récupérer les données de la base de données en tant que DataFrame avec le nombre de connexions
def get_dataframe_from_db():
    st.cache_data.clear()
    utilisateurs = get_utilisateurs()
    
    # Créer le DataFrame
    df = pd.DataFrame(utilisateurs, columns=['ID', 'Nom', 'Prénom', 'Email', 'Connexions', 'Date-Heure-Connexion'])
    
    return df

# Page de connexion
st.title('Bienvenue sur notre Plateforme')

st.markdown('<style>img {width: 20000px; height: 100px;}</style>', unsafe_allow_html=True)
st.image('https://media.discordapp.net/attachments/1058516706139570216/1187710783333867632/bca78bfd9aeba00c2759d442afd9d6a9.png?ex=65b3905d&is=65a11b5d&hm=9346a69c8b6ddb2b89e13ed92597b2014137d669b0366f620e28cd8eeb9e9593&=&format=webp&quality=lossless')

# Formulaire
nom = st.text_input('Nom', key='nom')
prenom = st.text_input('Prénom', key='prenom')
mail = st.text_input('Email', key='email')

# Bouton de soumission
if st.button('Connection'):
    # Vérifier si l'utilisateur existe
    if utilisateur_existe(nom, prenom, mail):
        # Ne pas afficher le message ici, car la fonction utilisateur_existe affiche le message de bienvenue
        pass
    else:
        # Si l'utilisateur n'existe pas, l'ajouter à la base de données
        inserer_utilisateur(nom, prenom, mail)
        st.success(f'Bienvenue, {prenom} {nom}! Votre compte a été créé avec succès.')

# Bouton pour afficher les données de la base de données
with st.expander("Détails des Utilisateurs"):
    df = get_dataframe_from_db()
    st.dataframe(df)

# Formulaire pour la suppression
with st.expander("Supprimer un Utilisateur par ID"):
    id_a_supprimer = st.number_input('Entrez l\'ID de l\'utilisateur à supprimer:', min_value=1)
    if st.button('Confirmer la Suppression'):
        conn = sqlite3.connect('ma_base_de_donnees.db')
        c = conn.cursor()
        c.execute('DELETE FROM utilisateurs WHERE id=?', (id_a_supprimer,))
        conn.commit()
        st.success(f'L\'utilisateur avec l\'ID {id_a_supprimer} a été supprimé avec succès.')
