import sqlite3
import os
#_______________________________________________________________________________________________________________________

def create_history_table():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, date TEXT
                              , file_name TEXT, url TEXT, location TEXT);''')

def create_config_table():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, location TEXT, start_time_hour INTEGER
                              , start_time_minute INTEGER, end_time_hour INTEGER, end_time_minute INTEGER);''')
        if not connection.execute(f'select * from config WHERE id = 1;').fetchone():
            connection.execute(
                'INSERT INTO config (location, start_time_hour, start_time_minute, end_time_hour, end_time_minute) VALUES (?, ?, ?, ?, ?);'
                , (os.getcwd(), 0, 0, 12, 0))


def add_to_history(date, file_name, url, location):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('INSERT INTO history (date, file_name, url, location) VALUES (?, ?, ?, ?);'
                           , (date, file_name, url, location))

def get_all_history():
    connection = sqlite3.connect('Database.db')
    with connection:
        return connection.execute('SELECT * FROM history;').fetchall()

def clear_history():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('DELETE FROM history;')

def set_config(location, start_time_hour, start_time_minute, end_time_hour, end_time_minute):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute(f'DELETE FROM config WHERE id = 1;')
        connection.execute(
            'INSERT INTO config (location, start_time_hour, start_time_minute, end_time_hour, end_time_minute) VALUES (?, ?, ?, ?, ?);'
            , (location, start_time_hour, start_time_minute, end_time_hour, end_time_minute))

def reset_config():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute(f'DELETE FROM config WHERE id = 1;')
        connection.execute(
            'INSERT INTO config (location, start_time_hour, start_time_minute, end_time_hour, end_time_minute) VALUES (?, ?, ?, ?, ?);'
            , (os.getcwd(), 0, 0, 12, 0))

def get_config():
    connection = sqlite3.connect('Database.db')
    with connection:
        return connection.execute(f'select * from config WHERE id = 1;').fetchone()
#_______________________________________________________________________________________________________________________

create_history_table()
create_config_table()