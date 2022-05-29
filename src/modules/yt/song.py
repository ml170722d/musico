import imp
import logging
import pytube as pt
import pytube.request as pyreq
import pytube.exceptions as exceptions
# import exception as ex


class Song:
    song: pt.YouTube | None
    size: int

    def __init__(self, url: str) -> None:
        try:
            self.song = pt.YouTube(url)
            self.size = pyreq.filesize(url)
        # TODO: Fix import exception
        except exceptions.RegexMatchError as e:
            print(e)
            # raise ex.NotYouTubeSong()
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

    def is_availability(self) -> bool:
        try:
            self.song.check_availability()
        except:
            return False
        return True
