import streamlit as st

# Set page configuration with custom icon
st.set_page_config(page_title="IBTIHAJ", page_icon="🌍", layout="wide")
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import folium_static
import pyautogui
from fpdf import FPDF

def show_Data_page():
    st.title("Data visualisation")

    st.sidebar.write("Téléchargement pdf")

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

    # Charger les limites du Maroc depuis un fichier GeoJSON (assurez-vous de remplacer le chemin)
    maroc_limites = gpd.read_file('Région-Maroc.geojson')
    morocco_polygon = maroc_limites.geometry.unary_union

    # Ajouter le choix de la date dans la sidebar
    selected_date = st.sidebar.date_input("Choisissez une date", min_value=datetime(2023, 11, 1), max_value=datetime(2024, 1, 1))

    # Fonction pour générer des données fictives de Propriété 1, Propriété 2, et Propriété 3 dans le Maroc avec évolution temporelle
    def generate_data(num_points):
        lons, lats, dates = [], [], []

        # Utiliser une seule date pour tous les points
        date_values = [datetime(2023, 12, 1)]

        for i in range(num_points):
            # Générer des points aléatoires et filtrer ceux à l'intérieur des frontières du Maroc
            while True:
                lon, lat = np.random.uniform(-13.0, -2.5), np.random.uniform(20, 35.5)
                point = Point(lon, lat)
                if point.within(morocco_polygon):
                    lons.append(lon)
                    lats.append(lat)
                    break

            # Utiliser les trois dates spécifiques de manière cyclique
            date_today = date_values[i % len(date_values)]
            dates.append(date_today)

        # Propriété 1 évoluant avec le temps (simulation aléatoire)
        property1_data = np.random.uniform(low=10, high=30, size=num_points)

        # Propriété 2 évoluant avec le temps (simulation inverse à la Propriété 1)
        property2_data = np.random.uniform(low=0, high=10, size=num_points) + 10 - property1_data / 3

        # Assurer que les valeurs ne deviennent pas négatives
        property2_data = np.maximum(property2_data, 0)

        # Propriété 3 avec des valeurs de texte aléatoires
        property3_data = [f'Text_{i}' for i in range(num_points)]

        # Attributs jour
        attribut_cols = {
            'Attribut1': np.random.uniform(low=0, high=100, size=num_points),
            'Attribut2': np.random.uniform(low=0, high=20, size=num_points),
            'Attribut3': np.random.uniform(low=0, high=50, size=num_points),
        }

        # Création du DataFrame
        data = {'geometry': [Point(lon, lat) for lon, lat in zip(lons, lats)], 'Date': dates, 'Property1': property1_data, 'Property2': property2_data, 'Property3': property3_data}
        for attribut_name, attribut_values in attribut_cols.items():
            for j in range(0, -7, -1):
                col_name = f"{attribut_name}Jour{j}"
                data[col_name] = np.random.choice(attribut_values, size=num_points)

        # Création du GeoDataFrame
        gdf = gpd.GeoDataFrame(data, geometry='geometry')
        
        return gdf

    # Génération du dataset fictif avec 1000 points et Propriété 1/Propriété 2/Propriété 3 évoluant avec le temps
    dataset = generate_data(1000)

    # Sauvegarde en format GeoParquet
    dataset.to_parquet('votre_dataset.geoparquet', index=False)

    # Charger le fichier geoparquet
    gdf = gpd.read_parquet('votre_dataset.geoparquet')

    # Afficher les premières lignes du GeoDataFrame
    print(gdf.head())

    # Créer une carte centrée sur le Maroc
    m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

    # Utiliser MarkerCluster pour regrouper les points
    marker_cluster = MarkerCluster().add_to(m)

    # Ajouter chaque point au MarkerCluster
    for idx, row in dataset.iterrows():
        folium.Marker(location=[row.geometry.y, row.geometry.x],
                    popup=f"géométrie: {row.geometry}, Propriété 1: {row.Property1}, Propriété 2: {row.Property2}, Propriété 3: {row.Property3}",
                    icon=None).add_to(marker_cluster)


    # Afficher la carte dans Streamlit
    folium_static(m)

