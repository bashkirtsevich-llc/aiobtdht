from .utils import decode_id
from .utils import decode_nodes
from .utils import decode_peers
from .utils import encode_id
from .utils import encode_nodes
from .utils import encode_peers

_ID_ENCODE_SCHEMA = {"type": "binary", "minlength": 20, "maxlength": 20, "coerce": encode_id}
_ID_DECODE_SCHEMA = {"type": "integer", "coerce": decode_id}

_INFO_HASH_ENCODE_SCHEMA = _ID_ENCODE_SCHEMA
_INFO_HASH_DECODE_SCHEMA = _ID_DECODE_SCHEMA

_NODES_ENCODE_SCHEMA = {"type": "binary", "coerce": encode_nodes}
_NODES_DECODE_SCHEMA = {"type": "list", "coerce": decode_nodes}

_VALUES_ENCODE_SCHEMA = {"type": "list", "coerce": encode_peers, "schema": {"type": "binary"}}
_VALUES_DECODE_SCHEMA = {"type": "list", "coerce": decode_peers}

_TOKEN_SCHEMA = {"type": "binary"}

PING_ARGS = {"id": {"required": True, **_ID_DECODE_SCHEMA}}
PING_RESULT = {"id": {"required": True, **_ID_ENCODE_SCHEMA}}
PING_ARGS_REMOTE = {"id": {"required": True, **_ID_ENCODE_SCHEMA}}
PING_RESULT_REMOTE = {"id": {"required": True, **_ID_DECODE_SCHEMA}}

FIND_NODE_ARGS = {
    "id": {"required": True, **_ID_DECODE_SCHEMA},
    "target": {"required": True, **_ID_DECODE_SCHEMA}}
FIND_NODE_RESULT = {
    "id": {"required": True, **_ID_ENCODE_SCHEMA},
    "nodes": {"required": True, **_NODES_ENCODE_SCHEMA}}
FIND_NODE_ARGS_REMOTE = {
    "id": {"required": True, **_ID_ENCODE_SCHEMA},
    "target": {"required": True, **_ID_ENCODE_SCHEMA}}
FIND_NODE_RESULT_REMOTE = {
    "id": {"required": True, **_ID_DECODE_SCHEMA},
    "nodes": {"required": True, **_NODES_DECODE_SCHEMA}}

GET_PEERS_ARGS = {
    "id": {"required": True, **_ID_DECODE_SCHEMA},
    "info_hash": {"required": True, **_INFO_HASH_DECODE_SCHEMA}}
GET_PEERS_RESULT = {
    "id": {"required": True, **_ID_ENCODE_SCHEMA},
    "token": {"type": "binary", "required": True},
    "nodes": _NODES_ENCODE_SCHEMA,
    "values": _VALUES_ENCODE_SCHEMA
}
GET_PEERS_ARGS_REMOTE = {
    "id": {"required": True, **_ID_ENCODE_SCHEMA},
    "info_hash": {"required": True, **_INFO_HASH_ENCODE_SCHEMA}}
GET_PEERS_RESULT_REMOTE = {
    "id": {"required": True, **_ID_DECODE_SCHEMA},
    "token": {"type": "binary", "required": True},
    "nodes": _NODES_DECODE_SCHEMA,
    "values": _VALUES_DECODE_SCHEMA
}

ANNOUNCE_PEER_ARGS = {
    "id": {"required": True, **_ID_DECODE_SCHEMA},
    "info_hash": {"required": True, **_INFO_HASH_DECODE_SCHEMA},
    "token": {"required": True, **_TOKEN_SCHEMA},
    "implied_port": {"type": "integer", "required": False, "min": 0, "max": 1}}
ANNOUNCE_PEER_RESULT = {"id": {"required": True, **_ID_ENCODE_SCHEMA}}
ANNOUNCE_PEER_ARGS_REMOTE = {
    "id": {"required": True, **_ID_ENCODE_SCHEMA},
    "info_hash": {"required": True, **_INFO_HASH_ENCODE_SCHEMA},
    "token": {"required": True, **_TOKEN_SCHEMA},
    "implied_port": {"type": "integer", "required": False, "min": 0, "max": 1}}
ANNOUNCE_PEER_RESULT_REMOTE = {"id": {"required": True, **_ID_DECODE_SCHEMA}}
