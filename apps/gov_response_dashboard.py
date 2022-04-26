from apps.geocode import geocoder
import folium
import copy
import branca.colormap as cm
import json
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import leafmap.foliumap as leafmap
from vega_datasets import data
import time

from streamlit.scriptrunner.script_runner import RerunException


ROLLING_WINDOW = 7

relevant_locations = [
    "US",
    "US_AL",
    "US_AK",
    "US_AS",
    "US_AZ",
    "US_AR",
    "US_CA",
    "US_CO",
    "US_CT",
    "US_DE",
    "US_DC",
    "US_FL",
    "US_GA",
    "US_GU",
    "US_HI",
    "US_ID",
    "US_IL",
    "US_IN",
    "US_IA",
    "US_KS",
    "US_KY",
    "US_LA",
    "US_ME",
    "US_MD",
    "US_MA",
    "US_MI",
    "US_MN",
    "US_MS",
    "US_MO",
    "US_MT",
    "US_NE",
    "US_NV",
    "US_NH",
    "US_NJ",
    "US_NM",
    "US_NY",
    "US_NC",
    "US_ND",
    "US_MP",
    "US_OH",
    "US_OK",
    "US_OR",
    "US_PA",
    "US_PR",
    "US_RI",
    "US_SC",
    "US_SD",
    "US_TN",
    "US_TX",
    "US_UT",
    "US_VT",
    "US_VA",
    "US_VI",
    "US_WA",
    "US_WV",
    "US_WI",
    "US_WY",
]


LOCATION_ABBREVIATION_MAP = {
    "US": "US",
    "ALABAMA": "US_AL",
    "ALASKA": "US_AK",
    "AMERICAN SAMOA": "US_AS",
    "ARIZONA": "US_AZ",
    "ARKANSAS": "US_AR",
    "CALIFORNIA": "US_CA",
    "COLORADO": "US_CO",
    "CONNECTICUT": "US_CT",
    "DELAWARE": "US_DE",
    "DISTRICT OF COLUMBIA": "US_DC",
    "FLORIDA": "US_FL",
    "GEORGIA": "US_GA",
    "GUAM": "US_GU",
    "HAWAII": "US_HI",
    "IDAHO": "US_ID",
    "ILLINOIS": "US_IL",
    "INDIANA": "US_IN",
    "IOWA": "US_IA",
    "KANSAS": "US_KS",
    "KENTUCKY": "US_KY",
    "LOUISIANA": "US_LA",
    "MAINE": "US_ME",
    "MARYLAND": "US_MD",
    "MASSACHUSETTS": "US_MA",
    "MICHIGAN": "US_MI",
    "MINNESOTA": "US_MN",
    "MISSISSIPPI": "US_MS",
    "MISSOURI": "US_MO",
    "MONTANA": "US_MT",
    "NEBRASKA": "US_NE",
    "NEVADA": "US_NV",
    "NEW HAMPSHIRE": "US_NH",
    "NEW JERSEY": "US_NJ",
    "NEW MEXICO": "US_NM",
    "NEW YORK": "US_NY",
    "NORTH CAROLINA": "US_NC",
    "NORTH DAKOTA": "US_ND",
    "NORTHERN MARIANA IS": "US_MP",
    "OHIO": "US_OH",
    "OKLAHOMA": "US_OK",
    "OREGON": "US_OR",
    "PENNSYLVANIA": "US_PA",
    "PUERTO RICO": "US_PR",
    "RHODE ISLAND": "US_RI",
    "SOUTH CAROLINA": "US_SC",
    "SOUTH DAKOTA": "US_SD",
    "TENNESSEE": "US_TN",
    "TEXAS": "US_TX",
    "UTAH": "US_UT",
    "VERMONT": "US_VT",
    "VIRGINIA": "US_VA",
    "VIRGIN ISLANDS": "US_VI",
    "WASHINGTON": "US_WA",
    "WEST VIRGINIA": "US_WV",
    "WISCONSIN": "US_WI",
    "WYOMING": "US_WY",
}

