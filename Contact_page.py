import streamlit as st

st.set_page_config(page_title="IBTIHAJ", page_icon="🌍", layout="wide")
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText
from fpdf import FPDF
import pyautogui

def show_Contact_page():
    st.title("Contact")

    # Informations sur les propriétaires
    proprietaire1 = {
        'nom': 'MASKINI IBTISSAME',
        'photo_path': 'photo-temp.png'
    }

    proprietaire2 = {
        'nom': 'HAMZAOUI HAJAR',
        'photo_path': 'photo-temp.png'
    }


    # Titre de l'application
    st.write('Cette application a été réalisé par :')

    # Créer une disposition en colonne
    col1, col2= st.columns(2)

    # Affichage des informations du propriétaire 1 dans la première colonne
    with col1:
        st.header(proprietaire1['nom'])
        # Center the image in the column
        st.image('ibtissame.jpeg', width=200, output_format='auto')

    # Affichage des informations du propriétaire 2 dans la deuxième colonne
    with col2:
        st.header(proprietaire2['nom'])
        # Center the image in the column
        st.image('hajar.jpg', width=200, output_format='auto')

    # Section pour les commentaires des utilisateurs
    st.sidebar.header('Commentaires ')

    # Boîte de texte pour les commentaires
    commentaire_utilisateur = st.sidebar.text_area('Laissez vos commentaires ou posez vos questions ici:', height=200)

    # Bouton pour soumettre les commentaires
    if st.sidebar.button('Soumettre'):
        # Traitement des commentaires
        st.sidebar.success('Commentaire soumis avec succès!')

        # Configuration des informations du serveur SMTP
        smtp_server = '127.0.0.1'  # Remplacez par l'adresse correcte du serveur SMTP
        smtp_port = 587

        # Informations pour l'e-mail
        destinataire_email = 'ibtissamemaskini@gmail.com'
        sujet = 'Nouveau commentaire utilisateur'

        # Corps de l'e-mail
        corps_email = f"Un nouvel utilisateur a laissé un commentaire:\n\n{commentaire_utilisateur}"

        # Configuration de l'e-mail
        msg = MIMEText(corps_email)
        msg['Subject'] = sujet
        msg['From'] = 'votre_email@example.com'
        msg['To'] = destinataire_email

        # Envoi de l'e-mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login('votre_email@example.com', 'votre_mot_de_passe')  # Remplacez par votre adresse e-mail et mot de passe
            server.sendmail('votre_email@example.com', destinataire_email, msg.as_string())

    st.sidebar.header("Téléchargement pdf")

    # Fonction pour générer le rapport PDF
    def generate_pdf():
        st.sidebar.success("pdf générée avec succès !")
        screenshot = pyautogui.screenshot()
        screenshot.save('capture.png')
        
        # Création d'un PDF à partir de l'image capturée
        pdf = FPDF(orientation='L')
        pdf.add_page()
        pdf.image('capture.png', 0, 0, 297, 210)  # Ajustez la taille de l'image selon vos besoins
        pdf.output("dashboard_report.pdf")

    # Bouton pour exporter en PDF
    if st.sidebar.button("Exporter en PDF"):
        generate_pdf()