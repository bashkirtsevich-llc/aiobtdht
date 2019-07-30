import asyncio
from collections import namedtuple
from datetime import datetime

from aiokrpc import KRPCServer
from aiokrpc.exceptions import KRPCErrorResponse
from aiokrpc.exceptions import KRPCProtocolError

from .routing_table import RoutingTable
from .schemas import ANNOUNCE_PEER_ARGS
from .schemas import ANNOUNCE_PEER_ARGS_REMOTE
from .schemas import ANNOUNCE_PEER_RESULT
from .schemas import ANNOUNCE_PEER_RESULT_REMOTE
from .schemas import FIND_NODE_ARGS
from .schemas import FIND_NODE_ARGS_REMOTE
from .schemas import FIND_NODE_RESULT
from .schemas import FIND_NODE_RESULT_REMOTE
from .schemas import GET_PEERS_ARGS
from .schemas import GET_PEERS_ARGS_REMOTE
from .schemas import GET_PEERS_RESULT
from .schemas import GET_PEERS_RESULT_REMOTE
from .schemas import PING_ARGS
from .schemas import PING_ARGS_REMOTE
from .schemas import PING_RESULT
from .schemas import PING_RESULT_REMOTE
from .utils import calc_sha1
from .utils import call_timeout
from .utils import decode_info_hash
from .utils import random
from .utils import run_every

PeerInfo = namedtuple("peer_info", ["addr", "port", "implied_port", "added"])


class ArgsError(Exception):
    pass


class ResultError(Exception):
    pass


