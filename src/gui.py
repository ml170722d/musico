from __future__ import annotations
from cmath import sin
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import multiprocessing as mp
import os
import time
from tkinter import ttk
from tkinter import *
from turtle import update
import webbrowser
import logging

import src.app as app


logger = logging.getLogger(__name__)

COLUMN = {
    # 'ttk_main_panel': 0,
    'ttk_song_card_list': 0,
    'download_button': 10,
    'exit_button': 0,
    'load_button': 10,
    'msg_label': 0,
    'url_input': 0,
    'ttk_report_bug': 0
}

ROW = {
    # 'ttk_main_panel': 0,
    'ttk_song_card_list': 10,
    'download_button': 20,
    'exit_button': 40,
    'load_button': 0,
    'msg_label': 20,
    'url_input': 0,
    'ttk_report_bug': 30
}


class App(Tk):
    songs: list[app.Song]
    label_text: StringVar
    url: StringVar
    curr_song: StringVar
    loaded: bool

    ttk_song_card_list: ttk.Frame
    ttk_main_panel: ttk.Frame
    ttk_input_url: ttk.Entry
    ttk_opt_manu: OptionMenu

    edit_panel: EditPanel

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

        # ttk.Button(self.ttk_main_panel, text="Load", command=lambda: Thread(
        #     target=self.loadUrl).start()).grid(column=COLUMN['load_button'], row=ROW['load_button'])

        # self.ttk_input_url = ttk.Entry(
        #     self.ttk_main_panel, width=75, textvariable=self.url)
        # self.ttk_input_url.grid(
        #     column=COLUMN['url_input'], row=ROW['url_input'])
        # self.ttk_input_url.insert(0, self.INPUT_URL_PACEHOLDER)
        # self.ttk_input_url.bind(
        #     '<Button-1>', lambda *args: self.ttk_input_url.delete(0, 'end'))

        InputPanel(self, self.load).grid(column=0, row=0)

        self.edit_panel = EditPanel(self, self.songs)
        self.edit_panel.grid(column=0, row=1)

        self.ttk_song_card_list = ttk.Frame(
            self.ttk_main_panel, padding=10)

        ttk.Button(self.ttk_main_panel, text="Exit",
                   command=self.end).grid(column=COLUMN['exit_button'], row=ROW['exit_button'])

        ttk.Button(self.ttk_main_panel, text="Report Bugs", command=lambda: webbrowser.open(
            'https://github.com/ml170722d/musico/issues/new')).grid(column=COLUMN['ttk_report_bug'], row=ROW['ttk_report_bug'])

        self.curr_song = StringVar()
        self.ttk_opt_manu = OptionMenu(
            self.ttk_song_card_list, self.curr_song, [])

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
        thread.setDaemon(True)
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

    def load(self, url):
        t = Thread(target=lambda: self.loadUrl(url))
        t.setDaemon(True)
        t.start()
        pass

    def loadUrl(self, url: str):
        if self.loaded:
            self.ttk_song_card_list.grid_forget()
            self.loaded = False
            self.songs = []

        task = TextChangingTask(self.label_text, [
            "Loading",
            "Loading.",
            "Loading..",
            "Loading...",
        ])
        thread = Thread(target=task.run)
        thread.setDaemon(True)
        thread.start()

        # url = self.url.get()
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

        self.add_song_list_frame(self.songs)

        task.terminate()
        thread.join()
        self.label_text.set("")

        self.edit_panel.set_song_list(self.songs)

        self.loaded = True
        pass

    def add_song_list_frame(self, songs: list[app.Song]) -> None:
        self.ttk_song_card_list.grid(
            column=COLUMN['ttk_song_card_list'], row=ROW['ttk_song_card_list'])
        self.update_dropdown_list()

        pass

    def update_dropdown_list(self):
        menu = self.ttk_opt_manu["menu"]
        menu.delete(0, "end")
        for song in self.songs:
            menu.add_command(label=song.title,
                             command=lambda value=song.title: self.curr_song.set(value))
        pass

    def start(self):
        self.mainloop()

    def end(self):
        self.destroy()


