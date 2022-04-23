from datetime import timedelta, datetime
import streamlit as st

st.set_page_config(layout="wide", page_icon=":shark:")
import pandas as pd
from datetime import datetime
import altair as alt

DATA_URL = 'data/dashboard_metrics.csv'
BASELINE_URL = 'data/baseline_dashboard_metrics.csv'


def load_data(url):
    data = pd.read_csv(url)
    return data


def build_metric(state, date_slider, baseline_daashboard_data):
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)

    state_info = covid_data[covid_data["state"] == state]
    state_info_date = state_info[state_info["date"] == date_slider]
    baseline_value = baseline_daashboard_data[baseline_daashboard_data["state"] == state]
    prev_beds = 0
    if state_info_date.empty or state_info.empty:
        st.header("No data available :'(")

    else:
        cases = state_info_date["new_confirmed"]
        deceased = state_info_date["new_deceased"]

        total_beds = state_info_date["inpatient_beds"].values[0]
        baseline_total_beds = baseline_value["inpatient_beds"].values[0]
        change_total_beds = total_beds - prev_beds

        beds_utilization = state_info_date["inpatient_beds_utilization"].values[0]
        baseline_beds_utilization = baseline_value["inpatient_beds_utilization"].values[0]
        percentage_change_beds_utilization = ((beds_utilization + 1) - (baseline_beds_utilization + 1)) * 100 / (
                baseline_beds_utilization + 1)

        beds_covid = state_info_date["percent_of_inpatients_with_covid"].values[0]

        icu_utilization = state_info_date["adult_icu_bed_utilization"].values[0]
        baseline_icu_utilization = baseline_value["adult_icu_bed_utilization"].values[0]
        percentage_change_icu_utilization = ((icu_utilization + 1) - (baseline_icu_utilization + 1)) * 100 / (
                baseline_icu_utilization + 1)

        icu_covid_utilization = state_info_date["adult_icu_bed_covid_utilization"].values[0]

        staff_shortage = state_info_date["critical_staffing_shortage_today_yes"].values[0]
        baseline_staff_shortage = baseline_value["critical_staffing_shortage_today_yes"].values[0]
        percentage_change_staff_shortage = int(staff_shortage - baseline_staff_shortage)

        col1.metric("Cases today", round(cases, 2), None)
        col2.metric("Deaths today", deceased, None)

        col3.metric("Hospital beds utilization", round(beds_utilization, 2),
                    str(round(percentage_change_beds_utilization, 2)) + " %", delta_color="inverse")
        col4.metric("Hospital beds utilization COVID patients", round(beds_covid, 2), None, delta_color="inverse")
        col5.metric("ICU bed utilization", round(icu_utilization, 2), percentage_change_icu_utilization,
                    delta_color="inverse")
        col6.metric("ICU bed utilization COVID patients", round(icu_covid_utilization, 2), None, delta_color="inverse")
        col7.metric("Number of hospitals with staff shortage", staff_shortage, percentage_change_staff_shortage,
                    delta_color="inverse")
        col8.metric("Total beds", total_beds, str(int(change_total_beds)), delta_color="inverse")


covid_data = load_data(DATA_URL)
baseline_daashboard_data = load_data(BASELINE_URL)
covid_data["date"] = covid_data["date"].map(
    lambda row: datetime.strptime(row, "%Y-%m-%d").date())
state = st.selectbox('Select a State', set(covid_data['state']))
date_slider = st.slider('Silde the Date to see how these parameters vary with time', min(covid_data['date']),
                        max(covid_data['date']), min(covid_data['date']),
                        step=timedelta(days=10), help="Slide over to see different dates")
build_metric(state, date_slider, baseline_daashboard_data)



################### NEW YORK ######################

col_utilization_ny, deaths_ny = st.columns(2)

# in-patient beds utilization vs icu-beds utilization


new_york_df = covid_data[covid_data["state"] == "NY"]
new_york_df = new_york_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
new_york_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
new_york_df = new_york_df.melt("Date", var_name='Parameter', value_name='Value')

# New York stacked chart

new_york_stacked = covid_data[covid_data["state"] == "NY"]

new_york_stacked_normal = new_york_stacked[
    ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
new_york_stacked_normal["Available"] = new_york_stacked_normal["inpatient_beds"] - \
                                       new_york_stacked["inpatient_beds_used"] - \
                                       new_york_stacked["inpatient_beds_used_covid"]

new_york_stacked_normal["inpatient_beds_used"] = new_york_stacked_normal["inpatient_beds_used"] / \
                                                 new_york_stacked_normal["inpatient_beds"]
new_york_stacked_normal["inpatient_beds_used_covid"] = new_york_stacked_normal["inpatient_beds_used_covid"] / \
                                                       new_york_stacked_normal["inpatient_beds"]
new_york_stacked_normal["Available"] = new_york_stacked_normal["Available"] / \
                                       new_york_stacked_normal["inpatient_beds"]

new_york_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

new_york_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
new_york_stacked_normal = new_york_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

new_york_stacked_normal["Type"] = "Normal"
new_york_stacked_normal = new_york_stacked_normal.fillna(0)
# st.write(new_york_stacked_normal)

new_york_stacked_icu = new_york_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                         "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                         "total_staffed_adult_icu_beds"]]
new_york_stacked_icu["Available"] = new_york_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    new_york_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] = new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          new_york_stacked_icu["total_staffed_adult_icu_beds"]
new_york_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = new_york_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   new_york_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
new_york_stacked_icu["Available"] = new_york_stacked_icu["Available"] / \
                                    new_york_stacked_icu["total_staffed_adult_icu_beds"]

new_york_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

new_york_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
new_york_stacked_icu = new_york_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

new_york_stacked_icu["Type"] = "ICU"
new_york_stacked_icu = new_york_stacked_icu.fillna(0)
# st.write(new_york_stacked_icu)

new_york_stacked_data = new_york_stacked_normal.append(new_york_stacked_icu, ignore_index=True)

