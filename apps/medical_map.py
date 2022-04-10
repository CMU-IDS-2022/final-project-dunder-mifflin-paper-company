import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta

@st.cache
def read_files():
    df = pd.read_csv("data/cases_hospital_bed_usa_statewise.csv")
    states = alt.topo_feature(data.us_10m.url, 'states')
    df['date'] = df['date'].map(lambda row: datetime.strptime(row, '%Y-%m-%d').date())
    return df, states

def medical_state_vis(location_df, states):

    # Slider for date
    date_slider = st.slider('Silde the Date to see how the Hospitilization vary with time', min(location_df['date']), max(location_df['date']), min(location_df['date']),
                            step=timedelta(days=1), help="Slide over to see different dates")

    # Get subset of dataframe based on selection
    # This requires location_df to be grouped by year and month already
    # temp_df = location_df[location_df['year'] == date_slider.year]
    # temp_df = temp_df[temp_df['month'] == date_slider.month]

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

    return

if __name__ =="__main__":
    df, states = read_files()
    medical_state_vis(df, states)
