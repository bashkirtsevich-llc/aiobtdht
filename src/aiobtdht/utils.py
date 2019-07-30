import asyncio
from hashlib import sha1
from os import getrandom
from socket import inet_aton, inet_ntoa


def random(size=1):
    return getrandom(size)


def calc_sha1(data):
    return sha1(data).digest()


def encode_id(id_):
    return id_.to_bytes(20, "big")


def decode_id(id_):
    if len(id_) != 20:
        raise ValueError("Wrong length")

    return int.from_bytes(id_, "big")


def decode_info_hash(info_hash):
    return decode_id(info_hash)


def encode_addr(addr):
    host, port = addr
    return b"".join((inet_aton(host), port.to_bytes(2, "big")))


def decode_addr(addr):
    host, port = addr[:4], addr[4:6]
    return (inet_ntoa(host), int.from_bytes(port, "big"))


def encode_nodes(nodes):
    return b"".join(b"".join((encode_id(id_), encode_addr(addr))) for id_, addr in nodes)


def decode_nodes(nodes):
    if len(nodes) % 26 != 0:
        raise ValueError("Wrong length")

    return [(decode_id(nodes[i: i + 20]), decode_addr(nodes[i + 20: i + 26])) for i in range(0, len(nodes), 26)]


def encode_peers(peers):
    return [encode_addr(peer) for peer in peers]


def decode_peers(peers):
    return [decode_addr(peer) for peer in peers]


async def run_every(f, delay):
    while True:
        r = f()

        if asyncio.iscoroutine(r):
            await r

        await asyncio.sleep(delay)


async def call_timeout(f, timeout, default):
    try:
        return await asyncio.wait_for(f, timeout)
    except asyncio.TimeoutError:
        return default