ny_brush = alt.selection(type='interval', encodings=["x"])
ny_bed_utilization_chart = alt.Chart(new_york_df, title= "Trend in Hospital bed utilization in New York").mark_line().encode(
    x='Date:T',
    y='Value:Q',
    color=alt.Color("Parameter", scale=alt.Scale(scheme='set1'), legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15)),
    strokeDash='Parameter:N',
).properties(
    width=650,
    height=400
).add_selection(
    ny_brush
).configure_title(fontSize=16)
col_utilization_ny.write(ny_bed_utilization_chart)

# New York deaths chart
new_york_deaths = covid_data[covid_data["state"] == "NY"]
new_york_deaths = new_york_deaths[["date", "new_deceased"]]
new_york_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                            inplace=True)
new_york_deaths_chart = alt.Chart(new_york_deaths, title="Daily Deaths in New York over time").mark_line(color="#d147ed").encode(
    alt.X('Date:T', axis=alt.Axis(title='Date')),
    alt.Y('Deaths:Q')
).interactive().properties(
    width=500,
    height=400
).configure_title(fontSize=16)
deaths_ny.write(new_york_deaths_chart)

# Testing Vs Results

new_york_test_results = pd.read_csv("data/testing_results.csv")
new_york_test_results = new_york_test_results[new_york_test_results["state"] == "NY"]
new_york_test_results = new_york_test_results[["date", "new_tested", "new_results_reported"]]
new_york_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
new_york_test_results = new_york_test_results.melt("Date", var_name='Parameter', value_name='Count')
new_york_test_results_chart = alt.Chart(new_york_test_results, title = "Graph of Testing Vs Result reports for New York").mark_line().encode(
    x='Date:T',
    y='Count:Q',
    color=alt.Color("Parameter", scale=alt.Scale(scheme='set2'), legend=alt.Legend(orient="left", titleFontSize=15, labelFontSize=15))
).interactive().properties(
    width=1000,
    height=400
).configure_title(fontSize=16)

st.write(new_york_test_results_chart)

# st.altair_chart(ny_bed_utilization_chart | new_york_deaths_chart)

new_york_stacked_chart = alt.Chart(new_york_stacked_data).mark_bar().encode(
    x='count()',
    y='Type:N',
    color='Parameter:N'
).transform_filter(
    ny_brush
).properties(
    width=550,
).configure_title(fontSize=16)
st.write(new_york_stacked_chart)

# Shortage Vs Deaths

# Decide whether to connect it
# For all visualization, cut off everything until may 2020
# Fix color scheme

