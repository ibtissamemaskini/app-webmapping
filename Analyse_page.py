import streamlit as st

st.set_page_config(page_title="IBTIHAJ", page_icon="🌍", layout="wide")
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np
from datetime import datetime
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static 
import altair as alt
import json
import rasterio
import matplotlib.pyplot as plt
import ast
import os
from osgeo import gdal
import pyautogui
from fpdf import FPDF
from folium.raster_layers import ImageOverlay
import glob
import imageio
from branca.colormap import LinearColormap
import leafmap

def show_Analyse_page():

    # Utiliser un graphique interactif pour la navigation avec des noms personnalisés
    selected_page = st.sidebar.radio("Sélectionnez une page", ["Cartographie du jour J", "Slider", "Timelapse", "Graph + Recheche d'un point", "Filtrage", "COG"])

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

    def custom_main_page():
        st.title("Cartographie du jour J")
        # Charger les limites du Maroc depuis un fichier GeoJSON (assurez-vous de remplacer le chemin)
        maroc_limites = gpd.read_file('Région-Maroc.geojson')
        morocco_polygon = maroc_limites.geometry.unary_union

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

        # Ajouter le choix de la date dans la sidebar
        selected_date = st.sidebar.date_input("Choisissez une date", min_value=datetime(2023, 11, 1), max_value=datetime(2024, 1, 1))

        # Afficher les premières lignes du GeoDataFrame
        print(gdf.head())

        # Charger le fichier GeoJSON contenant les limites des régions en utilisant l'encodage utf-8
        with open('Région-Maroc.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Créer une carte centrée sur le Maroc
        m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

        # Calculer les rayons proportionnels en fonction de la colonne 'Propriété 1' de tes données
        # Ici, je suppose que 'dataset' est ton DataFrame contenant les données
        min_radius = 5  # Rayon minimum pour les cercles
        max_radius = 20  # Rayon maximum pour les cercles
        dataset['radius_property1'] = np.interp(dataset['Property1'], (dataset['Property1'].min(), dataset['Property1'].max()), (min_radius, max_radius))

        # Calculer les rayons proportionnels en fonction de la colonne 'Propriété 2' de tes données
        min_radius_property2 = 5  # Rayon minimum pour les cercles de Propriété 2
        max_radius_property2 = 20  # Rayon maximum pour les cercles de Propriété 2
        dataset['radius_property2'] = np.interp(dataset['Property2'], (dataset['Property2'].min(), dataset['Property2'].max()), (min_radius_property2, max_radius_property2))

        # Créer deux groupes de couches pour les propriétés 1 et 2
        layer_group_property1 = folium.FeatureGroup(name='Carte Propriété 1')
        layer_group_property2 = folium.FeatureGroup(name='Carte Propriété 2')

        # Parcourir chaque feature du GeoJSON pour obtenir les centres des régions et placer des cercles proportionnels
        for feature, radius_property1, radius_property2 in zip(geojson_data['features'], dataset['radius_property1'], dataset['radius_property2']):
            # Calculer le centre de la région en utilisant ses limites géographiques
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                coordinates = geometry['coordinates'][0]  # Prendre les coordonnées du premier anneau extérieur
                center = [sum([point[1] for point in coordinates]) / len(coordinates),
                        sum([point[0] for point in coordinates]) / len(coordinates)]

                # Ajouter un cercle proportionnel pour Propriété 1 au centre de la région dans la couche Property 1
                folium.CircleMarker(
                    location=center,
                    radius=radius_property1,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.6,
                    popup=f"Region: {feature['properties']['NOM_REG_1']}<br>Propriété 1: {radius_property1:.2f}"
                ).add_to(layer_group_property1)

                # Ajout de l'image PNG en bas à gauche
                image_path = 'Légende.png'  # Remplacez par le chemin de votre image PNG
                icon = folium.CustomIcon(
                    icon_image=image_path,
                    icon_size=(150, 150),
                    icon_anchor=(0, 0)  # Ajustez ces valeurs pour positionner l'image correctement
                )

                image_marker = folium.Marker(
                    location=[27.165,-7.778],  # Coordonnées pour placer en bas à gauche
                    icon=icon
                ).add_to(layer_group_property1)

                # Ajouter un cercle proportionnel pour Propriété 2 au centre de la région dans la couche Property 2
                folium.CircleMarker(
                    location=center,
                    radius=radius_property2,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.6,
                    popup=f"Region: {feature['properties']['NOM_REG_1']}<br>Propriété 2: {radius_property2:.2f}"
                ).add_to(layer_group_property2)

                # Ajout de l'image PNG en bas à gauche
                image_path = 'Légende Red.png'  # Remplacez par le chemin de votre image PNG
                icon = folium.CustomIcon(
                    icon_image=image_path,
                    icon_size=(150, 150),
                    icon_anchor=(0, 0)  # Ajustez ces valeurs pour positionner l'image correctement
                )

                image_marker = folium.Marker(
                    location=[27.165,-7.778],  # Coordonnées pour placer en bas à gauche
                    icon=icon
                ).add_to(layer_group_property2)

        # Ajouter les groupes de couches à la carte
        layer_group_property1.add_to(m)
        layer_group_property2.add_to(m)

        # Ajouter la boîte de contrôle des couches
        folium.LayerControl().add_to(m)

        # Afficher la carte dans Streamlit
        folium_static(m)

    def custom_sub_page_1():
        st.title("Slider")
        # Charger les limites du Maroc depuis un fichier GeoJSON (assurez-vous de remplacer le chemin)
        maroc_limites = gpd.read_file('Région-Maroc.geojson')
        morocco_polygon = maroc_limites.geometry.unary_union

        # Charger le fichier geoparquet
        gdf = gpd.read_parquet('votre_dataset.geoparquet')

        # Ajouter le choix de la date dans la sidebar
        selected_date = st.sidebar.date_input("Choisissez une date", min_value=datetime(2023, 11, 1), max_value=datetime(2024, 1, 1))

        # Sélectionner l'attribut à afficher
        attribut_selectionne = st.sidebar.selectbox("Sélectionnez l'attribut à afficher", ["attribut1", "attribut2", "attribut3"])

        # Sélectionner le jour à afficher
        jour_selectionne = st.sidebar.slider('Sélectionnez le jour à afficher', min_value=-6, max_value=0, step=1, value=0)

        # Charger le fichier GeoJSON contenant les limites des régions en utilisant l'encodage utf-8
        with open('Région-Maroc.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Créer une carte centrée sur le Maroc
        m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

        # Créer deux groupes de couches pour les propriétés 1 et 2
        layer_group_carte_ratser = folium.FeatureGroup(name='Attribut-raster')

        # Chemin vers le dossier contenant les fichiers GeoTIFF
        dossier_raster = 'raster-interp'

        # Construire le chemin du fichier GeoTIFF en fonction des sélections
        chemin_image_tiff = f'{dossier_raster}/{attribut_selectionne}-Jour{jour_selectionne}.tif'

        # Charger l'image TIFF avec rasterio
        with rasterio.open(chemin_image_tiff) as src:
            image_data = src.read(1)  # Lire la première bande du raster

        # Définir une mapping entre attributs et colormaps
        colormap_mapping = {
            "attribut1": "plasma",
            "attribut2": "YlGnBu",
            "attribut3": "hot",
        }

        # Créer une colormap différente pour chaque attribut
        def colormap(x, attribute):
            # Utiliser la colormap correspondant à l'attribut
            cmap = plt.get_cmap(colormap_mapping[attribute])

            # Normaliser la valeur de l'attribut entre 0 et 1
            normalized_value = x / np.max(image_data)

            # Obtenir la couleur de la colormap en fonction de la valeur normalisée
            rgba_color = cmap(normalized_value)

            # Convertir les valeurs de couleur de 0-1 à 0-255
            rgba_color = tuple(int(val * 255) for val in rgba_color)

            # Mettre à jour l'opacité en fonction de l'attribut
            rgba_color = rgba_color[:-1] + (x,)

            return rgba_color
        
        # Ajouter l'image GeoTIFF à la carte Folium avec la colormap en fonction de l'attribut
        folium.raster_layers.ImageOverlay(
            image=image_data,
            bounds=[[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]],
            colormap=lambda x: colormap(x, attribut_selectionne),
        ).add_to(layer_group_carte_ratser)

        # Pre-define three color palettes
        color_palettes = {
            "attribut1": ['#965707','#983868','#542933','#199364','#050383'],
            "attribut2": ['#ffffcc','#a1dab4','#41b6c4','#225ea8','#081d58'],
            "attribut3": ['#fee08b','#ef6548','#d7301f','#990000','#4d0000'],
        }

        # Define vmin and vmax for each attribute
        attribute_limits = {
            "attribut1": {"vmin":0, "vmax": 100},
            "attribut2": {"vmin": 0, "vmax": 20},
            "attribut3": {"vmin": 0, "vmax": 50},
        }

        # Get vmin and vmax based on selected attribute
        min_value = attribute_limits[attribut_selectionne]["vmin"]
        max_value = attribute_limits[attribut_selectionne]["vmax"]

        # Choose the color palette based on the selected attribute
        selected_palette = color_palettes[attribut_selectionne]

        # Create a linear color map based on the selected palette
        color_map = LinearColormap(selected_palette, vmin=min_value, vmax=max_value)

        # Customize the caption based on the selected attribute
        if attribut_selectionne == "attribut1":
            color_map.caption = f"{attribut_selectionne} (%)"
        elif attribut_selectionne == "attribut2":
            color_map.caption = f"{attribut_selectionne} (%)"
        elif attribut_selectionne == "attribut3":
            color_map.caption = f"{attribut_selectionne} (%)"

        m.add_child(color_map)

        # Add the carte-raster layer to the map
        layer_group_carte_ratser.add_to(m)

        # Ajouter la boîte de contrôle des couches
        folium.LayerControl().add_to(m)

        # Afficher la carte dans Streamlit
        folium_static(m)

    def custom_sub_page_2():
        st.title("Timelapse")

        # Chemin vers le dossier contenant les fichiers GeoTIFF
        dossier_raster = 'raster-interp'

        # Sélectionner l'attribut à afficher
        attribut_selectionne = st.sidebar.selectbox("Sélectionnez l'attribut à afficher", ["attribut1", "attribut2", "attribut3"])

        # Sélectionner le jour à afficher
        jour_selectionne = st.sidebar.slider('Sélectionnez le jour à afficher', min_value=-6, max_value=0, step=1, value=0)

        # Construire le chemin du fichier GeoTIFF en fonction des sélections
        chemin_image_tiff = f'{dossier_raster}/{attribut_selectionne}-Jour{jour_selectionne}.tif'

        # Charger l'image TIFF avec rasterio
        with rasterio.open(chemin_image_tiff) as src:
            image_data = src.read(1)  # Lire la première bande du raster

        # Définir une mapping entre attributs et colormaps
        colormap_mapping = {
            "attribut1": "plasma",
            "attribut2": "YlGnBu",
            "attribut3": "hot",
        }

        def load_images(folder):
            image_files = sorted(glob.glob(folder + '/*.tif'))
            return image_files

        def create_timelapse(image_files, fps):
            images = []
            for file in image_files:
                with rasterio.open(file) as src:
                    image_data = src.read(1)
                    # Appliquer une colormap personnalisée
                    rgba_image = plt.cm.magma((image_data / np.max(image_data)))  # Exemple avec colormap 'viridis'
                    rgba_image = (rgba_image[:, :, :3] * 255).astype('uint8')
                    images.append(rgba_image)

            # Enregistrement du timelapse en format GIF
            with imageio.get_writer('timelapse.gif', mode='I', duration=100, loop=0, fps=fps) as writer:
                for image in images:
                    writer.append_data(image)

        # Récupération des images
        folder = "raster-interp"
        image_files = load_images(folder)

        # Création du timelapse
        create_timelapse(image_files, fps=10)

        # Create a folium Map centered on Morocco
        m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

        # Replace 'your_gif_filename.gif' with the actual path to your GIF file
        gif_filename = 'timelapse.gif'

        # Add the GIF layer to the map
        gif_layer = ImageOverlay(
            gif_filename,  # Replace with the actual GIF filename
            bounds=[[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]],
            opacity=0.7,
            name='GIF Layer'
        ).add_to(m)

        # Add LayerControl to the map to allow toggling between layers
        folium.LayerControl().add_to(m)

        # Display the map in Streamlit
        folium_static(m)

    def custom_sub_page_3():
        st.title("Graph + Recheche d'un point")
        # Charger les limites du Maroc depuis un fichier GeoJSON (assurez-vous de remplacer le chemin)
        maroc_limites = gpd.read_file('Région-Maroc.geojson')
        morocco_polygon = maroc_limites.geometry.unary_union

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
        
        # Charger les limites du Maroc depuis un fichier GeoJSON (assurez-vous de remplacer le chemin)
        maroc_limites = gpd.read_file('Région-Maroc.geojson')
        morocco_polygon = maroc_limites.geometry.unary_union

        # Charger le fichier geoparquet
        gdf = gpd.read_parquet('votre_dataset.geoparquet')

        # Charger le fichier GeoJSON contenant les limites des régions en utilisant l'encodage utf-8
        with open('Région-Maroc.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Créer une carte centrée sur le Maroc
        m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

        # Créer deux groupes de couches pour les propriétés 1 et 2
        layer_group_data_graph = folium.FeatureGroup(name='data-graph')

        # Create a MarkerCluster layer for the points with popups containing charts
        marker_cluster = MarkerCluster(name='data-graph')

        for index, row in gdf.iterrows():
            # Create a marker for each point
            marker = folium.Marker(location=[row['geometry'].y, row['geometry'].x])

            # Create a chart using Altair
            data = {
                'Jour': list(range(-6, 0)),
                'Attribut1': row[[f'Attribut1Jour{i}' for i in range(-6, 0)]].values,
                'Attribut2': row[[f'Attribut2Jour{i}' for i in range(-6, 0)]].values,
                'Attribut3': row[[f'Attribut3Jour{i}' for i in range(-6, 0)]].values
            }
            df_chart = pd.DataFrame(data).melt('Jour')
            chart = alt.Chart(df_chart).mark_line().encode(
                x='Jour',
                y='value:Q',
                color='variable:N',
            ).properties(width=300, height=150)

            # Add the chart to a popup
            popup = folium.Popup(max_width=350).add_child(folium.VegaLite(chart, width=350, height=150))
            marker.add_child(popup)

            # Add the marker to the MarkerCluster layer
            marker_cluster.add_child(marker)

        # Add the MarkerCluster layer to the map
        marker_cluster.add_to(layer_group_data_graph)

        # Add the data-graph layer to the map
        layer_group_data_graph.add_to(m)

        # Ajouter une boîte de recherche par coordonnées dans Streamlit
        search_coordinates = st.sidebar.text_input("Rechercher un point par ses coordonnées (lat, lon)", "")

        if search_coordinates:
            try:
                lat, lon = map(float, search_coordinates.split(','))

                # Créer un GeoDataFrame avec le point recherché
                search_point = gpd.GeoDataFrame(geometry=[Point(lon, lat)])

                # Calculer les distances entre le point recherché et tous les points dans le GeoDataFrame initial
                distances = dataset.distance(search_point.geometry.iloc[0])

                # Trouver l'indice du point le plus proche
                nearest_index = distances.idxmin()

                # Récupérer les informations du point le plus proche
                nearest_point_info = dataset.loc[nearest_index].squeeze()

                # Ajouter le point recherché à la carte existante
                search_marker = folium.Marker(location=[lat, lon], icon=folium.Icon(color='red'))
                search_popup = folium.Popup(max_width=400)
                search_marker.add_child(search_popup)

                # Create a chart using Altair for the found point
                data = {
                    'Jour': list(range(-6, 0)),
                    'Attribut1': nearest_point_info[[f'Attribut1Jour{i}' for i in range(-6, 0)]].values,
                    'Attribut2': nearest_point_info[[f'Attribut2Jour{i}' for i in range(-6, 0)]].values,
                    'Attribut3': nearest_point_info[[f'Attribut3Jour{i}' for i in range(-6, 0)]].values
                }
                df_chart = pd.DataFrame(data).melt('Jour')
                chart = alt.Chart(df_chart).mark_line().encode(
                    x='Jour',
                    y='value:Q',
                    color='variable:N',
                ).properties(width=300, height=150)

                # Add the chart to the popup
                search_popup.add_child(folium.VegaLite(chart, width=350, height=150))

                # Afficher les informations du point dans la sidebar
                st.sidebar.write("Informations sur le point le plus proche de la Data :")
                st.sidebar.write(nearest_point_info)

                # Add the marker to the map
                m.add_child(search_marker)

            except ValueError:
                st.warning("Format incorrect. Utilisez le format 'latitude, longitude'.")

        folium_static(m)

    def custom_sub_page_4():
        st.title("Filtrage")
        # Charger le GeoDataFrame à partir du fichier GeoParquet
        gdf = gpd.read_parquet('votre_dataset.geoparquet')

        # Filtrage par condition sur les colonnes
        st.sidebar.subheader("Filtrage par condition")

        # Boîte de texte pour la condition globale
        global_condition = st.sidebar.text_input("Condition globale (utilisez les noms de colonnes et '>', '<', '==', etc.)", "")

        # Appliquer le filtre global
        if global_condition:
            try:
                # Essayer d'appliquer la condition globale
                filtered_gdf = gdf.query(global_condition)
            except pd.errors.ParserError as e:
                st.sidebar.error(f"Erreur d'analyse de la condition : {e}")
                st.stop()  # Arrêter l'exécution si la condition est invalide
        else:
            filtered_gdf = gdf

        # Ajouter la possibilité de télécharger un fichier Shapefile ou GeoJSON
        uploaded_file = st.sidebar.file_uploader("Télécharger un fichier Shapefile ou GeoJSON", type=["shp", "geojson"])

        # Charger le fichier téléchargé s'il existe
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/octet-stream":
                    # Si le fichier est un Shapefile
                    uploaded_gdf = gpd.read_file(uploaded_file)
                elif uploaded_file.type == "application/json":
                    # Si le fichier est un GeoJSON
                    with st.spinner("Chargement du fichier GeoJSON..."):
                        geojson_data = json.load(uploaded_file)
                        uploaded_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"], crs="EPSG:4326")  # Spécifiez la projection ici
            except Exception as e:
                st.sidebar.error(f"Erreur lors du chargement du fichier : {e}")
        else:
            uploaded_gdf = None
            

        # Demander à l'utilisateur de saisir des coordonnées si aucun fichier n'est téléchargé
        if uploaded_gdf is None:
            # Utiliser une clé unique pour éviter la DuplicateWidgetID error
            polygon_coords_text = st.sidebar.text_area("Coordonnées du polygone (ex: [(lon1, lat1), (lon2, lat2), ...]) - Saisie manuelle", key="manual_coords")

            # Définir le polygone à partir des coordonnées saisies
            try:
                polygon_coords = ast.literal_eval(polygon_coords_text)
                polygon = Polygon(polygon_coords)
            except (SyntaxError, TypeError) as e:
                st.sidebar.error(f"Erreur lors de l'évaluation des coordonnées du polygone : {e}")
                polygon = None
        else:
            # Utiliser le polygone du fichier téléchargé
            polygon = uploaded_gdf.unary_union

        # Filtrer les données en fonction du polygone
        if polygon:
            filtered_gdf = filtered_gdf[filtered_gdf.geometry.within(polygon)]
        else:
            filtered_gdf = filtered_gdf

        # Créer une carte centrée sur le Maroc
        m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

        # Utiliser MarkerCluster pour regrouper les points
        marker_cluster = MarkerCluster().add_to(m)

        # Ajouter chaque point au MarkerCluster
        for idx, row in filtered_gdf.iterrows():
            folium.Marker(location=[row.geometry.y, row.geometry.x],
                        popup=f"géométrie: {row.geometry}, Propriété 1: {row.Property1}, Propriété 2: {row.Property2}, Propriété 3: {row.Property3}",
                        icon=None).add_to(marker_cluster)

        # Ajouter le polygone à la carte
        if polygon:
            folium.Polygon(locations=list(polygon.exterior.coords), color='red', weight=2.5, fill=True, fill_color='red', fill_opacity=0.3).add_to(m)

        # Ajouter la boîte de contrôle des couches
        folium.LayerControl().add_to(m)

        # Afficher la carte dans Streamlit
        folium_static(m)

    def custom_sub_page_5():
        st.title("COG")

        st.write("Conversion GeoTIFF vers COG")

        # Chemin vers le répertoire contenant les fichiers GeoTIFF
        directory_path = 'raster-interp'

        # Récupérer tous les fichiers GeoTIFF dans le répertoire spécifié
        raster_files = [file for file in os.listdir(directory_path) if file.endswith('.tif')]

        # Sélectionner le fichier GeoTIFF à convertir
        selected_file = st.selectbox("Sélectionner un fichier GeoTIFF", raster_files)

        # Chemin complet du fichier sélectionné
        input_geotiff = os.path.join(directory_path, selected_file)

        # Fonction pour convertir GeoTIFF en COG
        def convert_to_cog(input_path, output_path):
            input_ds = gdal.Open(input_path)
            if input_ds:
                gdal.Translate(output_path, input_ds, format='COG', creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2'])
                st.success("Conversion réussie en COG !")
            else:
                st.error("Erreur lors de l'ouverture du fichier GeoTIFF.")

        # Bouton pour lancer la conversion
        if selected_file:
            output_cog = '{selected_file}_cog.tif'  # Chemin de sortie pour le fichier COG
            if st.button("Convertir en COG"):
                convert_to_cog(input_geotiff,output_cog)
        
    if selected_page == "Cartographie du jour J":
        custom_main_page()
    elif selected_page == "Slider":
        custom_sub_page_1()
    elif selected_page == "Timelapse":
        custom_sub_page_2()
    elif selected_page == "Graph + Recheche d'un point":
        custom_sub_page_3()
    elif selected_page == "Filtrage":
        custom_sub_page_4()
    elif selected_page == "COG":
        custom_sub_page_5()
