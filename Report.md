# Final Project Report

**Project URL**: https://share.streamlit.io/cmu-ids-2022/final-project-dunder-mifflin-paper-company/main

**Video URL**: https://youtu.be/NzRktLDfCC8

## Introduction

The COVID-19 pandemic has impacted society in various ways, affecting almost every single aspect of our daily lives. Though COVID-19 is a crisis worldwide, there have been stark differences in how various regions have approached curbing the spread of the infection. Every government has uniquely responded to this pandemic in terms of their masking policies, early vaccinations, shutting down schools and workplaces, restricting public transport, etc. Variations in these responses are dependent on the distinctive institutional arrangements, political and geographical factors, and cultural orientation of each state, and thus, there is no One-Size-Fits-All strategy. However, it can also be argued that such distinct policies are a result of the fact that we as a society were grossly under-prepared to handle a pandemic of this scale. It is vital that we now analyze the different policies taken to be better prepared in the event of a future pandemic.

In this project, we focus on analyzing how different states in the US approached the COVID-19 pandemic. We plan to do this from two different directions. The first would be to analyze from the perspective of the government and the containment measures adopted to prevent the spread of COVID. The second will be to look at it from the perspective of the citizens and how their behavior in terms of their search trends, mobility levels change through time. This will enable the viewer to answer questions such as:

* Has COVID-19 infected citizens throughout the country uniformly? Have certain states been more affected?
* How has the rapid spread of the COVID-19 disease affected the existing medical infrastructure in the US? How did the Medical Infrastructure of the US cope with the COVID-19 pandemic?
* Does a strict government policy response (closing schools and workplaces, canceling public events, etc.) entail lower morbidity?
* Can we predict the spread of infection to help governments plan and scale up their resources ahead of time?
* Is there a correlation between user searches on vaccination related information and spread of COVID cases?


## Related Work