class DHT(KRPCServer):
    def __init__(self, local_id, **kwargs):
        super().__init__(**kwargs)

        self.id = local_id
        self.routing_table = RoutingTable(local_id)

        self.torrents = {}
        self.salts = []

        # region Callbacks registration
        self.register_callback(self.ping, arg_schema=PING_ARGS, result_schema=PING_RESULT)
        self.register_callback(self.find_node, arg_schema=FIND_NODE_ARGS, result_schema=FIND_NODE_RESULT)
        self.register_callback(self.get_peers, arg_schema=GET_PEERS_ARGS, result_schema=GET_PEERS_RESULT)
        self.register_callback(self.announce_peer, arg_schema=ANNOUNCE_PEER_ARGS, result_schema=ANNOUNCE_PEER_RESULT)
        # endregion

    # region Server methods
    def ping(self, addr, id):
        self._add_node(node_id=id, addr=addr)
        return self._get_result_id()

    def find_node(self, addr, id, target):
        self._add_node(node_id=id, addr=addr)
        return {
            "nodes": self.routing_table[target],
            **self._get_result_id()
        }

    def get_peers(self, addr, id, info_hash):
        self._add_node(node_id=id, addr=addr)

        peers = self.torrents.get(info_hash, None)
        if peers:
            return {
                **self._get_result_id(), **self._get_result_token(addr),
                "values": list(map(lambda it: (it.addr[0], it.addr[1] if it.implied_port else it.port), peers))
            }
        else:
            return {**self.find_node(addr, id, info_hash), **self._get_result_token(addr)}

    def announce_peer(self, addr, id, info_hash, port, token, implied_port=0):
        if self._check_token(addr, token):
            self.torrents.setdefault(info_hash, set()).add(
                PeerInfo(
                    addr=addr,
                    port=port,
                    implied_port=implied_port,
                    added=datetime.now()
                )
            )
            return self._get_result_id()
        else:
            raise KRPCProtocolError("Bad token")

    # endregion

    # region Utils
    def _get_result_id(self):
        return {"id": self.id}

    def _gen_tokens(self, addr):
        for salt in self.salts:
            yield calc_sha1(b"".join((bytes(str(addr), "utf-8"), salt)))

    def _gen_token(self, addr):
        return next(self._gen_tokens(addr))

    def _get_result_token(self, addr):
        return {"token": self._gen_token(addr)}

    def _check_token(self, addr, token):
        return any(token == t for t in self._gen_tokens(addr))

    def _add_node(self, node_id, addr):
        self.routing_table.add(node_id, addr)

    def _run_every(self, f, delay):
        self._run_future(run_every(f, delay))

    # endregion

    # region Remote calls

    async def _remote_call(self, addr, method, kwargs, timeout=3, arg_schema=None, result_schema=None):
        def _args_error(e):
            raise ArgsError()

        def _result_error(e):
            raise ResultError()

        try:
            result = await call_timeout(
                self.call_remote(
                    addr, method, **self.apply_schema(kwargs, arg_schema or {}, _args_error)
                ), timeout, None
            )
            if result:
                return result[0], self.apply_schema(result[1], result_schema or {}, _result_error)

            return None
        except (KRPCErrorResponse, ResultError):
            return None

    async def remote_ping(self, addr, timeout=3):
        return await self._remote_call(
            addr, "ping",
            kwargs={"id": self.id},
            timeout=timeout,
            arg_schema=PING_ARGS_REMOTE,
            result_schema=PING_RESULT_REMOTE
        )

    async def remote_find_node(self, addr, target_id, timeout=3):
        return await self._remote_call(
            addr, "find_node",
            kwargs={"id": self.id, "target": target_id},
            timeout=timeout,
            arg_schema=FIND_NODE_ARGS_REMOTE,
            result_schema=FIND_NODE_RESULT_REMOTE
        )

    async def remote_get_values(self, addr, info_hash, timeout=3):
        return await self._remote_call(
            addr, "get_peers",
            kwargs={"id": self.id, "info_hash": info_hash},
            timeout=timeout,
            arg_schema=GET_PEERS_ARGS_REMOTE,
            result_schema=GET_PEERS_RESULT_REMOTE
        )

    async def remote_announce_peer(self, addr, info_hash, port, token, implied_port, timeout=3):
        return await self._remote_call(
            addr, "announce_peer",
            kwargs={"id": self.id, "info_hash": info_hash, "port": port, "token": token, "implied_port": implied_port},
            timeout=timeout,
            arg_schema=ANNOUNCE_PEER_ARGS_REMOTE,
            result_schema=ANNOUNCE_PEER_RESULT_REMOTE
        )

    # endregion

    def connection_made(self):
        for args in (
                (self._refresh_nodes, 60),
                (self._rotate_salts, 60),
                (self._forget_torrents, 60)):
            self._run_every(*args)

    # region Periodic tasks
    async def _refresh_nodes(self):
        responses = filter(
            lambda response: response,
            await asyncio.gather(
                *(self.remote_ping(node[1]) for node in self.routing_table.enum_nodes_for_refresh()),
                loop=self.loop
            )
        )

        for addr, data in responses:
            self._add_node(node_id=data["id"], addr=addr)

    def _rotate_salts(self):
        self.salts.insert(0, calc_sha1(random(128)))

        if len(self.salts) > 10:
            self.salts.pop(-1)

    def _forget_torrents(self):
        now = datetime.now()

        for info_hash, values in list(self.torrents.items()):
            for value in list(values):
                if (now - value.added).seconds >= 30 * 60:
                    values.remove(value)

            if not values:
                self.torrents.pop(info_hash)

    # endregion

    async def _group_invoke(self, cb, peers):
        return filter(
            lambda response: response and response[1]["id"] != self.id,
            await asyncio.gather(
                *(cb(peer) for peer in peers),
                loop=self.loop
            )
        )

    async def _get_values(self, info_hash, announce=False, port=None):
        result = set()
        known = set()
        tokens = set()
        peers = map(lambda it: it[1], self.routing_table[info_hash])

        while True:
            responses = await self._group_invoke(lambda peer: self.remote_get_values(peer, info_hash), peers)

            candidates = set()
            for addr, data in responses:
                candidates.update(data.get("nodes", []))
                result.update(data.get("values", []))

                token = data.get("token")
                if token:
                    tokens.add((addr, token))

            closest = RoutingTable.get_k_closest(info_hash, candidates - known, key=lambda it: it[0])

            if closest:
                known.update(candidates)
                peers = map(lambda it: it[1], closest)
            else:
                if announce:
                    await self._group_invoke(
                        lambda it: self.remote_announce_peer(
                            it[0], info_hash, port or 0, it[1], 1 if port is None else 0),
                        tokens
                    )
                    return
                else:
                    return result

    async def bootstrap(self, initial_peers):
        known = set()
        peers = initial_peers

        while True:
            responses = await self._group_invoke(lambda peer: self.remote_find_node(peer, self.id), peers)

            candidates = set()
            for addr, data in responses:
                self._add_node(node_id=data["id"], addr=addr)
                candidates.update(data["nodes"])

            closest = RoutingTable.get_k_closest(self.id, candidates - known, key=lambda it: it[0])

            if closest:
                known.update(candidates)
                peers = map(lambda it: it[1], closest)
            else:
                break

    async def announce(self, info_hash, port=None):
        await self._get_values(decode_info_hash(info_hash), announce=True, port=port)

    def __getitem__(self, item):
        return self._get_values(decode_info_hash(item))
