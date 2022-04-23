import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta
import pydeck as pdk
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

DATA_URL = 'data/dashboard_metrics.csv'
BASELINE_URL = 'data/baseline_dashboard_metrics.csv'


def load_data(url):
    data = pd.read_csv(url)
    return data


@st.cache
def read_files_medical_state_vis():
    df_hospital = pd.read_csv("data/cases_hospital_bed_usa_statewise.csv")
    states = alt.topo_feature(data.us_10m.url, 'states')
    df_hospital['date'] = df_hospital['date'].map(lambda row: datetime.strptime(row, '%Y-%m-%d').date())

    return df_hospital, states


@st.cache
def get_four_state_map_files(df_medical):

    df_med = df_medical[df_medical["type"] == "Medicine Facility"]
    df_medicine_vaccination = df_medical[df_medical["type"] == "Med&Vac"]

    # return df_ny, df_oh, df_ut, df_ca
    return df_med, df_medicine_vaccination



def get_df_bed_util(state, covid_data):

    df = covid_data[covid_data["state"] == state]
    df = df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
    df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                       "adult_icu_bed_utilization": "ICU beds utilization"},
              inplace=True)

    df = df.melt("Date", var_name='Parameter', value_name='Value')

    return df

@st.cache
def read_medicine_facility_files():
    df_medical_vaccination_facility = pd.read_csv("data/vaccination_medical_facility.csv")

    return df_medical_vaccination_facility


@st.cache
def read_testing_files():

    df_test = pd.read_csv("data/testing_results.csv")

    return df_test


@st.cache
def read_dashboard_files():

    covid_data = load_data(DATA_URL)
    baseline_dashboard_data = load_data(BASELINE_URL)
    covid_data["date"] = covid_data["date"].map(
        lambda row: datetime.strptime(row, "%Y-%m-%d").date())

    return covid_data, baseline_dashboard_data


@st.cache
def read_files_model():
    df_values = {}
    df_features = {}
    df_values_thirty = {}

    path = "./data/model/"
    dir_list = os.listdir(path)

    for file in dir_list:
        if file.endswith('.csv'):
            df = pd.read_csv(path+file)
            vals = file.split('_')
            # Normal
            if len(vals) == 3:
                if vals[2].split('.')[0] == 'values':
                    df = df[['date', 'y', 'pred']]
                    df['diff'] = df.apply(lambda row: abs(row['y'] - row['pred']), axis=1)
                    df['diff_sq'] = df.apply(lambda row: row['diff'] * row['diff'], axis=1)
                    df = df.rename(columns={"date": "Date", "y": "Actual", "pred": "Predicted"})
                    df_values[vals[1]] = df
                else:
                    df = df[['feature', 'importance']]
                    data = {wrd: cnt for wrd, cnt in zip(df['feature'], df['importance'])}
                    df_features[vals[1]] = data
            # 30
            else:
                if vals[2] == 'values':
                    df = df[['date', 'y', 'pred']]
                    df['diff'] = df.apply(lambda row: abs(row['y'] - row['pred']), axis=1)
                    df['diff_sq'] = df.apply(lambda row: row['diff'] * row['diff'], axis=1)
                    df = df.rename(columns={"date": "Date", "y": "Actual", "pred": "Predicted"})
                    df_values_thirty[vals[1]] = df

    return df_values, df_features, df_values_thirty