new_york_shortage_vs_deaths = covid_data[covid_data["state"] == "NY"]
new_york_shortage_vs_deaths = new_york_shortage_vs_deaths[
    ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
new_york_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                     "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                            inplace=True)
new_york_shortage_vs_deaths_chart = alt.Chart(new_york_shortage_vs_deaths,
                                              title="Graph of Daily deaths and hospitals with staff shortage (NY)").mark_point().encode(
    x='Date:T',
    y='Deaths:Q',
    color=alt.Color("# Hospitals with shortage:Q",
                    scale=alt.Scale(scheme='goldred'))
).interactive().properties(
    width=1000,
    height=400
)
st.write(new_york_shortage_vs_deaths_chart)




################### UTAH ######################

# in-patient beds utilization vs icu-beds utilization


utah_df = covid_data[covid_data["state"] == "UT"]
utah_df = utah_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
utah_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
utah_df = utah_df.melt("Date", var_name='Parameter', value_name='Value')

# Utah stacked chart

utah_stacked = covid_data[covid_data["state"] == "UT"]

utah_stacked_normal = utah_stacked[
    ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
utah_stacked_normal["Available"] = utah_stacked_normal["inpatient_beds"] - \
                                       utah_stacked["inpatient_beds_used"] - \
                                       utah_stacked["inpatient_beds_used_covid"]

utah_stacked_normal["inpatient_beds_used"] = utah_stacked_normal["inpatient_beds_used"] / \
                                                 utah_stacked_normal["inpatient_beds"]
utah_stacked_normal["inpatient_beds_used_covid"] = utah_stacked_normal["inpatient_beds_used_covid"] / \
                                                       utah_stacked_normal["inpatient_beds"]
utah_stacked_normal["Available"] = utah_stacked_normal["Available"] / \
                                       utah_stacked_normal["inpatient_beds"]

utah_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

utah_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
utah_stacked_normal = utah_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

utah_stacked_normal["Type"] = "Normal"
utah_stacked_normal = utah_stacked_normal.fillna(0)
# st.write(new_york_stacked_normal)

utah_stacked_icu = utah_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                         "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                         "total_staffed_adult_icu_beds"]]
utah_stacked_icu["Available"] = utah_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    utah_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    utah_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

utah_stacked_icu["staffed_adult_icu_bed_occupancy"] = utah_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          utah_stacked_icu["total_staffed_adult_icu_beds"]
utah_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = utah_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   utah_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
utah_stacked_icu["Available"] = utah_stacked_icu["Available"] / \
                                    utah_stacked_icu["total_staffed_adult_icu_beds"]

utah_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

utah_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
utah_stacked_icu = utah_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

utah_stacked_icu["Type"] = "ICU"
utah_stacked_icu = utah_stacked_icu.fillna(0)
# st.write(new_york_stacked_icu)

utah_stacked_data = utah_stacked_normal.append(new_york_stacked_icu, ignore_index=True)

utah_brush = alt.selection(type='interval', encodings=["x"])
utah_bed_utilization_chart = alt.Chart(utah_df, title= "Trend in Hospital bed utilization in Utah").mark_line().encode(
    x='Date:T',
    y='Value:Q',
    color='Parameter:N',
    strokeDash='Parameter:N',
).properties(
    width=775,
    height=400
).add_selection(
    utah_brush
)
st.write(utah_bed_utilization_chart)

# Utah deaths chart
utah_deaths = covid_data[covid_data["state"] == "UT"]
utah_deaths = utah_deaths[["date", "new_deceased"]]
utah_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                            inplace=True)
utah_deaths_chart = alt.Chart(utah_deaths, title="Daily Deaths in Utah over time").mark_line().encode(
    alt.X('Date:T', axis=alt.Axis(title='Date')),
    alt.Y('Deaths:Q')
).interactive().properties(
    width=500,
    height=400
)
st.write(utah_deaths_chart)

utah_stacked_chart = alt.Chart(utah_stacked_data).mark_bar().encode(
    x='count()',
    y='Type:N',
    color='Parameter:N'
).transform_filter(
    utah_brush
).properties(
    width=550,
)
st.write(utah_stacked_chart)

# Shortage Vs Deaths

# Decide whether to connect it
# For all visualization, cut off everything until may 2020
# Fix color scheme
utah_shortage_vs_deaths = covid_data[covid_data["state"] == "UT"]
utah_shortage_vs_deaths = utah_shortage_vs_deaths[
    ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
utah_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                     "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                            inplace=True)
utah_shortage_vs_deaths_chart = alt.Chart(utah_shortage_vs_deaths, title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
    x='Date:T',
    y='Deaths:Q',
    color=alt.Color("# Hospitals with shortage:Q",
                    scale=alt.Scale(scheme='goldred'))
).interactive().properties(
    width=1000,
    height=400
)
st.write(utah_shortage_vs_deaths_chart)

# Testing Vs Results

utah_test_results = pd.read_csv("data/testing_results.csv")
utah_test_results = utah_test_results[utah_test_results["state"] == "UT"]
utah_test_results = utah_test_results[["date", "new_tested", "new_results_reported"]]
utah_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
utah_test_results = utah_test_results.melt("Date", var_name='Parameter', value_name='Count')
utah_test_results_chart = alt.Chart(utah_test_results, title = "Graph of Testing Vs Result reports for Utah").mark_line().encode(
    x='Date:T',
    y='Count:Q',
    color='Parameter:N'
).interactive().properties(
    width=1000,
    height=400
)

st.write(utah_test_results_chart)


################# OHIO #######################

# in-patient beds utilization vs icu-beds utilization


ohio_df = covid_data[covid_data["state"] == "CA"]
ohio_df = ohio_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
ohio_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
ohio_df = ohio_df.melt("Date", var_name='Parameter', value_name='Value')

# ohio stacked chart

ohio_stacked = covid_data[covid_data["state"] == "CA"]

ohio_stacked_normal = ohio_stacked[
    ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
ohio_stacked_normal["Available"] = ohio_stacked_normal["inpatient_beds"] - \
                                       ohio_stacked["inpatient_beds_used"] - \
                                       ohio_stacked["inpatient_beds_used_covid"]

ohio_stacked_normal["inpatient_beds_used"] = ohio_stacked_normal["inpatient_beds_used"] / \
                                                 ohio_stacked_normal["inpatient_beds"]
ohio_stacked_normal["inpatient_beds_used_covid"] = ohio_stacked_normal["inpatient_beds_used_covid"] / \
                                                       ohio_stacked_normal["inpatient_beds"]
ohio_stacked_normal["Available"] = ohio_stacked_normal["Available"] / \
                                       ohio_stacked_normal["inpatient_beds"]

ohio_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

ohio_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
ohio_stacked_normal = ohio_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

ohio_stacked_normal["Type"] = "Normal"
ohio_stacked_normal = ohio_stacked_normal.fillna(0)
# st.write(new_york_stacked_normal)

ohio_stacked_icu = ohio_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                         "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                         "total_staffed_adult_icu_beds"]]
ohio_stacked_icu["Available"] = ohio_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    ohio_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] = ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          ohio_stacked_icu["total_staffed_adult_icu_beds"]
ohio_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = ohio_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   ohio_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
ohio_stacked_icu["Available"] = ohio_stacked_icu["Available"] / \
                                    ohio_stacked_icu["total_staffed_adult_icu_beds"]

ohio_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

ohio_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
ohio_stacked_icu = ohio_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

ohio_stacked_icu["Type"] = "ICU"
ohio_stacked_icu = ohio_stacked_icu.fillna(0)
# st.write(new_york_stacked_icu)

ohio_stacked_data = ohio_stacked_normal.append(new_york_stacked_icu, ignore_index=True)

ohio_brush = alt.selection(type='interval', encodings=["x"])
ohio_bed_utilization_chart = alt.Chart(ohio_df, title= "Trend in Hospital bed utilization in ohio").mark_line().encode(
    x='Date:T',
    y='Value:Q',
    color='Parameter:N',
    strokeDash='Parameter:N',
).properties(
    width=775,
    height=400
).add_selection(
    ohio_brush
)
st.write(ohio_bed_utilization_chart)

# ohio deaths chart
ohio_deaths = covid_data[covid_data["state"] == "CA"]
ohio_deaths = ohio_deaths[["date", "new_deceased"]]
ohio_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                            inplace=True)
ohio_deaths_chart = alt.Chart(ohio_deaths, title="Daily Deaths in ohio over time").mark_line().encode(
    alt.X('Date:T', axis=alt.Axis(title='Date')),
    alt.Y('Deaths:Q')
).interactive().properties(
    width=500,
    height=400
)
st.write(ohio_deaths_chart)

ohio_stacked_chart = alt.Chart(ohio_stacked_data).mark_bar().encode(
    x='count()',
    y='Type:N',
    color='Parameter:N'
).transform_filter(
    ohio_brush
).properties(
    width=550,
)
st.write(ohio_stacked_chart)

# Shortage Vs Deaths

# Decide whether to connect it
# For all visualization, cut off everything until may 2020
# Fix color scheme
ohio_shortage_vs_deaths = covid_data[covid_data["state"] == "CA"]
ohio_shortage_vs_deaths = ohio_shortage_vs_deaths[
    ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
ohio_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                     "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                            inplace=True)
ohio_shortage_vs_deaths_chart = alt.Chart(ohio_shortage_vs_deaths, title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
    x='Date:T',
    y='Deaths:Q',
    color=alt.Color("# Hospitals with shortage:Q",
                    scale=alt.Scale(scheme='goldred'))
).interactive().properties(
    width=1000,
    height=400
)
st.write(ohio_shortage_vs_deaths_chart)

# Testing Vs Results

ohio_test_results = pd.read_csv("data/testing_results.csv")
ohio_test_results = ohio_test_results[ohio_test_results["state"] == "CA"]
ohio_test_results = ohio_test_results[["date", "new_tested", "new_results_reported"]]
ohio_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
ohio_test_results = ohio_test_results.melt("Date", var_name='Parameter', value_name='Count')
ohio_test_results_chart = alt.Chart(ohio_test_results, title = "Graph of Testing Vs Result reports for ohio").mark_line().encode(
    x='Date:T',
    y='Count:Q',
    color='Parameter:N'
).interactive().properties(
    width=1000,
    height=400
)

st.write(ohio_test_results_chart)



############### CALIFORNIA ################
# in-patient beds utilization vs icu-beds utilization


california_df = covid_data[covid_data["state"] == "CA"]
california_df = california_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
california_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
california_df = california_df.melt("Date", var_name='Parameter', value_name='Value')

# california stacked chart

california_stacked = covid_data[covid_data["state"] == "CA"]

california_stacked_normal = california_stacked[
    ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
california_stacked_normal["Available"] = california_stacked_normal["inpatient_beds"] - \
                                       california_stacked["inpatient_beds_used"] - \
                                       california_stacked["inpatient_beds_used_covid"]

california_stacked_normal["inpatient_beds_used"] = california_stacked_normal["inpatient_beds_used"] / \
                                                 california_stacked_normal["inpatient_beds"]
california_stacked_normal["inpatient_beds_used_covid"] = california_stacked_normal["inpatient_beds_used_covid"] / \
                                                       california_stacked_normal["inpatient_beds"]
california_stacked_normal["Available"] = california_stacked_normal["Available"] / \
                                       california_stacked_normal["inpatient_beds"]

california_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

california_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
california_stacked_normal = california_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

california_stacked_normal["Type"] = "Normal"
california_stacked_normal = california_stacked_normal.fillna(0)
# st.write(new_york_stacked_normal)

california_stacked_icu = california_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                         "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                         "total_staffed_adult_icu_beds"]]
california_stacked_icu["Available"] = california_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    california_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    california_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

california_stacked_icu["staffed_adult_icu_bed_occupancy"] = california_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          california_stacked_icu["total_staffed_adult_icu_beds"]
california_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = california_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   california_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
california_stacked_icu["Available"] = california_stacked_icu["Available"] / \
                                    california_stacked_icu["total_staffed_adult_icu_beds"]

california_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

california_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
california_stacked_icu = california_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

california_stacked_icu["Type"] = "ICU"
california_stacked_icu = california_stacked_icu.fillna(0)
# st.write(new_york_stacked_icu)

california_stacked_data = california_stacked_normal.append(new_york_stacked_icu, ignore_index=True)

california_brush = alt.selection(type='interval', encodings=["x"])
california_bed_utilization_chart = alt.Chart(california_df, title= "Trend in Hospital bed utilization in california").mark_line().encode(
    x='Date:T',
    y='Value:Q',
    color='Parameter:N',
    strokeDash='Parameter:N',
).properties(
    width=775,
    height=400
).add_selection(
    california_brush
)
st.write(california_bed_utilization_chart)

# california deaths chart
california_deaths = covid_data[covid_data["state"] == "CA"]
california_deaths = california_deaths[["date", "new_deceased"]]
california_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                            inplace=True)
california_deaths_chart = alt.Chart(california_deaths, title="Daily Deaths in california over time").mark_line().encode(
    alt.X('Date:T', axis=alt.Axis(title='Date')),
    alt.Y('Deaths:Q')
).interactive().properties(
    width=500,
    height=400
)
st.write(california_deaths_chart)

california_stacked_chart = alt.Chart(california_stacked_data).mark_bar().encode(
    x='count()',
    y='Type:N',
    color='Parameter:N'
).transform_filter(
    california_brush
).properties(
    width=550,
)
st.write(california_stacked_chart)

# Shortage Vs Deaths

# Decide whether to connect it
# For all visualization, cut off everything until may 2020
# Fix color scheme
california_shortage_vs_deaths = covid_data[covid_data["state"] == "CA"]
california_shortage_vs_deaths = california_shortage_vs_deaths[
    ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
california_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                     "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                            inplace=True)
california_shortage_vs_deaths_chart = alt.Chart(california_shortage_vs_deaths, title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
    x='Date:T',
    y='Deaths:Q',
    color=alt.Color("# Hospitals with shortage:Q",
                    scale=alt.Scale(scheme='goldred'))
).interactive().properties(
    width=1000,
    height=400
)
st.write(california_shortage_vs_deaths_chart)

# Testing Vs Results

california_test_results = pd.read_csv("data/testing_results.csv")
california_test_results = california_test_results[california_test_results["state"] == "CA"]
california_test_results = california_test_results[["date", "new_tested", "new_results_reported"]]
california_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
california_test_results = california_test_results.melt("Date", var_name='Parameter', value_name='Count')
california_test_results_chart = alt.Chart(california_test_results, title = "Graph of Testing Vs Result reports for california").mark_line().encode(
    x='Date:T',
    y='Count:Q',
    color='Parameter:N'
).interactive().properties(
    width=1000,
    height=400
)

st.write(california_test_results_chart)





## ICU utilisation
st.write("https://www.nytimes.com/interactive/2020/us/covid-hospitals-near-you.html")

## Staff shortage
st.write("https://www.npr.org/sections/health-shots/2022/01/20/1074493907/the-nursing-home-staffing-crisis-right-now-is-like-nothing-weve-seen-before")

## Staff only are sick
st.write("https://www.theguardian.com/world/2022/jan/14/southern-us-hospitals-staff-shortages-record-covid-cases")

## Test turnaround time
st.write("https://www.cnbc.com/2020/08/15/forty-percent-of-us-covid-19-tests-come-back-too-late-to-be-clinically-meaningful-data-show.html")


def new_york_infrastructure_chart():
    col_utilization_ny, deaths_ny = st.columns(2)

    # in-patient beds utilization vs icu-beds utilization

    new_york_df = covid_data[covid_data["state"] == "NY"]
    new_york_df = new_york_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
    new_york_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                                "adult_icu_bed_utilization": "ICU beds utilization"},
                       inplace=True)
    new_york_df = new_york_df.melt("Date", var_name='Parameter', value_name='Value')

    # New York stacked chart

    new_york_stacked = covid_data[covid_data["state"] == "NY"]

    new_york_stacked_normal = new_york_stacked[
        ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
    new_york_stacked_normal["Available"] = new_york_stacked_normal["inpatient_beds"] - \
                                           new_york_stacked["inpatient_beds_used"] - \
                                           new_york_stacked["inpatient_beds_used_covid"]

    new_york_stacked_normal["inpatient_beds_used"] = new_york_stacked_normal["inpatient_beds_used"] / \
                                                     new_york_stacked_normal["inpatient_beds"]
    new_york_stacked_normal["inpatient_beds_used_covid"] = new_york_stacked_normal["inpatient_beds_used_covid"] / \
                                                           new_york_stacked_normal["inpatient_beds"]
    new_york_stacked_normal["Available"] = new_york_stacked_normal["Available"] / \
                                           new_york_stacked_normal["inpatient_beds"]

    new_york_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

    new_york_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                            "inpatient_beds_used_covid": "Covid",
                                            "Available": "Available"},
                                   inplace=True)
    new_york_stacked_normal = new_york_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

    new_york_stacked_normal["Type"] = "Normal"
    new_york_stacked_normal = new_york_stacked_normal.fillna(0)
    # st.write(new_york_stacked_normal)

    new_york_stacked_icu = new_york_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                             "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                             "total_staffed_adult_icu_beds"]]
    new_york_stacked_icu["Available"] = new_york_stacked_icu["total_staffed_adult_icu_beds"] - \
                                        new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                        new_york_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

    new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] = new_york_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                              new_york_stacked_icu["total_staffed_adult_icu_beds"]
    new_york_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = new_york_stacked_icu[
                                                                                           "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                       new_york_stacked_icu[
                                                                                           "total_staffed_adult_icu_beds"]
    new_york_stacked_icu["Available"] = new_york_stacked_icu["Available"] / \
                                        new_york_stacked_icu["total_staffed_adult_icu_beds"]

    new_york_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

    new_york_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                         "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                                inplace=True)
    new_york_stacked_icu = new_york_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

    new_york_stacked_icu["Type"] = "ICU"
    new_york_stacked_icu = new_york_stacked_icu.fillna(0)
    # st.write(new_york_stacked_icu)

    new_york_stacked_data = new_york_stacked_normal.append(new_york_stacked_icu, ignore_index=True)

    ny_brush = alt.selection(type='interval', encodings=["x"])
    ny_bed_utilization_chart = alt.Chart(new_york_df,
                                         title="Trend in Hospital bed utilization in New York").mark_line().encode(
        x='Date:T',
        y='Value:Q',
        color=alt.Color("Parameter", scale=alt.Scale(scheme='set1'),
                        legend=alt.Legend(orient="top", titleFontSize=15, labelFontSize=15)),
        strokeDash='Parameter:N',
    ).properties(
        width=650,
        height=400
    ).add_selection(
        ny_brush
    ).configure_title(fontSize=16)
    col_utilization_ny.write(ny_bed_utilization_chart)

    # New York deaths chart
    new_york_deaths = covid_data[covid_data["state"] == "NY"]
    new_york_deaths = new_york_deaths[["date", "new_deceased"]]
    new_york_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                           inplace=True)
    new_york_deaths_chart = alt.Chart(new_york_deaths, title="Daily Deaths in New York over time").mark_line(
        color="#d147ed").encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Deaths:Q')
    ).interactive().properties(
        width=500,
        height=400
    ).configure_title(fontSize=16)
    deaths_ny.write(new_york_deaths_chart)

    # Testing Vs Results

    new_york_test_results = pd.read_csv("data/testing_results.csv")
    new_york_test_results = new_york_test_results[new_york_test_results["state"] == "NY"]
    new_york_test_results = new_york_test_results[["date", "new_tested", "new_results_reported"]]
    new_york_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                          "new_results_reported": "# Results reported"},
                                 inplace=True)
    new_york_test_results = new_york_test_results.melt("Date", var_name='Parameter', value_name='Count')
    new_york_test_results_chart = alt.Chart(new_york_test_results,
                                            title="Graph of Testing Vs Result reports for New York").mark_line().encode(
        x='Date:T',
        y='Count:Q',
        color=alt.Color("Parameter", scale=alt.Scale(scheme='set2'),
                        legend=alt.Legend(orient="left", titleFontSize=15, labelFontSize=15))
    ).interactive().properties(
        width=1000,
        height=400
    ).configure_title(fontSize=16)

    st.write(new_york_test_results_chart)

    # st.altair_chart(ny_bed_utilization_chart | new_york_deaths_chart)

    new_york_stacked_chart = alt.Chart(new_york_stacked_data).mark_bar().encode(
        x='count()',
        y='Type:N',
        color='Parameter:N'
    ).transform_filter(
        ny_brush
    ).properties(
        width=550,
    ).configure_title(fontSize=16)
    st.write(new_york_stacked_chart)

    # Shortage Vs Deaths

    # Decide whether to connect it
    # For all visualization, cut off everything until may 2020
    # Fix color scheme

    new_york_shortage_vs_deaths = covid_data[covid_data["state"] == "NY"]
    new_york_shortage_vs_deaths = new_york_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    new_york_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                                "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                                       inplace=True)
    new_york_shortage_vs_deaths_chart = alt.Chart(new_york_shortage_vs_deaths,
                                                  title="Graph of Daily deaths and hospitals with staff shortage (NY)").mark_point().encode(
        x='Date:T',
        y='Deaths:Q',
        color=alt.Color("# Hospitals with shortage:Q",
                        scale=alt.Scale(scheme='goldred'))
    ).interactive().properties(
        width=1000,
        height=400
    )
    st.write(new_york_shortage_vs_deaths_chart)

