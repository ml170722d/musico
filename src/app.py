from __future__ import annotations

import os
import yaml
import logging.config
import logging
import coloredlogs

import pytube as pt
import pytube.request as pyreq
import pytube.exceptions as exceptions
import youtube_dl


def setup_logging(default_path='logging.config.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


setup_logging()


class Song:
    song: pt.YouTube | None
    size: int

    author: str
    title: str
    length: str
    url: str
    thumbnail_url: str

    def __init__(self, url: str) -> None:
        try:
            self.song = pt.YouTube(url)
            self.size = pyreq.filesize(url)

            self.author = self.song.author
            self.title = self.song.title
            self.length = self.song.length
            self.url = self.song.watch_url
            self.thumbnail_url = self.song.thumbnail_url

        # TODO: Fix import exception
        except exceptions.RegexMatchError as e:
            print(e)
            raise e
        except Exception as e:
            logging.warn(e)
            self.song = None

        return None

    def details(self) -> dict[str, str]:
        return {
            'author': f'{self.song.author}',
            'title': f'{self.song.title}',
            'length': f'{self.song.length}',
            'size': f'{self.size}',
            'url': f'{self.song.watch_url}',
            'thumbnail_url': f'{self.song.thumbnail_url}'
        }

    def is_available(self) -> bool:
        try:
            self.song.check_availability()
        except:
            return False
        return True

    def download(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'./test/{self.author} - {self.title}.mp3',
            'noplaylist': True,
            'continue_dl': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.cache.remove()
            ydl.download([self.url])

        pass


class NotYouTubeURL(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotYouTubeSong(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