def medical_state_vis(location_df, states, date_slider, column):

    temp_df = location_df[location_df['date'] == date_slider]

    cols = ["date", "state", "inpatient_beds_utilization", "new_confirmed", "latitude", "longitude", "cases_per_population"]
    temp_df = temp_df[cols]
    temp_df.rename(columns={"inpatient_beds_utilization": "Bed Utilization", "new_confirmed": "Cases", "cases_per_population": "Case Density"},
              inplace=True)
    # Background chart
    background = alt.Chart(states, title="").mark_geoshape(
        fill='white ',
        stroke='black'
    ).project('albersUsa').properties(
        width=650,
        height=400
    )

    # Points chart

    # First aggregate latitutde longitude points based on country, then plot them, where the count = number of new cases
    points = alt.Chart(temp_df).mark_circle().encode(
        latitude='latitude:Q',
        longitude='longitude:Q', # points with utilization 0.1 have some blue color. its a bit misleasding
        color=alt.Color("Bed Utilization:Q", scale=alt.Scale(domain=[0.4, 0.6, 0.8, 1.0],
                                                                        range=['green', 'yellow', 'red', 'purple']),
                        legend=alt.Legend(orient="left", titleFontSize=15, labelFontSize=15)),
        size=alt.Size('Cases:Q', scale=alt.Scale(range=[10, 1000], domain=[0, 10000]),
                      legend=alt.Legend(values=[0, 5000, 10000, 50000], symbolFillColor="grey",
                                        labelColor="white", direction="vertical",
                                        labelFontSize=16, titleColor="white",
                                        titleFontSize=16, titleAlign="right")),
        tooltip=[alt.Tooltip("state", title="State"), alt.Tooltip('Bed Utilization:Q', title= "Bed Utilization"),
                 alt.Tooltip('Cases:Q', title="Cases"), alt.Tooltip('Case Density:Q', title="Cases per state population")]
    )

    # Plot both
    glob_plot = background + points
    with column:
        column.header("Hospital bed utilization over time in the US")
        column.write(glob_plot, use_container_width=True)

    return

def four_state_map_vis(df_medical, df_medicine_vaccination, state):

    if state == "NY":
        ny_map_vis(df_medical, df_medicine_vaccination)
    elif state == "CA":
        ca_map_vis(df_medical, df_medicine_vaccination)
    elif state == "OH":
        oh_map_vis(df_medical, df_medicine_vaccination)
    elif state == "UT":
        ut_map_vis(df_medical, df_medicine_vaccination)
    else:
        us_map_vis(df_medical, df_medicine_vaccination)



def ny_map_vis(df_medical, df_medical_and_vac):

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
                data=df_medical_and_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    tooltip={"text": "Type: {type}\nState: {State Code}"}))

    return

def us_map_vis(df_medical, df_medical_and_vac):

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=38.00,
            longitude=-100.4,
            zoom=3.5,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[180, 0, 200, 150],
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical_and_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[0, 255, 0, 60],
                pickable=True,
            )
        ],
        tooltip={"text": "Type: {type}\nState: {State Code}"}))

    return


def ca_map_vis(df_medical, df_medical_and_vac):
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
                data=df_medical_and_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    tooltip={"text": "Type: {type}\nState: {State Code}"}))

    return


def oh_map_vis(df_medical, df_medical_and_vac):

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
                data=df_medical_and_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2],
                pickable=True,
            )
        ],
    tooltip={"text": "Type: {type}\nState: {State Code}"}))
    return


def ut_map_vis(df_medical, df_medical_and_vac):
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
                get_fill_color=[180, 0, 200, 90], # purple
                pickable=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df_medical_and_vac,
                get_position='[lon, lat]',
                auto_highlight=True,
                get_radius=5000,
                get_fill_color=[34, 200, 48, 2], # green
                pickable=True,
            )
        ],
    tooltip={"text": "Type: {type}\nState: {State Code}"}))

    return


