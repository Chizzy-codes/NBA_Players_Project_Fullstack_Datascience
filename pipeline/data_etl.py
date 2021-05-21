import time
import datetime
import os
import sqlite3
import pandas as pd
import MySQLdb, psycopg2
from sqlalchemy_utils import create_database, database_exists
import sqlalchemy as sal


def get_lake_path():
    parent_dir = str(os.getcwd())
    new_dir = 'Lake'

    lake_path = os.path.join(parent_dir, new_dir)

    return lake_path


def remove_spaces(x):
    new = x.split(' ')
    new = [x for x in new if x != '']
    try:
        word = new[0] + ' ' + new[1] + ' ' + new[2]
    except:
        try:
            word = new[0] + ' ' + new[1]
        except:
            word = new[0]
    return word


def correct_spelling(x):
    if x == 'Foward':
        return 'Forward'
    elif x == 'Foward-Center':
        return 'Forward-Center'
    else:
        return x


def etl(my_database):

    # get lake path
    lake_path = get_lake_path()


    username = my_database.get('user')
    password = my_database.get('password')
    host = my_database.get('host')
    database_name = my_database.get('db')
    #port = my_database.get('port')
    
    # Extract needed data from the data lake

    # find the last added file
    file_list = []
    t = 0
    filename = ''

    for file in os.listdir(lake_path):
        time_stored = list(os.stat(path= os.path.join(lake_path, str(file))))[-1]
        file_list.append((file, time_stored))
        
        if t < time_stored:
            t = time_stored
    for f in file_list:
        if f[1] == t:
            filename = os.path.join(lake_path, f[0]) # file path

    # read data into pandas dataframe
    conn = sqlite3.connect(str(filename))

    query = pd.read_sql_query('SELECT * FROM players', con=conn)

    data = pd.DataFrame(query, columns=['name', 'player_link', 'team', 'team_link', 'age', 'number', 'position',
                                        'height', 'weight', 'last_attended', 'country', 'birth_date', 'experience', 'draft', 'ppg', 'rpg', 'apg', 'pie'])

    data.country = data.country.apply(lambda x: 'United States' if x == 'USA' else x)

    
    # remove the excess spaces in the team names
    data.team = data.team.apply(remove_spaces)

    # Replace rookie with 0
    data.experience = data.experience.apply(lambda x: 0 if x=='Rookie' else x) 

    # Change the experience column to integer type
    data.experience = data.experience.astype('int')

    # first convert birth_date to a datetime object
    data.birth_date = pd.to_datetime(data.birth_date)

    # Extracting birth year from the birth_dtae column

    data['birth_year'] = data.birth_date.dt.year

    # extract draft year and draft pick from draft

    data['draft_year'] = data.draft.apply(lambda x: x.split(' ')[0])
    data['draft_pick'] = data.draft.apply(lambda x: x.split(' ')[-1])

    # identify the age at which players began their nba career

    # change experience to type int
    data.experience = data.experience.astype('int')

    data['age_drafted'] = data.age - data.experience

    # identify the players body mass index (bmi)

    data['bmi'] = data.weight / (data.height * data.height)

    # Correct spellings in the position columm
    data.position = data.position.apply(correct_spelling)


    # drop birth_date and draft

    data.drop(['draft', 'player_link', 'team_link', 'number'], axis=1, inplace=True)



    # Move processed data into the data warehouse which in this case is a MySQL Database

    # It is important to note which database your are making use of and make necessary adjustments to the create engine code
    # Make sure your database server is running first. Restart if needed. Connect to mysql database 

    # create engine MySQL
    #engine = sal.create_engine(f'mysql+mysqldb://{username}:{password}@{host}') # add the port if your are not connecting via localhost

    # create engine PostgreSQL
    engine = sal.create_engine(f'postgresql+psycopg2://{p_username}:{p_password}@{host}/nba')

    # Create a new database MySQL
    #engine.execute('CREATE DATABASE IF NOT EXISTS nba')

    # for postgresql
    if not database_exists(engine.url):
    create_database(engine.url)


    # Use nba database (for MySQL)
    #engine.execute('USE nba') # Auto commits

    # Insert into MySQL using pandas
    # If exist is set to replace so as to update the table to its current state in recent runs
    engine.execute('DROP TABLE IF EXISTS players')
    data.to_sql('players', con=engine, index=False, if_exists= 'replace')

    engine.dispose()