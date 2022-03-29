import user_view
import database
from threading import Timer
import download_manager
from datetime import datetime

def main():
    # load downloads form download list temp
    download_manager.downloading_thread.load_downloads_from_database()
    print('* if you have any problem enter "help".\n\n')
    while(True):
        instruction = user_view.get_input()
        if instruction[0] == 'exit':
            break
        user_view.run_the_insturction(instruction)

main()