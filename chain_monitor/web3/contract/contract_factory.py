import json

from requests.exceptions import ConnectionError

from chain_monitor.configurations.configuration import WEB3_CONTRACT_CALL_RETRIES, TUSD
from chain_monitor.configurations.logger import get_logger
from chain_monitor.web3.contract.web3_wrapper import web3

logger = get_logger(__name__)


class Web3ContractConnectionError(Exception):
    pass


def retry_on_connection_errors(contract_function):
    def wrapper(self, *args, **kwargs):
        for attempt in range(WEB3_CONTRACT_CALL_RETRIES):
            try:
                return contract_function(self, *args, **kwargs)
            except ConnectionError as error:
                logger.warning(f'Trying to execute {contract_function.__name__}, got {error} on '
                               f'attempt number {attempt}')

        try:
            return contract_function(self, *args, **kwargs)
        except ConnectionError as error:
            raise Web3ContractConnectionError(
                f'Could not execute {contract_function.__name__} after {WEB3_CONTRACT_CALL_RETRIES} retries'
            ) from error

    return wrapper


class CommonControllerContractFunctionsMixin:
    @retry_on_connection_errors
    def instant_mint_threshold(self):
        return self.instance.functions.instantMintThreshold().call()

    @retry_on_connection_errors
    def instant_mint_pool(self):
        return self.instance.functions.instantMintPool().call()

    @retry_on_connection_errors
    def fetch_mint_key(self):
        return self.instance.functions.mintKey().call()

    def get_instant_mint_call_data(self, to_address, amount):
        return self.instance.encodeABI(fn_name='instantMint', args=[to_address, amount])

    def get_request_mint_call_data(self, to_address, amount):
        return self.instance.encodeABI(fn_name='requestMint', args=[to_address, amount])

    @retry_on_connection_errors
    def ratifier_mint_pool(self):
        return self.instance.functions.ratifiedMintPool().call()


class RegistryContract:
    def __init__(self):
        with open('./chain_monitor/web3/contract/abi/contract_abi/registry_abi.json', 'r') as abi:
            self.abi = json.load(abi)
            self.address = web3.to_checksum_address(TUSD.get('REGISTRY_ADDRESS'))
            self.instance = web3.create_contract_instance(self.address, self.abi)

    def get_setAttributeValue_call_data(self, address, attribute, value):
        address = web3.to_checksum_address(address)
        return self.instance.encodeABI(fn_name='setAttributeValue', args=[address, attribute, value])

    def estimate_setAttributeValue_gas(self, address, attribute, value, from_address):
        address = web3.to_checksum_address(address)
        return self.instance.functions.setAttributeValue(address, attribute, value).estimateGas({'from': from_address})

    def hasAttribute(self, address, attribute):
        address = web3.to_checksum_address(address)
        return self.instance.functions.hasAttribute(address, attribute).call()


registry_contract = RegistryContract()


class ControllerContract(CommonControllerContractFunctionsMixin):
    def __init__(self, address):
        if ControllerContract.abi is None:
            with open('./chain_monitor/web3/contract/abi/contract_abi/controller_abi.json', 'r') as abi:
                ControllerContract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, ControllerContract.abi)


class ControllerV2Contract(CommonControllerContractFunctionsMixin):
    def __init__(self, address):
        if ControllerV2Contract.abi is None:
            with open('./chain_monitor/web3/contract/abi/contract_abi/controller_v2_abi.json', 'r') as abi:
                ControllerV2Contract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, ControllerV2Contract.abi)

    def get_set_can_burn_call_data(self, to_address, value):
        return self.instance.encodeABI(fn_name='setCanBurn', args=[to_address, value])


class EACAggregatorProxyContract:
    abi = None

    def __init__(self, address, web3=web3):
        self.reset(address, web3)

    def reset(self, address, web3):
        if EACAggregatorProxyContract.abi is None:
            with open('./chain_monitor/web3/contract/abi/contract_abi/EACAggregatorProxy.json', 'r') as abi:
                EACAggregatorProxyContract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, EACAggregatorProxyContract.abi)

    def latest_answer(self):
        return self.instance.functions.latestAnswer().call()

    def latest_timestamp(self):
        return self.instance.functions.latestTimestamp().call()

    def latest_round(self):
        return self.instance.functions.latestRound().call()

    def latest_round_data(self):
        return self.instance.functions.latestRoundData().call()

    def get_answer(self, roundId):
        return self.instance.functions.getAnswer().call(roundId)

    def get_timestamp(self, roundId):
        return self.instance.functions.getTimestamp().call(roundId)

    def get_round_data(self, roundId):
        """
        [
          { "internalType": "uint80",  "name": "roundId", "type": "uint80" },
          { "internalType": "int256",  "name": "answer", "type": "int256" },
          { "internalType": "uint256", "name": "startedAt", "type": "uint256" },
          { "internalType": "uint256", "name": "updatedAt", "type": "uint256" },
          { "internalType": "uint80",  "name": "answeredInRound", "type": "uint80" }
        ]
        """
        return self.instance.functions.getRoundData().call(roundId)

    def decimals(self):
        return self.instance.functions.decimals().call()


class TrueUSDContract:
    abi = None

    def __init__(self, address, web3=web3):
        self.reset(address, web3)

    def reset(self, address, web3):
        if TrueUSDContract.abi is None:
            with open('./chain_monitor/web3/contract/abi/contract_abi/TrueUSD.json', 'r') as abi:
                TrueUSDContract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, TrueUSDContract.abi)

    def decimals(self):
        return self.instance.functions.decimals().call()

    def totalSupply(self):
        return self.instance.functions.totalSupply().call()

    def proofOfReserveEnabled(self):
        return self.instance.functions.proofOfReserveEnabled().call()

    def chainReserveHeartbeat(self):
        return self.instance.functions.chainReserveHeartbeat().call()

    def chainReserveFeed(self):
        return self.instance.functions.chainReserveFeed().call()


class USDTContract:
    abi = None

    def __init__(self, address, web3=web3):
        self.reset(address, web3)

    def reset(self, address, web3):
        if USDTContract.abi is None:
            with open('./chain_monitor/web3/contract/abi/contract_abi/USDT.json', 'r') as abi:
                USDTContract.abi = json.load(abi)
        self.address = web3.to_checksum_address(address)
        self.instance = web3.create_contract_instance(self.address, USDTContract.abi)

    def isBlackListed(self, address):
        address = web3.to_checksum_address(address)
        return self.instance.functions.isBlackListed(address).call()

    def balanceOf(self, address):
        address = web3.to_checksum_address(address)
        return self.instance.functions.balanceOf(address).call()


ControllerContract.abi = None
ControllerV2Contract.abi = None
