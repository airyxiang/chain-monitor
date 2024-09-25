import json
import re
from typing import List

from web3 import Web3

from chain_monitor.configurations.configuration import AVA_WEB3_PROVIDER_URL, AVA_BLOCK_STEP_SIZE
from chain_monitor.configurations.logger import get_logger
from chain_monitor.exceptions import FieldError
from chain_monitor.web3.blockchains.blockchain import Blockchain, TransactionStatus
from chain_monitor.web3.blockchains.exceptions import BlockchainRPCError
from chain_monitor.web3.contract.exceptions import CheckSumAddressError
from chain_monitor.web3.contract.web3_wrapper import web3

logger = get_logger(__name__)


class Ava(Blockchain):
    ID = 'AVA'

    @staticmethod
    def name():
        return 'Avalanche'

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
        return AVA_WEB3_PROVIDER_URL

    @classmethod
    def fetch_transaction(cls, transaction_hash, retries=3):
        transaction_obj = cls._make_request(data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionByHash',
            'id': int(transaction_hash, 16) % 256,
            'params': [
                transaction_hash
            ]
        }))
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
            receipt = cls._make_request(data=json.dumps({
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionReceipt',
                'id': int(transaction_hash, 16) % 257,
                'params': [
                    transaction_hash
                ]
            }))
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
    def latest_event(cls, address, event_str):
        event = Web3.sha3(text=event_str).hex()
        end_block = cls.block_number()
        to_block = end_block
        from_block = max(end_block - AVA_BLOCK_STEP_SIZE, 0)
        while True:
            request_data = {
                'address': address,
                'fromBlock': from_block,
                'toBlock': to_block,
                'topics': [event]
            }
            logger.info(f'Scanning blocks {from_block} to {to_block} on Avalanche')
            events = web3.get_logs(request_data)
            if events:
                logger.info(f'Found {event_str} on Avalanche: {events[-1]}')
                return events[-1]
            to_block = from_block
            from_block = max(from_block - AVA_BLOCK_STEP_SIZE, 0)

    @classmethod
    def events_from(cls, address, event_str, from_block):
        event = Web3.sha3(text=event_str).hex()

        end_block = cls.block_number()
        start_block = max(end_block - AVA_BLOCK_STEP_SIZE, from_block)

        all_events = []
        while True:
            request_data = {
                'address': address,
                'fromBlock': start_block,
                'toBlock': end_block,
                'topics': [event]
            }
            logger.info(f'Scanning blocks {start_block} to {end_block} on Avalanche')
            events = web3.get_logs(request_data)
            events = [
                {
                    **event,
                    'transactionHash': event['transactionHash'].hex(),
                } for event in events
            ]
            all_events += events
            end_block = start_block
            if start_block == from_block:
                logger.info('Collected all events on Avalanche')
                return events
            start_block = max(start_block - AVA_BLOCK_STEP_SIZE, from_block)
