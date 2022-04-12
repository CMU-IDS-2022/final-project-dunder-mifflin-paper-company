import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta
import pydeck as pdk
import time

@st.cache
def read_files():
    df_hospital = pd.read_csv("data/cases_hospital_bed_usa_statewise.csv")
    states = alt.topo_feature(data.us_10m.url, 'states')
    df_medical_fac = pd.read_csv("data/medical_facilities.csv")
    df_vac_fac = pd.read_csv("data/vaccination_sites.csv")

    df_hospital['date'] = df_hospital['date'].map(lambda row: datetime.strptime(row, '%Y-%m-%d').date())

    df_medical_fac = df_medical_fac[df_medical_fac['State Code'].isin(['OH', 'NY', 'CA', 'UT'])]
    df_vac_fac = df_vac_fac[df_vac_fac['state'].isin(['OH', 'NY', 'CA', 'UT'])]
    df_medical_fac['lat'] = df_medical_fac['latitude']
    df_medical_fac['lon'] = df_medical_fac['longitude']
    df_vac_fac['lat'] = df_vac_fac['facility_latitude']
    df_vac_fac['lon'] = df_vac_fac['facility_longitude']

    df_medicals = []
    df_vacs = []
    df_medicals.append(df_medical_fac[df_medical_fac['State Code'] == 'NY'][['lat', 'lon']])
    df_medicals.append(df_medical_fac[df_medical_fac['State Code'] == 'CA'][['lat', 'lon']])
    df_medicals.append(df_medical_fac[df_medical_fac['State Code'] == 'OH'][['lat', 'lon']])
    df_medicals.append(df_medical_fac[df_medical_fac['State Code'] == 'UT'][['lat', 'lon']])

    df_vacs.append(df_vac_fac[df_vac_fac['state'] == 'NY'][['lat', 'lon']])
    df_vacs.append(df_vac_fac[df_vac_fac['state'] == 'CA'][['lat', 'lon']])
    df_vacs.append(df_vac_fac[df_vac_fac['state'] == 'OH'][['lat', 'lon']])
    df_vacs.append(df_vac_fac[df_vac_fac['state'] == 'UT'][['lat', 'lon']])

    return df_hospital, states, df_medicals, df_vacs

def medical_state_vis(location_df, states):

    # Slider for date
    date_slider = st.slider('Silde the Date to see how the Hospitilization vary with time',
                            min(location_df['date']), max(location_df['date']), min(location_df['date']),
                            step=timedelta(days=1), help="Slide over to see different dates")

    temp_df = location_df[location_df['date'] == date_slider]

    cols = ["date", "state", "inpatient_beds_utilization", "new_confirmed", "latitude", "longitude"]
    temp_df = temp_df[cols]

    # Background chart
    background = alt.Chart(states, title="Variation of Hospital bed usage over time").mark_geoshape(
        fill='white ',
        stroke='black',
    ).project('albersUsa').properties(
        width=650,
        height=400
    )

    # Points chart

    # First aggregate latitutde longitude points based on country, then plot them, where the count = number of new cases
    points = alt.Chart(temp_df).mark_circle().encode(
        latitude='latitude:Q',
        longitude='longitude:Q',
        color=alt.Color("inpatient_beds_utilization:Q", scale=alt.Scale(domain=[0.4, 0.6, 0.8, 1.0], range=['green', 'yellow', 'red', 'purple'])),
        size=alt.Size('new_confirmed:Q', scale=alt.Scale(range=[10, 1000], domain=[0, 10000]), legend=None),
        tooltip=[alt.Tooltip("state", title="State"), alt.Tooltip('inpatient_beds_utilization:Q', title= "Hospitilizations"),
                 alt.Tooltip('new_confirmed:Q', title="Cases")]
    )

    # Plot both
    glob_plot = background + points
    st.altair_chart(glob_plot, use_container_width=True)

    if st.button('Play DONT CLICK  (WIP)'):
        while date_slider <= max(location_df['date']):
            date_slider += timedelta(days=10)
            time.sleep(10)

    return

def four_state_map_vis(df_medical, df_vac):
    ny_map_vis(df_medical[0], df_vac[0])
    ca_map_vis(df_medical[1], df_vac[1])
    oh_map_vis(df_medical[2], df_vac[2])
    ut_map_vis(df_medical[3], df_vac[3])

def ny_map_vis(df_medical, df_vac):

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=42.76,
            longitude=-75.4,
            zoom=5.5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[180, 0, 200, 90],
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    ))

    return

def ca_map_vis(df_medical, df_vac):

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-119.4,
            zoom=4.8,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[180, 0, 200, 90],
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    ))

    return

def oh_map_vis(df_medical, df_vac):

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=40.76,
            longitude=-82.4,
            zoom=5.5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[180, 0, 200, 90],
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    ))
    return

def ut_map_vis(df_medical, df_vac):
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=39.76,
            longitude=-111.4,
            zoom=5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[180, 0, 200, 90],
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    ))

    return

if __name__ =="__main__":
    df_hospital, states, df_medical_fac, df_vac_fac = read_files()
    medical_state_vis(df_hospital, states)

    # TO DO - ADD TOOLTIP
    four_state_map_vis(df_medical_fac, df_vac_fac)
