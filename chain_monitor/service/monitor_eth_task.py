from chain_monitor.configurations.configuration import ETH, MONITOR_SLACK_URL
from chain_monitor.remote.htx import htx
from chain_monitor.remote.polo import polo
from chain_monitor.slack import slack_service, SlackMessage
from chain_monitor.utils.money import convert_to_float
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

contract_address = ETH.get('TRON_CONTRACT')
contract = TokenContract(contract_address)
channel = MONITOR_SLACK_URL

title = ['total_supply', 'polo_account', 'polo_wallet', 'htx_account', 'htx_wallet', 'reserve', 'supplemented']


def monitor_supplemented_eth():
    eth_total_balance = convert_to_float(contract.total_supply())

    polo_account_eth = polo.get_account_balance_by_currency('ETH')
    htx_account_eth = htx.get_account_balance_by_currency('ETH')

    tron_reserve_eth = convert_to_float(contract.balance_of('TUgSgCQL6pMSy9zByn4sgxqrJa95sZExBG'))
    polo_wallet_eth = convert_to_float(contract.balance_of('TWhDfwC8QE6pQyiYy248dNor3uphPEw5M2'))
    htx_wallet_eth = convert_to_float(contract.balance_of('TUgSgCQL6pMSy9zByn4sgxqrJa95sZExBG'))

    supplemented_eth = eth_total_balance - polo_account_eth - htx_account_eth - tron_reserve_eth

    slack_message = SlackMessage()
    slack_message.add_table(title, [
        [eth_total_balance, polo_account_eth, polo_wallet_eth, htx_account_eth, htx_wallet_eth, tron_reserve_eth,
         supplemented_eth]
    ])
    if supplemented_eth > 0:
        slack_message.add_message(f'Supplemented supply is {supplemented_eth}')
        slack_message.add_warning('lily', 'tahoe')
    if polo_wallet_eth > polo_account_eth:
        slack_message.add_message(
            f'Poloniex wallet balance is {polo_wallet_eth}, account balance is {polo_account_eth}'
        )
        slack_message.add_warning('lily', 'tahoe')
    if htx_wallet_eth > htx_account_eth:
        slack_message.add_message(f'HTX wallet balance is {htx_wallet_eth}, account balance is {htx_account_eth}')
        slack_message.add_warning('lily', 'tahoe')

    slack_service.send_message(channel=channel, message=slack_message)


def get_wallet_balance():
    pass