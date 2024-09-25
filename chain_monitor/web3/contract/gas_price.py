import requests
import json

from chain_monitor.configurations.configuration import ETHERSCAN_GAS_API_KEY, BSCSCAN_GAS_API_KEY, \
    ETHERSCAN_GAS_TRACKER_URL, BSCSCAN_GAS_TRACKER_URL, ETHERSCAN_API_TIMEOUT, BSCSCAN_API_TIMEOUT, \
    BSC_DEFAULT_GAS_PRICE, DEFAULT_GAS_PRICE, WEB3_PROVIDER_URL
from chain_monitor.configurations.logger import get_logger

logger = get_logger(__name__)

LOW_URGENCY = 1
MEDIUM_URGENCY = 5
HIGH_URGENCY = 9

ETHERSCAN_API_KEYS = {
    "ETH": ETHERSCAN_GAS_API_KEY,
    "BSC": BSCSCAN_GAS_API_KEY,
}

ETHERSCAN_GAS_TRACKER_URLS = {
    "ETH": ETHERSCAN_GAS_TRACKER_URL,
    "BSC": BSCSCAN_GAS_TRACKER_URL,
}

ETHERSCAN_API_TIMEOUTS = {
    "ETH": ETHERSCAN_API_TIMEOUT,
    "BSC": BSCSCAN_API_TIMEOUT,
}


class EtherscanGasEstimateError(Exception):
    pass


class GasStationGasEstimateError(Exception):
    pass


def get_gas_price(urgency=MEDIUM_URGENCY, blockchain='ETH'):
    try:
        return get_etherscan_gas_estimate(urgency, blockchain=blockchain)
    except EtherscanGasEstimateError as error:
        logger.error(f'Error fetching gas estimate from Etherscan: {error}')
        if blockchain != "ETH":
            return BSC_DEFAULT_GAS_PRICE
        try:
            return get_gas_fee_estimate_fallback()
        except Exception as error:
            logger.warning(f'Error fetching gas estimate from fallback provider: {error}')
            return DEFAULT_GAS_PRICE


def get_etherscan_gas_estimate(urgency=MEDIUM_URGENCY, blockchain="ETH"):
    params = {
        'module': 'gastracker',
        'action': 'gasoracle',
        'apikey': ETHERSCAN_API_KEYS[blockchain]
    }
    ETHERSCAN_GAS_TRACKER_URL = ETHERSCAN_GAS_TRACKER_URLS[blockchain]
    ETHERSCAN_API_TIMEOUT = ETHERSCAN_API_TIMEOUTS[blockchain]
    try:
        result = requests.get(ETHERSCAN_GAS_TRACKER_URL, params=params, timeout=ETHERSCAN_API_TIMEOUT).json()
    except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
        raise EtherscanGasEstimateError(f'Error getting gas_price from {blockchain} - timeout')

    logger.info(f'Got gas price estimate from etherscan: {result}')
    try:
        gas_estimate = result['result']
    except (KeyError, TypeError):
        raise EtherscanGasEstimateError(f'Error getting gas_price from {blockchain} - missing result parameter')

    if gas_estimate == 'Max rate limit reached':
        raise EtherscanGasEstimateError(gas_estimate)

    try:
        fast_gas_price = gas_estimate['FastGasPrice']
    except (KeyError, TypeError):
        raise EtherscanGasEstimateError(f'Could not retrieve fast gas price from: {gas_estimate}')
    else:
        gas_price = int(fast_gas_price) * 1000000000 + 1
        return gas_price


def get_gas_fee_estimate_fallback():
    data = json.dumps({'jsonrpc': '2.0', 'method': 'eth_gasPrice', 'params': [], 'id': 1})
    gas_result = requests.post(WEB3_PROVIDER_URL, data=data).json()['result']
    return int(gas_result, 16)