INDICATORS_MAP = {
    "School Closing": "school_closing",
    "Workplace Closing": "workplace_closing",
    "Cancel Public Events": "cancel_public_events",
    "Restrictions On Gatherings": "restrictions_on_gatherings",
    "Public Transport Closing": "public_transport_closing",
    "Stay At Home Requirements": "stay_at_home_requirements",
    "Restrictions on Internal Movement": "restrictions_on_internal_movement",
    "Income Support": "income_support",
    "Debt Relief": "debt_relief",
    "Fiscal Measures": "fiscal_measures",
    "Public Information Campaigns": "public_information_campaigns",
    "Testing Policy": "testing_policy",
    "Contact Tracing": "contact_tracing",
    "Emergency Investment In Healthcare": "emergency_investment_in_healthcare",
    "Investment In Vaccines": "investment_in_vaccines",
    "Facial Coverings": "facial_coverings",
    "Vaccination Policy": "vaccination_policy",
    "Stringency Index": "stringency_index",
}

@st.cache
def get_geocoder():
    return geocoder("data/usa_shape/usa-states-census-2014.shp")


@st.cache
def read_files():
    government_response_df = pd.read_csv(
        "data/oxford-government-response_filtered.csv"
    )
    government_response_df["date"] = pd.to_datetime(government_response_df["date"])

    cases_df = pd.read_csv("data/epidemiology_filtered.csv")
    cases_df["date"] = pd.to_datetime(cases_df["date"])

    with open("data/us_states.json", "r") as fp:
        polygons = json.load(fp)

    return government_response_df, cases_df, polygons


def compute_correlation(
    government_response_df, cases_df, shift, location_key, indicators
):

    location_cases = cases_df[cases_df["location_key"] == location_key][
        ["date", "new_confirmed"]
    ]
    cases_values = (
        location_cases["new_confirmed"]
        .rolling(ROLLING_WINDOW)
        .mean()[ROLLING_WINDOW - 1 :]
    )
    dates = location_cases["date"][ROLLING_WINDOW - 1 :]

    location_indicator_values = government_response_df[
        government_response_df["location_key"] == location_key
    ]

    if len(indicators):
        indicator_values = location_indicator_values[indicators][
            ROLLING_WINDOW - 1 :
        ].sum(axis=1)
    else:
        indicator_values = location_indicator_values[ROLLING_WINDOW - 1 :].sum(axis=1)

    if shift == 0:
        shifted_indicator_values = indicator_values
        shifted_case_values = cases_values
    else:
        shifted_indicator_values = indicator_values[:-shift]
        shifted_case_values = cases_values[shift:]
        dates = dates[shift:]

    shifted_indicator_values /= max(shifted_indicator_values)
    # shifted_case_values /= max(shifted_case_values)

    corref = np.corrcoef(
        x=shifted_indicator_values / max(shifted_indicator_values),
        y=shifted_case_values / max(shifted_case_values),
    )

    return round(corref[0][1], 3)


def plot_map(polygons):

    usa_map = leafmap.Map(center=[37, -90], zoom=4)
    colormap = cm.LinearColormap(
        ["DarkBlue", "LightBlue", "yellow", "red"],
        vmin=-1,
        vmax=1,
    )

    colormap.caption = "Correlation"

    def get_colour(prop):
        if np.isnan(prop["properties"]["Correlation"]):
            return "gray"
        else:
            return colormap(prop["properties"]["Correlation"])

    def get_weight(prop):
        if prop["properties"]["State"] == st.session_state["selected_region"]:
            return 8
        else:
            return 1

    def get_boundary_colour(prop):
        if prop["properties"]["State"] == st.session_state["selected_region"]:
            return "white"
        else:
            return "white"

    def get_opacity(prop):
        if prop["properties"]["State"] == st.session_state["selected_region"]:
            return 1.0
        else:
            return 0.75

    geo_map = folium.features.GeoJson(
        polygons,
        style_function=lambda x: {
            "weight": get_weight(x),
            "color": get_boundary_colour(x),
            "fillColor": get_colour(x),
            "fillOpacity": get_opacity(x),
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=["State", "Correlation"],
            aliases=["State: ", "Correlation: "],
            style=(
                "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
            ),
        ),
    )
    colormap.add_to(usa_map)
    usa_map.add_child(geo_map)

    return usa_map


