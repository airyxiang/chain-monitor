from typing import List
from urllib.parse import urlencode

import requests
from tronpy.keys import is_address, to_base58check_address

from chain_monitor.configurations.configuration import TRONGRID_API_URL, TRONGRID_API_KEY
from chain_monitor.configurations.logger import get_logger
from chain_monitor.exceptions import FieldError
from chain_monitor.web3.blockchains.blockchain import TransactionStatus
from chain_monitor.web3.constants import Blockchain

logger = get_logger(__name__)


class UnexpectedTransactionStatus(Exception):
    pass


class TrongridClient:
    URL = TRONGRID_API_URL
    MIN_PER_PAGE = 20
    MAX_PER_PAGE = 200

    def get_transaction_info(self, transaction_id):
        """
        https://developers.tron.network/reference#transaction-info-by-id
        """
        return self._send_request(f'{self.URL}/wallet/gettransactioninfobyid?value={transaction_id}')

    def get_transaction_by_id(self, transaction_id):
        return self._send_request(f'{self.URL}/walletsolidity/gettransactionbyid?value={transaction_id}')

    def get_transaction_events(self, transaction_id):
        """
        https://developers.tron.network/reference#events-by-transaction-id
        """
        return self._send_request(f'{self.URL}/v1/transactions/{transaction_id}/events?only_confirmed=True')

    def get_events(self, contract_address, event_name, min_block_timestamp=0, limit=MIN_PER_PAGE, only_confirmed=False,
                   only_first_page=False, max_block_timestamp=0):
        """
        Default limit per page is 20, max 200.
        https://developers.tron.network/reference#events-by-contract-address
        """
        payload = urlencode({
            'event_name': event_name,
            'limit': limit,
            'order_by': 'block_timestamp,desc',
            'min_block_timestamp': min_block_timestamp,
            'max_block_timestamp': max_block_timestamp,
            'only_confirmed': only_confirmed
        })
        endpoint = f'{self.URL}/v1/contracts/{contract_address}/events?{payload}'
        logger.info(f'Fetching {limit} {event_name} events for {contract_address}...')
        return self._get_single_page(endpoint) if only_first_page else self._get_next_page(endpoint)

    def _get_single_page(self, link):
        response = self._send_request(link)
        return response['data']

    def _get_next_page(self, link):
        response = self._send_request(link)
        data = response['data']
        links = response['meta'].get('links')
        if links:
            next_page_link = links['next']
            return data + self._get_next_page(next_page_link)
        return data

    @staticmethod
    def _send_request(link):
        raw_response = requests.get(link, headers={
            'TRON-PRO-API-KEY': TRONGRID_API_KEY
        })
        return raw_response.json()


class Tron(Blockchain):
    ID = 'TRON'

    @staticmethod
    def name():
        return 'TRON'

    @staticmethod
    def validate_address(blockchain_address) -> List[FieldError]:
        validation_error = FieldError('tron_address', f'{blockchain_address} is not a valid checksum address',
                                      'invalid_address')
        try:
            return [] if is_address(blockchain_address) else [validation_error]
        except ValueError:
            return [validation_error]

    @staticmethod
    def get_from_address(tx_data):
        """
        Given the signing-service transaction data, determine the from address
        """
        hex_address = tx_data['raw_data']['contract'][0]['parameter']['value']['owner_address']
        return to_base58check_address(hex_address)

    @classmethod
    def latest_event(cls, address, event_str):
        return TrongridClient().get_events(address, event_str, limit=1, only_first_page=True)[0]

    @classmethod
    def events_from(cls, address, event_str, from_timestamp):
        return TrongridClient().get_events(address, event_str, min_block_timestamp=from_timestamp,
                                           limit=TrongridClient.MAX_PER_PAGE)

    @staticmethod
    def fetch_transaction(transaction_hash, retries=3):
        return TrongridClient().get_transaction_info(transaction_hash)

    @classmethod
    def fetch_transaction_status(cls, transaction_hash):
        transaction_info = cls.fetch_transaction(transaction_hash)
        if transaction_info == {}:
            return TransactionStatus.NOT_FOUND

        try:
            result = transaction_info['receipt']['result']
        except KeyError:
            raise UnexpectedTransactionStatus(transaction_info)

        if result == 'SUCCESS':
            return TransactionStatus.CONFIRMED_SUCCESS
        elif result in ('REVERT', 'OUT_OF_ENERGY'):
            return TransactionStatus.CONFIRMED_FAILURE
        else:
            raise UnexpectedTransactionStatus(transaction_info)
