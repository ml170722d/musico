from __future__ import annotations

import os
import re
# from tkinter.tix import InputOnly
import yaml
import logging.config
import logging
import coloredlogs

import pytube as pt
import pytube.request as pyreq
import pytube.exceptions as exceptions
# import youtube_dl
import music_tag as mt

LOCATION = './data/downloads'

# TODO: Mode to somekind of setup file/dir
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


# setup_logging()

# TODO: Move to separate file
class Song:
    song: pt.YouTube | None
    size: int

    author: str
    title: str
    album: str
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
            self.album = ''

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
        # TODO: Move to config file of something like that

        self.author = ''.join(self.author.split('\\')).strip()
        self.title = ''.join(self.title.split('\\')).strip()

        try:
            itag = self.song.streams.filter(only_audio=True).get_audio_only().itag
            self.song.streams.get_by_itag(itag).download(output_path=f'{LOCATION}', filename=f'{self.author} - {self.title}.mp3')
        except Exception as e:
            print(f'Faild to download {self.author} - {self.title}! ({self.url})')

        # ydl_opts = {
        #     'format': 'bestaudio/best',
        #     'outtmpl': f'{LOCATION}/{self.album}/{self.author} - {self.title}.mp3',
        #     'noplaylist': True,
        #     'continue_dl': True,
        #     'postprocessors': [{
        #         'key': 'FFmpegExtractAudio',
        #         'preferredcodec': 'mp3',
        #         'preferredquality': '192', }]
        # }

        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        #     ydl.cache.remove()
        #     ydl.download([self.url])


        pass

class PlayList:
    url: str

    def __init__(self, url: str) -> None:
        if re.match('.*youtube.*list=.*', url) is None:
            raise NotYouTubePlaylist()
        self.url = url

    def getSongs(self) -> list[Song]:
        list = []
        pl = pt.Playlist(self.url)

        for song_url in pl.video_urls:
            song = Song(song_url)
            list.append(song)

        return list

class MP3TagEditor:
    def __init__(self, location: str, song: Song) -> None:
        try:
            file = mt.load_file(f'{location}/{song.album}/{song.author} - {song.title}.mp3')
            file['artist'] = song.author
            file['title'] = song.title
            file['album'] = song.album
            file.save()
        except Exception as e:
            print(f'Error editing tags for "{location}/{song.album}/{song.author} - {song.title}.mp3": {e}')

        pass

# TODO: Move to separate file
class NotYouTubeURL(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# TODO: Move to separate file
class NotYouTubePlaylist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# TODO: Move to separate file
class NotYouTubeSong(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
