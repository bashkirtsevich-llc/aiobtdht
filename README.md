# Asyncio Bittorrent DHT Server
[![Build Status](https://travis-ci.org/bashkirtsevich-llc/aiobtdht.svg?branch=master)](https://travis-ci.org/bashkirtsevich-llc/aiobtdht)

Simply async distributed hash table for Bittorrent network.

Based on [aio-KRPC](https://github.com/bashkirtsevich-llc/aiokrpc) and [aio-UDP](https://github.com/bashkirtsevich-llc/aioudp).

Class hierarchy:
* UDPServer — low level async [U]ser [D]atagram [P]rotocol socket server;
  * KRPCServer — async [K]ademlia [R]emote [P]rocedure [C]all protocol provider; 
    * DHT — implementation of Bittorrent [D]istributed [H]ash [T]able;


## Methods

### `DHT.__init__`

Arguments:
* `local_id` (int) — local node identifier in range [0..2^160).

Optional arguments:
* `upload_speed` (int, default `0`) — outgoing traffic throttler;
* `download_speed` (int, default `0`) — incoming traffic throttler;
* `recv_max_size` (int, default `256 * 1024`) — socket reading buffer size.


### `run`

Launch servering.

Arguments:  
* `host` (str) — local host address, e.g. `0.0.0.0`;
* `port` (int) — local port for outgoing and incoming UDP traffic;
* `loop` (object, default `None`) — asyncio eventloop, will create while `None` and run forever.

Result: `None`.


### async `bootstrap`

Method for initializing routing table.

Arguments:
* `initial_peers` (list, example: `[(ip: str, port: int), ...]`) — list of router for initialize routing table;

Result: `None`.

### async `announce`

Announce peer for specified `info_hash`.

Arguemtns:
* `info_hash` (20 bytes) — binary form of `info_hash`;
* `port` (int, default `None`) — information for announce, value is DHT-server listen port when `None`.

Result: `None`.


### async `__getitem__`

Get peers for torrent by `info_hash`.

Arguemtns:
* `info_hash` (20 bytes) — binary form of `info_hash`;

Result: `Set((host: str, port: int), ...)`.


## Example

```python
import asyncio
from aiobtdht import DHT
from aioudp import UDPServer


async def main(loop):
    initial_nodes = [
        ("67.215.246.10", 6881),  # router.bittorrent.com
        ("87.98.162.88", 6881),  # dht.transmissionbt.com
        ("82.221.103.244", 6881)  # router.utorrent.com
    ]

    udp = UDPServer()
    udp.run("0.0.0.0", 12346, loop=loop)

    dht = DHT(int("0x54A10C9B159FC0FBBF6A39029BCEF406904019E0", 16), server=udp, loop=loop)

    print("bootstrap")
    await dht.bootstrap(initial_nodes)
    print("bootstrap done")

    print("search peers for Linux Mint torrent (8df9e68813c4232db0506c897ae4c210daa98250)")
    peers = await dht[bytes.fromhex("8df9e68813c4232db0506c897ae4c210daa98250")]
    print("peers:", peers)

    print("peer search for ECB3E22E1DC0AA078B48B7323AEBBA827AD9BD80")
    peers = await dht[bytes.fromhex("ECB3E22E1DC0AA078B48B7323AEBBA827AD9BD80")]
    print("peers:", peers)

    print("announce with port `2357`")
    await dht.announce(bytes.fromhex("ECB3E22E1DC0AA078B48B7323AEBBA827AD9BD80"), 2357)
    print("announce done")

    print("search our own ip")
    peers = await dht[bytes.fromhex("ECB3E22E1DC0AA078B48B7323AEBBA827AD9BD80")]
    print("peers:", peers)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
```

Output:
```
bootstrap
bootstrap done
search peers for Linux Mint torrent (8df9e68813c4232db0506c897ae4c210daa98250)
peers: {('146.120.244.10', 1078), ('162.244.138.182', 42000), ('79.226.71.128', 16881), ('24.236.49.9', 41785), ('91.138.144.37', 1487), ('68.44.225.100', 8967), ('80.44.205.104', 6881), ('212.32.229.66', 1160), ('108.204.244.160', 51413), ('66.130.106.74', 49160), ('90.128.48.99', 1348), ('188.232.107.50', 61025), ('173.44.55.179', 8589), ('46.242.8.31', 51413), ('181.97.186.68', 51413), ('68.114.220.251', 49237), ('172.98.67.53', 31545), ('94.212.149.191', 16881), ('188.163.46.182', 31217), ('185.148.3.42', 58489), ('37.24.80.202', 6881), ('86.159.123.195', 51413), ('88.202.177.238', 41280), ('87.79.216.207', 50000), ('73.24.30.122', 35727), ('212.32.229.66', 1842), ('97.103.206.29', 53314), ('58.6.89.141', 1157), ('78.92.112.15', 60745), ('124.176.208.220', 51413), ('68.44.225.100', 5051), ('188.6.231.166', 51413), ('58.6.89.141', 1099), ('99.28.209.57', 29694), ('108.172.92.81', 55555), ('46.107.192.126', 8999), ('212.232.79.196', 27886), ('24.236.49.9', 14100), ('84.28.172.201', 51413), ('188.195.3.8', 51413), ('92.110.18.80', 8999), ('91.153.229.129', 51413), ('5.196.71.175', 51413), ('185.21.217.21', 56031), ('93.77.142.76', 63193), ('145.130.138.96', 51413), ('73.14.170.195', 51413), ('79.121.6.189', 6318), ('78.142.23.65', 57171), ('101.112.156.11', 51413), ('195.242.156.241', 1194), ('92.247.152.29', 54217), ('81.171.9.199', 50781), ('75.108.45.243', 51413), ('172.98.67.53', 1842), ('68.44.225.100', 53849), ('81.171.9.199', 23542), ('37.214.48.240', 51413), ('72.177.3.209', 51413), ('93.203.236.159', 51413), ('95.154.19.186', 6881), ('50.39.164.144', 16881), ('88.223.24.14', 51413), ('213.188.38.130', 8999), ('85.3.104.53', 51413), ('173.69.6.72', 51413), ('46.166.190.136', 46825), ('45.231.194.211', 41481), ('77.50.127.80', 41446), ('5.39.88.54', 49420), ('78.42.236.30', 16881), ('5.227.15.139', 42068), ('31.17.12.154', 51413), ('41.188.115.45', 56763), ('46.246.123.24', 39574), ('144.172.126.68', 65516), ('72.14.181.193', 62904), ('90.128.48.99', 1347), ('90.92.181.147', 16881), ('184.175.133.66', 8999), ('185.45.195.161', 20064), ('188.243.178.111', 51413), ('139.47.117.179', 49967), ('88.138.252.41', 57837), ('91.237.164.182', 57310), ('199.204.160.119', 51413), ('50.39.198.212', 8999), ('183.89.65.240', 44808), ('90.154.5.75', 51413), ('68.44.225.100', 58836), ('89.165.156.40', 32435), ('23.227.192.103', 51413), ('217.10.117.5', 55179), ('83.149.46.57', 51413), ('217.120.102.36', 22449), ('27.255.16.95', 40001), ('68.44.225.100', 11790), ('98.142.213.39', 7401), ('38.141.32.249', 49222), ('71.38.191.134', 51413), ('68.44.225.100', 15234), ('24.236.49.9', 42805), ('74.205.141.130', 8999), ('46.158.232.118', 63782), ('66.78.249.53', 42065), ('78.239.83.41', 50505), ('89.134.45.63', 51413), ('89.202.42.62', 51413), ('198.48.184.203', 51157), ('172.98.67.53', 2623), ('109.104.17.83', 50000), ('80.128.42.85', 51413), ('82.253.238.71', 51413), ('81.171.9.199', 10128), ('68.44.225.100', 47320), ('88.172.132.57', 12464), ('84.57.138.103', 51413), ('68.44.225.100', 7158), ('23.82.10.32', 40779), ('5.189.164.178', 62924), ('86.171.122.135', 51413), ('91.226.253.69', 1039), ('188.32.24.204', 17691), ('79.121.6.189', 1060), ('68.44.225.100', 34255), ('68.44.225.100', 42549), ('91.227.46.177', 51413), ('87.253.244.34', 16881), ('73.64.230.136', 51413), ('203.184.52.1', 8999), ('66.78.249.53', 8999), ('109.197.193.160', 56172), ('109.252.2.116', 8197), ('151.252.157.50', 61213), ('37.53.35.117', 32852), ('74.140.192.66', 18954), ('71.197.139.141', 51413), ('173.179.36.233', 58948), ('75.174.143.174', 55265), ('70.56.193.245', 51413)}
peer search for ECB3E22E1DC0AA078B48B7323AEBBA827AD9BD80
peers: {('192.168.10.10', 2357)}
announce with port `2357`
announce done
search our own ip
peers: {('192.168.10.10', 2357)}
```

## Links

* [AIO-KRPC](https://github.com/bashkirtsevich-llc/aiokrpc); 
* [AIO-UDP](https://github.com/bashkirtsevich-llc/aioudp);
* [BEP 0005](http://www.bittorrent.org/beps/bep_0005.html);
* [DHT on Wikipedia](https://en.wikipedia.org/wiki/Distributed_hash_table);