from chain_monitor.configurations.configuration import ETH, MONITOR_SLACK_URL
from chain_monitor.remote.htx import htx
from chain_monitor.remote.polo import polo
from chain_monitor.slack import slack_service
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

contract_address = ETH.get('TRON_CONTRACT')
contract = TokenContract(contract_address)
channel = MONITOR_SLACK_URL


def monitor_supplemented_eth():
    eth_total_balance = contract.total_supply()

    polo_account_eth = polo.get_account_balance_by_currency('ETH')
    htx_account_eth = htx.get_account_balance_by_currency('ETH')

    tron_reserve_eth = contract.balance_of('')
    polo_wallet_eth = contract.balance_of('')
    htx_wallet_eth = contract.balance_of('')

    supplemented_eth = eth_total_balance - polo_account_eth - htx_account_eth - tron_reserve_eth
    if supplemented_eth > 0:
        slack_service.send_direct_message(channel, f'Supplemented supply is {supplemented_eth}')
    if polo_wallet_eth > polo_account_eth:
        slack_service.send_direct_message(
            channel,
            f'Poloniex wallet balance is {polo_wallet_eth}, account balance is {polo_account_eth}'
        )
    if htx_wallet_eth > htx_account_eth:
        slack_service.send_direct_message(
            channel,
            f'HTX wallet balance is {htx_wallet_eth}, account balance is {htx_account_eth}'
        )
