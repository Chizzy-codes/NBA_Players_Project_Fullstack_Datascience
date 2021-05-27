from airflow import DAG
from airflow.operators.python import PythonOperator

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import re
import MySQLdb
import sqlalchemy as sal
import pandas as pd
import time
import datetime
from datetime import timedelta, datetime
import os
import sqlite3
import random
from selenium.webdriver.chrome.options import Options

# import the python scripts and functions
import data_collection
from data_collection import updated_players_list
import insert_into_lake
from insert_into_lake import insert_into_sqlite, create_lake
import data_etl
from data_etl import etl

# instantiate project specific variables
# chrome driver path; change this to the path of the chrome driver exe on your system
CHROME_PATH = os.environ.get("CHROMEDRIVER_PATH")

# database details; edit this
DATABASE = {'host': 'localhost',
'user': 'admin',
'password': 'admin',
'db': 'nba'
}



# Define default and Dag specific arguements

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021,5,2),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delays': timedelta(minutes=1)
}



# Instantiate a DAG

dag = DAG('nba', default_args=default_args,  description="Dag for the nba pipeline",  schedule_interval = '0 12 * * 6')



# Define three tasks created by instantiating the python operators

task1 = PythonOperator(
    task_id = 'Data_collection',
    python_callable = updated_players_list,
    op_kwargs = {'driver_path': CHROME_PATH},
    dag=dag
)

task2 = PythonOperator(
    task_id = 'Insert_into_lake',
    python_callable = insert_into_sqlite,
    dag=dag
)

task3 = PythonOperator(
    task_id = 'Data_ETL',
    python_callable = etl,
    op_kwargs = {'my_database': DATABASE},
    dag=dag
)


# Setting up task dependencies
# set task2 to depend on task1 running successfully to run
task1.set_downstream(task2)

# set task3 to depend on task2 running successfully to run
task2.set_downstream(task3)

