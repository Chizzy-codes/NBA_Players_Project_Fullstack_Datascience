# NBA_Players_Project_Fullstack_Datascience
A Full-Stack, End to End Data Science Project implemented with data i got from the NBA Website.


## Project Aim
The aim of this was to simplify and limit the time it takes for an NBA fan or a curious individual to find out useful facts about the current active players in the NBA.


## DATA PIPELINE
The data pipeline for this process was built and scheduled (weekly) using Apache Airflow (https://airflow.apache.org/). After each successful run (every week) the data warehouse is updated using the most recent data from the data lake.

## Project Workflow
The first component of the workflow was data collection. I used the NBA website as my data source and proceeded to gather data on all active players via web scraping (using requests, beautifulsoup4 and selenium). This includes players name, team, position, date of birth, nationality, last attended school, height, weight, age, current basketball stats for the ongoing season, etc.

This data is inserted into a sqlite3 database file and stored in a data lake; which in this case is a simple file folder (Second Component).

The third component extracts the most recent entry to the data lake, performs a custom ETL (Extraction, Transformation and Loading) process and Feature Engineering on the data. The processed data is then stored or used to update my data warehouse; a remote PostgreSQL Database instance on elephantsql.com. 


## Machine Learning
I also developed an outlier detection machine learning model to identify outlier players present in the database (Jupyter Notebook nbviewer link: https://nbviewer.jupyter.org/github/Chizzy-codes/NBA_Players_Project_Fullstack_Datascience/blob/master/jupyter_notebook/project_notebook.ipynb) 


## DATA PRODUCT
The final product was an Apache Superset Dashboard which i published on Heroku. The dashboard provides users with an intuitive, interactive and simple one stop shop for finding out the most important information on the current active players in the NBA. Check it out here https://nba-superset.herokuapp.com/superset/dashboard/4/

### ENJOY!!!