The article [“Covid Overload: US Hospitals Are Running Out of Beds for Patients”](https://www.nytimes.com/2020/11/27/health/covid-hospitals-overload.html) from The New York Times describes multiple scenarios of hospitals teeming with record numbers of Covid patients and its effect on other patients that seek care. Another article, [“How Full Are Hospital I.C.U.s Near You?”](https://www.nytimes.com/interactive/2020/us/covid-hospitals-near-you.html) provides an interesting visualization which gives the reader an insight into the state of ICU beds across the country. These articles further strengthen the fact that having appropriate medical facilities is extremely important! In [this](https://www.webmd.com/lung/news/20220114/why-covid-tests-take-so-long) article, Kathleen Doheny talks about the reasons for Covid test results taking a long time and mentions that though timely results are important, we should not sacrifice speed for accuracy!
In [this](https://www.sciencedirect.com/science/article/pii/S002248042030812X?casa_token=eoSnvAWt7G8AAAAA:rUOY3l0GtR_R1j19eM9MPSKotPCNKiPb2Kl-qtsnf7D2IJKV6NtMWcVPuRpnl3p-xMsOGnIBuw) work, the authors carry out an analysis of COVID-19 mortality rates and conclude that they are likely affected by multiple factors, including hospital resources, personnel, and bed capacity. Inspired by these works, we have built our Medical Infrastructure dashboard to allow users to explore these parameters and gain insights into how the US medical infrastructure coped with the COVID-19 pandemic. 




## Methods


### Exploratory Data Analysis

In the exploratory data analysis phase, we first aim to visualize the trend of various statistics about COVID-19 so that we get an initial understanding about how the United States as a whole has been impacted by the pandemic throughout the last two years. To achieve this, we use the [Epidemiology table](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-epidemiology.md) under the [COVID-19 Open Data dataset](https://github.com/GoogleCloudPlatform/covid-19-open-data) archived by Google and extract columns including daily confirmed cases, daily deceased cases, and daily tested cases. We drop the daily recovered column here due to insufficient per-state samples. In addition, we join the [Epidemiology table](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-epidemiology.md) with the [Hospitalization table](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-hospitalizations.md) and [Vaccination table](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-vaccinations.md) on the region key in order to get the daily hospitalized and vaccinated data. With these time series data aggregated by different states, we provide an interactive line chart that allows users to select the region and the types of statistics they want to visualize.

![alt text](https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/images/Exploratory%20Data%20Analysis%20%E2%80%93%20COVID-19%20Trend.png)


With a basic understanding of the overall COVID trend in the US over the last two years, we next want to answer the questions: “Has COVID-19 infected citizens throughout the country uniformly? Have certain states been more affected?” In the second section, we present two main components: (1) a map plot that visualizes the number of COVID statistics (e.g. daily confirmed) across different states, and (2) a bar plot that sorts and compares cumulative COVID statistics in different states. Both plots represent comparisons between different states on the selected month. The map plot uses circle marks to indicate the magnitude of the selected parameter, with darker-colored and larger circles representing a higher number of cases. This gives us a geographical sense of which parts of the US are affected more by COVID. The bar plot then directly displays which states control the pandemic the best or worst in the US. Note that we choose to use cumulative and percentage data for the bar plot instead of the monthly average and absolute number that we use for map plot. This is because cumulative data provides a more holistic view on which states are affected the most, while percentage data such as confirmed rate instead of confirmed cases gives us an unbiased result as it accounts for the fact that states with larger populations naturally would have more cases.

![alt text](https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/images/Exploratory%20Data%20Analysis%20%E2%80%93%20Comparison%20across%20States.png)

After knowing which states are affected the most or are controlling the pandemic the best, we need to know what attributes of those states contribute to such results. Here we select COVID confirmed rate (cumulative confirmed cases divided by population) and death rate (cumulative death cases divided by population) as target parameters and try to find which columns in the datasets correlate to them. In this step, we use tables include [Vaccinations](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-vaccinations.md), [Geography](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-geography.md), [Health](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-health.md), and [Weather](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-weather.md). We present three plots: (1) a pie chart that shows the distribution of different vaccine brands in different regions, (2) a heat map that shows the correlation between confirmed / death rate, and how many percent a state distributes each vaccine brand, (3) a heat map that shows the correlation between confirmed / death rate and weather / population / geography / health attributes.

![alt text](https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/images/Exploratory%20Data%20Analysis%20%E2%80%93%20Correlation%20Analysis.png)

In the last step of our exploratory data analysis, we show how the historical trend of citizens mobilities including “Retail and Recreation”, “Grocery and Pharmacy”, “Parks”, “Transit stations”, and “Workplaces”, affect or were affected by the trend of confirmed COVID cases. Line chart is chosen as the visualization technique again and we allow users to switch on / off the types of mobility data they want to see.

![alt text](https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/images/Exploratory%20Data%20Analysis%20%E2%80%93%20Mobility%20Trend.png)


### Medical Infrastructure Dashboard

It is important to pay attention to the overall capacity of the nation’s public health system as it protects and promotes the health of all people in all our communities. Public health infrastructure enables every level of government to prevent disease, promote health, prepare for and respond to both emergency situations and ongoing challenges. Through a set of interesting visualizations and statistics, we try to answer the question: How did the Medical Infrastructure of the US cope with the COVID-19 pandemic? And through this process, we attempt to gain insights regarding possible strategies that can be adopted in the event of a future pandemic.
The first portion of this dashboard deals with the variation in hospital bed utilization in terms of the proportion of in-patient beds and ICU beds used. We get this data from the hospital capacity dataset from [U.S. Department of Health and Human Services](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh). From this dataset, we calculated In-patient bed utilization = inpatient_beds_used/total_inpatient_beds and ICU-bed utilization = staffed_adult_icu_bed_occupancy/total_staffed_adult_icu_beds. Using available data, we also calculated additional metrics such as Hospital bed utilization by COVID patients, ICU bed utilization by COVID patients. Using all this data, we plot a mini dashboard which displays the change in bed utilization across states through time on a map and also displays detailed metrics numerically per state. 


#### Medical Infrastructure Dashboard – Bed utilization


As seen from the image, we make use of color and point size to indicate utilization and the number of cases simultaneously. This allows us to display more than one feature simultaneously and gives the user an idea of how many hospital beds were as the number of cases increased. This enables the user to identify certain states that they might want to look into deeper and can focus on in the coming visualizations.

Next, we dive deeper into Hospital bed utilization by splitting it into ICU bed utilization and in-patient bed utilization. We explore how these two parameters affect the COVID-Deaths on a per state basis. We also link how staff shortages in hospitals affect COVID deaths by creating connected charts where the user can select an interval from the chart on the left to see the corresponding region for the chart on the right for a more fine-grained look. 


#### Medical Infrastructure Dashboard – Bed Shortage

During a pandemic, Testing plays a key role in the efforts to contain and mitigate the pandemic by identifying infected individuals to help prevent further person-to-person transmission of the infection. In the next part of our dashboard, we try to gain insight into whether all covid test sample results were returned in a reasonable amount of time. This is done by a simple line chart across time that showcases the number of samples taken and the number of test results returned. The user can also interact with the chart via zoom and pan. This enables the user to see how much pressure was on the testing facilities and whether adequate testing infrastructure is present in every state. 


#### Medical Infrastructure Dashboard – Testing Infrastructure

We next focus on the spread of vaccination and COVID-19 therapeutic facilities across the country. Vaccines reduce a person's risk of contracting the virus that causes COVID-19. Hence, we wanted to visualize how these facilities are present across the country and what is the average time taken to reach the nearest one. This allows the user to see how different states approached vaccination and medicine distribution across the state and will allow insights to be gained regarding good distribution strategies in the event of a future pandemic. We make use of a map chart for this section since it makes it easy to perceive the spread geographically.


#### Medical Infrastructure Dashboard – Vaccination Map

#### Medical Infrastructure Dashboard – Vaccination travel

The final portion of the Medical Infrastructure dashboard involves a COVID-19 daily cases forecasting model. We try to explore how effective forecasting methods can be and whether the predicted values are accurate enough to be able to be used in case of a future pandemic. We try to predict the cases 7 days in the future as well as 30 days in the future. This is done to check how effectively the forecasting models can be used ,i.e whether it can be used for procuring immediate requirements like food (if it can predict cases 7 days ahead) and if it can also be used for procuring long term requirements like ICU beds (if it can predict cases 30 days ahead). We also display the most important features in forecasting to allow the user to gain some interesting insights about which previous days are most important in predicting the future cases! 

Medical Infrastructure Dashboard – Forecasting Plot 
Medical Infrastructure Dashboard – Forecasting Features
Through these visualizations we empower the viewer with insights into the state of the medical infrastructure of the US through the course of the COVID-19 pandemic. 

### Search Trend Dashboard

The internet often serves as the first point of information for many people today. Building on this fact, we try to answer an important question: whether trends in search patterns can be helpful in detecting COVID 19 outbreaks. For this, we make use of the COVID-19 Search Trends symptoms dataset. This dataset collates the volume of Google searches for a broad set of symptoms, signs and health conditions related to COVID 19. It provides an integer trend value for each search string, which reflects the volume of Google searches for that search string. This trend value is captured on a daily basis. More information pertaining the curation of this dataset can be found on this [page](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-search-trends.md).

Using this dataset we build the Search Trend Dashboard, which enables users to analyze what search strings are most effective in hinting towards a rise of COVID 19 cases in the future, and whether this is consistent across different regions in the United States. We do so by calculating the correlation between the search trend values and the number of COVID 19 cases, and add capability to perform this analysis for different regions in the United States. To allow analysis against future rise of cases we introduce a parameter `lag`, which calculates the correlation between search trend values and the number of cases `lag` days in the future. Intuitively, we expect a positive correlation between these two, since a higher search trend value should indicate a rise in cases.

As a preprocessing step, we filter out the search strings in the dataset and use only the set of symptoms that are associated with COVID 19 [(as documented by CDC)](https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html). These search strings include `fever`, `chills`, `cough`, `shallow breathing`, `shortness of breath`, `fatigue`, `headache`, `cluster headache`, `sore throat`, `nasal congestion`, `nausea`, `vomiting`, `diarrhea`, `chest pain`, `burning chest pain`, and `back pain`. Furthermore, we normalize the trend values for each string to a scale of 0 to 1, for ease of visualization and analysis. We extract the number of cases from the [Epidemiology dataset](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-epidemiology.md) available via [COVID 19 open data](https://health.google.com/covid-19/open-data/raw-data). The data is aggregated on a daily basis, and the analysis is done for every day between 1st January 2021 and 31st December 2021.

Our primary visualization is a choropleth map, where the color intensity indicates the correlation between search trend and cases for the selected parameters. The dashboard allows two configurable parameters: (i) the set of search strings to run the analysis on, and (ii) the number of days in the future to make the comparison with. When multiple search strings are selected, we aggregate the data across all the selected search strings. This can allow users to explore whether a combination of search strings is a better indicator instead of just an individual one.


#### Search Trend Dashboard – Choropleth map


#### Search Trend Dashboard – Search history

Each state in the map is selectable, and upon selection the analysis is recomputed for that particular state. Additionally, we also visualize the raw data used for the analysis (number of cases over time, and normalized search trend values over time) using a twin y axis line plot. To help users keep track of the parameters they have explored in a session, we maintain a search history line plot. This presents the parameters that the users have selected (region, lag, and search strings), and the resulting correlation.
Government Response Dashboard

Different governments have adopted different policies to tackle the rise of COVID 19 cases. With the Government Response Dashboard, we enable users to explore which policies have been the most effective in reducing the rise in cases, and whether this is consistent across different regions in the United States or not. We make use of the The Oxford Covid-19 [Government Response Tracker](https://www.bsg.ox.ac.uk/research/research-projects/covid-19-government-response-tracker) (OxCGRT) dataset for this purpose.

OxCGRT collects systematic information on policy measures that governments have taken to tackle COVID-19. These responses are categorized into different indicators types, which include:
Containment and closure policies (such as school closures and restrictions in movement)
Economic policies (such as income support to citizens and debit relief)
Health system policies (such as facial coverings)
Vaccine policies

Each indicator is assigned an integer value, reflecting the extent of government action. A higher value indicates a more extensive policy (such as more stringent health system policies,  or higher economic relief to citizens). More information on how these values are calculated can be found on the [OxCGRT page](https://www.bsg.ox.ac.uk/research/research-projects/covid-19-government-response-tracker).

To understand whether policies have been effective, we calculate the correlation between the indicator value and the number of cases. Intuitively, we expect a negative correlation between these two, since a stronger government response should entail lower morbidity. One important point to note is that government policy decisions, even the most extensive ones, often take time in achieving their desired results. To incorporate this, we introduce a variable `lag`, which enables a comparison between the policy indicator value and number of cases `lag` days in the future.

As a preprocessing step, we normalize the indicator values for each policy  to a scale of 0 to 1, for ease of visualization and analysis. We extract the number of cases from the [Epidemiology dataset](https://github.com/GoogleCloudPlatform/covid-19-open-data/blob/main/docs/table-epidemiology.md) available via [COVID 19 open data](https://health.google.com/covid-19/open-data/raw-data). For both datasets, the data is aggregated on a daily basis, and the analysis is done for every day between 1st January 2021 and 31st December 2021.

Similar to the Search Trend Dashboard, our primary visualization is a choropleth map, where the color intensity indicates the correlation between search trend and cases for the selected parameters. The dashboard allows two configurable parameters: (i) the set of policy indicator values to run the analysis on, and (ii) the number of days in the future to make the comparison with. When multiple indicators are selected, we aggregate the data across all the selected indicators. This can allow users to explore whether a combination of policy decisions is better than just an individual one.


#### Government Response Dashboard – Choropleth Map


#### Search Trend Dashboard – Search history

In this dashboard as well, each state in the map is selectable, and upon selection the analysis is recomputed for that particular state. Additionally, we also visualize the raw data used for the analysis (number of cases over time, and normalized policy indicator values over time) using a twin y axis line plot. To help users keep track of the parameters they have explored in a session, we maintain a search history line plot. This presents the parameters that the users have selected (region, lag, and policies), and the resulting correlation.

## Results

### Exploratory Data Analysis

With the interactive dashboard in the Exploratory Data Analysis page, we provide a storyline on what questions users can answer by playing around with the data visualizations. In the following paragraphs, we will go through each of the questions and discuss what the data has told us.

1. How have COVID statistics varied in the different states in the US?
	From what we can see on the dashboard, there are in general three major spikes of daily confirmed cases: October 2020 - February 2021, July 2021 - October 2021, and December 2021 - February 2022. These three periods can be mapped to the Alpha, Delta, and Omicron variants. Among the three spikes, the Omicron period has the largest number of confirmed cases, however, the death cases didn’t go up proportionally. This can be attributed to the fact that most of the people already got fully vaccinated by April 2021, as the plot shows.
	In terms of the comparison between different states, we can notice from the bar plot that California, Illinois, and Washington had the earliest confirmed cases when the pandemic started in January 2020. By May 2020, the virus had already spread to the whole country with New York being the most seriously affected. In terms of confirmed rate, Rhode Island, Utah, Alaska, North Dakota, and South Carolina have the highest number (> 30%) by April 2022, while Oregon, DC, Maryland, Hawaii, and outlying islands are less than 18%. Other states having anomalous statistics include Arizona, Kentucky, and Guam, which have the highest death rate, hospitalized rate, and fully vaccinated rate respectively.

2. How does the proportion of different vaccines affect COVID confirmed / death rate in that region?
	From the pie plot and the first heat map plot, we can find out that Pfizer is the most used vaccine brand in the US. The US government distributes 59% Pfizer, 37% Moderna, and 4% other vaccines. Interestingly, the more a state government favors Pfizer over other brands, the better that state handles the pandemic. The percentage of Pfizer vaccine is medium-to-strong negatively correlated to both confirmed rate and death rate, with coefficients 0.43 and 0.57.

3. How are geography, population, and health parameters correlated to COVID confirmed / death rate?
	By the second heat map plot that analyzes the correlation between state attributes (population density, life expectancy, vaccination facility access, elevation, rainfall, humidity, temperature) with COVID confirmed rate and death rate, we have two interesting findings. First, life expectancy is medium-to-strong negatively correlated to COVID confirmed rate and death rate, which can be explained as COVID affects more on regions who already have relatively unhealthy populations or lack of medical infrastructure. Second, average temperature is negatively correlated to the confirmed / death rate in a region.

4. How does the mobility of citizens change over time?
	Over the last two years, most of the mobility categories – “Retail and Recreation”, “Grocery and Pharmacy”, and “Transit Stations” have the same trend that whenever there is a spike for the number of confirmed cases, we see plunges in those mobility categories. However, “Workplaces” mobility remains to go up after only the first plunge.

### Medical Infrastructure Dashboard
One interesting observation is the relation between staff shortages and deaths. As we see more hospitals reporting shortage of staff (the points becoming more reddish), we shortly see a sharp incline in the deaths. This shows that it is of utmost importance to have sufficient availability of medical staff as well in the event of a future pandemic. This is something that needs to be planned out carefully as you cannot simply 'procure' more medical staff in a short time! 
Another observation was that when the ICU bed utilization crosses the 0.7 ~ 0.75 mark, there is a significant increase in the number of deaths shortly thereafter. This is seen in almost every state and hence can be used as a threshold in the event of a future pandemic. We should not allow the utilization of ICU beds to cross the 0.75 mark and procure enough ICU beds or plan out effective upscaling strategies to prevent this from happening in the event of a future pandemic.
 

#### Medical Infrastructure Dashboard – Effect of shortage

It was also interesting to see that during the peaks of COVID, the number of test results returned was significantly lower than the number of samples taken, indicating that the testing facilities were put under immense pressure by the pandemic. While most of the states were initially able to keep up with the testing demands, almost all the states could not handle the testing demands during the last peak (Jan - Apr 2022). This is another crucial dimension where the medical infrastructure should be scaled up. It is equally important to have enough labs that can process all the test samples and return their results within a finite amount of time. Timely results will help curb the spread of infection as infected individuals can be alerted to stay quarantined and prevent the spread further. 

Medical Infrastructure Dashboard – Testing Infrastructure results
Further, from our experiments with the forecasting model, we were able to see that a simple model that only considers historical cases data is able to perform decently well in forecasting the cases for 7-days from the current day except for the peaky regions where there is a lag. But predicting cases 1 month into the future with a simple historical case-based model is difficult. This tells us that using a model to predict 7 days into the future can help us procure essentials in a short term such as food and water but it is too short a duration for expanding essentials such as hospital beds, medical staff etc. This can possibly be overcomed by using a more sophisticated model and the government could explore this avenue further by bolstering the strength of forecasting models using features such as mobility, regulations in place, deaths, hospitalizations etc.

#### Medical Infrastructure Dashboard – Forecasting Model Comparison 1 & 2

The user can dive deep into other visualizations and have a look at our application for more insights!
Search Trend Dashboard

As a case study, we try to check the correlation between the trend values for the search string “fever” and the rise of COVID 19 cases in the state of California. The first figure illustrates the correlation between the two with lag = 0 days, while the second illustrates the correlation between the trend value and cases 9 days in the future (lag = 9). We can clearly see that there is a stronger correlation (0.657) in the second cases, indicating that trend values for the search string “fever” can be an indicator of a rise in COVID 19 cases in the near future. This can be useful for authorities for preemptively making decisions (such as making provisions for dealing with cases).



#### Correlation between fever and cases with lag = 0 days for California


#### Correlation between fever and cases with lag = 9 days for California



### Government Response Dashboard

As a case study, we try to check the correlation between government response for the policy decisions on “facial coverings” and the rise of COVID 19 cases. The first figure illustrates the correlation between the two with lag = 0 days, while the second illustrates the correlation between the two 45 days in the future (lag = 45). We can clearly see that there is a highly negative correlation in the second cases, indicating that having extensive policies pertinent to facial coverings can be effective in reducing the number of COVID 19 cases.

#### Correlation between facial coverings and cases with lag = 0 days


#### Correlation between facial coverings and cases with lag = 45 days



## Discussion

During exploratory data analysis, there are several findings of our dashboard that provide interesting insights regarding the trend of COVID across different states and thus are worth discussing. For example, as we point out in the Results section, hotter regions tend to control COVID better. Although this result does not sound straightforward, it is actually consistent with some other [research papers](https://www.nature.com/articles/s41598-021-87803-w) that mention Coronavirus transmits slower in regions with higher average temperatures. Another interesting yet peculiar result is that Workplace mobility didn’t go down whenever there was a spike in COVID cases like other mobility categories did. This can be explained by the fact that more and more companies are asking their employees to be back to office. Such company policies are not easy to change frequently once a decision is made because the cost to relocate employees is high.

Through the Medical Infrastructure dashboard the audience can see that there is high pressure on the medical sector to procure a large number of beds quickly due to the large increase in the number of COVID cases. We can also see that in a majority of the states, as soon as the ICU bed utilization crosses the ~75% barrier, the number of deaths see a sharp incline. This tells the audience about the importance of having pre-defined strategies in place that allow hospitals to quickly increase the ICU bed availability, before it crosses the 75% barrier, in the event of a future pandemic. The audience is also able to see that the testing infrastructure is another important factor during a pandemic and there should be an adequate number of labs that can process all the test samples and return their results within a finite amount of time to curb the spread of infection. Additionally, the forecasting model with a 7-day step size looks to be a promising direction to invest more resources in to strengthen its performance to accurately predict cases. This also strengthens the fact that using intelligent algorithms to forecast factors such as cases, deaths etc. can help in procuring required resources beforehand to prevent any shortage. 

From the search trend dashboard, we can see that there are strong positive correlations between certain search terms (for instance fever and headache) and the number of COVID 19 cases 6 to 10 days in the future. This is a critical and expected insight, as people usually resort to internet searches in an attempt to know more about symptoms when they first fall sick. It usually takes 6-10 days for COVID 19 symptoms to get severe, and for patients to require professional medical care.  This dashboard can be of great help to government bodies, which can preemptively make emergency provisions and scale up their medical infrastructure when they see a spike in certain search terms. 

The government response dashboard shows a strong negative correlation between the extent of many government policy decisions (such as more stringent facial covering policies and restrictions on gatherings) and COVID 19 cases 40-50 days in the future. Such a delay (in the number of days) is expected, since policies often take time in achieving their desired results. However, we do notice that this correlation is not the same across different regions in the United States, which hints towards other factors playing a role. 

## Future Work

In this project, we only use the COVID-19 dataset in the US as we aimed to cut down the scope to cover more in-depth analysis with interactive visualization components. With our preliminary results, our techniques are easily transferable to cover a global dataset.  Besides, in the exploratory data analysis phase we are comparing data only in a per-state granularity. An interesting future work will be to re-perform our works on a finer regional granularity such as per-city or per-neighborhood. This will surely give us a more abundant dataset to compare with and thus lead to a higher quality result when finding attributes that are correlated with the COVID confirmed rate.

The Medical Infrastructure dashboard could be extended to include visualizations and details about the number of personnel(doctors and health staff) working in every state and whether they have had to do extra hours during the pandemic to overcome the staff shortage. Another interesting avenue to explore would be how the advancements in the healthcare industry in terms of the funding for research and development were affected by the pandemic. It would also be interesting to explore how the immunization rates for other vaccines were affected by the ongoing pandemic and if there was any change in the level of spread of seasonal communicable diseases.

The search trend dashboard currently focuses on a small set of search strings, which are common COVID 19 symptoms. In the future we would like to extend this to other pertinent search terms, such as search terms related to vaccinations. Furthermore, the current analysis is on a state level; in the future we would like to extend this to smaller regions (such as individual counties). This can help government bodies identify smaller, more manageable regions which are at a risk of outbreak. The government response dashboard covers different policies, but their results are not consistent across different states. This hints towards other factors playing a role, which should be explored in the future. Furthermore, currently selecting multiple policies simply aggregates the data for selected policies; there could be a polynomial relationship between different policies and a decrease in COVID 19 cases, which cannot be captured by our tool. We hope to explore these complex relationships between different policy decisions in the future.
