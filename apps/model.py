import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta
import pydeck as pdk
import time
import sklearn.metrics as metrics
import os

@st.cache
def read_files():
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
                    df = df.rename(columns={"date": "Date", "y": "Actual", "pred": "Predicted"})
                    df_values[vals[1]] = df
                else:
                    df = df[['feature', 'importance']]
                    df_features[vals[1]] = df
            # 30
            else:
                if vals[2] == 'values':
                    df = df[['date', 'y', 'pred']]
                    df = df.rename(columns={"date": "Date", "y": "Actual", "pred": "Predicted"})
                    df_values_thirty[vals[1]] = df

    return df_values, df_features, df_values_thirty

def model_plot_7(df_values):
    states = list(sorted(df_values.keys()))
    # Edit below to select dynamically

    selected_state = st.selectbox('Select a State', states)
    df = df_values[selected_state]

    data = df.melt("Date", var_name='Type', value_name='Cases')
    chart = alt.Chart(data, title="Actual vs Predicted cases for a 7 day step size for " + selected_state + " state")\
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


if __name__ =="__main__":
   df_values, df_features, df_values_thirty = read_files()
   model_plot_7(df_values)
   model_plot_30(df_values_thirty)

   # How to show df_features?