def utah_infrastructure_chart():
    utah_df = covid_data[covid_data["state"] == "UT"]
    utah_df = utah_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
    utah_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
    utah_df = utah_df.melt("Date", var_name='Parameter', value_name='Value')

    # Utah stacked chart

    utah_stacked = covid_data[covid_data["state"] == "UT"]

    utah_stacked_normal = utah_stacked[
        ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
    utah_stacked_normal["Available"] = utah_stacked_normal["inpatient_beds"] - \
                                       utah_stacked["inpatient_beds_used"] - \
                                       utah_stacked["inpatient_beds_used_covid"]

    utah_stacked_normal["inpatient_beds_used"] = utah_stacked_normal["inpatient_beds_used"] / \
                                                 utah_stacked_normal["inpatient_beds"]
    utah_stacked_normal["inpatient_beds_used_covid"] = utah_stacked_normal["inpatient_beds_used_covid"] / \
                                                       utah_stacked_normal["inpatient_beds"]
    utah_stacked_normal["Available"] = utah_stacked_normal["Available"] / \
                                       utah_stacked_normal["inpatient_beds"]

    utah_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

    utah_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
    utah_stacked_normal = utah_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

    utah_stacked_normal["Type"] = "Normal"
    utah_stacked_normal = utah_stacked_normal.fillna(0)
    # st.write(new_york_stacked_normal)

    utah_stacked_icu = utah_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                     "total_staffed_adult_icu_beds"]]
    utah_stacked_icu["Available"] = utah_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    utah_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    utah_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

    utah_stacked_icu["staffed_adult_icu_bed_occupancy"] = utah_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          utah_stacked_icu["total_staffed_adult_icu_beds"]
    utah_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = utah_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   utah_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
    utah_stacked_icu["Available"] = utah_stacked_icu["Available"] / \
                                    utah_stacked_icu["total_staffed_adult_icu_beds"]

    utah_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

    utah_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
    utah_stacked_icu = utah_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

    utah_stacked_icu["Type"] = "ICU"
    utah_stacked_icu = utah_stacked_icu.fillna(0)
    # st.write(new_york_stacked_icu)

    utah_stacked_data = utah_stacked_normal.append(utah_stacked_icu, ignore_index=True)

    utah_brush = alt.selection(type='interval', encodings=["x"])
    utah_bed_utilization_chart = alt.Chart(utah_df,
                                           title="Trend in Hospital bed utilization in Utah").mark_line().encode(
        x='Date:T',
        y='Value:Q',
        color='Parameter:N',
        strokeDash='Parameter:N',
    ).properties(
        width=775,
        height=400
    ).add_selection(
        utah_brush
    )
    st.write(utah_bed_utilization_chart)

    # Utah deaths chart
    utah_deaths = covid_data[covid_data["state"] == "UT"]
    utah_deaths = utah_deaths[["date", "new_deceased"]]
    utah_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                       inplace=True)
    utah_deaths_chart = alt.Chart(utah_deaths, title="Daily Deaths in Utah over time").mark_line().encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Deaths:Q')
    ).interactive().properties(
        width=500,
        height=400
    )
    st.write(utah_deaths_chart)

    utah_stacked_chart = alt.Chart(utah_stacked_data).mark_bar().encode(
        x='count()',
        y='Type:N',
        color='Parameter:N'
    ).transform_filter(
        utah_brush
    ).properties(
        width=550,
    )
    st.write(utah_stacked_chart)

    # Shortage Vs Deaths

    # Decide whether to connect it
    # For all visualization, cut off everything until may 2020
    # Fix color scheme
    utah_shortage_vs_deaths = covid_data[covid_data["state"] == "UT"]
    utah_shortage_vs_deaths = utah_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    utah_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                            "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                                   inplace=True)
    utah_shortage_vs_deaths_chart = alt.Chart(utah_shortage_vs_deaths,
                                              title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
        x='Date:T',
        y='Deaths:Q',
        color=alt.Color("# Hospitals with shortage:Q",
                        scale=alt.Scale(scheme='goldred'))
    ).interactive().properties(
        width=1000,
        height=400
    )
    st.write(utah_shortage_vs_deaths_chart)

    # Testing Vs Results

    utah_test_results = pd.read_csv("data/testing_results.csv")
    utah_test_results = utah_test_results[utah_test_results["state"] == "UT"]
    utah_test_results = utah_test_results[["date", "new_tested", "new_results_reported"]]
    utah_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
    utah_test_results = utah_test_results.melt("Date", var_name='Parameter', value_name='Count')
    utah_test_results_chart = alt.Chart(utah_test_results,
                                        title="Graph of Testing Vs Result reports for Utah").mark_line().encode(
        x='Date:T',
        y='Count:Q',
        color='Parameter:N'
    ).interactive().properties(
        width=1000,
        height=400
    )

    st.write(utah_test_results_chart)


