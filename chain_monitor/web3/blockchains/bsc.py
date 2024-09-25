import json
import re
from typing import List

import requests
from web3 import Web3

from chain_monitor.configurations.configuration import BSC_WEB3_PROVIDER_URL, BSC_BLOCK_STEP_SIZE
from chain_monitor.exceptions import FieldError
from chain_monitor.web3.blockchains.blockchain import Blockchain, TransactionStatus
from chain_monitor.web3.blockchains.exceptions import BlockchainRPCError
from chain_monitor.configurations.logger import get_logger
from chain_monitor.web3.contract.exceptions import CheckSumAddressError
from chain_monitor.web3.contract.web3_wrapper import bsc_web3 as web3

logger = get_logger(__name__)
DEFAULT_RPC_HEADERS = {'Content-Type': 'application/json'}


class Bsc(Blockchain):
    ID = 'BSC'

    @staticmethod
    def name():
        return 'BNB Smart Chain'

    @staticmethod
    def starting_block_number():
        return 26049102

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
        return BSC_WEB3_PROVIDER_URL

    @classmethod
    def fetch_transaction(cls, transaction_hash, retries=3):
        transaction_obj = requests.post(cls.rpc(), data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionByHash',
            'id': int(transaction_hash, 16) % 256,
            'params': [
                transaction_hash
            ]
        }), headers=DEFAULT_RPC_HEADERS).json()
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
            }), headers=DEFAULT_RPC_HEADERS).json()
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

    @staticmethod
    def process_request_mint_hash(request_mint_hash):
        receipt = web3.get_transaction_receipt(request_mint_hash)
        logs = receipt.get('logs')[0]
        controller_contract_address = logs.get('address')
        return controller_contract_address, str(int(logs.get('data')[:66], 16))

    @staticmethod
    def format_transaction_explorer_link(transaction_hash):
        return 'https://bscscan.com/tx/' + transaction_hash

    @classmethod
    def block_number(cls):
        obj = requests.post(cls.rpc(), data=json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }), headers=DEFAULT_RPC_HEADERS).json()
        return int(obj['result'], 16)

    #
    # @classmethod
    # def latest_event(cls, address, event_str):
    #     event_hex = Web3.sha3(text=event_str).hex()
    #     end_block = cls.block_number()
    #     to_block = end_block
    #     latest_searched = get_bsc_latest_event_searched_block(event_str)
    #     from_block = int(latest_searched) if latest_searched else cls.starting_block_number()
    #
    #     event = None
    #     for block_number in range(to_block, from_block, -BSC_BLOCK_STEP_SIZE):
    #         events = cls.__get_events(address,
    #                                   from_block=block_number - BSC_BLOCK_STEP_SIZE,
    #                                   to_block=block_number,
    #                                   event_hex=event_hex)
    #         if events:
    #             event = events[-1]
    #             block_number = int(event["blockNumber"], 16)
    #             set_bsc_latest_event_block(event_str, block_number)
    #             break
    #     else:
    #         latest_event_block = get_bsc_latest_event_block(event_str)
    #         # event not found in
    #         if latest_event_block is not None:
    #             latest_event_block = int(latest_event_block)
    #             events = cls.__get_events(address,
    #                                       from_block=latest_event_block,
    #                                       to_block=latest_event_block,
    #                                       event_hex=event_hex)
    #             event = events[-1]
    #
    #     # set searched block here in case querying blocks failed due to rpc error
    #     set_bsc_latest_event_searched_block(event_str, to_block)
    #     return event

    @classmethod
    def events_from(cls, address, event_str, from_block: str | int):
        event_hex = Web3.sha3(text=event_str).hex()
        if isinstance(from_block, str):
            from_block = int(from_block, 16)
        to_block = cls.block_number()
        events = []
        for block_number in range(from_block, to_block + 1, BSC_BLOCK_STEP_SIZE):
            scanned_events = cls.__get_events(address,
                                              from_block=block_number,
                                              to_block=block_number + BSC_BLOCK_STEP_SIZE,
                                              event_hex=event_hex)
            events.extend(scanned_events)
        return events

    @classmethod
    def __get_events(cls, address: str, *, event_hex, from_block: int, to_block: int = None) -> list:
        events_response = requests.post(cls.rpc(), data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getLogs',
            'id': int(address, 16) % 512 + (to_block % 513 if to_block else 0),
            'params': [{
                'address': address,
                'fromBlock': hex(from_block),
                'toBlock': hex(to_block) if to_block else 'latest',
                'topics': [event_hex]
            }]
        }), headers=DEFAULT_RPC_HEADERS).json()
        return events_response.get('result', [])

    @staticmethod
    def bscscan_rpc():
        return 'https://api.bscscan.com'
