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
                    df_values[vals[1]] = df
                else:
                    df = df[['feature', 'importance']]
                    df_features[vals[1]] = df
            # 30
            else:
                if vals[2] == 'values':
                    df = df[['date', 'y', 'pred']]
                    df_values_thirty[vals[1]] = df

    return df_values, df_features, df_values_thirty

def model_plot(df_values):
    states = list(df_values.keys())
    # Edit below to select dynamically

    selected_state = 'NY'
    df = df_values[selected_state]
    # Plot date on x axis and y and pred on y axis
    data = df.melt("date", var_name='Type', value_name='Value')
    chart = alt.Chart(data).mark_line().encode(
      x='date:T',
      y='Value:Q',
      color='Type:N'
    ).interactive().properties(
        width=1000,
        height=400
    )
    st.write(chart)
    return


if __name__ =="__main__":
   df_values, df_features, df_values_thirty = read_files()
   model_plot(df_values)
