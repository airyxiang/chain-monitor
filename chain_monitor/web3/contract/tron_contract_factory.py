import json

from .contract_factory import retry_on_connection_errors
from .tron_client import TronProxyClient
from .tron_new_http_provider import HTTPProvider
from ...configurations.configuration import TRONGRID_API_URL, TRONGRID_API_KEY


class BaseTronContract:
    ABI_PATH = None
    abi = None

    def __init__(self, address, client=None):
        client = client or TronProxyClient(HTTPProvider(endpoint_uri=TRONGRID_API_URL, api_key=TRONGRID_API_KEY))
        self.__load_abi()
        self.instance = client.get_contract_with_custom_abi(address, self.abi)

    @classmethod
    def __load_abi(cls):
        if cls.abi is None:
            with open(cls.ABI_PATH, 'r') as abi:
                cls.abi = json.load(abi)


class ControllerContract(BaseTronContract):
    ABI_PATH = './chain_monitor/web3/contract/abi/tron_abi/controller_abi.json'

    def get_instant_mint_call_data(self, to_address, amount):
        return self.instance.functions.instantMint(to_address, amount)

    def get_request_mint_call_data(self, to_address, amount):
        return self.instance.functions.requestMint(to_address, amount)

    def get_set_can_burn_call_data(self, to_address, value):
        return self.instance.functions.setCanBurn(to_address, value)

    def get_add_blacklist_call_data(self, to_address):
        return self.instance.functions.addBlacklist(to_address)

    @retry_on_connection_errors
    def instant_mint_threshold(self):
        return self.instance.functions.instantMintThreshold()

    @retry_on_connection_errors
    def instant_mint_pool(self):
        return self.instance.functions.instantMintPool()

    @retry_on_connection_errors
    def fetch_mint_key(self):
        return self.instance.functions.mintKey()

    @retry_on_connection_errors
    def ratifier_mint_pool(self):
        return self.instance.functions.ratifiedMintPool()


class TokenContract(BaseTronContract):
    ABI_PATH = './chain_monitor/web3/contract/abi/contract_abi/token_abi.json'

    @retry_on_connection_errors
    def can_burn(self, redemption_address: str):
        return self.instance.functions.canBurn(redemption_address)

    @retry_on_connection_errors
    def balance_of(self, address: str):
        return self.instance.functions.balanceOf(address)

    @retry_on_connection_errors
    def total_supply(self):
        return self.instance.functions.totalSupply()


ControllerContract.abi = None
TokenContract.abi = None
