import streamlit as st
from apps.app import MedicalVis
# Import here and call accordingly down below

def display_graph(selection="Take me Home!"):

    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == "Exploratory Data Analysis":
        MedicalVis()

    elif selection == "Medical Infrastructure":
        MedicalVis()

    elif selection == "Government Response":
        MedicalVis()


if __name__=="__main__":
    st.sidebar.image("images/panel_black.png", use_column_width=True, output_format="PNG")

    selector = st.sidebar.selectbox(
            "What Would You Like to Look at?",
            ("Exploratory Data Analysis", "Medical Infrastructure", "Government Response"),
            on_change=display_graph(),
            # Initially load the EDA page
            key="menu",
        )