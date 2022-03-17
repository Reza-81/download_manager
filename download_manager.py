import requests
from pathlib import Path
from threading import Timer
from datetime import datetime
import time
import database
import os
#_______________________________________________________________________________________________________________________

def remaining_time(hour, minute):
    now = datetime.now()
    temp = (datetime(1, 1, 1, hour, minute) - datetime(1, 1, 1, now.hour, now.minute)).total_seconds()
    if temp >= 0:
        return temp
    return 0

class downloading_thread():
    ID = 0
    downloading_list = []
    download_speed = 0

    def __init__(self, url, location, start_time_hour, start_time_minute, end_time_hour, end_time_minute, force_to_run):
        self.id = downloading_thread.ID
        downloading_thread.ID += 1
        self.url = url
        self.size = int(requests.get(url, stream=True).headers.get('content-length')) * 0.000001
        self.location = location
        self.stop_flag = False
        self.started = False
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
        self.started = True
        self.stop_flag = False
        self.download_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute), self.download)
        self.download_thread.start()
        self.kill_thread = Timer(remaining_time(self.end_time_hour, self.end_time_minute) + 2
                                 , downloading_thread.terminate_dowload_procces_with_id, [self.id])
        self.kill_thread.start()

    def download(self):
        chunk_length = 0.032768 # 32 * 1024 mega byte
        downloaded_length = 0
        file_name = self.url.rsplit("/", 1)[1]
        database.add_to_history(str(datetime.now()), file_name, self.url, self.location)
        if Path(self.location + '/' + file_name).is_file():
            print(self.url, ' resuming...')
            path = Path(self.location + '/' + file_name)
            resume_header = ({'Range': f'bytes={path.stat().st_size}-'})
            try:
                download_request = requests.get(self.url, stream=True, headers=resume_header)
                with open(self.location + '/' + file_name, 'ab') as file:
                    start = time.time()
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.stop_flag:
                            return
                        file.write(chunk)
                        downloaded_length += chunk_length
                        downloading_thread.download_speed = downloaded_length/(time.time() - start)
                    print('')
            except Exception as e:
                print(e)
        else:
            print(self.url, ' started...')
            try:
                download_request = requests.get(self.url, stream=True)
                with open(self.location + '/' + file_name, 'wb') as file:
                    start = time.time()
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.stop_flag:
                            return
                        file.write(chunk)
                        downloaded_length += chunk_length
                        downloading_thread.download_speed = downloaded_length/(time.time() - start)
                    print('')
            except Exception as e:
                print(e)
        downloading_thread.download_speed = 0
        downloading_thread.downloading_list.remove(self)
        if hasattr(self, 'kill_thread'):
            self.kill_thread.cancel()
        if downloading_thread.downloading_list:
            downloading_thread.downloading_list[0].run_thread()

    def cancel(self):
        downloading_thread.download_speed = 0
        self.started = False
        if remaining_time(self.start_time_hour, self.start_time_minute) > 5:
            self.download_thread.cancel()
        else:
            self.stop_flag = True
        if hasattr(self, 'kill_thread'):
            self.kill_thread.cancel()
        print('killed')

    @classmethod
    def terminate_dowload_procces_with_id(cls, id):
        for thread in downloading_thread.downloading_list:
            if id == thread.id:
                thread.cancel()
                if downloading_thread.downloading_list:
                    for new_thread in downloading_thread.downloading_list:
                        if new_thread.started:
                            return thread
                    if downloading_thread.downloading_list[0] != thread:
                        downloading_thread.downloading_list[0].run_thread()
                return thread

    @classmethod
    def terminate_all_downloads(cls):
        for thread in downloading_thread.downloading_list:
            thread.cancel()

    @classmethod
    def delte_by_id(cls, id):
        temp = downloading_thread.terminate_dowload_procces_with_id(id)
        if temp:
            downloading_thread.downloading_list.remove(temp)

    @classmethod
    def delte_all(cls):
        downloading_thread.terminate_all_downloads()
        downloading_thread.downloading_list.clear()

    @classmethod
    def speed(cls):
        print(downloading_thread.download_speed)

    @classmethod
    def show_downloading_set(cls):
        thread = None
        print('------------------------------------------------------------------------')
        for thread in downloading_thread.downloading_list:
            file_name = thread.url.rsplit("/", 1)[1]
            downloaded_size = os.path.getsize(thread.location + '/' + file_name) * 0.000001
            print(thread.id, '\n', file_name, '\n', thread.location, '\n', thread.size
                  , '\n', (downloaded_size/thread.size) * 100, '\n', thread.started)
            print('------------------------------------------------------------------------')
        if not thread:
            print('there is nothing to download.')
            print('------------------------------------------------------------------------')