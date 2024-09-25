import json
import re
from typing import List

import requests
from web3 import Web3

from chain_monitor.configurations.configuration import WEB3_PROVIDER_URL, ETH_BLOCK_STEP_SIZE
from chain_monitor.configurations.logger import get_logger
from chain_monitor.exceptions import FieldError
from chain_monitor.web3.blockchains.blockchain import TransactionStatus
from chain_monitor.web3.blockchains.exceptions import BlockchainRPCError
from chain_monitor.web3.constants import Blockchain
from chain_monitor.web3.contract.exceptions import CheckSumAddressError
from chain_monitor.web3.contract.web3_wrapper import web3

ETH_CENT = 10 ** 16
logger = get_logger(__name__)
NONWHITELISTED_INSTANT_MINT_POOL = 10000000000000000000000000


class Eth(Blockchain):
    ID = 'ETH'

    @staticmethod
    def name():
        return 'Ethereum'

    @staticmethod
    def validate_address(blockchain_address) -> List[FieldError]:
        field_errors = []
        if not re.match('^0x[a-fA-F0-9]{40}$', blockchain_address):
            field_errors.append(FieldError(
                'eth_address', 'eth address must be 42 hexadecimal characters hex and starts with 0x', 'invalid_address'
            ))
        try:
            web3.to_checksum_address(blockchain_address)
        except CheckSumAddressError:
            field_errors.append(FieldError('eth_address', 'must be valid checksum address', 'invalid_address'))
        return field_errors

    @staticmethod
    def rpc():
        return WEB3_PROVIDER_URL

    @classmethod
    def fetch_transaction(cls, transaction_hash, retries=3):
        transaction_obj = requests.post(cls.rpc(), data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionByHash',
            'id': int(transaction_hash, 16) % 256,
            'params': [
                transaction_hash
            ]
        })).json()
        if 'error' in transaction_obj:
            if retries > 0:
                return cls.fetch_transaction(transaction_hash, retries=retries - 1)
            logger.warning(transaction_obj['error'])
            raise BlockchainRPCError(transaction_obj)
        transaction = transaction_obj['result']
        if retries > 0 and transaction is None:
            return cls.fetch_transaction(transaction_hash, retries=retries - 1)
        if isinstance(transaction, dict) and 'input' in transaction:
            transaction['data'] = transaction['input']
        return transaction

    @classmethod
    def fetch_transaction_status(cls, transaction_hash):
        assert transaction_hash.startswith('0x')
        # first, get the transaction, to see if it is still pending
        transaction = cls.fetch_transaction(transaction_hash)
        if transaction is None:
            return TransactionStatus.NOT_FOUND
        if transaction['blockNumber'] is None:
            return TransactionStatus.PENDING
        # if the transaction is confirmed, need receipt to check the status
        errors = []
        for attempt in range(5):
            receipt = requests.post(cls.rpc(), data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionReceipt',
                'id': int(transaction_hash, 16) % 257,
                'params': [
                    transaction_hash
                ]
            })).json()
            if 'error' in receipt:
                logger.warning(receipt['error'])
                raise BlockchainRPCError(receipt)
            result = receipt['result']
            if result is None:
                # this seems to be a transient rpc error
                logger.warning(f'no result for eth_getTransactionReceipt of {transaction_hash}')
                errors.append(receipt)
                continue
            if result['status'] == '0x1':
                return TransactionStatus.CONFIRMED_SUCCESS
            else:
                return TransactionStatus.CONFIRMED_FAILURE
        else:
            raise BlockchainRPCError(errors)

    @classmethod
    def block_number(cls):
        obj = requests.post(cls.rpc(), data=json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        })).json()
        return int(obj['result'], 16)

    @classmethod
    def latest_event(cls, address, event_str):
        event = Web3.sha3(text=event_str).hex()
        end_block = cls.block_number()
        to_block = hex(end_block)
        from_block = hex(end_block - ETH_BLOCK_STEP_SIZE)
        while True:
            events_obj = requests.post(cls.rpc(), data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getLogs',
                'id': int(address, 16) % 512 + int(to_block, 16) % 513,
                'params': [{
                    'address': address,
                    'fromBlock': from_block,
                    'toBlock': to_block,
                    'topics': [event]
                }]
            })).json()
            events = events_obj['result']
            if events:
                return events[-1]
            to_block = from_block
            from_block = hex(int(from_block, 16) - ETH_BLOCK_STEP_SIZE)

    @classmethod
    def events_from(cls, address, event_str, from_block):
        event = Web3.sha3(text=event_str).hex()
        if isinstance(from_block, int):
            from_block = hex(from_block)
        to_block = 'latest'
        data = json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getLogs',
            'id': int(address, 16) % 512 + int(from_block, 16) % 513,
            'params': [{
                'address': address,
                'fromBlock': from_block,
                'toBlock': to_block,
                'topics': [event]
            }]
        })
        events_obj = requests.post(cls.rpc(), data=data).json()
        events = events_obj['result']
        return events

    # @staticmethod
    # def etherscan_rpc():
    #     return config.ether
    #
    # @classmethod
    # def find_transactions(cls, address, indices):
    #     api_key = ETHERSCAN_API_KEY
    #     txs = requests.get(
    #         cls.etherscan_rpc() + f'?module=account&action=txlist&address={address}&apikey={api_key}'
    #     ).json()['result']
    #     results = []
    #     address_lower = address.lower()
    #     for index in indices:
    #         str_index = str(index)
    #         for tx in txs:
    #             if tx['from'] == address_lower and tx['nonce'] == str_index:
    #                 results.append(tx['hash'])
    #                 break
    #         else:
    #             results.append(None)
    #     return results
