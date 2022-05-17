import requests
from pathlib import Path
from threading import Timer
from datetime import datetime
import time
import database
import cgi
import os
#_______________________________________________________________________________________________________________________
def bool_between(start_hour: int, start_minute: int, end_hour: int, end_minute: int, now_hour: int, now_minute: int) -> bool:
    """this function checks that the given time is between start and end point or not.
    """
    if start_hour != now_hour and end_hour != now_hour:
        counter_hour = start_hour + 1
        while(counter_hour != start_hour):
            if counter_hour >= 24:
                counter_hour = 0
                continue
            if counter_hour == now_hour:
                return True
            if counter_hour == end_hour:
                return False
            counter_hour += 1
    if start_hour == now_hour:
        return start_minute < now_minute
    return end_minute < now_minute


def remaining_time(start_hour: int, start_minute: int, end_hour: int, end_minute: int, state: bool) -> int:
    """calculating the remaining time for start the thread.

    Args:
        state (bool): if state was True, the remaining time calculated for download thread thread.
                      the otherwise it will calculate the time for kill _thread.
    """
    now = datetime.now()
    if state:
        if bool_between(start_hour, start_minute, end_hour, end_minute, now.hour, now.minute):
            return 0
        remaining = (datetime(1, 1, 1, start_hour, start_minute) - datetime(1, 1, 1, now.hour, now.minute)).total_seconds()
        if remaining >= 0:
            return remaining
        return 86400 - (datetime(1, 1, 1, now.hour, now.minute) - datetime(1, 1, 1, start_hour, start_minute)).total_seconds()
    remaining = (datetime(1, 1, 1, end_hour, end_minute) - datetime(1, 1, 1, now.hour, now.minute)).total_seconds()
    if remaining >= 0:
        return remaining
    return 86400 - (datetime(1, 1, 1, now.hour, now.minute) - datetime(1, 1, 1, end_hour, end_minute)).total_seconds()


