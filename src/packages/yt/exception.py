class NotYouTubeURL(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotYouTubeSong(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
