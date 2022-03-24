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

    elif instruction == 'delete':
        id = get_number('/> enter the id: ')
        return ['delete', id]

    elif instruction == 'delete_all':
        return ['delete_all']

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

    elif instruction == 'exit':
        return ['exit']
    return [None]


def run_the_insturction(inputs):
    if inputs[0] == 'new':
        download_manager.downloading_thread(inputs[1], inputs[2], database.get_config()[2], database.get_config()[3],
                                            database.get_config()[4], database.get_config()[5], False)

    elif inputs[0] == 'new_now':
        download_manager.downloading_thread(inputs[1], inputs[2], datetime.now().hour, datetime.now().minute,
                                            database.get_config()[4], database.get_config()[5], True)

    elif inputs[0] == 'start':
        for thread in download_manager.downloading_thread.downloading_list:
            if inputs[1] == thread.id:
                thread.run_thread()

    elif inputs[0] == 'speed':
        print('please wait.')
        print(download_manager.downloading_thread.speed(), 'MB/s')

    elif inputs[0] == 'delete':
        download_manager.downloading_thread.delte_by_id(inputs[1])

    elif inputs[0] == 'delete_all':
        download_manager.downloading_thread.delte_all()

    elif inputs[0] == 'cancel':
        download_manager.downloading_thread.terminate_dowload_procces_with_id(inputs[1])

    elif inputs[0] == 'cancel_all':
        download_manager.downloading_thread.terminate_all_downloads()

    elif inputs[0] == 'history':
        for i in database.get_all_history():
            print(i)

    elif inputs[0] == 'clear_history':
        database.clear_history()

    elif inputs[0] == 'list':
        download_manager.downloading_thread.show_downloading_set()

    elif inputs[0] == 'config':
        print(database.get_config())

    elif inputs[0] == 'set_config':
        database.set_config(inputs[1], inputs[2], inputs[3], inputs[4], inputs[5])
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)

    elif inputs[0] == 'reset_config':
        database.reset_config()
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, __file__] + sys.argv)

    elif inputs[0] == 'cls':
        os.system('cls')