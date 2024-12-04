from chain_monitor.configurations.configuration import STUSDT, USDT, AETHUSDT, HTX_43, STUSDT_TECH_FINANCE
from chain_monitor.slack import SlackMessage, slack_service
from chain_monitor.web3.contract.contract_factory import USDTContract
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

TRON_WITHDRAW = STUSDT.get('TRON_WITHDRAW')
TRON_USDT_MINTER = STUSDT.get('TRON_USDT_MINTER')
TRON_USDT_CONTRACT = TokenContract(USDT.get('TRON_CONTRACT'))

ETH_WITHDRAW = STUSDT.get('ETH_WITHDRAW')
ETH_USDT_MINTER = STUSDT.get('ETH_USDT_MINTER')
ETH_USDT_CONTRACT = USDTContract(USDT.get('ETH_CONTRACT'))

AETHH_USDT_CONTRACT = USDTContract(AETHUSDT)
htx_43 = HTX_43

channel = STUSDT_TECH_FINANCE


def monitor_eth_balance():
    eth_withdraw_balance = convert(ETH_USDT_CONTRACT.balanceOf(ETH_WITHDRAW))
    eth_usdt_minter_balance = convert(ETH_USDT_CONTRACT.balanceOf(ETH_USDT_MINTER))

    message = SlackMessage()
    message.add_message(f'`{ETH_WITHDRAW}`(Eth withdraw) balance is `{eth_withdraw_balance}`')
    message.add_message(f'`{ETH_USDT_MINTER}`(Tron withdraw) balance is `{eth_usdt_minter_balance}`')
    slack_service.send_message(message=message, channel=channel)


def monitor_tron_balance():
    tron_with_draw_balance = convert(TRON_USDT_CONTRACT.balance_of(TRON_WITHDRAW))
    tron_usdt_minter_balance = convert(TRON_USDT_CONTRACT.balance_of(TRON_USDT_MINTER))

    message = SlackMessage()
    message.add_message(f'`{TRON_WITHDRAW}`(Tron withdraw) balance is `{tron_with_draw_balance}`')
    message.add_message(f'`{TRON_USDT_MINTER}`(Tron usdt minter) balance is `{tron_usdt_minter_balance}`')
    slack_service.send_message(message=message, channel=channel)


def monitor_aave_balance():
    htx_43_balance = convert(AETHH_USDT_CONTRACT.balanceOf(htx_43))

    message = SlackMessage()
    message.add_message(f'`{htx_43}`(Aave) balance is `{htx_43_balance}`')
    slack_service.send_message(message=message, channel=channel)


def convert(balance: int):
    return round(balance / 1000000, 2)
