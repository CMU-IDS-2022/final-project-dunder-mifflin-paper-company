from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# st.set_page_config(layout="wide")

US_STATE_TO_ABBREV = {
    "United States": "US",
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}
US_ABBREV_TO_STATE = {v: k for k, v in US_STATE_TO_ABBREV.items()}


@st.cache
def read_datasets():
    us_timeseries_df = pd.read_csv(
        "./data/open_data/us_timeseries_data.csv", parse_dates=["date"]
    )
    us_timeseries_df["date"] = us_timeseries_df["date"].map(lambda d: d.date())
    us_per_states_df = pd.read_csv("./data/open_data/us_per_state_data.csv")

    # location_key: US_NY -> NY
    def remove_prefix(state):
        return state if state == "US" else state.split("_")[1]

    us_timeseries_df.location_key = us_timeseries_df.location_key.map(remove_prefix)
    us_per_states_df.location_key = us_per_states_df.location_key.map(remove_prefix)

    # calculate cumulative confirmed rate
    us_per_states_df["cumulative_confirmed_rate"] = (
        us_per_states_df["cumulative_confirmed"] / us_per_states_df["population"]
    )

    return us_timeseries_df, us_per_states_df


def visualize_timeseries(us_timeseries_df):
    st.header(
        "How have the average daily confirmed / deceased / tested / hospitalized / vaccinated / fully vaccinated cases varied in the US?"
    )
    region = st.selectbox(
        "Select the region you would like to view!", US_STATE_TO_ABBREV.keys(), index=0
    )
    region = US_STATE_TO_ABBREV[region]

    parameters = [
        "Average Daily Confirmed",
        "Average Daily Deceased",
        "Average Daily Tested",
        "Average Daily Hospitalized",
        "Average Daily Vaccinated",
        "Average Daily Fully Vaccinated",
    ]
    param_colors = ["brown", "red", "yellow", "blue", "green", "lawngreen"]
    selected_fields = st.multiselect(
        "Select the parameters you would like to view!",
        parameters,
        default=[
            "Average Daily Confirmed",
            "Average Daily Deceased",
            "Average Daily Fully Vaccinated",
        ],
    )

    df = us_timeseries_df[us_timeseries_df.location_key == region]
    plot_data = df[selected_fields + ["date"]]
    plot_data = plot_data.melt("date", var_name="parameter", value_name="count")
    plot_data["Name"] = plot_data["parameter"]

    plot = (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Count"),
            color=alt.Color(
                "parameter:N", scale=alt.Scale(domain=parameters, range=param_colors)
            ),
            tooltip=["parameter", "count"],
        )
        .interactive()
        .properties(
            width=1000, height=400, title="Average daily COVID statistics in the US"
        )
    )
    # col1, col2, col3 = st.columns([1, 5, 1])
    # with col2:
    st.altair_chart(plot)

    # insert texts
    write_paragraph(
        "Try to play around with different parameters and regions. You can also zoom in and out of the chart. How does the trend look like in your home town?"
    )
    write_paragraph(
        "If we take a look at the trend of average daily confirmed cases across the last two years, we can identify <span style='color:#900C3F'>3 major spikes</span>:  (1) October 2020 - February 2021 (2) July 2021 - October 2021 (3) December 2021 - February 2022"
    )
    write_paragraph(
        "The 3 spikes respectively correspond to the emerging COVID variants of <span style='color:#900C3F'>Alpha, Delta, and Omicron</span>. Among the variants, we can observe that Omicron is the most infectious as the average daily confirmed cases soared to around 63,000 in early January 2022. However, as the below plots show, the <span style='color:#900C3F'>death cases does not increase proportionally with confirmed cases</span>. Coupled with the fact that most of the people got fully vaccinated in around April 2021, this can mean vaccination does help on reducing the death rate."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("Cases")
        new_confirmed_plot = (
            get_timeseries_plot(df[["date", "Average Daily Confirmed"]])
            .properties(width=460, height=350, title="Average daily confirmed in US")
            .configure_line(color="brown")
        )
        st.write(new_confirmed_plot)
    with col2:
        st.header("Deaths")
        deceased_plot = (
            get_timeseries_plot(df[["date", "Average Daily Deceased"]])
            .properties(width=460, height=350, title="Average daily deceased in US")
            .configure_line(color="red")
        )
        st.write(deceased_plot)

    write_paragraph(
        "Now that we know the overall trend of COVID statistics in the US, let’s try to explore data in a <span style='color:#900C3F'>per state basis</span> and compare which states handle COVID better."
    )


def visualize_map(col, df_by_state, us_per_states_df):
    # select parameter
    parameters = [
        "Average Daily Confirmed",
        "Average Daily Deceased",
        "Average Daily Tested",
        "Average Daily Hospitalized",
        "Average Daily Vaccinated",
        "Average Daily Fully Vaccinated",
    ]
    param_colors = {
        "Average Daily Confirmed": "red",
        "Average Daily Deceased": "brown",
        "Average Daily Tested": "darkgoldenrod",
        "Average Daily Hospitalized": "blue",
        "Average Daily Vaccinated": "lawngreen",
        "Average Daily Fully Vaccinated": "green",
    }
    with col:
        selected_field = st.selectbox(
            "Select a parameter you would like to view!", parameters, index=0
        )
    selected_color = param_colors[selected_field]

    # map chart background
    states = alt.topo_feature(data.us_10m.url, "states")
    map_bg = (
        alt.Chart(states, title=f"{selected_field} counts across states")
        .mark_geoshape(fill="white", stroke="black")
        .project("albersUsa")
        .properties(width=460, height=500)
    )
    # foreground dots
    param_by_state = df_by_state[["location_key", selected_field]]
    long_lats = us_per_states_df[["location_key", "longitude", "latitude"]]
    param_by_state = param_by_state.merge(
        long_lats, how="inner", left_on=["location_key"], right_on=["location_key"]
    )

    # TODO: add death rate as color,
    dots = (
        alt.Chart(param_by_state)
        .mark_circle()
        .encode(
            latitude="latitude:Q",
            longitude="longitude:Q",
            color=alt.Color(
                f"{selected_field}:Q",
                scale=alt.Scale(range=["white", selected_color]),
                legend=alt.Legend(
                    orient="top-right",
                    title=None
                    # legendX=240,
                    # legendY=100,
                    # direction="horizontal",
                    # titleAnchor="middle",
                ),
            ),
            size=alt.Size(f"{selected_field}:Q"),
            tooltip=[
                alt.Tooltip("location_key", title="State"),
                alt.Tooltip(f"{selected_field}:Q", title=selected_field),
            ],
        )
    )

    map_plot = map_bg + dots
    with col:
        col.write(map_plot)


def visualize_bars(col, df_by_state, us_per_states_df):
    df_by_state = df_by_state.rename(
        columns={
            "cumulative_confirmed": "Cumulative Confirmed Rate",
            "cumulative_deceased": "Cumulative Deceased Rate",
            "cumulative_tested": "Cumulative Tested Rate",
            "cumulative_hospitalized_patients": "Cumulative Hospitalized Rate",
            "cumulative_persons_vaccinated": "Cumulative Vaccinated Rate",
            "cumulative_persons_fully_vaccinated": "Cumulative Fully Vaccinated Rate",
        }
    )
    # select parameter
    parameters = [
        "Cumulative Confirmed Rate",
        "Cumulative Deceased Rate",
        "Cumulative Tested Rate",
        "Cumulative Hospitalized Rate",
        "Cumulative Vaccinated Rate",
        "Cumulative Fully Vaccinated Rate",
    ]
    param_colors = {
        "Cumulative Confirmed Rate": "blue",
        "Cumulative Deceased Rate": "red",
        "Cumulative Tested Rate": "darkgoldenrod",
        "Cumulative Hospitalized Rate": "brown",
        "Cumulative Vaccinated Rate": "lawngreen",
        "Cumulative Fully Vaccinated Rate": "green",
    }

    with col:
        selected_field = st.selectbox(
            "Select a parameter you would like to view!", parameters, index=0
        )
        selected_color = param_colors[selected_field]
        df_by_state = df_by_state[["location_key", selected_field]]

        # divide parameter by population
        population_by_state = us_per_states_df[["location_key", "population"]]
        df_by_state = df_by_state.merge(
            population_by_state,
            how="inner",
            left_on=["location_key"],
            right_on=["location_key"],
        )
        df_by_state[selected_field] = (
            df_by_state[selected_field] / df_by_state["population"]
        )
        df_by_state.rename(columns={"location_key": "state"}, inplace=True)
        # st.write(df_by_state)

        chart = (
            alt.Chart(df_by_state, title=f"{selected_field}s in different states")
            .mark_bar()
            .encode(
                x=alt.X(selected_field, title=selected_field),
                y=alt.Y(
                    "state",
                    sort=alt.EncodingSortField(
                        field=selected_field, order="descending"
                    ),
                    title="states",
                ),
                color=alt.Color(
                    # f"{selected_field}:Q",
                    # scale=alt.Scale(range=["white", selected_color]),
                    "state",
                    scale=alt.Scale(scheme="category10"),
                    legend=None,
                ),
                tooltip=["state", alt.Tooltip(f"{selected_field}:Q", format=".1%")],
            )
            .properties(width=460, height=1100)
        )
        col.write(chart)


def visualize_map_bars(us_timeseries_df, us_per_states_df):
    st.header("How have COVID statistics varied across different states over time?")

    # slider for date
    date_options = us_timeseries_df[us_timeseries_df.location_key == "US"].date.unique()
    date_options = list(map(lambda d: f"{d.year}/{d.month}", date_options))
    selected_date = st.select_slider(
        "Slide the date to see statistics vary with time",
        options=date_options,
        value=date_options[-1],
    )
    selected_date = datetime.strptime(selected_date, "%Y/%m").date()
    df_by_state = us_timeseries_df[us_timeseries_df.date == selected_date]
    df_by_state = df_by_state[df_by_state.location_key != "US"]

    col1, col2 = st.columns([1, 1])
    visualize_map(col1, df_by_state, us_per_states_df)
    with col1:
        write_paragraph(
            "You can slide the timeline to explore how many people were infected in each state in any given month from January 2020 to April 2022. Also, as the selected time changes, the bar plot shows the comparison across different states on the <span style='color:#900C3F'>cumulative confirmed rate</span>. We calculate the cumulative confirmed rate by <span style='color:#900C3F'>(cumulative_confirmed_cases / population)</span>. This can help us to explore which states are impacted more or are handling COVID better <span style='color:#900C3F'>without favoring states with smaller population</span>."
        )
        write_paragraph(
            "We can notice that <span style='color:#900C3F'>California</span>, <span style='color:#900C3F'>Illinois</span>, and <span style='color:#900C3F'>Washington</span> had the earliest confirmed cases when the pandemic started in January 2020. By May 2020, the virus had already spread to the whole country with <span style='color:#900C3F'>New York</span> being the most seriously affected. In terms of confirmed rate, <span style='color:#900C3F'>Rhode Island</span>, <span style='color:#900C3F'>Utah</span>, <span style='color:#900C3F'>Alaska</span>, <span style='color:#900C3F'>North Dakota</span>, and <span style='color:#900C3F'>South Carolina</span> have the highest number (> 30%) by April 2022, while <span style='color:#900C3F'>Oregon</span>, <span style='color:#900C3F'>DC</span>, <span style='color:#900C3F'>Maryland</span>, <span style='color:#900C3F'>Hawaii</span>, and <span style='color:#900C3F'>outlying islands</span> are less than 18%. Other states having anomalous statistics include <span style='color:#900C3F'>Arizona</span>, <span style='color:#900C3F'>Kentucky</span>, and <span style='color:#900C3F'>Guam</span>, which have the highest death rate, hospitalized rate, and fully vaccinated rate respectively."
        )
    visualize_bars(col2, df_by_state, us_per_states_df)
    write_paragraph(
        "As the bar chart shows, the COVID confirmed rate (or other statistics) across different states in the US vary a lot over the past two years. Although we might find some common attributes, e.g. lower population density, among those states with lower confirmed rate, attributing such consequence to any factors can be extremely complex because of the difference in mobility, governmental response, ethnics, and geography across different states."
    )
    write_paragraph(
        "In the following sections, we explore the <span style='color:#900C3F'>vaccination, geography, population, and mobility datasets</span> with an aim toward finding out attributes that potentially correlate with COVID confirmed rate."
    )


def get_cor_plot(df):
    cor_data = (
        df.corr()
        .stack()
        .reset_index()
        .rename(
            columns={
                0: "correlation",
                "level_0": "Variable 1",
                "level_1": "Variable 2",
            }
        )
    )
    cor_data["correlation_label"] = cor_data["correlation"].map(
        "{:.2f}".format
    )  # Round to 2 decimal

    base = alt.Chart(cor_data).encode(x="Variable 1:O", y="Variable 2:O")
    text = base.mark_text().encode(
        text="correlation_label",
        color=alt.condition(
            alt.datum.correlation > 0.5, alt.value("white"), alt.value("black")
        ),
    )
    cor_plot = base.mark_rect().encode(color="correlation:Q")
    return alt.layer(cor_plot, text)


def visualize_vaccine_types_effect(us_per_states_df):
    st.header(
        "How is the proportion of different vaccines affect COVID confirmed / death rate in that region?"
    )
    col1, col2 = st.columns([2, 3])

    # 1. pie chart showing the proportion of 3 vaccine brands (by country / state)
    vaccine_administored_cols = [
        "cumulative_vaccine_doses_administered_pfizer",
        "cumulative_vaccine_doses_administered_moderna",
        "cumulative_vaccine_doses_administered_janssen",
    ]
    doses_administored_by_state = us_per_states_df[
        ["location_key"] + vaccine_administored_cols
    ]
    doses_administored_by_state.rename(
        columns={
            "cumulative_vaccine_doses_administered_pfizer": "pfizer",
            "cumulative_vaccine_doses_administered_moderna": "moderna",
            "cumulative_vaccine_doses_administered_janssen": "jannsen",
        },
        inplace=True,
    )
    doses_administored_by_state["sum"] = (
        doses_administored_by_state["pfizer"]
        + doses_administored_by_state["moderna"]
        + doses_administored_by_state["jannsen"]
    )
    for c in ["pfizer", "moderna", "jannsen"]:
        doses_administored_by_state[c] = (
            doses_administored_by_state[c] / doses_administored_by_state["sum"]
        )
    doses_administored_by_state.drop(columns=["sum"], inplace=True)

    # select region
    with col1:
        region_text = st.selectbox(
            "Select the region you would like to view!",
            US_STATE_TO_ABBREV.keys(),
            index=0,
            key="vvte",
        )
    region = US_STATE_TO_ABBREV[region_text]
    doses_by_brand = doses_administored_by_state[
        doses_administored_by_state.location_key == region
    ]
    doses_by_brand = doses_by_brand.melt(
        "location_key", var_name="category", value_name="percentage"
    )

    pie_chart = (
        alt.Chart(doses_by_brand)
        .mark_arc(outerRadius=120)
        .encode(
            theta=alt.Theta(field="percentage", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
            tooltip=["category", alt.Tooltip("percentage:Q", format=".1%")],
        )
        .properties(
            width=400, height=320, title=f"Administored vaccines in {region_text}"
        )
        .configure_title(fontSize=16)
        .configure_legend(titleFontSize=15, labelFontSize=13, orient="bottom-left")
    )
    with col1:
        st.write(pie_chart)

    # 2. vaccine brand vs covid cases / death rate
    new_cols = ["cumulative_confirmed_rate", "death_rate"]
    doses_administored_by_state[new_cols] = us_per_states_df[new_cols]
    doses_administored_by_state.rename(
        columns={
            "cumulative_confirmed_rate": "COVID confirmed rate",
            "death_rate": "Death rate",
            "jannsen": "Jannsen %",
            "moderna": "Moderna %",
            "pfizer": "Pfizer %",
        },
        inplace=True,
    )

    cor_plot = (
        get_cor_plot(
            doses_administored_by_state,
        )
        .configure_title(fontSize=16, offset=20)
        .configure_legend(titleFontSize=13, labelFontSize=11)
        .configure_axis(title=None)
        .properties(
            width=520,
            height=520,
            title="COVID confirmed/death rate vs vaccine brand percentage",
        )
    )
    with col2:
        st.write(cor_plot)

    write_paragraph(
        "We compute the percentage of each vaccines by <span style='color:#900C3F'>(number of such vaccine applied / number of total vaccines applied)</span>. Observe the correlation coefficients of different vaccine with confirmed rate and death rate. Surprisingly, The percentage of Pfizer vaccine is medium-to-strong negatively correlated to both confirmed rate and death rate, with coefficients <span style='color:#900C3F'>0.43</span> and <span style='color:#900C3F'>0.57</span>."
    )


def visualize_correlations(us_per_states_df):
    # COVID confirm rate / death rate vs:
    # 1. vaccine facility per person
    # 2. life expectancy
    # 3. population density (population / area)
    # 4. geography (elavation, temperature, rainfall, humidity)
    st.header(
        "How are geography, population, and health parameters correlate to COVID confirmed / death rate?"
    )
    us_per_states_df = us_per_states_df[us_per_states_df.location_key != "US"]
    cols = [
        "cumulative_confirmed_rate",
        "death_rate",
        "life_expectancy",
        "elevation_m",
        "average_temperature_celsius",
        "rainfall_mm",
        "relative_humidity",
    ]
    df = us_per_states_df[cols]
    df["vax_facility_cnt_person"] = (
        us_per_states_df["vaccine_facility_cnt"] / us_per_states_df["population"]
    )
    df["population_density_kmsq"] = (
        us_per_states_df["population"] / us_per_states_df["area_sq_km"]
    )
    cor_plot = (
        get_cor_plot(df)
        .configure_title(fontSize=15)
        .configure_axis(title=None)
        .configure_legend(titleFontSize=13, labelFontSize=11)
        .properties(
            width=700,
            height=700,
            title="COVID confirmed/death rate vs parameters",
        )
    )

    write_paragraph(
        "Next we gather the geography, population, and health attributes for each state to see if any of them correlate to COVID confirmed / death rate. Such attributes include:"
    )
    write_paragraph(
        "<ul><li style='font-size:18px'>Population density (count / square km)</li> <li style='font-size:18px'>Life expectancy</li> <li style='font-size:18px'>Number of vaccination facilities allocated per person</li> <li style='font-size:18px'>Elevation, rainfall, humidity, temperature</li> </ul><br>"
    )
    st.write(cor_plot)
    write_paragraph(
        "<br>An interesting result in the correlation matrix is that <span style='color:#900C3F'>life expectancy is medium-to-strong negatively correlated to COVID confirmed rate and death rate</span>, which can be explained as COVID affects more on regions who already have relatively unhealthy population or lack of medical infrastructure. Another thing worth pointing out is that <span style='color:#900C3F'>average temperature is negatively correlated to confirmed / death rate</span>, which is a consistent result with some <a href='https://www.nature.com/articles/s41598-021-87803-w'>other research papers</a> that mentioned COVID transmits slower in regions with higher average temperature."
    )


def get_timeseries_plot(plot_data):
    plot_data = plot_data.melt("date", var_name="parameter", value_name="count")
    plot_data["Name"] = plot_data["parameter"]
    return (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Count"),
            tooltip=["parameter", "count", "date"],
        )
        .interactive()
    )


def visualize_mobility(us_timeseries_df):
    st.header("How does the mobility of citizens change over time?")
    # rename mobility columns
    mobility_cols = {
        "mobility_retail_and_recreation": "Retail and Recreation",
        "mobility_grocery_and_pharmacy": "Grocery and Pharmacy",
        "mobility_parks": "Parks",
        "mobility_transit_stations": "Transit stations",
        "mobility_workplaces": "Workplaces",
    }
    df = us_timeseries_df.rename(columns=mobility_cols)
    df = df[df.location_key == "US"]

    parameters = list(mobility_cols.values())
    param_colors = ["brown", "red", "yellow", "blue", "green"]
    selected_fields = st.multiselect(
        "Select the parameters you would like to view!",
        parameters,
        default=parameters,
    )

    plot_data = df[selected_fields + ["date"]]
    plot_data = plot_data.melt("date", var_name="parameter", value_name="change (%)")
    plot_data["Name"] = plot_data["parameter"]

    plot = (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("change (%):Q", title="Change (%)"),
            color=alt.Color(
                "parameter:N",
                scale=alt.Scale(domain=parameters, range=param_colors),
                legend=alt.Legend(orient="top-right"),
            ),
            tooltip=["parameter", "change (%)"],
        )
        .interactive()
        .properties(width=900, height=350, title="Mobility trend over time in US")
    )

    new_confirmed_plot = (
        get_timeseries_plot(df[["date", "Average Daily Confirmed"]])
        .properties(
            width=900,
            height=350,
            title="Average daily confirmed COVID cases over time in US",
        )
        .configure_line(color="red")
    )

    # col1, col2 = st.columns([2, 1])
    # with col1:
    st.altair_chart(plot)
    st.altair_chart(new_confirmed_plot)
    # with col2:
    write_paragraph(
        "<br><br>The Y axis of the line plot shows <span style='color:#900C3F'>what percentage more / less citizens go to the places in selected parameters</span>. We also present the confirmed cases over time in the plot below to compare how the changes in new confirmed cases affect citizens’ mobility."
    )
    write_paragraph(
        "The trends of mobility for “Retail and Recreation”, “Grocery and Pharmacy”, and “Transit Stations” roughly remain the same — they all experienced plunges in April 2020 when the pandemic first spread out, in January 2021 with the Alpha variant, and in January 2022 with the Omicron outbreak."
    )
    write_paragraph(
        "On the other hand, <span style='color:#900C3F'>the mobility to workplaces gradually increases</span> as time advanced except the initial plunge. This corresponds to the fact that more and more companies are loosing up their stringency and starting to ask their employees to go back to office."
    )


