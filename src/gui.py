from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
# import os
from threading import Thread
import multiprocessing as mp
import time
from tkinter import ttk
from tkinter import *
import webbrowser
import logging

import src.app as app


logger = logging.getLogger(__name__)


class App(Tk):
    app_panel: AppPanel

    def __init__(self) -> None:
        super().__init__()
        self.app_panel = AppPanel(self, self.end)
        self.app_panel.grid(column=0, row=0)

    def start(self):
        self.mainloop()

    def end(self):
        self.destroy()


class AppPanel(Frame):
    label_var: StringVar
    loaded: bool
    edit_panel: EditPanel

    def __init__(self, master: Misc | None, end_cb) -> None:
        super().__init__(master)
        self.label_var = StringVar()
        self.loaded = False

        # input feild and load button
        InputPanel(self, self.load).grid(column=0, row=0)

        # label for displaying app status
        Label(self, textvariable=self.label_var).grid(
            column=0, row=1)

        # Download button
        Button(self, text="Download", command=Thread(
            target=self.start_download).start).grid(column=1, row=1)

        # panel for editing song info
        self.edit_panel = EditPanel(self)
        self.edit_panel.grid(column=0, row=2)

        Button(self, text="Exit",
               command=end_cb).grid(column=2, row=3)

        Button(self, text="Report Bugs", command=lambda: webbrowser.open(
            'https://github.com/ml170722d/musico/issues/new')).grid(column=1, row=3)

    def load(self, url) -> None:
        t = Thread(target=lambda: self.loadUrl(url))
        t.setDaemon(True)
        t.start()
        pass

    def loadUrl(self, url: str) -> None:
        task = TextChangingTask(self.label_var, [
            "Loading",
            "Loading.",
            "Loading..",
            "Loading...",
        ])
        thread = Thread(target=task.run)
        thread.setDaemon(True)
        thread.start()

        songs = []
        try:
            pl = app.PlayList(url)
            songs = pl.getSongs()
        except:
            try:
                song = app.Song(url)
                songs.append(song)
            except:
                task.terminate()
                thread.join()
                self.label_var.set("Invalid url")
                return
            pass

        task.terminate()
        thread.join()

        self.label_var.set("Loaded")
        self.loaded = True
        self.edit_panel.set_song_list(songs)
        pass

    def download(self, song: app.Song) -> bool:
        for i in range(3):
            try:
                # logger.debug("I'm process", os.getpid())
                song.download()
            except:
                # logger.warning(f'Process: {os.getpid()} fail number: {i+1}')
                continue

            logger.info(
                f'Successfully downloaded: {song.author} - {song.title}')
            return True

        logger.info(f'Failed to download: {song.author} - {song.title}')
        return False

    def start_download(self) -> None:
        edited_songs = self.edit_panel.get_edited_songs()

        if not self.loaded:
            self.label_var.set("Load song or playlist first!!!")
            return

        task = TextChangingTask(self.label_var, [
            "Downloading",
            "Downloading.",
            "Downloading..",
            "Downloading...",
        ])
        thread = Thread(target=task.run)
        thread.setDaemon(True)
        thread.start()

        # with ThreadPoolExecutor(max_workers=mp.cpu_count()) as pool:
        with ThreadPoolExecutor(max_workers=1) as pool:
            results = pool.map(self.download, edited_songs)

        for r in results:
            if (r != True):
                task.terminate()
                thread.join()

                self.label_var.set("Could not download all selected song(s)")
                return


        for song in edited_songs:
            app.MP3TagEditor(app.LOCATION, song)
            pass


        task.terminate()
        thread.join()

        self.label_var.set("Success!!!")
        pass


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
        self.om.bind('<ButtonRelease>', lambda *args: self.show())

        # Button(self, text='View', command=self.show).grid(column=1, row=0)

        self.song_panel = SongPanel(self, self.update_song)
        self.song_panel.grid(column=0, row=1)

    def set_song_list(self, songs: list[app.Song]):
        self.songs = songs
        self.all_titles = [song.title for song in self.songs]
        self.curr.set(self.all_titles[0])
        self.update()
        self.show()
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

    def get_edited_songs(self) -> list[app.Song]:
        return self.songs


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
