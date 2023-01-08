import os
from datetime import datetime
import database
import download_manager
import requests
#-----------------------------------------------------------------------------------------------------------------------

def get_number(text: str = '', min_limite: int = float('-inf'), max_limite: int = float('inf')) -> int:
    """get int number from user between given range.

    Returns:
        int
    """
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

def get_directory(text: str) -> str:
    """get path and check. if the input was empty, return the path
       that saved in database.
    """
    directory = input(text)
    while(directory != ''):
        if os.path.exists(directory):
            return directory
        print('your location is not exist. try again: ')
        directory = input(text)
    return database.get_config()[1]

def check_url(url: str) -> bool:
    try:
        return requests.get(url, stream=True).headers.get('content-length')
    except:
        return False

def user_command():
    """get user commands
    """
    instruction = input('/> enter the insturction: ')
    os.system('cls')
    match instruction:
        case 'help':
            print(
    '''\nThis is the set of instructions that you can use:
        1) for start new download, just enter the url.
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

        case 'new_now':
            url = input('/> enter the url: ')
            if check_url(url):
                location = get_directory('/> enter the location: ')
                database.add_to_download(url, location, 1)
                download_manager.downloading_thread(url, location, datetime.now().hour, datetime.now().minute,
                                                    database.get_config()[4], database.get_config()[5], True)
            else:
                print('your input is incorrect, please check.')

        case 'start':
            id = get_number('/> enter the id: ')
            thread = download_manager.downloading_thread.search_thread(id)
            if thread:
                thread.run_thread()

        case 'speed':
            print('please wait...')
            average = 0
            counter = 0
            for thread in download_manager.downloading_thread.downloading_list:
                if thread.downloading_flag:
                    counter += 1
                    average += thread.speed()
            if counter:
                print(round(average/counter, 1), 'MB/s')
            else:
                print(0, 'MB/s')

        case 'cancel':
            id = get_number('/> enter the id: ')
            download_manager.downloading_thread.delete_dowload_with_id(id)

        case 'cancel_all':
            download_manager.downloading_thread.delete_all_dowloads()
            database.delete_all_downloads()

        case 'puase':
            id = get_number('/> enter the id: ')
            download_manager.downloading_thread.pause_dowload_with_id(id)

        case 'puase_all':
            download_manager.downloading_thread.pause_all_downloads()

        case 'history':
            i = None
            print('------------------------------------------------------------------------')
            for i in database.get_all_history():
                print(f' Id: {i[0]}')
                print(f' Date: {i[1]}')
                print(f' File name: {i[2]}')
                print(f' File url: {i[3]}')
                print(f' File location: {i[4]}')
                print('------------------------------------------------------------------------')
            if not i:
                print('there is no history!')
                print('------------------------------------------------------------------------')

        case 'clear_history':
            database.clear_history()
            print('history cleared.')

        case 'list':
            download_manager.downloading_thread.show_downloading_list()

        case 'config':
            print(database.get_config())

        case 'location':
            location = get_directory('/> enter the location: ')
            database.set_location(location)
            download_manager.downloading_thread.delete_all_dowloads()
            download_manager.downloading_thread.load_downloads_from_database()

        case 'start_timer':
            start_time_hour = get_number('/> enter the start time (hour): ', 0, 23)
            start_time_minute = get_number('/> enter the start time (minute): ', 0, 59)
            database.set_start_time(start_time_hour, start_time_minute)
            download_manager.downloading_thread.delete_all_dowloads()
            download_manager.downloading_thread.load_downloads_from_database()

        case 'end_timer':
            end_time_hour = get_number('/> enter the end time (hour): ', 0, 23)
            end_time_minute = get_number('/> enter the end time (minute): ', 0, 59)
            database.set_end_time(end_time_hour, end_time_minute)
            download_manager.downloading_thread.delete_all_dowloads()
            download_manager.downloading_thread.load_downloads_from_database()

        case 'shutdown':
            shutdown = database.get_config()[-1]
            if shutdown:
                print('shutdown is OFF.')
                shutdown = 0
            else:
                print('shutdown is ON.')
                shutdown = 1
            database.set_shutdown_boolean(shutdown)

        case 'set_config':
            location = get_directory('/> enter the location: ')
            start_time_hour = get_number('/> enter the start time (hour): ', 0, 23)
            start_time_minute = get_number('/> enter the start time (minute): ', 0, 59)
            end_time_hour = get_number('/> enter the end time (hour): ', 0, 23)
            end_time_minute = get_number('/> enter the end time (minute): ', 0, 59)
            database.set_config(location, start_time_hour, start_time_minute, end_time_hour, end_time_minute)
            download_manager.downloading_thread.delete_all_dowloads()
            download_manager.downloading_thread.load_downloads_from_database()

        case 'reset_config':
            database.reset_config()
            download_manager.downloading_thread.delete_all_dowloads()
            download_manager.downloading_thread.load_downloads_from_database()

        case 'cls':
            os.system('cls')
        
        case 'exit':
            download_manager.downloading_thread.pause_all_downloads()
            return -1
        
        case _:
            url = instruction
            if check_url(url):
                location = get_directory('/> enter the location: ')
                database.add_to_download(url, location, 0)
                download_manager.downloading_thread(url, location, database.get_config()[2], database.get_config()[3],
                                                        database.get_config()[4], database.get_config()[5], False)
            else:
                print('your input is incorrect, please check.')