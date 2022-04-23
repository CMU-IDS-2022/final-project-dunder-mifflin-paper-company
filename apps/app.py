import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta
import pydeck as pdk
import os


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


def build_metric(covid_data, state, date_slider, columnleft, columnright):

    st.write("<p align='right' style='font-family:Courier New, monospace; font-size:12px'>**Figures (Increase and Decrease) represent <br> change with respect to the previous day</p><br><br>", unsafe_allow_html=True)
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

def testing_and_results_chart(df_test, state):

    df_test_results = df_test[df_test["state"] == state]
    df_test_results = df_test_results[["date", "new_tested", "new_results_reported"]]
    df_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                    "new_results_reported": "# Results reported"},
                           inplace=True)
    df_test_results = df_test_results.melt("Date", var_name='Parameter', value_name='Count')

    df_test_results_chart = alt.Chart(df_test_results,
                                            title="Graph of Testing Vs Result reports for "+ state).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        y=alt.Y('Count:Q', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        color=alt.Color("Parameter", scale=alt.Scale(scheme='set2'),
                        legend=alt.Legend(orient="right", titleFontSize=15, labelFontSize=15)),
        tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip('Parameter:N', title="Parameter"),
                 alt.Tooltip('Count:Q', title="Count")]
    ).interactive().properties(
        width=1000,
        height=400
    ).configure_title(fontSize=16)

    st.write(df_test_results_chart)


def describe_hospital_utilization():
   st.header("Hospital bed utilization")
   # Added Content HERE
   st.markdown("Hospital Bed utilization is a key component of throughput for all in-patient care hospitals."
               " The goal is to have enough hospital beds available to meet the needs of newly admitted patients, "
               "without compromising the quality of service to already admitted patients. "
               "In our analysis, we measure Hospital Bed utilization as the average of the percentage of beds that are being utilized in hospitals in a given state.")
   r'''
         $$\hspace{60mm} Utilization = \frac{\#Occupied\ beds}{\#Available\ beds}$$
    '''
   st.markdown("Let us now get an overview of how the Hospital bed utilization varied across states for the duration of the pandemic.")


def conclusion_hospital_utilization():
    text = "We see that over time the bed utlization in hospitals has increased as indicated by the change in " \
           "color gradient from <span style='font-family:sans-serif; color:yellowgreen;'>yellowish-green</span> to " \
           "<span style='font-family:sans-serif; color:#953553;'>reddish-purple</span>"
    st.markdown(text, unsafe_allow_html=True)
    text = "It is also seen that as the number of cases (indicated by the size of the circles) increases, the utilization" \
           " moves towards the upper end. This tells us that there were some degree of patients infected with Covid, " \
           "that were seeking care at hospitals. We can also see this displayed in the dashboard above from the <b>Hospital bed utilization COVID patients</b> metric. " \
           "<br> It is imperative that hospitals be able to provide care to infected individuals during a future pandemic. " \
           "<br> We also see that the number of available Hospital beds increased by significant numbers as the pandemic progressed and the number of cases increased." \
           " This indicates a high degree of pressure on the medical sector to procure large number of beds quickly due to large increase in the number of COVID cases. " \
           "<br><br>But, were we able to procure beds <i>quickly</i> enough? Let us now take a deeper dive to find out more about this. <br> "
    st.markdown(text, unsafe_allow_html=True)


def conclusion_access_to_vaccination_medication():
    text = "The medicine facilities are locations of publicly available COVID-19 Therapeutics that require prescription. " \
           "From the map, we see that the Eastern states contain more number of medical facilities than the Western states, while the Central states have a much lesser density of these facilities. However, " \
           "the population of the east is almost double that of the west [ADD REFERENCE], explaining the higher number of facilities, but it does not proportionally account for the lesser number of facilities in Central states. " \
           "Across all states, we can also see that there are more Medicine/Therapeutic facilities than Vaccination centers. The " \
           "vaccination centers seem to be concentrated in major cities. One can argue that this non-uniform spread of facilities, " \
           "leading to difficulties for some citizens to reach these facilities, can be a part of the reason that " \
           "the rate of vaccination in the US was comparatively lower [ADD REFERENCE] than other countries. <br><br>"

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

    text = "Vaccination sites need to be acccessible to the public for a successful rollout. On analyzing the maximum average travel" \
           "time to the nearest vacciation sites around the country, it is seen that driving to the vaccination site is the quickest way, " \
           "followed by walking and then public transit (Odd!). These numbers reflect the average maximum time across the US that one would have to " \
           "travel to reach a vaccination site."
    st.markdown(text, unsafe_allow_html=True)


