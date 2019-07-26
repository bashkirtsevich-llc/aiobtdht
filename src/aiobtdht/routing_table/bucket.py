from .node_stat import NodeStat


class Bucket:
    def __init__(self, range_min, range_max, max_capacity=8):
        self._range_min = range_min
        self._range_max = range_max
        self._max_capacity = max_capacity
        self._nodes = {}

    def __hash__(self):
        return hash((self._range_min, self._range_max))

    def id_in_range(self, id_):
        return self._range_min <= id_ < self._range_max

    def add(self, node):
        if not self.id_in_range(node.id):
            raise IndexError("Node id not in bucket range")

        if node in self._nodes:
            self._nodes[node].renew()
            return True
        elif len(self._nodes) < self._max_capacity:
            self._nodes[node] = NodeStat()
            return True
        else:
            can_delete = list(filter(lambda it: it[1].rate < 0, self._enum_nodes()))
            if can_delete:
                for it in can_delete:
                    self._nodes.pop(it)

                return self.add(node)
            else:
                return False

    def _enum_nodes(self):
        for node, stat in self._nodes.items():
            yield node, stat

    def enum_nodes_for_refresh(self):
        return map(lambda it: it[0].addr, filter(lambda it: it[1].rate <= 0, self._enum_nodes()))

    @property
    def range_min(self):
        return self._range_min

    @property
    def range_max(self):
        return self._range_max

    @property
    def max_capacity(self):
        return self._max_capacity

    @property
    def nodes(self):
        # Return only good nodes
        return map(lambda it: it[0], filter(lambda it: it[1].rate > 0, self._enum_nodes()))

    def __contains__(self, item):
        if isinstance(item, int):
            return any(item == node.id for node in self._nodes)
        elif isinstance(item, tuple):
            return any(item == node for node in self._nodes)
        else:
            raise TypeError("Unsupported type")
