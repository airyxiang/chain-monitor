from huobi.client.account import AccountClient
from chain_monitor.configurations.configuration import HTX_API_KEY, HTX_API_SECRET_KEY
from chain_monitor.configurations.logger import get_logger

logger = get_logger(__name__)

account_client = AccountClient(api_key=HTX_API_KEY, secret_key=HTX_API_SECRET_KEY, url='https://api.huobi.pro')


def get_account_balance_by_currency(currency):
    account_balance_list = account_client.get_account_balance()
    account_balances = account_balance_list[0]
    balance = [balance for balance in account_balances.list if balance.currency == currency]
    if not balance:
        return 0
    return balance[0].balance
