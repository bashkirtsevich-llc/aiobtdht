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

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Node):
            return False

        return self.id == __o.id and self.addr == __o.addr