def ohio_infrastructure_chart():
    ohio_df = covid_data[covid_data["state"] == "CA"]
    ohio_df = ohio_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
    ohio_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                            "adult_icu_bed_utilization": "ICU beds utilization"},
                   inplace=True)
    ohio_df = ohio_df.melt("Date", var_name='Parameter', value_name='Value')

    # ohio stacked chart

    ohio_stacked = covid_data[covid_data["state"] == "CA"]

    ohio_stacked_normal = ohio_stacked[
        ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
    ohio_stacked_normal["Available"] = ohio_stacked_normal["inpatient_beds"] - \
                                       ohio_stacked["inpatient_beds_used"] - \
                                       ohio_stacked["inpatient_beds_used_covid"]

    ohio_stacked_normal["inpatient_beds_used"] = ohio_stacked_normal["inpatient_beds_used"] / \
                                                 ohio_stacked_normal["inpatient_beds"]
    ohio_stacked_normal["inpatient_beds_used_covid"] = ohio_stacked_normal["inpatient_beds_used_covid"] / \
                                                       ohio_stacked_normal["inpatient_beds"]
    ohio_stacked_normal["Available"] = ohio_stacked_normal["Available"] / \
                                       ohio_stacked_normal["inpatient_beds"]

    ohio_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

    ohio_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                        "inpatient_beds_used_covid": "Covid",
                                        "Available": "Available"},
                               inplace=True)
    ohio_stacked_normal = ohio_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

    ohio_stacked_normal["Type"] = "Normal"
    ohio_stacked_normal = ohio_stacked_normal.fillna(0)
    # st.write(new_york_stacked_normal)

    ohio_stacked_icu = ohio_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                     "total_staffed_adult_icu_beds"]]
    ohio_stacked_icu["Available"] = ohio_stacked_icu["total_staffed_adult_icu_beds"] - \
                                    ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                    ohio_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"]

    ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] = ohio_stacked_icu["staffed_adult_icu_bed_occupancy"] / \
                                                          ohio_stacked_icu["total_staffed_adult_icu_beds"]
    ohio_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = ohio_stacked_icu[
                                                                                       "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                   ohio_stacked_icu[
                                                                                       "total_staffed_adult_icu_beds"]
    ohio_stacked_icu["Available"] = ohio_stacked_icu["Available"] / \
                                    ohio_stacked_icu["total_staffed_adult_icu_beds"]

    ohio_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

    ohio_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                     "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                            inplace=True)
    ohio_stacked_icu = ohio_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

    ohio_stacked_icu["Type"] = "ICU"
    ohio_stacked_icu = ohio_stacked_icu.fillna(0)
    # st.write(new_york_stacked_icu)

    ohio_stacked_data = ohio_stacked_normal.append(ohio_stacked_icu, ignore_index=True)

    ohio_brush = alt.selection(type='interval', encodings=["x"])
    ohio_bed_utilization_chart = alt.Chart(ohio_df,
                                           title="Trend in Hospital bed utilization in ohio").mark_line().encode(
        x='Date:T',
        y='Value:Q',
        color='Parameter:N',
        strokeDash='Parameter:N',
    ).properties(
        width=775,
        height=400
    ).add_selection(
        ohio_brush
    )
    st.write(ohio_bed_utilization_chart)

    # ohio deaths chart
    ohio_deaths = covid_data[covid_data["state"] == "CA"]
    ohio_deaths = ohio_deaths[["date", "new_deceased"]]
    ohio_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                       inplace=True)
    ohio_deaths_chart = alt.Chart(ohio_deaths, title="Daily Deaths in ohio over time").mark_line().encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Deaths:Q')
    ).interactive().properties(
        width=500,
        height=400
    )
    st.write(ohio_deaths_chart)

    ohio_stacked_chart = alt.Chart(ohio_stacked_data).mark_bar().encode(
        x='count()',
        y='Type:N',
        color='Parameter:N'
    ).transform_filter(
        ohio_brush
    ).properties(
        width=550,
    )
    st.write(ohio_stacked_chart)

    # Shortage Vs Deaths

    # Decide whether to connect it
    # For all visualization, cut off everything until may 2020
    # Fix color scheme
    ohio_shortage_vs_deaths = covid_data[covid_data["state"] == "CA"]
    ohio_shortage_vs_deaths = ohio_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    ohio_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                            "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                                   inplace=True)
    ohio_shortage_vs_deaths_chart = alt.Chart(ohio_shortage_vs_deaths,
                                              title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
        x='Date:T',
        y='Deaths:Q',
        color=alt.Color("# Hospitals with shortage:Q",
                        scale=alt.Scale(scheme='goldred'))
    ).interactive().properties(
        width=1000,
        height=400
    )
    st.write(ohio_shortage_vs_deaths_chart)

    # Testing Vs Results

    ohio_test_results = pd.read_csv("data/testing_results.csv")
    ohio_test_results = ohio_test_results[ohio_test_results["state"] == "CA"]
    ohio_test_results = ohio_test_results[["date", "new_tested", "new_results_reported"]]
    ohio_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                      "new_results_reported": "# Results reported"},
                             inplace=True)
    ohio_test_results = ohio_test_results.melt("Date", var_name='Parameter', value_name='Count')
    ohio_test_results_chart = alt.Chart(ohio_test_results,
                                        title="Graph of Testing Vs Result reports for ohio").mark_line().encode(
        x='Date:T',
        y='Count:Q',
        color='Parameter:N'
    ).interactive().properties(
        width=1000,
        height=400
    )

    st.write(ohio_test_results_chart)

