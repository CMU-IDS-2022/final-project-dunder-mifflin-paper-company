import streamlit as st
from apps.medical_infrastructure_app import MedicalVis
# Import here and call accordingly down below

def display_graph(selection="Introduction"):

    if "menu" in st.session_state:
        selection = st.session_state.menu
    if selection == "Exploratory Data Analysis":
        MedicalVis()

    elif selection == "Medical Infrastructure":
        MedicalVis()

    elif selection == "Government Response":
        MedicalVis()

    elif selection == "Introduction" or selection == "Select One":
        text = "<h1 style='text-align: center; color: #7f32a8;'>COVID-19 Dashboard<h1>"
        st.write(text, unsafe_allow_html=True)


if __name__=="__main__":

    with st.sidebar:
        text = "<h1 align='center'>Navigation Panel</h1>"
        st.write(text, unsafe_allow_html=True)
    st.sidebar.image("images/panel_black.png", use_column_width=True, output_format="PNG")
    selector = st.sidebar.selectbox(
            "What would you like to look at?",
            ("Introduction", "Exploratory Data Analysis", "Government Response", "Medical Infrastructure"),
            on_change=display_graph(),
            # Initially load a page
            key="menu",
        )


