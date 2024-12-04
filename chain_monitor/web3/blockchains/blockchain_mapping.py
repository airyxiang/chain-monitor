from .ava import Ava
from .bsc import Bsc
from .eth import Eth
# from .tron import Tron, is_address as is_tron_address
from .tron import Tron
from ..constants import Blockchain


class UnknownBlockchainId(Exception):
    pass


def blockchain_id_for_address(address):
    if len(address) == 42 and address.startswith('0x'):
        return Blockchain.ETH
    # elif is_tron_address(address):
    #     return Blockchain.TRON
    else:
        raise NotImplementedError


def get_blockchain_by_id(blockchain_id):
    try:
        return _get_blockchain_by_id(blockchain_id)
    except KeyError as e:
        raise UnknownBlockchainId(blockchain_id) from e


def _get_blockchain_by_id(blockchain_id):
    mapping = {
        Blockchain.ETH: Eth,
        Blockchain.AVA: Ava,
        Blockchain.TRON: Tron,
        Blockchain.BSC: Bsc,
    }
    return mapping[blockchain_id]