def plot_government_response_dashboard():

    government_response_df, cases_df, polygons = read_files()
    polygons = copy.deepcopy(polygons)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("## Effect of government response on COVID 19 morbidity")
        st.markdown("***")

        st.markdown(
            """
        The Oxford Covid-19 [Government Response Tracker](https://www.bsg.ox.ac.uk/research/research-projects/covid-19-government-response-tracker) 
        (OxCGRT) collects systematic information on policy measures that governments have taken to tackle COVID-19.
        These responses are categorised into different indicators types, which include:
        - Containment and closure policies (such as school closures and restrictions in movement)
        - Economic policies (such as income support to citizens and debit relief)
        - Health system policies (such as facial coverings)
        - Vaccine policies
        """
        )
        st.markdown(
            """
            With this dashboard, we try to gauge which government policies have been most effective in reducing the rise in COVID 19 
            cases across different states. **Intuitively, we expect a negative correlation between these two, since a stronger government response should entail lower morbidity.**
            """
        )

        st.markdown(
            """
        Each indictor is assigned an integer value, reflecting the extent of government action.
        A higher value indicates a more extensive policy (such as more stringent health system policies, 
        or higher economic relief to citizens). 
        More information on how these values
        are calculated can be found on the [OxCGRT page](https://www.bsg.ox.ac.uk/research/research-projects/covid-19-government-response-tracker).
        """
        )

        st.markdown(
            """
        We normalize these indicators to a scale of 0 to 1 for ease of visualisations.
        """
        )

    st.markdown("***")

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown(
            """
        When multiple indicators are selected, we aggregate the value by summing up each indicator's value.
        Stringency Index is calculated by aggregating all the individual indicators.
        """
        )
        indicator_strings = st.multiselect(
            # "",
            "Government Response Indicators:",
            INDICATORS_MAP.keys(),
            default=["Stringency Index"],
        )

    with col2:
        st.markdown("***")
        st.markdown(
            "Government policy decisions, even the most extensive ones, often take time in achieving their desired results. We introduce a variable `lag`, which enables a comparision between policy indicators and number of cases `lag` days in the future."
        )
        shift = st.slider("Number of days in the future (Lag)", 0, 90)

    indicators = list(
        map(lambda indicator: INDICATORS_MAP[indicator], indicator_strings)
    )

    for ind, ele in enumerate(polygons["features"]):
        location_key = "US_" + ele["id"]
        ele["properties"]["State"] = ele["properties"]["name"]
        del ele["properties"]["name"]

        correlation = compute_correlation(
            government_response_df, cases_df, shift, location_key, indicators
        )

        ele["properties"]["Correlation"] = correlation

    location = LOCATION_ABBREVIATION_MAP[st.session_state["selected_region"].upper()]
    location_cases = cases_df[cases_df["location_key"] == location][
        ["date", "new_confirmed"]
    ]
    cases_values = (
        location_cases["new_confirmed"]
        .rolling(ROLLING_WINDOW)
        .mean()[ROLLING_WINDOW - 1 :]
    )
    dates = location_cases["date"][ROLLING_WINDOW - 1 :]

    location_indicator_values = government_response_df[
        government_response_df["location_key"] == location
    ]

    if len(indicators):
        indicator_values = location_indicator_values[indicators][
            ROLLING_WINDOW - 1 :
        ].sum(axis=1)
    else:
        indicator_values = location_indicator_values[ROLLING_WINDOW - 1 :].sum(axis=1)

    if shift == 0:
        shifted_indicator_values = indicator_values
        shifted_case_values = cases_values
    else:
        shifted_indicator_values = indicator_values[:-shift]
        shifted_case_values = cases_values[shift:]
        dates = dates[shift:]

    shifted_indicator_values /= max(shifted_indicator_values)

    corref = round(
        np.corrcoef(
            x=shifted_indicator_values / max(shifted_indicator_values),
            y=shifted_case_values / max(shifted_case_values),
        )[0][1],
        3,
    )

    with col2:
        st.markdown("***")
        st.markdown(
            """
            <div style="width: 100%; text-align: center;">
                <div style="width: 50%; float: left; "> 
                    Selected Region
                    <br />
                    <span style = 'font-size: 40px;'>"""
            + st.session_state["selected_region"]
            + """</span>
                </div>
                <div style="margin-left: 50%;"> 
                    Correlation
                    <br />
                    <span style = 'font-size: 40px;'>"""
            + str(corref)
            + """</span>
                </div>
            </div>        
        """,
            unsafe_allow_html=True,
        )

    usa_map = plot_map(polygons)
    with col1:
        st.markdown(
            """
            This map shows the correlation between COVID 19 cases and governenment response indicators for the selected lag across different states.
            <br />
        """,
            unsafe_allow_html=True,
        )
        usa_map_folium = usa_map.to_streamlit(
            height=500, width=900, add_layer_control=True, bidirectional=True
        )
        st.markdown(
            """
        <div style="width: 100%; text-align: left;">
            Click on a state to examine its data.
            Click outside the United States boundary to examine aggergated data across all states.
        """,
            unsafe_allow_html=True,
        )

    try:
        click = usa_map.st_last_click(usa_map_folium)
    except:
        click = None

    if click is not None:
        region = get_geocoder().geocode(click[0], click[1])

        if region is None:
            region = "US"
        else:
            region = region["NAME"]

        if region != st.session_state["selected_region"]:
            st.session_state["selected_region"] = region
            st.experimental_rerun()

    col1, col2 = st.columns([2, 1])

    data = pd.DataFrame()
    data["shifted_case_values"] = shifted_case_values.tolist()
    data["shifted_indicator_values"] = shifted_indicator_values.tolist()
    data["x"] = dates.values

    cases_chart = (
        alt.Chart(data)
        .mark_line(opacity=1, color="#57A44C")
        .encode(
            alt.X(
                "x",
                title="Date (2021)",
            ),
            alt.Y(
                "shifted_case_values",
                title="Number of new cases",
                axis=alt.Axis(title="Number of new cases", titleColor="#57A44C"),
            ),
        )
        .interactive()
    )

    trends_chart = (
        alt.Chart(data)
        .mark_line(opacity=1, color="#5276A7")
        .encode(
            alt.X(
                "x",
                title="Date (2021)",
                # scale=alt.Scale(domain=['2021-01-01','2021-12-31'])
            ),
            alt.Y(
                "shifted_indicator_values",
                title="trend",
                axis=alt.Axis(
                    title="Government Response Indicator (normalised)", titleColor="#5276A7"
                ),
            ),
        )
        .interactive()
    )

    chart = alt.layer(cases_chart, trends_chart).resolve_scale(y="independent")
    with col2:
        st.markdown(
            "***",
        )
        text = (
            "This graph compares the number daily of COVID 19 cases and government response indiactors (normalised to a scale of 0 to 1) with the selected lag (%d days in the future) "
            % (shift)
        )
        st.markdown("<p align=center> %s </p>" % (text), unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)

    ############### HISTORICAL CHART ###############

    if (
        not len(st.session_state["indicator_history"]["region"])
        or st.session_state["indicator_history"]["region"][-1]
        != st.session_state["selected_region"]
        or st.session_state["indicator_history"]["indicators"][-1] != set(indicator_strings)
        or st.session_state["indicator_history"]["shift"][-1] != shift
        or st.session_state["indicator_history"]["correlation"][-1] != corref
    ):

        st.session_state["indicator_history"]["region"].append(
            st.session_state["selected_region"]
        )
        st.session_state["indicator_history"]["indicators"].append(set(indicator_strings))
        st.session_state["indicator_history"]["shift"].append(shift)
        st.session_state["indicator_history"]["correlation"].append(corref)

    historical_data = pd.DataFrame(st.session_state["indicator_history"])
    historical_chart = (
        alt.Chart(historical_data.reset_index(), title="Search history")
        .mark_line(point=True, color="#000000")
        .encode(
            alt.Y(
                "correlation",
                title="Correlation",
                scale=alt.Scale(domain=[-1, 1]),
                # axis=alt.Axis(tickSize=0),
            ),
            alt.X(
                "index",
                title="History",
                scale=alt.Scale(
                    domain=[-1, len(st.session_state["indicator_history"]["correlation"])],
                    type="point",
                ),
                axis=alt.Axis(tickMinStep=1),
            ),
            tooltip=[
                alt.Tooltip("region", title="Region"),
                alt.Tooltip("shift", title="Shift"),
                alt.Tooltip("indicators", title="Response Indicators"),
                alt.Tooltip("correlation", title="Correlation"),
            ],
        )
        .interactive()
    )

    with col1:
        st.markdown("***")
        st.markdown("")
        st.markdown(
            """
        <div style="width: 100%; text-align: left;">
            This graph shows the correlation between COVID 19 cases and governenment response indicators for previously explored parameters in this dashboard.
            <b>This can be used to track how changing certain parameters (for instance, lag) affects the correlation.</b>
            <br />
            <br />
        """,
            unsafe_allow_html=True,
        )

        st.altair_chart(historical_chart, use_container_width=True)