def conclusion_utilization_shortage():
    st.markdown("<p style='font-family:Courier New, monospace; font-size:14px'>Feel free to select an interval on the graph on the left <br> and slide across to get a more focused view of the graph on the right! </p> <br><br>", unsafe_allow_html=True)
    text = "From the graph on the left we see that during the pandemic there is more variation in the utilization of ICU beds, " \
           "whereas the in-patient beds seem to be relatively around the same level as it was  before. One can argue that it looks like a majority of COVID-19 affected patients" \
           " did not require to be admitted. Only cases where the individual suffers from other co-morbidities were more likely" \
           " required to be admitted, but they required ICU beds. This can lead us to the conclusion that for a similar future pandemic, one must place emphasis on procuring ICU beds and not general beds. " \
           "However, if we take a look at the dashboard above again, we see that the number of available beds has increased significantly as the pandemic progressed! " \
           "Therefore the relative stable level of In-patient bed utilization is due the fact that hospitals were  able to quickly procure a large number of <i>in-patient</i> beds to meet their demand. " \
           "The same however cannot be said for the ICU beds. ICU beds are very complex mechanisms that cannot be quickly procured with the current state of the medical infrastructure." \
            " But if we look closely, we can see that across a majority of the states, as soon as the ICU bed utilization crosses the <b>~75%</b> barrier, the number of deaths see a sharp incline. " \
           "Therefore it is of utmost importance to have pre-defined strategies in place that allow hospitilizations to quickly increase the ICU bed availability, before it crosses the 75% barrier, in the event of a  future pandemic. <br><br>" \
           "Another interesting observation is the relation between staff shortages and deaths. As we see more number of hospitals reporting" \
           " shortage of staff (the points becoming more <span style='font-family:sans-serif; color:rgba(173, 18, 18, 0.8);'>reddish</span>), we shortly see a sharp incline in the deaths. This shows that is of equal importance to also have sufficient availability of medical staff" \
           " as well in the event of a future pandemic. This is something that needs to be planned out carefully as you cannot simply 'procure' more medical staff in a short time!  "
    st.markdown(text, unsafe_allow_html=True)


def medical_infra_intro():
    st.header("How did the Medical Infrastructure of the US cope with the COVID-19 pandemic?")
    text = "Through our experiences with the COVID-19 pandemic, we should pay attention to the " \
           "overall capacity of the nation’s public health system as it protects and promotes the health " \
           "of all people in all our communities. " \
           "Public health infrastructure enables every level of government to prevent disease, promote health, prepare " \
           "for and respond to both emergency situations and ongoing challenges. Health departments also play a vital role in " \
           "educating the public about unexpected infectious disease threats as well as evidence-based interventions for " \
           "mitigation. <br>" \
           "We should not wait for the next pandemic to make us realize the strategic importance of public health agencies and the " \
           "critical role they play in protecting us. " \
           "Through a set of interesting visualizations and statistics, we explore how the medical infrastructure coped with the COVID-19 pandemic" \
           " and we attempt to gain insights regarding possible strategies that can be adopted in the event of a future pandemic. "
    st.markdown(text, unsafe_allow_html=True)


def medical_map_dashboard_vis(covid_data, df_hospital, states):

    describe_hospital_utilization()

    date_slider = st.slider('Silde the Date to see how the Hospital bed utilization and realated parameters vary with time',
                            min(df_hospital['date']), max(df_hospital['date']), min(df_hospital['date']),
                            step=timedelta(days=1), help="Slide over to see different dates")

    col1, col2, col3 = st.columns([3, 1, 1])
    medical_state_vis(df_hospital, states, date_slider, col1)
    with col2:
        list_states = sorted(list(set(covid_data['state'])))
        ny_ind = list_states.index("NY")
        state = st.selectbox('Select a State to see metrics for the chosen date', list_states, index=ny_ind)
    build_metric(covid_data, state, date_slider, col2, col3)

    conclusion_hospital_utilization()

    return


