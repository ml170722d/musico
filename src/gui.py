from __future__ import annotations
from cgi import test

import os, signal
from threading import Thread
from multiprocessing import Pool, cpu_count
from tkinter import ttk
from tkinter import *
import src.app as app
import logging

logger = logging.getLogger(__name__)

class App(Tk):
    label: StringVar

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _download(song: app.Song):
        for i in range(3):
            try:
                logger.debug("I'm process", os.getpid())
                song.download()
            except:
                logger.warning(f'Process: {os.getpid()} fail number: {i+1}')
                continue

            logger.info(f'Successfully downloaded: {song.author} - {song.title}')
            return True

        logger.info(f'Failed to download: {song.author} - {song.title}')
        return False

    def test(self):
        songs = []
        urls = [
            'https://www.youtube.com/watch?v=E8Ms56gX-Tc',
            'https://www.youtube.com/watch?v=fOg7mj1_-sk',
            'https://www.youtube.com/watch?v=bCt6T5KBID0',
            'https://www.youtube.com/watch?v=EAeZPiZbpvw',
            'https://www.youtube.com/watch?v=bQKK8gLjKHY',
            'https://www.youtube.com/watch?v=OKEyUfGH2tQ'
        ]
        for url in urls:
            songs.append(app.Song(url))

        with Pool(cpu_count()) as pool:
            result = pool.map(self._download, songs)
            print(result)

        for r in result:
            if (r != True):
                self.label.set("Fail!!!")

        self.label.set("Success!!!")

    # def test(self):
    #     thread = Thread(target=self.test2)
    #     thread.start()
    #     pass

    def start(self):
        panel = ttk.Frame(self, padding=10)
        panel.grid()

        self.label = StringVar()
        self.label.set("Not started")
        ttk.Label(panel, textvariable=self.label).grid(column=1, row=0)


        ttk.Button(panel, text="Test", command=Thread(target=self.test).start).grid(column=0, row=0)
        ttk.Button(panel, text="Exit", command=self.end).grid(column=0, row=1)

        self.mainloop()

    def end(self):
        os.killpg(os.getpid(), signal.SIGTERM)
        self.destroy()
