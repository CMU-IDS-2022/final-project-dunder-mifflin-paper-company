import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
from datetime import datetime, timedelta
import pydeck as pdk
import time
import pickle
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
                    data = {wrd: cnt for wrd, cnt in zip(df['feature'], df['importance'])}
                    df_features[vals[1]] = data
            # 30
            else:
                if vals[2] == 'values':
                    df = df[['date', 'y', 'pred']]
                    df = df.rename(columns={"date": "Date", "y": "Actual", "pred": "Predicted"})
                    df_values_thirty[vals[1]] = df

    return df_values, df_features, df_values_thirty

@st.cache
def read_model():
    # loading the trained model
    pickle_in = open('classifier.pkl', 'rb')
    classifier = pickle.load(pickle_in)

    return classifier

def model_plot_7(df_values):
    states = list(sorted(df_values.keys()))

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


def classifier_vis(classifier):

    Gender = st.selectbox('Gender', ("Male", "Female"))
    Married = st.selectbox('Marital Status', ("Unmarried", "Married"))
    ApplicantIncome = st.number_input("Applicants monthlyincome")
    LoanAmount = st.number_input("Total loan amount")
    Credit_History = st.selectbox('Credit_History', ("Unclear Debts", "No Unclear Debts"))
    result =""

    if st.button("Predict"):
        #result = prediction(classifier, Gender, Married, ApplicantIncome, LoanAmount, Credit_History)
        result = 10

    st.success('Your loan is {}'.format(result))
    print(LoanAmount)
    return


def prediction(classifier, Gender, Married, ApplicantIncome, LoanAmount, Credit_History):

    if Gender == "Male":
        Gender = 0
    else:
        Gender = 1

    if Married == "Unmarried":
        Married = 0
    else:
        Married = 1
    if Credit_History == "Unclear Debts":
        Credit_History = 0
    else:
        Credit_History = 1

    LoanAmount = LoanAmount / 1000

    # Making predictions
    prediction = classifier.predict([[Gender, Married, ApplicantIncome, LoanAmount, Credit_History]])

    if prediction == 0:
        pred = 'Rejected'
    else:
        pred = 'Approved'
    return pred

if __name__ =="__main__":
    df_values, df_features, df_values_thirty = read_files()
    model_plot_7(df_values)
    model_plot_30(df_values_thirty)
    features_plot(df_features)

    # classifier = read_model()
    # classifier_vis(classifier)
