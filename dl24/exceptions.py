class DL24Error(Exception):
    pass


class DL24NoResponseError(DL24Error):
    def __init__(self):
        super().__init__("no response")
