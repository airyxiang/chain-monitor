import requests
from huobi.client.account import AccountClient
from chain_monitor.configurations.configuration import HTX_API_KEY, HTX_API_SECRET_KEY
from chain_monitor.configurations.logger import get_logger
from chain_monitor.remote.htx.htx_sdk import HtxSDK

logger = get_logger(__name__)

API_URL = 'https://api.huobi.pro'
WALLET_API_URL = 'https://wallet-tron.huobi.com'

import asyncio


def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
        else:
            raise ex


loop = get_or_create_event_loop()


def get_account_balance_by_currency(currency):
    account_client = AccountClient(api_key=HTX_API_KEY, secret_key=HTX_API_SECRET_KEY, url=API_URL)
    account_balance_list = account_client.get_account_balance()
    account_balances = account_balance_list[0]
    balance = [balance for balance in account_balances.list if balance.currency == currency]
    if not balance:
        return 0
    return balance[0].balance


def get_wallet_balance():
    htx_sdk = HtxSDK()
    url = htx_sdk.wallet_request(host=WALLET_API_URL, path='/openapi/balance', method='GET')
    response = requests.get(url, params={})
    return float(response.json().get('data'))
