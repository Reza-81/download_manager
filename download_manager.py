import requests
from pathlib import Path
from threading import Timer
from datetime import datetime
import time
import database
import cgi
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

    def __init__(self, url, location, start_time_hour, start_time_minute, end_time_hour, end_time_minute, force_to_run):
        temp_request = requests.get(url, stream=True)
        self.id = downloading_thread.ID
        downloading_thread.ID += 1
        self.url = url
        self.file_name = downloading_thread.get_file_name(temp_request)
        self.size = int(temp_request.headers.get('content-length')) * 0.000001
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
        if self.started:
            return
        self.stop_flag = False
        self.download_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute), self.download)
        self.download_thread.start()
        self.kill_thread = Timer(remaining_time(self.end_time_hour, self.end_time_minute) + 2
                                 , downloading_thread.terminate_dowload_procces_with_id, [self.id])
        self.kill_thread.start()

    def download(self):
        self.started = True
        chunk_length = 0.032768 # 32 * 1024 mega byte
        database.add_to_history(str(datetime.now()), self.file_name, self.url, self.location)
        if Path(self.location + '/' + self.file_name).is_file():
            print(self.url, ' resuming...')
            path = Path(self.location + '/' + self.file_name)
            resume_header = ({'Range': f'bytes={path.stat().st_size}-'})
            try:
                download_request = requests.get(self.url, stream=True, headers=resume_header)
                with open(self.location + '/' + self.file_name, 'ab') as file:
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.stop_flag:
                            return
                        file.write(chunk)
            except Exception as e:
                print(e)
        else:
            print(self.url, ' started...')
            try:
                download_request = requests.get(self.url, stream=True)
                with open(self.location + '/' + self.file_name, 'wb') as file:
                    for chunk in download_request.iter_content(int(chunk_length * 1000000)):
                        if self.stop_flag:
                            return
                        file.write(chunk)
            except Exception as e:
                print(e)
        downloading_thread.downloading_list.remove(self)
        if hasattr(self, 'kill_thread'):
            self.kill_thread.cancel()
        if downloading_thread.downloading_list:
            downloading_thread.downloading_list[0].run_thread()

    @classmethod
    def get_file_name(cls, request):
        content_disposition = request.headers.get('Content-Disposition')
        if content_disposition and 'filename' in content_disposition:
            return cgi.parse_header(content_disposition)[1]['filename']
        else:
            return request.url.rsplit("/", 1)[1]

    def cancel(self):
        self.started = False
        if remaining_time(self.start_time_hour, self.start_time_minute) > 5:
            if self.download_thread:
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
        for thread in downloading_thread.downloading_list:
            if thread.started:
                size_1 = os.path.getsize(thread.location + '/' + thread.file_name) * 0.000001
                time.sleep(1)
                size_2 = os.path.getsize(thread.location + '/' + thread.file_name) * 0.000001
                return size_2 - size_1
        return 0

    @classmethod
    def show_downloading_set(cls):
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
            print(thread.id, '\n', thread.file_name, '\n', thread.location, '\n', thread.size
                  , '\n', '%', (downloaded_size/thread.size) * 100, '\n', time_to_end, 'min left', '\n', thread.started)
            print('------------------------------------------------------------------------')
        if not thread:
            print('there is nothing to download.')
            print('------------------------------------------------------------------------')