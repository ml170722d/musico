import enum
import pytube as pt
import pytube.request as pyreq
import pytube.exceptions as exceptions


class VideoType(enum.Enum):
    PRIVATE = 1
    AVAILABLE = 2
    UNAVAILABLE = 3
    NOT_VIDEO = 4


class NotYouTubeURL(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def details(url: str):
    if isPlaylist(url):
        return __playlist_details__(url)
    else:
        return __song_details__(url)


def __song_details__(url):
    size = pyreq.filesize(url)

    song = pt.YouTube(url, use_oauth=True)
    song.check_availability()

    return {
        'author': f'{song.author}',
        'title': f'{song.title}',
        'length': f'{song.length} s',
        'size': f'{size} B',
        'url': f'{song.watch_url}'
    }


def __playlist_details__(url):
    pl = pt.Playlist(url)

    try:
        return {
            'author': f'{pl.owner}',
            'title': f'{pl.title}',
            'length': f'{pl.length}',
            'size': None,
            'url': f'{pl.playlist_url}'
        }
    except:
        return {
            'author': None,
            'title': None,
            'length': None,
            'size': None,
            'url': None
        }


def isAvailable(url: str) -> VideoType:
    try:
        if not isPlaylist(url):
            pt.YouTube(url).check_availability()
        else:
            return VideoType.NOT_VIDEO

    except exceptions.VideoPrivate:
        return VideoType.PRIVATE
    except:
        return VideoType.UNAVAILABLE

    return VideoType.AVAILABLE


def isPlaylist(url: str) -> bool:
    try:
        pt.Playlist(url)
    except:
        return False
    return True
