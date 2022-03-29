import sqlite3
import os

#hitory_________________________________________________________________________________________________________________
def create_history_table():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, date TEXT
                              , file_name TEXT, url TEXT, location TEXT);''')

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

#config_________________________________________________________________________________________________________________
def create_config_table():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, location TEXT
                              , start_time_hour INTEGER, start_time_minute INTEGER, end_time_hour INTEGER
                              , end_time_minute INTEGER, shutdown_boolean INTEGER);''')
        if not connection.execute(f'select * from config WHERE id = 1;').fetchone():
            connection.execute('''INSERT INTO config (location, start_time_hour, start_time_minute, end_time_hour,
                                  end_time_minute, shutdown_boolean) VALUES (?, ?, ?, ?, ?, ?);'''
                               , (os.getcwd(), 0, 0, 12, 0, 0))

def set_location(location):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('UPDATE config SET location = ? where id = 1;', (location,))

def set_start_time(hour, minute):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('UPDATE config SET start_time_hour = ?, start_time_minute = ? where id = 1;',
                           (hour, minute))

def set_end_time(hour, minute):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('UPDATE config SET end_time_hour = ?, end_time_minute = ? where id = 1;',
                           (hour, minute))

def set_shutdown_boolean(shutdown_boolean):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('UPDATE config SET shutdown_boolean = ? where id = 1', (shutdown_boolean,))


def reset_config():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''UPDATE config SET location = ?, start_time_hour = ?, start_time_minute = ?,
                              end_time_hour = ?, end_time_minute = ? , shutdown_boolean = ? where id = 1''',
                           (os.getcwd(), 0, 0, 12, 0, 0))

def set_config(location, start_time_hour, start_time_minute, end_time_hour, end_time_minute):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''UPDATE config SET location = ?, start_time_hour = ?, start_time_minute = ?,
                              end_time_hour = ?, end_time_minute = ? where id = 1''',
                           (location, start_time_hour, start_time_minute, end_time_hour, end_time_minute))

def get_config():
    connection = sqlite3.connect('Database.db')
    with connection:
        return connection.execute(f'select * from config WHERE id = 1;').fetchone()

#download list temp_____________________________________________________________________________________________________
def create_download_table():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS download (url TEXT, location TEXT);''')

def get_all_downloads():
    connection = sqlite3.connect('Database.db')
    with connection:
        return connection.execute('SELECT * FROM download;').fetchall()

def add_to_download(url, location):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('INSERT INTO download (url, location) VALUES (?, ?);', (url, location))

def delete_download(url, location):
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('DELETE FROM download WHERE url = ? AND location = ?;', (url, location))

def delete_all_downloads():
    connection = sqlite3.connect('Database.db')
    with connection:
        connection.execute('DELETE FROM download;')

create_history_table()
create_config_table()
create_download_table()