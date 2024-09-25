import json
import requests
from typing import List

from chain_monitor.configurations.logger import get_logger
from chain_monitor.exceptions import FieldError
from chain_monitor.utils.data import SimpleEnum
from chain_monitor.web3.blockchains.exceptions import BlockchainRPCError

logger = get_logger(__name__)


class TransactionStatus(SimpleEnum):
    NOT_FOUND = 'not_found'
    PENDING = 'pending'
    CONFIRMED_FAILURE = 'confirmed_failure'
    CONFIRMED_SUCCESS = 'confirmed_success'


class Blockchain:
    ID = None

    @staticmethod
    def name():
        """
        returns the long-form name of this blockchain
        """
        raise NotImplementedError

    @staticmethod
    def get_from_address(tx_data):
        """
        Given the signing-service transaction data, determine the from address
        """
        return tx_data['from']

    @staticmethod
    def validate_address(blockchain_address) -> List[FieldError]:
        """
        Validate if a given blockchain address is valid, returns a list of FieldErrors
        """
        raise NotImplementedError

    def fetch_transaction(transaction_hash):
        """
        Given a transaction hash as returned by signing_service.mign_transaction
        Return the transaction, as returned by construct_mint
        """
        raise NotImplementedError

    def fetch_transaction_status(transaction_hash):
        """
        Given a transaction hash as returned by signing_service.mign_transaction
        Return the status of the transaction:
        * NOT_FOUND: the transaction is not known to the blockchain
        * PENDING: the transaction is known to the blockchain but has not confirmed
        * CONFIRMED_FAILURE: the transaction confirmed in the blockchain but was unsuccessful
        * CONFIRMED_SUCCESS: the transaction confirmed in the blockchain and was successful
        """
        raise NotImplementedError

    @classmethod
    def fetch_transactions_by_event(cls, address, from_block_number, to_block_number, topic):
        data = json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getLogs',
            'address': address,
            'params': [{
                'fromBlock': hex(from_block_number),
                'toBlock': hex(to_block_number) if isinstance(to_block_number, int) else to_block_number,
                'topics': [topic],
            }],
            'id': from_block_number % 100 + 1
        })
        results = requests.post(cls.rpc(), data=data).json()
        if 'error' in results:
            print(results['error'])
            return []
        return results['result']

    @classmethod
    def fetch_block(cls, block_number, detail=False):
        errors = []
        for attempt in range(5):
            receipt = requests.post(cls.rpc(), data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getBlockByNumber',
                'id': int(block_number, 16) % 257,
                'params': [
                    block_number,
                    False
                ]
            })).json()
            if 'error' in receipt:
                logger.warning(receipt['error'])
                raise BlockchainRPCError(receipt)
            result = receipt['result']
            if result is None:
                logger.warning(f'no result for eth_getBlockByNumber of {block_number}')
                errors.append(receipt)
                continue
            return result
        else:
            raise BlockchainRPCError(errors)

    @staticmethod
    def rpc():
        raise NotImplementedError

    @classmethod
    def get_latest_block_number(cls, in_hex=False):
        data = json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_blockNumber',
            'params': [],
            'id': 1
        })
        results = requests.post(cls.rpc(), data=data).json()
        if 'error' in results:
            print(results['error'])
            return None
        value = results['result']
        return value if in_hex else int(value, 16)
