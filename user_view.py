import os
import sys
from datetime import datetime
import database
import download_manager
#-----------------------------------------------------------------------------------------------------------------------

def get_number(text='', min_limite=float('-inf'), max_limite=float('inf')):
    while(True):
        number = input(text)
        if number == '':
            return min_limite
        if number.isdigit():
            number = int(number)
            if min_limite <= number <= max_limite:
                return number
            print('your number is out of range. try again: ')
        else:
            print('your input is incorrect. try again: ')


def get_input():
    instruction = input('/> enter the insturction: ').lower()

    if instruction == 'new' or instruction == 'new_now':
        url = input('/> enter the url: ')
        location = input('/> enter the location: ')
        if location == '':
            location = database.get_config()[1]
        return [instruction, url, location]

    elif instruction == 'speed':
        return ['speed']

    elif instruction == 'start':
        id = get_number('/> enter the id: ')
        return ['start', id]

    elif instruction == 'puase':
        id = get_number('/> enter the id: ')
        return ['puase', id]

    elif instruction == 'puase_all':
        return ['puase_all']

    elif instruction == 'cancel':
        id = get_number('/> enter the id: ')
        return ['cancel', id]

    elif instruction == 'cancel_all':
        return ['cancel_all']

    elif instruction == 'history':
        return ['history']

    elif instruction == 'clear_history':
        return ['clear_history']

    elif instruction == 'list':
        return ['list']

    elif instruction == 'config':
        return ['config']

    elif instruction == 'location':
        location = input('/> enter the location: ')
        if location == '':
            location = database.get_config()[1]
        return ['location', location]

    elif instruction == 'start_timer':
        start_time_hour = get_number('/> enter the start time (hour): ', 0, 23)
        start_time_minute = get_number('/> enter the start time (minute): ', 0, 59)
        return ['start_timer', start_time_hour, start_time_minute]

    elif instruction == 'end_timer':
        end_time_hour = get_number('/> enter the end time (hour): ', 0, 23)
        end_time_minute = get_number('/> enter the end time (minute): ', 0, 59)
        return ['end_timer', end_time_hour, end_time_minute]

    elif instruction == 'shutdown':
        return ['shutdown']

    elif instruction == 'set_config':
        location = input('/> enter the location: ')
        if location == '':
            location = database.get_config()[1]
        start_time_hour = get_number('/> enter the start time (hour): ', 0, 23)
        start_time_minute = get_number('/> enter the start time (minute): ', 0, 59)
        end_time_hour = get_number('/> enter the end time (hour): ', 0, 23)
        end_time_minute = get_number('/> enter the end time (minute): ', 0, 59)
        return ['set_config', location, start_time_hour, start_time_minute, end_time_hour, end_time_minute]

    elif instruction == 'reset_config':
        return ['reset_config']

    elif instruction == 'cls':
        return ['cls']

    elif instruction == 'help':
        return ['help']

    elif instruction == 'exit':
        return ['exit']
    return [None]


def run_the_insturction(inputs):
    if inputs[0] == 'help':
        print(
'''\nThis is the set of instructions that you can use:
     1) new: add new download to download list.
     -----------------------------------------------------------
     2) new_now: add new download and start it instantly.
     -----------------------------------------------------------
     3) list: show the downloads that add to download list.
     -----------------------------------------------------------
     4) start: you can start the specific download that added
               in download list with download id.
     -----------------------------------------------------------
     5) speed: check the download speed.
     -----------------------------------------------------------
     6) pause: pause the download with download id. Note, the
               download will not be deleted.
     -----------------------------------------------------------
     7) pause_all: pause the all downloads.
     -----------------------------------------------------------
     8) cancel: cancel and delete a download from download list
                with download id.
     -----------------------------------------------------------
     9) cancel_all: delete all downloads.
     -----------------------------------------------------------
     10) history: show the history of downloads.
     -----------------------------------------------------------
     11) clear_history: clear your history.
     -----------------------------------------------------------
     12) config: show the config.
     -----------------------------------------------------------
     13) location: change the directory of downloaded files.
     -----------------------------------------------------------
     14) start_timer: set start time for downloads.
     -----------------------------------------------------------
     15) end_timer: set end time for downloads.
     -----------------------------------------------------------
     16) shutdown: set computer to shutdown after finish all
                   downloads.
     -----------------------------------------------------------
     17) set_config: you can set location, start and end time
                     for all downloads.
     -----------------------------------------------------------
     18) reset_config: reset the config.
     -----------------------------------------------------------
     19) cls: clear the screen.
     -----------------------------------------------------------
     20) exit: exit form program.\n''')

    elif inputs[0] == 'new':
        database.add_to_download(inputs[1], inputs[2])
        download_manager.downloading_thread(inputs[1], inputs[2], database.get_config()[2], database.get_config()[3],
                                            database.get_config()[4], database.get_config()[5], False)

    elif inputs[0] == 'new_now':
        database.add_to_download(inputs[1], inputs[2])
        download_manager.downloading_thread(inputs[1], inputs[2], datetime.now().hour, datetime.now().minute,
                                            database.get_config()[4], database.get_config()[5], True)

    elif inputs[0] == 'start':
        for thread in download_manager.downloading_thread.downloading_list:
            if inputs[1] == thread.id:
                thread.run_thread()

    elif inputs[0] == 'speed':
        print('please wait.')
        print(download_manager.downloading_thread.speed(), 'MB/s')

    elif inputs[0] == 'cancel':
        download_manager.downloading_thread.delete_dowload_with_id(inputs[1])

    elif inputs[0] == 'cancel_all':
        download_manager.downloading_thread.delete_all_dowloads()
        database.delete_all_downloads()

    elif inputs[0] == 'puase':
        download_manager.downloading_thread.pause_dowload_with_id(inputs[1])

    elif inputs[0] == 'puase_all':
        download_manager.downloading_thread.pause_all_downloads()

    elif inputs[0] == 'history':
        for i in database.get_all_history():
            print(i)

    elif inputs[0] == 'clear_history':
        database.clear_history()

    elif inputs[0] == 'list':
        download_manager.downloading_thread.show_downloading_list()

    elif inputs[0] == 'config':
        print(database.get_config())

    elif inputs[0] == 'location':
        database.set_location(inputs[1])
        download_manager.downloading_thread.delete_all_dowloads()
        download_manager.downloading_thread.load_downloads_from_database()

    elif inputs[0] == 'start_timer':
        database.set_start_time(inputs[1], inputs[2])
        download_manager.downloading_thread.delete_all_dowloads()
        download_manager.downloading_thread.load_downloads_from_database()

    elif inputs[0] == 'end_timer':
        database.set_end_time(inputs[1], inputs[2])
        download_manager.downloading_thread.delete_all_dowloads()
        download_manager.downloading_thread.load_downloads_from_database()

    elif inputs[0] == 'shutdown':
        shutdown = database.get_config()[-1]
        if shutdown:
            print('shutdown is OFF.')
            shutdown = 0
        else:
            print('shutdown is ON.')
            shutdown = 1
        database.set_shutdown_boolean(shutdown)

    elif inputs[0] == 'set_config':
        database.set_config(inputs[1], inputs[2], inputs[3], inputs[4], inputs[5])
        download_manager.downloading_thread.delete_all_dowloads()
        download_manager.downloading_thread.load_downloads_from_database()

    elif inputs[0] == 'reset_config':
        database.reset_config()
        download_manager.downloading_thread.delete_all_dowloads()
        download_manager.downloading_thread.load_downloads_from_database()

    elif inputs[0] == 'cls':
        os.system('cls')