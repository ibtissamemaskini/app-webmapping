import streamlit as st
import pyautogui
from fpdf import FPDF
st.set_page_config(page_title="IBTIHAJ", page_icon="🌍", layout="wide")


def show_home_page():
    st.title("")


        # Add a rotating Earth GIF, centered
    earth_gif_url = "ali-yalniz-world-is-spinning.gif"  # Replace with the actual URL of your GIF

        # Center the image
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
     st.image(earth_gif_url)


    st.title("IBTIHAJ")

# Note informative
    st.info("Bienvenue dans notre application dédiée à l'analyse de données géospatiales.Explorez les fonctionnalités disponibles pour visualiser, comprendre et interpréter les données de manière intuitive."
            "N'hésitez pas à explorer et à découvrir les possibilités offertes et si vous avez des questions, consultez la section d'aide ou contactez notre équipe de support."
)

    st.write("Téléchargement pdf")

    # Fonction pour générer le rapport PDF
    def generate_pdf():
        st.success("pdf générée avec succès !")
        screenshot = pyautogui.screenshot()
        screenshot.save('capture.png')
        
        # Création d'un PDF à partir de l'image capturée
        pdf = FPDF(orientation='L')
        pdf.add_page()
        pdf.image('capture.png', 0, 0, 297, 210)  # Ajustez la taille de l'image selon vos besoins
        pdf.output("dashboard_report.pdf")

    # Bouton pour exporter en PDF
    if st.button("Exporter en PDF"):
        generate_pdf()