def write_paragraph(text):
    st.write(f"<p style='font-size:18px'>{text}</p>", unsafe_allow_html=True)


def intro():
    st.header("Introduction")
    p = "The COVID-19 pandemic has impacted society in various ways,\
         affecting almost every single aspect of our daily lives. Though COVID-19 is a crisis\
         worldwide, there have been stark differences in how various regions have approached\
         curbing the spread of the infection. Every government has uniquely responded to this\
         pandemic in terms of their masking policies, early vaccinations, shutting down schools\
         and workplaces, restricting public transport, etc. Variations in these responses are\
         dependent on the distinctive institutional arrangements, political and geographical\
         factors, and cultural orientation of each state, and thus, <span style='color:#900C3F'>there is no One-Size-Fits-All\
         strategy</span>. However, it can also be argued that such distinct policies are a result of the\
         fact that we as a society were grossly under-prepared to handle a pandemic of this scale.\
         It is vital that we now analyze the different policies taken to be better prepared in the\
         event of a future pandemic."
    write_paragraph(p)
    p = "In this project, we will first perform <span style='color:#900C3F'>exploratory data analysis</span> on the\
         <a href='https://goo.gle/covid-19-open-data'>Google Health COVID-19 Open Data dataset</a>\
         to attempt to find initial insights on which states in the\
         United States do better jobs in handling COVID-19 and what are the related attributes that lead to such results. Next, we explore how human behaviors\
         such as <span style='color:#900C3F'>citizen mobility</span>, <span style='color:#900C3F'>search trend</span>, and <span style='color:#900C3F'>responses from state governments</span> affect\
         or are affected by the number of new COVID cases. Finally, we analyze the availability of\
         medical infrastructure in different regions in the US and discuss whether or not they were\
         sufficient for the pandemic. We also propose a COVID cases prediction model that helps governments to\
         scale up their resources in advance to prepare for a potential outbreak."
    write_paragraph(p)
    p = "Let’s jump into the first part and observe the overall trends of various COVID statistics in the US!"
    write_paragraph(p)


def EDA():
    us_timeseries_df, us_per_states_df = read_datasets()

    # st.markdown(
    #     "<h1><span style='color:#900C3F'>COVID-19</span> Coronavirus Open Data Dashboard</h1>",
    #     unsafe_allow_html=True,
    # )

    # intro()

    # st.header("Exploratory Data Analysis")

    visualize_timeseries(us_timeseries_df)

    visualize_map_bars(us_timeseries_df, us_per_states_df)

    visualize_vaccine_types_effect(us_per_states_df)

    visualize_correlations(us_per_states_df)

    visualize_mobility(us_timeseries_df)
