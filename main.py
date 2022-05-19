import user_view
import download_manager

def main():
    print('please wait...', end='\r')
    # load downloads form database
    download_manager.downloading_thread.load_downloads_from_database()
    print('* if you have any problem enter "help".\n\n')
    while(True):
        if user_view.user_command() == -1:
            break

main()