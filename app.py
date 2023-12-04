import streamlit as st
from streamlit_option_menu import option_menu
from home_page import show_home_page
from Data_page import show_Data_page
from Analyse_page import show_Analyse_page
from Contact_page import show_Contact_page
from Compare_page import show_Compare_page

# 2. horizontal menu
selected2 = option_menu(None, ["Home", "Data", "Analyse","Compare", "Contact"], 
    icons=['house', 'database', '', '', 'envelope'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "blue", "font-size": "25px"}, 
        "nav-link": {"font-size": "11px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "black"},
    }
)

# Afficher le contenu en fonction de la valeur sélectionnée dans le menu horizontal
if selected2 == "Home":
    show_home_page()
elif selected2 == "Data":
    show_Data_page()
elif selected2 == "Analyse":
    show_Analyse_page()
elif selected2 == "Compare":
    show_Compare_page()
elif selected2 == "Contact":
    show_Contact_page()