class downloading_thread():
    """ a class to represent a download object.

    Instance attributes:
        id : int
        url : str
        file_name : str
        size : int
            size of file
        location : str
        started : bool
            thread is started or not
        downloading_flag : bool
            download is started or not
        cancel_flag : bool
            flag for download process canceling
        start_time_hour : int
        start_time_minute : int
        end_time_hour : int
        end_time_minute : int
        download_thread : threading.Timer
        kill_thread : threading.Timer
    
    Class attributes:
        ID : int
        download_list : list
            list of download objects
    
    Instance methods:
        run_thread()
        download()
        cancel()
    
    Class methods:
        search_thread(id : int)
        get_file_name(request : requests.models.Response)
        pause_dowload_with_id(id : int)
        pause_all_downloads()
        delete_dowload_with_id(id : int)
        delete_all_dowloads()
        speed()
        load_downloads_from_database()
        show_downloading_list()
    """
    ID = 0
    downloading_list = []

    def __init__(self, url: str, location: str, start_time_hour: int, start_time_minute: int, end_time_hour: int, end_time_minute: int, force_to_run: bool):
        """initialize the download object

        Args:
            location (str): file location
            force_to_run (bool): download instantly
        """
        temp_request = requests.get(url, stream=True)
        self.id = downloading_thread.ID
        downloading_thread.ID += 1
        self.url = url
        self.file_name = downloading_thread.get_file_name(temp_request)
        self.size = int(temp_request.headers.get('content-length')) * 0.000001
        self.location = location
        self.started = False
        self.downloading_flag = False
        self.cancel_flag = False
        self.start_time_hour = start_time_hour
        self.start_time_minute = start_time_minute
        self.end_time_hour = end_time_hour
        self.end_time_minute = end_time_minute
        self.download_thread = None
        self.kill_thread = None
        if force_to_run or len(downloading_thread.downloading_list) == 0:
            self.run_thread()
        downloading_thread.downloading_list.append(self)

    def run_thread(self):
        """run the download thread by set the start and kill thread for download.
        """
        cancel_flag = False
        if self.started:
            return
        self.started = True
        self.download_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                                                    self.end_time_minute, True), self.download)
        self.download_thread.start()
        self.kill_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                                                self.end_time_minute, False) + 2
                                 , downloading_thread.pause_dowload_with_id, [self.id])
        self.kill_thread.start()

    def download(self):
        """this function downloads the file.
        """
        self.downloading_flag = True
        chunk_length = 0.032768 # 32 * 1024 mega byte
        database.add_to_history(str(datetime.now()), self.file_name, self.url, self.location)
        # if a file already exists
        if Path(self.location + '/' + self.file_name).is_file():
            print(self.url, ' resuming...')
            path = Path(self.location + '/' + self.file_name)
            resume_header = ({'Range': f'bytes={path.stat().st_size}-'})
            try:
                download_request = requests.get(self.url, stream=True, headers=resume_header)
                with open(self.location + '/' + self.file_name, 'ab') as file:
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.cancel_flag:
                            return
                        file.write(chunk)
            except Exception as e:
                print(e)
        # new file
        else:
            print(self.url, ' started...')
            try:
                download_request = requests.get(self.url, stream=True)
                with open(self.location + '/' + self.file_name, 'wb') as file:
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.cancel_flag:
                            return
                        file.write(chunk)
            except Exception as e:
                print(e)
        database.delete_download(self.url, self.location)
        downloading_thread.downloading_list.remove(self)
        self.kill_thread.cancel()
        # start nex download
        if downloading_thread.downloading_list:
            downloading_thread.downloading_list[0].run_thread()
        elif database.get_config()[6]:
            print('computer will shutdown in 5 secods...')
            time.sleep(5)
            os.system("shutdown /s /t 1")
    
    @classmethod
    def search_thread(cls, id : int):
        """search download object by given id in download_list.
           this search is binary search.

        Returns:
            downloading_thread:
        """
        start = 0
        end = len(downloading_thread.downloading_list) - 1
        while(end >= start):
            mid = (end + start)//2
            if downloading_thread.downloading_list[mid].id == id:
                return downloading_thread.downloading_list[mid]
            if downloading_thread.downloading_list[mid].id > id:
                end = mid - 1
            else:
                start = mid + 1
        return None

    @classmethod
    def get_file_name(cls, request: requests.models.Response) -> str:
        """return the name for downloading file
        """
        content_disposition = request.headers.get('Content-Disposition')
        if content_disposition and 'filename' in content_disposition:
            return cgi.parse_header(content_disposition)[1]['filename']
        else:
            return requests.utils.unquote(request.url.rsplit("/", 1)[1])

    def cancel(self):
        """cancel the downloading process.
        """
        self.downloading_flag = False
        if remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                          self.end_time_minute, False) > 5:
            if self.download_thread:
                self.download_thread.cancel()
        else:
            cancel_flag = True
        if self.kill_thread:
            self.kill_thread.cancel()
        print('killed')

    @classmethod
    def pause_dowload_with_id(cls, id: int):
        """puase a download procces with id

        Returns:
            downloading_thread:
        """
        thread = downloading_thread.search_thread(id)
        if thread:
            thread.cancel()
            return thread

    @classmethod
    def pause_all_downloads(cls):
        """puase all download processes
        """
        for thread in downloading_thread.downloading_list:
            thread.cancel()

    @classmethod
    def delete_dowload_with_id(cls, id: int):
        """puase and delete a download process in downloading_list by id 
        """
        thread = downloading_thread.search_thread(id)
        if thread:
            thread.cancel()
            database.delete_download(thread.url, thread.location)
            downloading_thread.downloading_list.remove(thread)

    @classmethod
    def delete_all_dowloads(cls):
        """puase and delete all download processes in downloading_list
        """
        downloading_thread.pause_all_downloads()
        downloading_thread.downloading_list.clear()

    @classmethod
    def speed(cls) -> int:
        """calculate download speed.

        Returns:
            int:
        """
        for thread in downloading_thread.downloading_list:
            if thread.started:
                size_1 = os.path.getsize(thread.location + '/' + thread.file_name) * 0.000001
                time.sleep(1)
                size_2 = os.path.getsize(thread.location + '/' + thread.file_name) * 0.000001
                return size_2 - size_1
        return 0

    @classmethod
    def load_downloads_from_database(cls):
        """load downloads form database when program is ran.
        """
        for download in database.get_all_downloads():
            downloading_thread(download[0], download[1], database.get_config()[2], database.get_config()[3],
                               database.get_config()[4], database.get_config()[5], False)

    @classmethod
    def show_downloading_list(cls):
        """show download list information.
        """
        thread = None
        print('------------------------------------------------------------------------')
        for thread in downloading_thread.downloading_list:
            try:
                downloaded_size = os.path.getsize(thread.location + '/' + thread.file_name) * 0.000001
                if thread.started:
                    time_to_end = ((thread.size - downloaded_size) / downloading_thread.speed()) / 60
                else:
                    time_to_end = 0
            except:
                downloaded_size = 0
                time_to_end = 0

            print(f'download id: {thread.id}\nfile name: {thread.file_name}\nlocation: {thread.location}\n'
                  f'file size: {thread.size} MB\nprogress: %{(downloaded_size/thread.size) * 100}\n'
                  f'remaining time: {time_to_end} min left\nstatus: {thread.downloading_flag}')
            print('------------------------------------------------------------------------')
        if not thread:
            print('there is nothing to download.')
            print('------------------------------------------------------------------------')