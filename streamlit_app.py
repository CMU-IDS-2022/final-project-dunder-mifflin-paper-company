import streamlit as st
from apps.medical_infrastructure_app import MedicalVis
from apps.introduction import Introduction
from apps.eda import EDA
from apps.search_trend_dashboard import plot_search_dashboard
from apps.gov_response_dashboard import plot_government_response_dashboard


# Import here and call accordingly down below
st.set_page_config(layout="wide")

def display_graph(selection):

    if selection == "Exploratory Data Analysis":
        EDA()

    elif selection == "Medical Infrastructure":
        MedicalVis()

    elif selection == "Introduction" or selection == "Select One":
        Introduction()

    elif selection == "Search Trend Dashboard":
        plot_search_dashboard()

    elif selection == "Government Response Dashboard":
        plot_government_response_dashboard()


if __name__=="__main__":

    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = "US"

    if "search_history" not in st.session_state:
        st.session_state["search_history"] = {
            "region": [],
            "searches": [],
            "shift": [],
            "correlation": [],
        }

    if "indicator_history" not in st.session_state:
        st.session_state["indicator_history"] = {
            "region": [],
            "indicators": [],
            "shift": [],
            "correlation": [],
        }

    if "selection" not in st.session_state:
        st.session_state["selection"] = None

    with st.sidebar:
        text = "<h1 align='center'>Navigation Panel</h1>"
        st.write(text, unsafe_allow_html=True)
    st.sidebar.image("images/panel_black.png", use_column_width=True, output_format="PNG")

    values = [
        "Introduction", 
        "Exploratory Data Analysis",
        "Medical Infrastructure",
        "Search Trend Dashboard",
        "Government Response Dashboard"
    ]

    selector = st.sidebar.selectbox(
        "What would you like to look at?",
        values
    )

    display_graph(selector)