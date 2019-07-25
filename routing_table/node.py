class Node:
    def __init__(self, id_, addr):
        self._id = id_
        self._addr = addr

    @property
    def id(self):
        return self._id

    @property
    def addr(self):
        return self._addr
