import time
import datetime
import os
import sqlite3
import random


# create a directory

def create_lake():
    parent_dir = str(os.getcwd())
    new_dir = 'Lake'

    lake_path = os.path.join(parent_dir, new_dir)
    try:
        os.mkdir(path=lake_path)
    except:
        pass

    return lake_path



def insert_into_sqlite(**context):

    # get the resulting updated players list returned from the first task
    players_list = context['ti'].xcom_pull(task_ids='Data_collection')

    # Get the lake path or create if not exists
    lake_path = create_lake()

    num = random.randint(1, 100000000)
    date = str(datetime.date.today())
    

    db = f'raw_nba_data{date}_{num}.db'

    database = os.path.join(lake_path, db)
    print(database)

    # creating the database

    conn = sqlite3.connect(database)

    cursor = conn.cursor()

    # create a table
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS players (id INT AUTO_INCREMENT, name VARCHAR(50) PRIMARY KEY, player_link VARCHAR(100), team VARCHAR(50), team_link VARCHAR(100), age INT, number VARCHAR(50), position VARCHAR(50), height FLOAT, weight INT, last_attended VARCHAR(50), country VARCHAR(50), birth_date DATE, experience VARCHAR(50), draft VARCHAR(50), ppg FLOAT, rpg FLOAT, apg FLOAT, pie FLOAT)'
    )

    # Insert Values from the completed players list into the table

    for p in players_list[0:2]:
        cursor.execute('INSERT INTO players(name, player_link, team, team_link, age, number, position, height, weight, last_attended, country, birth_date, experience, draft, ppg, rpg, apg, pie) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(p.name, p.link, p.team, p.team_link, p.age, p.number, p.position, p.height, p.weight, p.last_attended, p.country, p.birth_date, p.experience, p.draft, p.ppg, p.rpg, p.apg, p.pie))

    conn.commit()
    conn.close()

