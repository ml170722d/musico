from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor

import os
import signal
from threading import Thread
import multiprocessing as mp
from tkinter import ttk
from tkinter import *
import src.app as app
import logging

logger = logging.getLogger(__name__)


class App(Tk):
    labelText: StringVar
    songs: list[app.Song]
    url: StringVar
    errorMsg: StringVar

    def __init__(self) -> None:
        super().__init__()
        self.labelText = StringVar()
        self.errorMsg = StringVar()
        self.url = StringVar()
        self.songs = []

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
        with ThreadPoolExecutor(max_workers=mp.cpu_count()) as pool:
            results = pool.map(self.download, self.songs)

        for r in results:
            if (r != True):
                self.labelText.set("Fail!!!")

        self.labelText.set("Success!!!")

    def loadUrl(self):
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
                self.labelText.set("Invalid url")
                return
            pass
        self.labelText.set("")
        pass

    def start(self):
        panel = ttk.Frame(self, padding=10)
        panel.grid()

        ttk.Label(panel, textvariable=self.labelText).grid(column=1, row=0)

        ttk.Button(panel, text="Download", command=Thread(
            target=self.start_download).start).grid(column=0, row=0)
        ttk.Button(panel, text="Load", command=self.loadUrl).grid(
            column=0, row=1)
        ttk.Entry(panel, width=100, textvariable=self.url).grid(
            column=0, row=2)
        ttk.Button(panel, text="Exit", command=self.end).grid(column=10, row=10)

        self.mainloop()

    def end(self):
        os.killpg(os.getpid(), signal.SIGTERM)
        self.destroy()