def build_metric(state, date_slider, baseline_daashboard_data, columnleft, columnright):

    st.write("<p align='right'>**Figures are with respect to previous day</p>", unsafe_allow_html=True)
    state_info = covid_data[covid_data["state"] == state]
    state_info_date = state_info[state_info["date"] == date_slider]
    if date_slider == min(state_info["date"]):
        baseline_value = state_info_date
    else:
        baseline_value = state_info[state_info["date"] == date_slider - timedelta(days=1)]

    if state_info_date.empty or state_info.empty:
        columnright.header("No data available :'(")

    else:
        cases = state_info_date["new_confirmed"].values[0]
        baseline_cases = baseline_value["new_confirmed"].values[0]
        change_total_cases = int(cases - baseline_cases)

        deceased = state_info_date["new_deceased"].values[0]
        baseline_deceased = baseline_value["new_deceased"].values[0]
        change_total_deceased = int(deceased - baseline_deceased)

        total_beds = state_info_date["inpatient_beds"].values[0]
        baseline_total_beds = baseline_value["inpatient_beds"].values[0]
        change_total_beds = total_beds - baseline_total_beds

        beds_utilization = state_info_date["inpatient_beds_utilization"].values[0]
        baseline_beds_utilization = baseline_value["inpatient_beds_utilization"].values[0]
        percentage_change_beds_utilization = ((beds_utilization + 1) - (baseline_beds_utilization + 1)) * 100 / (
                baseline_beds_utilization + 1)

        beds_covid = state_info_date["percent_of_inpatients_with_covid"].values[0]
        baseline_beds_covid = baseline_value["percent_of_inpatients_with_covid"].values[0]
        percentage_change_beds_covid = ((beds_covid + 1) - (baseline_beds_covid + 1)) * 100 / (
                baseline_beds_covid + 1)

        icu_utilization = state_info_date["adult_icu_bed_utilization"].values[0]
        baseline_icu_utilization = baseline_value["adult_icu_bed_utilization"].values[0]
        percentage_change_icu_utilization = ((icu_utilization + 1) - (baseline_icu_utilization + 1)) * 100 / (
                baseline_icu_utilization + 1)

        icu_covid_utilization = state_info_date["adult_icu_bed_covid_utilization"].values[0]
        baseline_icu_covid = baseline_value["adult_icu_bed_covid_utilization"].values[0]
        percentage_change_icu_covid = ((icu_covid_utilization + 1) - (baseline_icu_covid + 1)) * 100 / (
                baseline_icu_covid + 1)

        staff_shortage = state_info_date["critical_staffing_shortage_today_yes"].values[0]
        baseline_staff_shortage = baseline_value["critical_staffing_shortage_today_yes"].values[0]
        percentage_change_staff_shortage = int(staff_shortage - baseline_staff_shortage)


        with columnleft:
            st.header("")
            st.metric("Cases today", int(cases), change_total_cases, delta_color="inverse")
            st.metric("Hospital bed utilization", str(round(beds_utilization, 2)),
                      str(round(percentage_change_beds_utilization, 2)) + " %", delta_color="inverse")

            if np.isnan(icu_utilization):
                st.metric("ICU bed utilization", "---")
            else:
                st.metric("ICU bed utilization", round(icu_utilization, 2), str(round(percentage_change_icu_utilization, 2)) + " %",
                      delta_color="inverse")

            st.metric("Number of hospitals with staff shortage", staff_shortage, percentage_change_staff_shortage,
                      delta_color="inverse")
        with columnright:
            st.header(" ")
            st.metric("Deaths today", int(deceased), change_total_deceased, delta_color="inverse")
            st.metric("Hospital bed utilization COVID patients", round(beds_covid, 2), str(round(percentage_change_beds_covid, 2)) + " %", delta_color="inverse")

            if np.isnan(icu_covid_utilization):
                st.metric("ICU bed utilization COVID patients", "---")
            else:
               st.metric("ICU bed utilization COVID patients", round(icu_covid_utilization, 2),
                         str(round(percentage_change_icu_covid, 2)) + " %", delta_color="inverse")

            st.metric("Total beds", int(total_beds), str(int(change_total_beds)))

    return


def bed_utilization_chart(df, state, column):

    df_brush = alt.selection(type='interval', encodings=["x"])
    df_bed_utilization_chart = alt.Chart(df,
                                         title="Trend in Hospital bed utilization in " + state).mark_line().encode(
        x='Date:T',
        y='Value:Q',
        color=alt.Color("Parameter", scale=alt.Scale(scheme='set1'),
                        legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15)),
        strokeDash='Parameter:N',
    ).properties(
        width=600,
        height=400
    ).add_selection(
        df_brush
    ).configure_title(fontSize=16)
    column.write(df_bed_utilization_chart)


