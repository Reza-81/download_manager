import user_view
import database
from threading import Timer
import download_manager
from datetime import datetime

def main():
    while(True):
        instruction = user_view.get_input()
        if instruction[0] == 'exit':
            break
        user_view.run_the_insturction(instruction)

main()