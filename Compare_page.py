import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from streamlit_folium import folium_static as st_folium_static
import os
from branca.colormap import LinearColormap
import pyautogui
from fpdf import FPDF

st.set_page_config(page_title="IBTIHAJ", page_icon="🌍", layout="wide")

def show_Compare_page():
    st.title("Compare")

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

    st.write("SplitMap pannel")

    # Create select boxes for choosing attribute and day
    selected_attribute = st.sidebar.selectbox("Selectionner Attribut ", ["attribut1", "attribut2", "attribut3"])

    image_name_left = st.sidebar.selectbox("Select left image:", [f"{selected_attribute}J{i}.tif" for i in range(0,7)])
    image_name_right = st.sidebar.selectbox("Select right image:", [f"{selected_attribute}J{i}.tif" for i in range(0,7) if f"{selected_attribute}-Jour{i}.tif" != image_name_left])
    image_name_left=f'https://hajar-hmz.github.io/split.github.io/{image_name_left}'
    image_name_right=f'https://hajar-hmz.github.io/split.github.io/{image_name_right}'
    # Pre-define three color palettes
    color_palettes = {
        "attribut1": ['#ffffcc','#a1dab4','#41b6c4','#225ea8','#081d58'],
        "attribut2": ['#ffffcc','#a1dab4','#41b6c4','#225ea8','#081d58'],
        "attribut3": ['#ffffcc','#a1dab4','#41b6c4','#225ea8','#081d58'],
    }

    # Define vmin and vmax for each attribute
    attribute_limits = {
        "attribut1": {"vmin":0, "vmax": 100},
        "attribut2": {"vmin": 0, "vmax": 20},
        "attribut3": {"vmin": 0, "vmax": 50},
    }

    # Get vmin and vmax based on selected attribute
    min_value = attribute_limits[selected_attribute]["vmin"]
    max_value = attribute_limits[selected_attribute]["vmax"]

    # Choose the color palette based on the selected attribute
    selected_palette = color_palettes[selected_attribute]


    # Load the GeoTIFFs into Leafmap
    m = leafmap.Map()
    m.split_map(image_name_left, image_name_right)

    # Create a linear color map based on the selected palette
    color_map = LinearColormap(selected_palette, vmin=min_value, vmax=max_value)

    # Customize the caption based on the selected attribute
    if selected_attribute == "attribut1":
        color_map.caption = f"{selected_attribute} (%)"
    elif selected_attribute == "attribut2":
        color_map.caption = f"{selected_attribute} (%)"
    elif selected_attribute == "attribut3":
        color_map.caption = f"{selected_attribute} (%)"

    m.add_child(color_map)

    # Print statement for debugging
    print("Map created successfully.")

    # Display the map in Streamlit
    st_folium_static(m)