def daily_deaths_chart(state, column):
    col_utilization, deaths = st.columns(2)
    # New York deaths chart
    df_deaths = covid_data[covid_data["state"] == state]
    df_deaths = df_deaths[["date", "new_deceased"]]
    df_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                           inplace=True)
    df_deaths_chart = alt.Chart(df_deaths, title="Daily Deaths in " + state + " over time").mark_line(
        color="#d147ed").encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Deaths:Q')
    ).interactive().properties(
        width=500,
        height=400
    ).configure_title(fontSize=16)
    column.write(df_deaths_chart)


def testing_and_results_chart(df_test, state):

    df_test_results = df_test[df_test["state"] == state]
    df_test_results = df_test_results[["date", "new_tested", "new_results_reported"]]
    df_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                    "new_results_reported": "# Results reported"},
                           inplace=True)
    df_test_results = df_test_results.melt("Date", var_name='Parameter', value_name='Count')

    df_test_results_chart = alt.Chart(df_test_results,
                                            title="Graph of Testing Vs Result reports for "+ state).mark_line().encode(
        x='Date:T',
        y='Count:Q',
        color=alt.Color("Parameter", scale=alt.Scale(scheme='set2'),
                        legend=alt.Legend(orient="right", titleFontSize=15, labelFontSize=15))
    ).interactive().properties(
        width=1000,
        height=400
    ).configure_title(fontSize=16)

    st.write(df_test_results_chart)


def staff_shortage_and_deaths_chart(df_shortage_vs_deaths, state, column):

    df_shortage_vs_deaths_chart = alt.Chart(df_shortage_vs_deaths,
                                                  title="Graph of Daily deaths and hospitals with staff shortage in " + state).mark_point().encode(
        x='Date:T',
        y='Deaths:Q',
        color=alt.Color("# Hospitals with shortage:Q",
                        scale=alt.Scale(scheme='goldred'),
                        legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15))
    ).interactive().properties(
        width=600,
        height=400
    ).configure_title(fontSize=16)
    column.write(df_shortage_vs_deaths_chart)


def describe_hospital_utilization():
   st.header("Hospital bed utilization")
   # Added Content HERE
   st.markdown("Bed utilization is a key component of throughput for all in-patient care hospitals."
               "The goal is to have enough hospital beds available to meet the needs of newly admitted patients. "
               "It is measured as the percentage of beds that are being utilized. ")
   r'''
         $$\hspace{60mm} Utilization = \frac{\#Occupied\ beds}{\#Available\ beds}$$
    '''


def conclusion_hospital_utilization():
    text = "From the graph we see that over time the utlization of hospitals has increased as indicated by the change in " \
           "color gradient from <span style='font-family:sans-serif; color:yellowgreen;'>yellowish-green</span> to " \
           "<span style='font-family:sans-serif; color:#953553;'>reddish-purple</span>"
    st.markdown(text, unsafe_allow_html=True)
    text = "We also see that as the number of cases (indicated by the size of the circles) increases, the utilization" \
           "moves towards the upper end. This tells us that patients infected with Covid were seeking care at hospitals." \
           "<br> It is imperative that hospitals be able to provide care to infected individuals during a future pandemic. " \
           "<br> Simply increasing bed capacity is not sustainable in terms of both economic and workforce requirement. It is " \
           "necessary for us to identify strategies that enable quick expansion of space, staff and supplies in the event of a" \
           "future pandemic. <br>" \
           "We will now study this is more detail for the states of New York(NY), Utah(UT), Ohio(OH) and California(CA) for" \
           " ease of interpretation and to contrast how these effects have spread across the country."
    st.markdown(text, unsafe_allow_html=True)


