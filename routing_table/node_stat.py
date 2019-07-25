from datetime import datetime


class NodeStat:
    def __init__(self):
        self._added = datetime.now()
        self._last_response = self._added

    def renew(self):
        self._last_response = datetime.now()

    @property
    def rate(self):
        now = datetime.now()
        delta = (now - self._last_response).seconds

        if delta < 15 * 60:
            return (now - self._last_response).seconds / (30 * 60) + 1
        elif delta > 30 * 60:
            return -1
        else:
            return 0

    @property
    def last_response(self):
        return self._last_response
