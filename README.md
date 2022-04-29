# CMU Interactive Data Science Final Project

* **Online URL**: https://share.streamlit.io/cmu-ids-2022/final-project-dunder-mifflin-paper-company/main
* **Team members**:
  * Contact person: buk@andrew.cmu.edu
  * rmampill@andrew.cmu.edu
  * heweil@andrew.cmu.edu
  * kushagr2@andrew.cmu.edu

## Title
COVID-19 Dashboard

## Summary Image
![summary image](https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/images/summary-image.png)

## Abstract
The COVID-19 pandemic has impacted society in various ways, affecting almost every single aspect of our daily lives. Though COVID-19 is a crisis worldwide, there have been stark differences in how various regions have approached curbing the spread of the infection. Every government has uniquely responded to this pandemic in terms of their masking policies, early vaccinations, shutting down schools and workplaces, restricting public transport, etc. Variations in these responses are dependent on the distinctive institutional arrangements, political and geographical factors, and cultural orientation of each state, and thus, there is no One-Size-Fits-All strategy. However, it can also be argued that such distinct policies are a result of the fact that we as a society were grossly under-prepared to handle a pandemic of this scale. It is vital that we now analyze the different policies taken to be better prepared in the event of a future pandemic.

In this project, we focus on analyzing how different states in the US approached the COVID-19 pandemic. We plan to do this from two different directions. The first would be to analyze from the perspective of the government and the containment measures adopted to prevent the spread of COVID. The second will be to look at it from the perspective of the citizens and how their behavior in terms of their search trends, mobility levels change through time. This will enable the viewer to answer questions such as:

* Has COVID-19 infected citizens throughout the country uniformly? Have certain states been more affected?
* How has the rapid spread of the COVID-19 disease affected the existing medical infrastructure in the US? How did the Medical Infrastructure of the US * cope with the COVID-19 pandemic?
* Does a strict government policy response (closing schools and workplaces, canceling public events, etc.) entail lower morbidity?
* Can we predict the spread of infection to help governments plan and scale up their resources ahead of time?
* Is there a correlation between user searches on vaccination related information and spread of COVID cases?


## Links
* Video: https://www.youtube.com/watch?v=NzRktLDfCC8
* Report: https://github.com/CMU-IDS-2022/final-project-dunder-mifflin-paper-company/blob/main/Report.md

## Running Instructions
```
pip3 install -r requirements.txt
streamlit run streamlit_app.py
```

## Work distribution

* Kushagra Singh: Search Trend Dashboard + Government Response Dashboard
* Ruben: Medical Infrastruture Dashboard -> Data Wrangling, Vaccination Facilities, Forecasting Model
* Bharani: Medical Infrastructure Dashboard -> Data processing, Hospital Utilization, Testing Infrastructure
* He-Wei Lee: Exploratory Data Analysis


## Deliverables

### Proposal

- [ ] The URL at the top of this readme needs to point to your application online. It should also list the names of the team members.
- [ ] A completed [proposal](Proposal.md). Each student should submit the URL that points to this file in their github repo on Canvas.

### Sketches

- [ ] Develop sketches/prototype of your project.

### Final deliverables

- [ ] All code for the project should be in the repo.
- [ ] Update the **Online URL** above to point to your deployed project.
- [ ] A detailed [project report](Report.md).  Each student should submit the URL that points to this file in their github repo on Canvas.
- [ ] A 5 minute video demonstration.  Upload the video to this github repo and link to it from your report.
