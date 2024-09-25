from chain_monitor.configurations.configuration import WEB3_PROVIDER_URL, AVA_WEB3_PROVIDER_URL, BSC_WEB3_PROVIDER_URL
from chain_monitor.configurations.logger import get_logger
from web3 import Web3, HTTPProvider
from chain_monitor.web3.contract.exceptions import CheckSumAddressError

logger = get_logger(__name__)


class Web3Wrapper:
    def __init__(self, provider_url=WEB3_PROVIDER_URL):
        self.provider_url = provider_url
        self.web3 = Web3(HTTPProvider(self.provider_url))

    def to_checksum_address(self, address):
        try:
            check_sum_address = self.web3.toChecksumAddress(address)
        except ValueError:
            raise CheckSumAddressError(f'Cannot convert {address} to checksum address')

        return check_sum_address

    def transaction_to_hash(self, raw_transaction):
        return Web3.sha3(raw_transaction).hex()

    def get_eth_price(self):
        return self.web3.eth.gasPrice

    def create_contract_instance(self, address, abi):
        address = self.to_checksum_address(address)
        return self.web3.eth.contract(address=address, abi=abi)

    def get_current_nonce(self, address):
        address = self.to_checksum_address(address)
        return self.web3.eth.getTransactionCount(address)

    def format_redemption_address(self, address_offset):
        """
        Converts integer to ethereum address
        """
        # https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros
        return self.to_checksum_address("{0:#0{1}x}".format(address_offset, 42))

    def get_transaction_receipt(self, transaction_hash):
        return self.web3.eth.getTransactionReceipt(transaction_hash)

    def get_block_number(self):
        return self.web3.eth.blockNumber

    def get_logs(self, request):
        return self.web3.eth.getLogs(request)


web3 = Web3Wrapper()
ava_web3 = Web3Wrapper(AVA_WEB3_PROVIDER_URL)
bsc_web3 = Web3Wrapper(BSC_WEB3_PROVIDER_URL)