def describe_access_to_vaccination_sites():
    st.title("Average time to reach closest vaccination site in the US")
    colwalking, coldriving, coltransit = st.columns(3)
    with colwalking:
        colwalking.header("Walking :runner:")
        text = "<b style='font-size: 30px;font-family:Monaco, monospace; color:yellow;'>37.5 mins</b>"
        colwalking.markdown(text, unsafe_allow_html=True)
    with coldriving:
        coldriving.header("Driving :car:")
        text = "<b style='font-size: 30px;font-family:Monaco, monospace; color:green;'>30 mins</b>"
        coldriving.markdown(text, unsafe_allow_html=True)
    with coltransit:
        coltransit.header("Public Transit :bus:")
        text = "<b style='font-size: 30px;font-family:Monaco, monospace; color:red;'>45 mins</b>"
        coltransit.markdown(text, unsafe_allow_html=True)


def conclusion_utilization_shortage():
    text = "From the graph on the left we see that during the pandemic there is more variation in the ICU beds, " \
           "whereas the im-patient beds seem to relatively be at the same level. A majority of COVID-19 affected patients" \
           "do not need to be admitted. Only cases where the individual is suffer from other co-morbidities required to be admitted" \
           "and these patients usually required sofisticated care that can be provided only in the ICU. Thus, it is important" \
           "to have adequate number of ICU beds. "
    st.markdown(text)


def medical_infra_intro():
    st.header("Effect of COVID-19 on the Medical Infrastructure of the US")
    text = "Through our experiences with the COVID-19 pandemic, we should pay attention to the " \
           "overall capacity of the nation’s public health system as it protects and promotes the health " \
           "of all people in all communities." \
           "Public health infrastructure enables every level of government to prevent disease, promote health, and prepare " \
           "for and respond to both emergency situations and ongoing challenges. Health departments also play a vital role in " \
           "educating the public about unexpected infectious disease threats as well as evidence-based interventions for " \
           "mitigation. <br>" \
           "We should wait for the next pandemic  to make us realize the strategic importance of public health agencies and the " \
           "critical role they play in protecting us. " \
           "Through a set of interesting visualizations and statistics, we explore the effect of COVID-19 on the medical infrastructure" \
           "and we attempt to gain insights regarding possible strategies that can be adopted in the event of a future pandemic. "
    st.markdown(text, unsafe_allow_html=True)


def medical_map_dashboard_vis(covid_data, df_hospital, states, baseline_dashboard_data):

    describe_hospital_utilization()

    date_slider = st.slider('Silde the Date to see how the Hospitilization and realated parameters vary with time',
                            min(df_hospital['date']), max(df_hospital['date']), min(df_hospital['date']),
                            step=timedelta(days=1), help="Slide over to see different dates")

    col1, col2, col3 = st.columns([3, 1, 1])
    medical_state_vis(df_hospital, states, date_slider, col1)
    with col2:
        list_states = sorted(list(set(covid_data['state'])))
        ny_ind = list_states.index("NY")
        state = st.selectbox('Select a State', list_states, index=ny_ind)
    build_metric(state, date_slider, baseline_dashboard_data, col2, col3)

    conclusion_hospital_utilization()

    return


def staff_shortage_and_bed_util_vis(covid_data):

    st.title("How does hospital utilization and staff shortage vary with time?")

    list_states_cov = sorted(list(set(covid_data['state'])))
    ny_ind = list_states_cov.index("NY")
    state = st.selectbox('Select a State!', list_states_cov, index=ny_ind)

    # Utilization Vs Shortage & Deaths
    utilization_col, deaths_col = st.columns([0.85, 1])

    df_shortage_vs_deaths = covid_data[covid_data["state"] == state]
    df_shortage_vs_deaths = df_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    df_staff = df_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                          "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},)

    df_bed = get_df_bed_util(state, covid_data)

    bed_utilization_chart(df_bed, state, utilization_col)
    staff_shortage_and_deaths_chart(df_staff, state, deaths_col)

    conclusion_utilization_shortage()

    return


def covid_test_vis(df_test):

    st.title("Are all covid test sample results reported?")
    list_states = sorted(list(set(df_test['state'])))
    ny_ind = list_states.index("NY")
    state = st.selectbox('Select a State', list_states , index=ny_ind)
    testing_and_results_chart(df_test, state)
    return


