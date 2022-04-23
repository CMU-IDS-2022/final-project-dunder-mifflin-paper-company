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

# """
#     We investigate searches that are relevant to covid symptoms
#         - Fever or chills
#         - Cough
#         - Shortness of breath or difficulty breathing
#         - Fatigue
#         - Muscle or body aches
#         - Headache
#         - New loss of taste or smell
#         - Sore throat
#         - Congestion or runny nose
#         - Nausea or vomiting
#         - Diarrhea
# """

SEARCH_STRINGS = [
    "fever",
    "chills",
    "cough",
    "shallow_breathing",
    "shortness_of_breath",
    "fatigue",
    "headache",
    "cluster_headache",
    "sore_throat",
    "nasal_congestion",
    "nausea",
    "vomiting",
    "diarrhea",
    "chest_pain",
    "burning_chest_pain",
    "back_pain",
]

# st.set_page_config(layout="wide")


@st.cache
def get_geocoder():
    return geocoder("data/usa_shape/usa-states-census-2014.shp")


@st.cache
def read_files():
    search_trend_df = pd.read_csv("data/google-search-trends_filtered.csv")
    search_trend_df["date"] = pd.to_datetime(search_trend_df["date"])

    cases_df = pd.read_csv("data/epidemiology_filtered.csv")
    cases_df["date"] = pd.to_datetime(cases_df["date"])

    with open("data/us_states.json", "r") as fp:
        polygons = json.load(fp)

    return search_trend_df, cases_df, polygons


