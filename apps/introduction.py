import streamlit as st

def Introduction():

    text = "<h1 style='text-align: center; color: #900C3F;'>COVID-19 Dashboard<h1>"
    st.write(text, unsafe_allow_html=True)
    text = "<p style='font-size:18px'>The COVID-19 pandemic has impacted society in various ways,\
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
         event of a future pandemic.</p>"
    st.write(text, unsafe_allow_html=True)

    text = "<p style='font-size:18px'>In this project, we will first perform <span style='color:#900C3F'>exploratory data analysis</span> on the\
         <a style='color:#900C3F' href='https://goo.gle/covid-19-open-data'>Google Health COVID-19 Open Data dataset</a>\
         to attempt to find initial insights on which states in the\
         United States do better jobs in handling COVID-19 and what are the related attributes that lead to such results. Next, we explore how human behaviors\
         such as <span style='color:#900C3F'>citizen mobility</span>, <span style='color:#900C3F'>search trend</span>, and <span style='color:#900C3F'>responses from state governments</span> affect\
         or are affected by the number of new COVID cases. Finally, we analyze the availability of\
         medical infrastructure in different regions in the US and discuss whether or not they were\
         sufficient for the pandemic. We also propose a COVID cases prediction model that helps governments to\
         scale up their resources in advance to prepare for a potential outbreak.</p>"
    st.write(text, unsafe_allow_html=True)

    text = "<p style='font-size:18px'>Select <span style='color:#900C3F'>Exploratory Data Analysis</span> on the left panel. Let’s jump into the first part and observe the overall trends of various COVID statistics in the US!"
    st.write(text, unsafe_allow_html=True)