def vac_and_med_loc_vis(df_medicine_vaccination_facility):

    st.title("How are the vaccination and Medicine facilities spread across the country?")

    text = "<p style='font-size: 30px;'><span style='font-family:sans-serif; color:rgba(34, 200, 48, 2);'>Vaccination </span> &" \
           "<span style='font-family:sans-serif; color:rgba(180, 0, 200, 90);'> Medicine </span>facilities</p>"

    st.markdown(text, unsafe_allow_html=True)
    text = "<p style='font-size: 30px;'>New York</p>"
    st.markdown(text, unsafe_allow_html=True)

    df_med, df_vac = df_medicine_vaccination_facility
    four_state_map_vis(df_med, df_vac, None)

    return

def model_vis(df_values, df_features, df_values_thirty):


    model_plot_7(df_values)
    model_plot_30(df_values_thirty)
    features_plot(df_features)
    return


def model_plot_7(df_values):
    states = list(sorted(df_values.keys()))

    selected_state = st.selectbox('Select a State', states)
    df = df_values[selected_state]

    mae = int(sum(df['diff'])/len(df))
    mse = int(sum(df['diff_sq'])/len(df))

    col1, col2, col3 = st.columns(3)

    with col3:
        st.write("MAE: ", f"{mae:,}")
        st.write("MSE: ", f"{mse:,}")

    with col1:
        df = df[['Date', 'Actual', 'Predicted']]
        data = df.melt("Date", var_name='Type', value_name='Cases')
        chart = alt.Chart(data, title="Actual vs Predicted cases for a 7 day step size for " + selected_state + " state") \
            .mark_line().encode(
            x='Date:T',
            y='Cases:Q',
            color='Type:N'
        ).interactive().properties(
            width=800,
            height=400
        )
        st.write(chart)
    return


def model_plot_30(df_values):

    states = sorted(list(df_values.keys()))
    # Edit below to select dynamically

    selected_state = st.selectbox('Select a State', states)
    df = df_values[selected_state]

    mae = int(sum(df['diff']) / len(df))
    mse = int(sum(df['diff_sq']) / len(df))

    col1, col2, col3 = st.columns(3)

    with col3:
        st.write("MAE: ", f"{mae:,}")
        st.write("MSE: ", f"{mse:,}")

    with col1:
        df = df[['Date', 'Actual', 'Predicted']]
        data = df.melt("Date", var_name='Type', value_name='Cases')
        chart = alt.Chart(data, title="Actual vs Predicted cases for a 30 day step size for " + selected_state + " state") \
            .mark_line().encode(
            x='Date:T',
            y='Cases:Q',
            color='Type:N'
        ).interactive().properties(
            width=800,
            height=400
        )
        st.write(chart)
    return


def features_plot(df_features):

    states = sorted(list(df_features.keys()))
    selected_state = st.selectbox('Select a State to show the Feature weights', states)
    data = df_features[selected_state]
    wc = WordCloud(width=800, height=400, max_words=200).generate_from_frequencies(data)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.show()
    st.pyplot(fig)

    # https://www.cienciadedatos.net/documentos/py27-time-series-forecasting-python-scikitlearn.html
    # Lag_7 means that last week same day. So day of the week matters?
    return

if __name__ =="__main__":

    covid_data, baseline_dashboard_data = read_dashboard_files()
    df_hospital, states = read_files_medical_state_vis()
    df_medicine_vaccination_facility = read_medicine_facility_files()
    df_test = read_testing_files()
    df_medical_fac_loc = get_four_state_map_files(df_medicine_vaccination_facility)
    df_values, df_features, df_values_thirty = read_files_model()

    medical_infra_intro()
    medical_map_dashboard_vis(covid_data, df_hospital, states, baseline_dashboard_data)
    staff_shortage_and_bed_util_vis(covid_data)
    covid_test_vis(df_test)
    vac_and_med_loc_vis(df_medical_fac_loc)
    describe_access_to_vaccination_sites()
    model_vis(df_values, df_features, df_values_thirty)