def staff_shortage_and_bed_util_vis(covid_data):

    st.title("How did Hospital bed utilization and staff shortage vary with time?")

    list_states_cov = sorted(list(set(covid_data['state']).difference(set(['AS']))))
    ny_ind = list_states_cov.index("NY")
    state = st.selectbox('Select a State!', list_states_cov, index=ny_ind)

    df_shortage_vs_deaths = covid_data[covid_data["state"] == state]
    df_shortage_vs_deaths = df_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    df_staff = df_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                          "critical_staffing_shortage_today_yes": "# Hospitals - staff shortage"},)

    df_bed = get_df_bed_util(state, covid_data)

    selection = alt.selection_interval(encodings=["x"])

    df_bed_utilization_chart = alt.Chart(df_bed,
                                         title="Trend in Hospital bed utilization in " + state).mark_point(tooltip=True).encode(
        x=alt.X('Date:T', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        y=alt.Y('Value:Q', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        color=alt.condition(selection, 'Parameter:N', alt.value('lightgray'),
                            legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15, direction="horizontal",
                                          padding=15))
    ).properties(
        width=600,
        height=400
    )

    df_shortage_vs_deaths_chart = alt.Chart(df_staff,
                                            title="Graph of Daily deaths and hospitals with staff shortage in " + state).mark_point().encode(
        x=alt.X('Date:T', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        y=alt.Y('Deaths:Q', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
        color=alt.Color("# Hospitals - staff shortage:Q",
                        scale=alt.Scale(scheme='goldred'),
                        legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15, direction="horizontal",
                                          padding=15)),
        tooltip=alt.Tooltip(["Deaths", "# Hospitals - staff shortage"])
    ).properties(
        width=600,
        height=400
    )

    final_chart = alt.hconcat(df_bed_utilization_chart.add_selection(selection),
                              df_shortage_vs_deaths_chart.transform_filter(selection),
                              config=alt.Config(title=alt.TitleConfig(fontSize=16, subtitlePadding=40)))


    st.write(final_chart)
    conclusion_utilization_shortage()

    return

def conclusion_testing_results():

    text = "It is clear that during the peaks of COVID, the number of test results returned is significantly lower than the number of samples taken, indicating" \
           " that the testing facilities were put under immense pressure by the pandemic. While most of the states were initially able to keep up with the testing demands," \
           " almost all the states could not handle the testing demands during the the last peak (Jan - Apr 2022).  This is" \
           " another crucial dimension where the medical infrastructure should be scaled up. It is equally important to have enough" \
           " labs that can process all the test samples and return their results within a finite amount of time. Timely results will" \
           " help curb the spread of infection as infected individuals can be alerted to stay quarantined and prevent the spread further. <br><br> " \

    st.markdown(text, unsafe_allow_html=True)


def covid_test_vis(df_test):

    st.title("Are all covid test sample results returned in a reasonable amount of time?")
    list_states = sorted(list(set(df_test['state'])))
    ny_ind = list_states.index("NY")
    state = st.selectbox('Select a State', list_states , index=ny_ind)
    testing_and_results_chart(df_test, state)
    conclusion_testing_results()
    return


def vac_and_med_loc_vis(df_medicine_vaccination_facility):

    st.title("How are the vaccination and Medicine facilities spread across the country?")

    text = "<p style='font-size: 30px;'><span style='font-family:sans-serif; color:rgba(34, 200, 48, 2);'>Vaccination </span> &" \
           "<span style='font-family:sans-serif; color:rgba(180, 0, 200, 90);'> Medicine </span>facilities</p>"

    st.markdown(text, unsafe_allow_html=True)

    df_med, df_vac = df_medicine_vaccination_facility
    us_map_vis(df_med, df_vac)

    return

def intro_model_plot():
    st.markdown(" Now that we have explored the data, let us see if we can build a Machine Learning model that can help us to predict the COVID cases in the future! ")
    st.title("COVID-19 Forecasting")
    text = "Forecasts of COVID-19 cases will help inform public health decision making by projecting " \
           "the likely impact of the pandemic in the coming weeks. Employing forecasting models gives us" \
           " an intuition on what to expect in the near future." \
           " We have explored forecasting the number of cases based on historical information using a back-testing forecasting" \
           " model [ADD REFERENCE]. We make use of the following metrics to evaluate the forecasts made by the model: " \
           "<ul>" \
           "<li>Mean Absolute Error (MAE):  Measures the average of all absolute errors. " \
           "The absolute average distance between the real data and the forecasted data, " \
           "but it fails to punish large errors in prediction.</li>" \
           "<li>Mean Square Error (MSE): Measures the average of the squares of the errors. " \
           "The average squared difference between the forecasted values and the actual value. " \
           "Since the error is being squared, even a single occurnec of a large prediction error will be heavily penalized." \
           "</li>" \
           "</ul>"
    st.write(text, unsafe_allow_html=True)


def conclusion_model_plot_7():
    text = "This model uses the covid cases of the past 90 days to forecast the number of cases 7 days from now." \
           " From the graph above we see that even a simple model that only considers historical case data (and no other feature) " \
           "is able to perform " \
           "decently in forecasting the cases for a week from the current day as noted by the close proximity of the" \
           " actual and predicted curves except for the last peak region (~ Jan - March) where there is a lag. " \
           "This mismatch in values across these dates is what contributes to the high large value of the " \
           "MSE metric as opposed to MAE. " \
           "This shows that Modelling techniques like Forecasting can be an ally to the government in making informed decisions. " \
           "However, forcasting for 7 days in the future will mainly be beneficial for procuring essentials in a short " \
           "term such as" \
           "food and water but it is too short a duration for expanding essentials such as hospital beds etc"
    st.markdown(text, unsafe_allow_html=True)


def intro_model_plot_30():
    text = "We now try extending this by attempting to forecast the cases 30 days in the future using the same historical case data of 90 days"
    st.markdown(text, unsafe_allow_html=True)


def conclusion_model_plot_30():
    text = "As seen form the forecast above, we see that the forcasted values are of much lesser quality (flat lines) and " \
           "MAE and MSE increase significantly. This indicates that the predicting cases a month into the " \
           "future with a simple historical case-based model is difficult. " \
           "This could be overcome by using a more sophisticated model and the government should  invest resources to explore " \
           "this avenue further by " \
           "using features such as mobility, regulations in place, deaths, hospitalizations etc. to develop a better performing Forecasting model. "
    st.markdown(text, unsafe_allow_html=True)


def intro_model_feature_importance():
    st.header("Importance of Lag features in the 7-day forecasting model")
    text = "The plot below shows us the relative importance of the lag features in making the forecast where " \
           "<br> <b>lag_7</b> is the feature representing the number of cases from 7 days ago."
    st.markdown(text, unsafe_allow_html=True)

def conclusion_model_feature_importance():
    text = "We see that on average across states, lag_1 and lag_7 appear to the most important features. This tells us that" \
           " the day of the week infiuences the number of cases since it is usually the case that people go to public places " \
           "during the weekends and home/office during the weekdays. This pattern can play a role in determining the number of" \
           " cases. The values of the previous day will also influence the overall direction of the change in trend."

    st.markdown(text, unsafe_allow_html=True)


def model_vis(df_values, df_features, df_values_thirty):

    intro_model_plot()
    model_plot_7(df_values)
    conclusion_model_plot_7()
    intro_model_plot_30()
    model_plot_30(df_values_thirty)
    conclusion_model_plot_30()
    intro_model_feature_importance()
    features_plot(df_features)
    conclusion_model_feature_importance()
    return


def model_plot_7(df_values):
    states = list(sorted(df_values.keys()))

    list_states = states
    ny_ind = list_states.index("NY")
    selected_state = st.selectbox('Select a State: ', list_states, index=ny_ind)
    df = df_values[selected_state]

    mae = int(sum(df['diff'])/len(df))
    val_mae = f"{mae:,}"
    mse = int(sum(df['diff_sq'])/len(df))
    val_mse = f"{mse:,}"
    col1, col2, col3 = st.columns(3)

    with col3:

        mae_text = f"""
        <span style='font-size: 30px;font-family:Monaco, monospace;'>MAE:</span><b style='font-size: 30px;font-family:Monaco, monospace; color:#41c0d1;'>{val_mae}</b>
        """
        st.write(mae_text, unsafe_allow_html=True)

        mse_text = f"""
                <span style='font-size: 30px;font-family:Monaco, monospace;'>MSE:</span><b style='font-size: 30px;font-family:Monaco, monospace; color:#ebb75e;'>{val_mse}</b>
                """
        st.write(mse_text, unsafe_allow_html=True)


    with col1:
        df = df[['Date', 'Actual', 'Predicted']]
        data = df.melt("Date", var_name='Type', value_name='Cases')
        chart = alt.Chart(data, title="Actual vs Predicted cases for a 7 day step size for " + selected_state + " state") \
            .mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
            y=alt.Y('Cases:Q', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
            color=alt.Color('Type:N', scale=alt.Scale(scheme='set2'),
                            legend=alt.Legend(orient="right", titleFontSize=15, labelFontSize=15)),
            tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip('Type:N', title="Type"),
                     alt.Tooltip('Cases:Q', title="Cases")]
        ).interactive().properties(
            width=800,
            height=400
        ).configure_title(fontSize=16)
        st.write(chart)
    return


def model_plot_30(df_values):

    states = sorted(list(df_values.keys()))
    # Edit below to select dynamically

    list_states = states
    ny_ind = list_states.index("NY")
    selected_state = st.selectbox('Select a State: ', list_states, index=ny_ind)
    df = df_values[selected_state]

    mae = int(sum(df['diff']) / len(df))
    val_mae = f"{mae:,}"
    mse = int(sum(df['diff_sq']) / len(df))
    val_mse = f"{mse:,}"

    col1, col2, col3 = st.columns(3)

    with col3:
        mae_text = f"""
                <span style='font-size: 30px;font-family:Monaco, monospace;'>MAE:</span><b style='font-size: 30px;font-family:Monaco, monospace; color:#41c0d1;'>{val_mae}</b>
                """
        st.write(mae_text, unsafe_allow_html=True)

        mse_text = f"""
                        <span style='font-size: 30px;font-family:Monaco, monospace;'>MSE:</span><b style='font-size: 30px;font-family:Monaco, monospace; color:#ebb75e;'>{val_mse}</b>
                        """
        st.write(mse_text, unsafe_allow_html=True)

    with col1:
        df = df[['Date', 'Actual', 'Predicted']]
        data = df.melt("Date", var_name='Type', value_name='Cases')
        chart = alt.Chart(data, title="Actual vs Predicted cases for a 30 day step size for " + selected_state + " state") \
            .mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
            y=alt.Y('Cases:Q', axis=alt.Axis(labelAngle=0, ticks=True, titleFontSize=16, titlePadding=15)),
            color=alt.Color('Type:N', scale=alt.Scale(scheme='set2'),
                            legend=alt.Legend(orient="right", titleFontSize=15, labelFontSize=15)),
            tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip('Type:N', title="Type"),
                     alt.Tooltip('Cases:Q', title="Cases")]
        ).interactive().properties(
            width=800,
            height=400
        ).configure_title(fontSize=16)
        st.write(chart)
    return