def california_infrastructure_chart():
    california_df = covid_data[covid_data["state"] == "CA"]
    california_df = california_df[["date", "inpatient_beds_utilization", "adult_icu_bed_utilization"]]
    california_df.rename(columns={"date": "Date", "inpatient_beds_utilization": "In-patient beds utilization",
                                  "adult_icu_bed_utilization": "ICU beds utilization"},
                         inplace=True)
    california_df = california_df.melt("Date", var_name='Parameter', value_name='Value')

    # california stacked chart

    california_stacked = covid_data[covid_data["state"] == "CA"]

    california_stacked_normal = california_stacked[
        ["date", "inpatient_beds_used", "inpatient_beds_used_covid", "inpatient_beds"]]
    california_stacked_normal["Available"] = california_stacked_normal["inpatient_beds"] - \
                                             california_stacked["inpatient_beds_used"] - \
                                             california_stacked["inpatient_beds_used_covid"]

    california_stacked_normal["inpatient_beds_used"] = california_stacked_normal["inpatient_beds_used"] / \
                                                       california_stacked_normal["inpatient_beds"]
    california_stacked_normal["inpatient_beds_used_covid"] = california_stacked_normal["inpatient_beds_used_covid"] / \
                                                             california_stacked_normal["inpatient_beds"]
    california_stacked_normal["Available"] = california_stacked_normal["Available"] / \
                                             california_stacked_normal["inpatient_beds"]

    california_stacked_normal.drop(['inpatient_beds'], axis=1, inplace=True)

    california_stacked_normal.rename(columns={"date": "Date", "inpatient_beds_used": "Others",
                                              "inpatient_beds_used_covid": "Covid",
                                              "Available": "Available"},
                                     inplace=True)
    california_stacked_normal = california_stacked_normal.melt("Date", var_name='Parameter', value_name='Value')

    california_stacked_normal["Type"] = "Normal"
    california_stacked_normal = california_stacked_normal.fillna(0)
    # st.write(new_york_stacked_normal)

    california_stacked_icu = california_stacked[["date", "staffed_adult_icu_bed_occupancy",
                                                 "staffed_icu_adult_patients_confirmed_and_suspected_covid",
                                                 "total_staffed_adult_icu_beds"]]
    california_stacked_icu["Available"] = california_stacked_icu["total_staffed_adult_icu_beds"] - \
                                          california_stacked_icu["staffed_adult_icu_bed_occupancy"] - \
                                          california_stacked_icu[
                                              "staffed_icu_adult_patients_confirmed_and_suspected_covid"]

    california_stacked_icu["staffed_adult_icu_bed_occupancy"] = california_stacked_icu[
                                                                    "staffed_adult_icu_bed_occupancy"] / \
                                                                california_stacked_icu["total_staffed_adult_icu_beds"]
    california_stacked_icu["staffed_icu_adult_patients_confirmed_and_suspected_covid"] = california_stacked_icu[
                                                                                             "staffed_icu_adult_patients_confirmed_and_suspected_covid"] / \
                                                                                         california_stacked_icu[
                                                                                             "total_staffed_adult_icu_beds"]
    california_stacked_icu["Available"] = california_stacked_icu["Available"] / \
                                          california_stacked_icu["total_staffed_adult_icu_beds"]

    california_stacked_icu.drop(['total_staffed_adult_icu_beds'], axis=1, inplace=True)

    california_stacked_icu.rename(columns={"date": "Date", "staffed_adult_icu_bed_occupancy": "Others",
                                           "staffed_icu_adult_patients_confirmed_and_suspected_covid": "Covid"},
                                  inplace=True)
    california_stacked_icu = california_stacked_icu.melt("Date", var_name='Parameter', value_name='Value')

    california_stacked_icu["Type"] = "ICU"
    california_stacked_icu = california_stacked_icu.fillna(0)
    # st.write(new_york_stacked_icu)

    california_stacked_data = california_stacked_normal.append(california_stacked_icu, ignore_index=True)

    california_brush = alt.selection(type='interval', encodings=["x"])
    california_bed_utilization_chart = alt.Chart(california_df,
                                                 title="Trend in Hospital bed utilization in california").mark_line().encode(
        x='Date:T',
        y='Value:Q',
        color='Parameter:N',
        strokeDash='Parameter:N',
    ).properties(
        width=775,
        height=400
    ).add_selection(
        california_brush
    )
    st.write(california_bed_utilization_chart)

    # california deaths chart
    california_deaths = covid_data[covid_data["state"] == "CA"]
    california_deaths = california_deaths[["date", "new_deceased"]]
    california_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths"},
                             inplace=True)
    california_deaths_chart = alt.Chart(california_deaths,
                                        title="Daily Deaths in california over time").mark_line().encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Deaths:Q')
    ).interactive().properties(
        width=500,
        height=400
    )
    st.write(california_deaths_chart)

    california_stacked_chart = alt.Chart(california_stacked_data).mark_bar().encode(
        x='count()',
        y='Type:N',
        color='Parameter:N'
    ).transform_filter(
        california_brush
    ).properties(
        width=550,
    )
    st.write(california_stacked_chart)

    # Shortage Vs Deaths

    # Decide whether to connect it
    # For all visualization, cut off everything until may 2020
    # Fix color scheme
    california_shortage_vs_deaths = covid_data[covid_data["state"] == "CA"]
    california_shortage_vs_deaths = california_shortage_vs_deaths[
        ["date", "new_deceased", "critical_staffing_shortage_today_yes"]]
    california_shortage_vs_deaths.rename(columns={"date": "Date", "new_deceased": "Deaths",
                                                  "critical_staffing_shortage_today_yes": "# Hospitals with shortage"},
                                         inplace=True)
    california_shortage_vs_deaths_chart = alt.Chart(california_shortage_vs_deaths,
                                                    title="Graph of Daily deaths and hospitals with staff shortage").mark_point().encode(
        x='Date:T',
        y='Deaths:Q',
        color=alt.Color("# Hospitals with shortage:Q",
                        scale=alt.Scale(scheme='goldred'))
    ).interactive().properties(
        width=1000,
        height=400
    )
    st.write(california_shortage_vs_deaths_chart)

    # Testing Vs Results

    california_test_results = pd.read_csv("data/testing_results.csv")
    california_test_results = california_test_results[california_test_results["state"] == "CA"]
    california_test_results = california_test_results[["date", "new_tested", "new_results_reported"]]
    california_test_results.rename(columns={"date": "Date", "new_tested": "# Tests conducted",
                                            "new_results_reported": "# Results reported"},
                                   inplace=True)
    california_test_results = california_test_results.melt("Date", var_name='Parameter', value_name='Count')
    california_test_results_chart = alt.Chart(california_test_results,
                                              title="Graph of Testing Vs Result reports for california").mark_line().encode(
        x='Date:T',
        y='Count:Q',
        color='Parameter:N'
    ).interactive().properties(
        width=1000,
        height=400
    )

    st.write(california_test_results_chart)

