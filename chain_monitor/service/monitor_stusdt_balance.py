from chain_monitor.configurations.configuration import STUSDT, USDT, AETHUSDT, HTX_43
from chain_monitor.slack import SlackMessage
from chain_monitor.web3.contract.contract_factory import USDTContract
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

TRON_WITHDRAW = STUSDT.get('TRON_WITHDRAW')
TRON_USDT_MINTER = STUSDT.get('TRON_USDT_MINTER')
TRON_USDT_CONTRACT = TokenContract(USDT.get('TRON_CONTRACT'))

ETH_WITHDRAW = STUSDT.get('ETH_WITHDRAW')
ETH_USDT_MINTER = STUSDT.get('ETH_USDT_MINTER')
ETH_USDT_CONTRACT = USDTContract(USDT.get('ETH_CONTRACT'))

aEthUSDT = AETHUSDT
htx_43 = HTX_43


def monitor_balance():
    tron_with_draw_balance = convert(TRON_USDT_CONTRACT.balance_of(TRON_WITHDRAW))
    tron_usdt_minter_balance = convert(TRON_USDT_CONTRACT.balance_of(TRON_USDT_MINTER))

    eth_withdraw_balance = convert(ETH_USDT_CONTRACT.balanceOf(ETH_WITHDRAW))
    eth_usdt_minter_balance = convert(ETH_USDT_CONTRACT.balanceOf(ETH_USDT_MINTER))

    htx_43_balance = convert(ETH_USDT_CONTRACT.balanceOf(AETHUSDT))

    message = SlackMessage()
    message.add_message(f'Tron withdraw(`{TRON_WITHDRAW}`) balance is `{tron_with_draw_balance}`')
    message.add_message(f'Tron usdt minter(`{TRON_USDT_MINTER}`) balance is `{tron_usdt_minter_balance}`')
    message.add_message(f'Eth withdraw(`{ETH_WITHDRAW}`) balance is `{eth_withdraw_balance}`')
    message.add_message(f'Tron withdraw(`{ETH_USDT_MINTER}`) balance is `{eth_usdt_minter_balance}`')
    message.add_message(f'Aava(`{htx_43}`) balance is `{htx_43_balance}`')

    print(message)


def convert(balance: int):
    return round(balance / 1000000, 2)