def features_plot(df_features):

    states = sorted(list(df_features.keys()))
    list_states = states
    ny_ind = list_states.index("AK")
    selected_state = st.selectbox('Select a State to show the Feature weights: ', list_states, index=ny_ind)
    data = df_features[selected_state]

    top10_lag = sorted(data, key=lambda k: data[k], reverse=True)[:10]
    top10_val = [data[i] for i in top10_lag]

    source = pd.DataFrame({
        'Lag': top10_lag,
        'Importance': top10_val
    })

    feat_imp_chart = alt.Chart(source, title="Feature importance for prediction").mark_bar().encode(
        x=alt.X('Lag:N', sort='-y', axis=alt.Axis(labelAngle=0, labelFontSize=16, ticks=True, titleFontSize=16, titlePadding=15)),
        y=alt.Y('Importance:Q', axis=alt.Axis(labelAngle=0, labelFontSize=16, ticks=True, titleFontSize=16, titlePadding=15)),
    ).interactive().properties(
            width=800,
            height=400
    ).configure_title(fontSize=16).configure_mark(
    opacity=0.8,
    color='#ebb434')

    st.write(feat_imp_chart)
    # https://www.cienciadedatos.net/documentos/py27-time-series-forecasting-python-scikitlearn.html
    # Lag_7 means that last week same day. So day of the week matters?
    return

def MedicalVis():

    covid_data, baseline_dashboard_data = read_dashboard_files()
    df_hospital, states = read_files_medical_state_vis()
    df_medicine_vaccination_facility = read_medicine_facility_files()
    df_test = read_testing_files()
    df_medical_fac_loc = get_four_state_map_files(df_medicine_vaccination_facility)
    df_values, df_features, df_values_thirty = read_files_model()

    medical_infra_intro()
    medical_map_dashboard_vis(covid_data, df_hospital, states)
    staff_shortage_and_bed_util_vis(covid_data)
    covid_test_vis(df_test)
    vac_and_med_loc_vis(df_medical_fac_loc)
    conclusion_access_to_vaccination_medication()
    describe_access_to_vaccination_sites()
    model_vis(df_values, df_features, df_values_thirty)

