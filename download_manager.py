import requests
from pathlib import Path
from threading import Timer
from datetime import datetime
import time
import database
import cgi
import os
#_______________________________________________________________________________________________________________________
def bool_between(start_hour, start_minute, end_hour, end_minute, now_hour, now_minute):
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


def remaining_time(start_hour, start_minute, end_hour, end_minute, state):
    # state, true -> start
    # state, false -> end
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
        self.download_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                                                    self.end_time_minute, True), self.download)
        self.download_thread.start()
        self.kill_thread = Timer(remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                                                self.end_time_minute, False) + 2
                                 , downloading_thread.pause_dowload_with_id, [self.id])
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
        database.delete_download(self.url, self.location)
        downloading_thread.downloading_list.remove(self)
        if hasattr(self, 'kill_thread'):
            self.kill_thread.cancel()
        if downloading_thread.downloading_list:
            downloading_thread.downloading_list[0].run_thread()
        elif database.get_config()[6]:
            print('computer will shutdown in 5 secods...')
            time.sleep(5)
            os.system("shutdown /s /t 1")

    @classmethod
    def get_file_name(cls, request):
        content_disposition = request.headers.get('Content-Disposition')
        if content_disposition and 'filename' in content_disposition:
            return cgi.parse_header(content_disposition)[1]['filename']
        else:
            return request.url.rsplit("/", 1)[1]

    def cancel(self):
        self.started = False
        if remaining_time(self.start_time_hour, self.start_time_minute, self.end_time_hour,
                          self.end_time_minute, False) > 5:
            if self.download_thread:
                self.download_thread.cancel()
        else:
            self.stop_flag = True
        if hasattr(self, 'kill_thread'):
            if self.kill_thread:
                self.kill_thread.cancel()
        print('killed')

    @classmethod
    def pause_dowload_with_id(cls, id):
        for thread in downloading_thread.downloading_list:
            if id == thread.id:
                thread.cancel()
                return thread

    @classmethod
    def pause_all_downloads(cls):
        for thread in downloading_thread.downloading_list:
            thread.cancel()

    @classmethod
    def delete_dowload_with_id(cls, id):
        temp = downloading_thread.pause_dowload_with_id(id)
        if temp:
            database.delete_download(temp.url, temp.location)
            downloading_thread.downloading_list.remove(temp)

    @classmethod
    def delete_all_dowloads(cls):
        downloading_thread.pause_all_downloads()
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
    def load_downloads_from_database(cls):
        for download in database.get_all_downloads():
            downloading_thread(download[0], download[1], database.get_config()[2], database.get_config()[3],
                               database.get_config()[4], database.get_config()[5], False)

    @classmethod
    def show_downloading_list(cls):
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
                  f'remaining time: {time_to_end} min left\nstatus: {thread.started}')
            print('------------------------------------------------------------------------')
        if not thread:
            print('there is nothing to download.')
            print('------------------------------------------------------------------------')