from ast import arg
import os
from multiprocessing import Pool, cpu_count
from tkinter import ttk
from tkinter import *
import src.app as app
import logging

logger = logging.getLogger(__name__)
root = None

def dl(song: app.Song):
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


def test(root: Tk):
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
        result = pool.map(dl, songs)
        print(result)

    root.destroy()


def init():
    root = Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    ttk.Button(frm, text="Start", command=lambda: test(root)).grid(column=1, row=0)
    root.mainloop()