def compute_correlation(search_trend_df, cases_df, shift, location_key, search_strings):

    location_cases = cases_df[cases_df["location_key"] == location_key][
        ["date", "new_confirmed"]
    ]
    cases_values = (
        location_cases["new_confirmed"]
        .rolling(ROLLING_WINDOW)
        .mean()[ROLLING_WINDOW - 1 :]
    )
    dates = location_cases["date"][ROLLING_WINDOW - 1 :]

    location_search_trends = search_trend_df[
        search_trend_df["location_key"] == location_key
    ]

    if len(search_strings):
        search_trend_values = location_search_trends[search_strings][
            ROLLING_WINDOW - 1 :
        ].sum(axis=1)
    else:
        search_trend_values = location_search_trends[ROLLING_WINDOW - 1 :].sum(axis=1)

    if shift == 0:
        shifted_search_trend_values = search_trend_values
        shifted_case_values = cases_values
    else:
        shifted_search_trend_values = search_trend_values[:-shift]
        shifted_case_values = cases_values[shift:]
        dates = dates[shift:]

    shifted_search_trend_values /= max(shifted_search_trend_values)
    # shifted_case_values /= max(shifted_case_values)

    corref = np.corrcoef(
        x=shifted_search_trend_values / max(shifted_search_trend_values),
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


def plot_search_dashboard():

    search_trend_df, cases_df, polygons = read_files()
    polygons = copy.deepcopy(polygons)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            "## Do internet search trends hint towards a rise in COVID 19 cases?"
        )
        st.markdown("***")

        st.markdown(
            """
            The internet often serves as the first point of information for many people today.
            Building on this fact, we try to answer an important question: whether trends in search patterns can be 
            helpful in detecting COVID 19 outbreaks.

            The COVID-19 Search Trends symptoms dataset collates the volume of Google 
            searches for a broad set of symptoms, signs and health conditions. More information
            pertaining the curation of this dataset can be found on this 
            [page](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-search-trends.md).
            The dataset provides trend values for each search string, which reflects volume of Google searches for that search string.
        """
        )
        st.markdown(
            """
            With this dashboard, we try to gauge which search strings are most effective in hinting towards a rise of COVID 19 cases
            in the future; we further break this analysis down on a state level. Since there can be a lag between people experiencing
            symptoms and actually getting tested positive, we introduce a parameter `lag`. Using this parameter, we can calculate the correlation
            between the search trend value and COVID 19 cases `lag` days in the future.

            **Intuitively, we expect a positive correlation between these two, since a higher search trend value should indicate a rise in cases.**

            As a preprocessing step, we filter out the search strings 
            in the dataset and use only the set of symptoms that are associated with COVID 19 
            [(as documented by CDC)](https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html).
            Some examples of these search strings include `fever`, `chest paing`, and `shallow breathing`. 
            We normalize the search trend values to a scale of 0 to 1 for ease of visualisations.
            """
        )

    st.markdown("***")

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown(
            """
            When multiple search strings are selected, we aggregate the value by summing up each search string's trend value.
            If no search string is selected, we aggregate all search strings' trend values.
        """
        )
        searches = st.multiselect("Search terms:", SEARCH_STRINGS, default=["fever"])

    with col2:
        st.markdown("***")
        st.markdown(
            """
            Since there can be a lag between people experiencing
            symptoms and actually getting tested positive, we introduce a parameter `lag`,
            which enables a comparision between search trends and number of cases `lag` days in the future.
        """
        )
        shift = st.slider("Number of days in the future (Lag)", 0, 30)

    search_strings = list(
        map(lambda search_string: "search_trends_" + search_string, searches)
    )

    for ind, ele in enumerate(polygons["features"]):
        location_key = "US_" + ele["id"]
        ele["properties"]["State"] = ele["properties"]["name"]
        del ele["properties"]["name"]

        correlation = compute_correlation(
            search_trend_df, cases_df, shift, location_key, search_strings
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

    location_search_trends = search_trend_df[
        search_trend_df["location_key"] == location
    ]

    if len(search_strings):
        search_trend_values = location_search_trends[search_strings][
            ROLLING_WINDOW - 1 :
        ].sum(axis=1)
    else:
        search_trend_values = location_search_trends[ROLLING_WINDOW - 1 :].sum(axis=1)

    if shift == 0:
        shifted_search_trend_values = search_trend_values
        shifted_case_values = cases_values
    else:
        shifted_search_trend_values = search_trend_values[:-shift]
        shifted_case_values = cases_values[shift:]
        dates = dates[shift:]

    shifted_search_trend_values /= max(shifted_search_trend_values)

    corref = round(
        np.corrcoef(
            x=shifted_search_trend_values / max(shifted_search_trend_values),
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
            This map shows the correlation between COVID 19 cases and search trend values for the selected lag across different states.
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
    data["shifted_search_trend_values"] = shifted_search_trend_values.tolist()
    data["x"] = dates.values

    cases_chart = (
        alt.Chart(data)
        .mark_line(opacity=1, color="#57A44C")
        .encode(
            alt.X(
                "x",
                title="Days",
            ),
            alt.Y(
                "shifted_case_values",
                title="Cases",
                axis=alt.Axis(title="Cases", titleColor="#57A44C"),
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
                title="Days",
                # scale=alt.Scale(domain=['2021-01-01','2021-12-31'])
            ),
            alt.Y(
                "shifted_search_trend_values",
                title="trend",
                axis=alt.Axis(
                    title="Search trend value (normalised)", titleColor="#5276A7"
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
            "This graph compares the number daily of COVID 19 cases and the search trend value (normalised to a scale of 0 to 1) with the selected lag (%d days in the future) "
            % (shift)
        )
        st.markdown("<p align=center> %s </p>" % (text), unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)

    ############### HISTORICAL CHART ###############

    searches_tooltip_value = ", ".join(sorted(list(set(searches))))

    if (
        not len(st.session_state["search_history"]["region"])
        or st.session_state["search_history"]["region"][-1]
        != st.session_state["selected_region"]
        or st.session_state["search_history"]["searches"][-1] != searches_tooltip_value
        or st.session_state["search_history"]["shift"][-1] != shift
        or st.session_state["search_history"]["correlation"][-1] != corref
    ):

        st.session_state["search_history"]["region"].append(
            st.session_state["selected_region"]
        )
        st.session_state["search_history"]["searches"].append(searches_tooltip_value)
        st.session_state["search_history"]["shift"].append(shift)
        st.session_state["search_history"]["correlation"].append(corref)

    historical_data = pd.DataFrame(st.session_state["search_history"])
    historical_chart = (
        alt.Chart(historical_data.reset_index(), title="Search history")
        .mark_line(point=True, color="#FFFFFF")
        .encode(
            alt.Y(
                "correlation",
                title="Correlation",
                scale=alt.Scale(domain=[-1, 1]),
                axis=alt.Axis(tickSize=0),
            ),
            alt.X(
                "index",
                title="History",
                scale=alt.Scale(
                    domain=[-1, len(st.session_state["search_history"]["correlation"])],
                    type="point",
                ),
                axis=alt.Axis(tickMinStep=1),
            ),
            tooltip=[
                alt.Tooltip("region", title="Region"),
                alt.Tooltip("shift", title="Shift"),
                alt.Tooltip("searches", title="Searches"),
                alt.Tooltip("correlation", title="Correlation"),
            ],
        )
        .interactive()
    )

    with col1:
        st.markdown("***")
        st.markdown(
            """
        <span style="width: 100%; text-align: left;">
            This graph shows the correlation between COVID 19 cases and search trend values for previously explored parameters in this dashboard.
            <b>This can be used to track how changing certain parameters (for instance, lag) affects the correlation.</b>
            <br />
            <br />
        """,
            unsafe_allow_html=True,
        )

        st.altair_chart(historical_chart, use_container_width=True)