class InputPanel(Frame):
    url_var: StringVar
    INPUT_PACEHOLDER = 'Enter song or playlint link here'

    def __init__(self, master: Misc | None = ..., callback=None) -> None:
        super().__init__(master)

        self.url_var = StringVar()
        input_field = Entry(self, width=75, textvariable=self.url_var)
        input_field.grid(column=0, row=0)
        input_field.insert(0, self.INPUT_PACEHOLDER)
        input_field.bind(
            '<Button-1>', lambda *args: input_field.delete(0, 'end'))

        Button(self, text="Load", command=lambda: callback(
            self.url_var.get())).grid(column=1, row=0)


class EditPanel(Frame):
    songs: list[app.Song]
    song_panel: SongPanel

    all_titles: list[str]

    om: OptionMenu
    curr: StringVar

    def __init__(self, master: Misc | None = ..., songs: list[app.Song] = []) -> None:
        super().__init__(master)
        self.songs = songs

        self.curr = StringVar()
        self.all_titles = []
        self.om = OptionMenu(self, self.curr, self.all_titles)
        self.om.grid(column=0, row=0)

        Button(self, text='View', command=self.show).grid(column=1, row=0)

        self.song_panel = SongPanel(self, self.update_song)
        self.song_panel.grid(column=0,row=1)

    def set_song_list(self, songs: list[app.Song]):
        self.songs = songs
        self.all_titles = [song.title for song in self.songs]
        self.curr.set(self.all_titles[0])
        self.update()
        pass

    def show(self):
        title = self.curr.get()

        s = None
        for song in self.songs:
            if song.title == title:
                s = song
                break
        self.song_panel.set_song(s)

    def update(self):
        menu = self.om["menu"]
        menu.delete(0, "end")
        for title in self.all_titles:
            menu.add_command(
                label=title, command=lambda value=title: self.curr.set(value))

    def update_song(self, song: app.Song):
        all_titles = [s.title for s in self.songs]
        song_index = self.all_titles.index(self.curr.get())
        self.all_titles = all_titles

        self.curr.set(song.title)
        self.songs[song_index] = song
        self.update()

        pass


class SongPanel(ttk.Frame):
    song: app.Song

    author_var: StringVar
    title_var: StringVar
    album_var: StringVar
    url_var: StringVar
    size_var: StringVar

    def __init__(self, master: Misc | None, callback=None) -> None:
        super().__init__(master)
        self.callback = callback
        # self.song = song
        self.author_var = StringVar()
        self.title_var = StringVar()
        self.album_var = StringVar()
        self.url_var = StringVar()
        self.size_var = StringVar()

        Label(self, text='Author: ').grid(column=0, row=1)
        tmp = Entry(self, textvariable=self.author_var,
                    width=30)
        tmp.grid(column=1, row=1)
        # tmp.insert(0, self.song.author)

        Label(self, text='Title: ').grid(column=0, row=2)
        tmp = Entry(self, textvariable=self.title_var,
                    width=30)
        tmp.grid(column=1, row=2)
        # tmp.insert(0, self.song.title)

        Label(self, text='Album: ').grid(column=0, row=3)
        tmp = Entry(self, textvariable=self.album_var,
                    width=30)
        tmp.grid(column=1, row=3)
        # tmp.insert(0, self.song.album)

        Label(self, text='Url: ').grid(column=0, row=4)
        Label(self, textvariable=self.url_var).grid(column=1, row=4)

        Label(
            self, text='Size: ').grid(column=0, row=5)
        Label(
            self, textvariable=self.size_var).grid(column=1, row=5)

        Button(self, text='Save', command=self.update).grid(column=1, row=6)

    def set_song(self, song: app.Song):
        self.song = song
        self.author_var.set(song.author)
        self.title_var.set(song.title)
        self.album_var.set(song.album)
        self.url_var.set(song.url)
        self.size_var.set(f'{round(song.size/1024/1024, 2)}MB')

    def update(self):
        self.song.author = self.author_var.get()
        self.song.title = self.title_var.get()
        self.song.album = self.album_var.get()
        self.callback(self.song)


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
