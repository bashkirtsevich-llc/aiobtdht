from .bucket import Bucket
from .node import Node


class RoutingTable:
    def __init__(self, local_id):
        self._local_id = local_id
        self._buckets = {Bucket(0, 2 ** 160)}

    def add(self, id_, addr):
        for bucket in self._buckets:
            if bucket.id_in_range(id_):
                added = bucket.add(Node(id_, addr))

                if not added and self._split(bucket):
                    return self.add(id_, addr)

    # region Internal methods
    def _split(self, bucket):
        if bucket.range_max - bucket.range_min < bucket.max_capacity:
            return False

        self._buckets.remove(bucket)

        median = (bucket.range_max + bucket.range_min) >> 1  # Divide by half

        for new_bucket in (Bucket(bucket.range_min, median), Bucket(median, bucket.range_max)):
            self._buckets.add(new_bucket)
            for node in bucket.nodes:
                if new_bucket.id_in_range(node.id):
                    new_bucket.add(node)

        return True

    def _get_closest(self, target_id, k=8):
        return self.get_k_closest(
            target_id,
            ((node.id, node.addr) for bucket in self._buckets for node in bucket.nodes),
            key=lambda it: it[0],
            k=k
        )

    # endregion

    def enum_nodes_for_refresh(self):
        for b in self._buckets:
            yield from b.enum_nodes_for_refresh()

    @staticmethod
    def get_k_closest(target, iterable, key=None, k=8):
        if key and not callable(key):
            raise

        return sorted(iterable, key=lambda n: (key(n) if key else n) ^ target)[:k]

    def __getitem__(self, item):
        # Item -- node_id or tuple (node_id, k), by default `k == 8`
        if isinstance(item, int):
            return self._get_closest(item)
        elif isinstance(item, tuple) and len(item) == 2:
            return self._get_closest(*item)
        else:
            raise TypeError("Unsupported type")

    def __contains__(self, item):
        return any(item in bucket for bucket in self._buckets)
