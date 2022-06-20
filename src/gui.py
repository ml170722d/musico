from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import multiprocessing as mp
import os
import time
from tkinter import ttk
from tkinter import *
import webbrowser
import logging

import src.app as app


logger = logging.getLogger(__name__)

COLUMN = {
    # 'ttk_main_panel': 0,
    'ttk_song_card_list': 0,
    'download_button': 1,
    'exit_button': 0,
    'load_button': 1,
    'msg_label': 0,
    'url_input': 0,
    'ttk_report_bug': 0
}

ROW = {
    # 'ttk_main_panel': 0,
    'ttk_song_card_list': 1,
    'download_button': 2,
    'exit_button': 4,
    'load_button': 0,
    'msg_label': 2,
    'url_input': 0,
    'ttk_report_bug': 3
}


class App(Tk):
    songs: list[app.Song]
    label_text: StringVar
    url: StringVar
    loaded: bool

    ttk_song_card_list: ttk.Frame
    ttk_main_panel: ttk.Frame
    ttk_input_url: ttk.Entry

    INPUT_URL_PACEHOLDER = 'Enter song or playlint link here'

    def __init__(self) -> None:
        super().__init__()
        self.label_text = StringVar()
        self.url = StringVar()
        self.songs = []
        self.loaded = False

        self.ttk_main_panel = ttk.Frame(self, padding=10)
        self.ttk_main_panel.grid()

        ttk.Button(self.ttk_main_panel, text="Download", command=Thread(
            target=self.start_download).start).grid(column=COLUMN['download_button'], row=ROW['download_button'])

        ttk.Label(self.ttk_main_panel, textvariable=self.label_text).grid(
            column=COLUMN['msg_label'], row=ROW['msg_label'])

        ttk.Button(self.ttk_main_panel, text="Load", command=lambda: Thread(
            target=self.loadUrl).start()).grid(column=COLUMN['load_button'], row=ROW['load_button'])

        self.ttk_input_url = ttk.Entry(
            self.ttk_main_panel, width=75, textvariable=self.url)
        self.ttk_input_url.grid(
            column=COLUMN['url_input'], row=ROW['url_input'])
        self.ttk_input_url.insert(0, self.INPUT_URL_PACEHOLDER)
        self.ttk_input_url.bind('<Button-1>', self.remove_paceholder)

        self.ttk_song_card_list = ttk.Frame(
            self.ttk_main_panel, padding=10)

        ttk.Button(self.ttk_main_panel, text="Exit",
                   command=self.end).grid(column=COLUMN['exit_button'], row=ROW['exit_button'])

        ttk.Button(self.ttk_main_panel, text="Report Bugs", command=lambda: webbrowser.open(
            'https://github.com/ml170722d/musico/issues/new')).grid(column=COLUMN['ttk_report_bug'], row=ROW['ttk_report_bug'])

    def remove_paceholder(self, *args):
        self.ttk_input_url.delete(0, 'end')

    @staticmethod
    def download(song: app.Song) -> bool:
        for i in range(3):
            try:
                logger.debug("I'm process", os.getpid())
                song.download()
            except:
                logger.warning(f'Process: {os.getpid()} fail number: {i+1}')
                continue

            logger.info(
                f'Successfully downloaded: {song.author} - {song.title}')
            return True

        logger.info(f'Failed to download: {song.author} - {song.title}')
        return False

    def start_download(self):
        if not self.loaded:
            self.label_text.set("Load song or playlist first!!!")
            return

        task = TextChangingTask(self.label_text, [
            "Downloading",
            "Downloading.",
            "Downloading..",
            "Downloading...",
        ])
        thread = Thread(target=task.run)
        thread.start()

        with ThreadPoolExecutor(max_workers=mp.cpu_count()) as pool:
            results = pool.map(self.download, self.songs)

        for r in results:
            if (r != True):
                task.terminate()
                thread.join()
                self.label_text.set("Fail!!!")
                return

        task.terminate()
        thread.join()
        self.label_text.set("Success!!!")
        pass

    def loadUrl(self):
        if self.loaded:
            self.ttk_song_card_list.grid_forget()
            self.loaded = False

        task = TextChangingTask(self.label_text, [
            "Loading",
            "Loading.",
            "Loading..",
            "Loading...",
        ])
        thread = Thread(target=task.run)
        thread.start()

        url = self.url.get()
        print(url)
        try:
            pl = app.PlayList(url)
            self.songs = pl.getSongs()
        except:
            try:
                song = app.Song(url)
                self.songs.append(song)
            except:
                task.terminate()
                thread.join()
                self.label_text.set("Invalid url")
                return
            pass

        self.add_song_list_frame([])

        task.terminate()
        thread.join()
        self.label_text.set("")

        self.loaded = True
        pass

    def add_song_list_frame(self, songs: list[app.Song]) -> None:
        self.ttk_song_card_list.grid(
            column=COLUMN['ttk_song_card_list'], row=ROW['ttk_song_card_list'])
        ttk.Button(self.ttk_song_card_list, text="QWERTY",
                   command=lambda: print("button")).grid(column=0, row=0)

    def start(self):
        self.mainloop()

    def end(self):
        self.destroy()


class ChankingTask:
    running: bool

    def __init__(self) -> None:
        self.running = True
        pass

    def run(self):
        pass

    def terminate(self):
        self.running = False


class TextChangingTask(ChankingTask):
    label: StringVar
    TIMEOUT = 0.3
    text_arr: list[str]

    def __init__(self, label: StringVar, text_array: list[str]) -> None:
        super().__init__()
        self.label = label
        self.text_arr = text_array

    def run(self):
        while True:
            for text in self.text_arr:
                self.label.set(text)
                if not self.running:
                    return
                time.sleep(self.TIMEOUT)
