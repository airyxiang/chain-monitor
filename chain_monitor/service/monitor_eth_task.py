from datetime import datetime

import pytz

from chain_monitor.configurations import configuration
from chain_monitor.configurations.configuration import ETH, ETH_MONITOR, POLO_COLD_WALLET, POLO_WARM_WALLET, \
    POLO_HOT_WALLET, TIME_ZONE
from chain_monitor.configurations.logger import get_logger
from chain_monitor.configurations.redis import get_redis_connection
from chain_monitor.remote.htx import htx
from chain_monitor.remote.polo import polo
from chain_monitor.slack import slack_service, SlackMessage
from chain_monitor.utils.formatter import generate_transaction_link
from chain_monitor.utils.money import convert_to_float
from chain_monitor.web3.blockchains.tron import TrongridClient
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

logger = get_logger(__name__)

contract_address = ETH.get('TRON_CONTRACT')
contract = TokenContract(contract_address)
channel = ETH_MONITOR

client = TrongridClient()


# 每日报告 total supply, polo_justinca_eth, htx_justinca_eth, tron链reserve余额，polo钱包ethold， htx钱包ethold
# 待补充eth = total supply- polo_justinca_eth- htx_justinca_eth-tron链reserve
# 如果待补充eth大于0，@lily tarinas，报警出来
# 如果 polo_wallet_ethtron > polo_justinca_eth
# htx_wallet_ethtron > htx_justinca_eth  也报警出来 (edited)

def monitor_supplemented_eth():
    eth_total_balance = convert_to_float(contract.total_supply())

    # todo api key
    # polo_HE_balance = polo.get_account_balance_by_currency('ETH')
    # htx_HE_balance = htx.get_account_balance_by_currency('ETH')
    # reserve = polo_HE_balance + htx_HE_balance
    reserve = 0

    polo_cold_wallet_balance = convert_to_float(contract.balance_of(POLO_COLD_WALLET))
    polo_warm_wallet_balance = convert_to_float(contract.balance_of(POLO_WARM_WALLET))
    polo_hot_wallet_balance = convert_to_float(contract.balance_of(POLO_HOT_WALLET))

    htx_wallet_eth = htx.get_wallet_balance()

    slack_message = SlackMessage()
    slack_message.add_code_block_message(f'Total Supply is {eth_total_balance}')

    polo_title = ['polo_HE_account', 'polo_cold_wallet', 'polo_warm_wallet', 'polo_hot_wallet']
    slack_message.add_table(polo_title, [
        ['Unknown', polo_cold_wallet_balance, polo_warm_wallet_balance, polo_hot_wallet_balance]
    ])

    htx_title = ['htx_HE_account', 'htx_wallet']
    slack_message.add_table(htx_title, [['Unknown', htx_wallet_eth]])

    # polo_wallet_eth = polo_cold_wallet_balance + polo_warm_wallet_balance + polo_hot_wallet_balance
    # supplemented_eth = eth_total_balance - polo_wallet_eth - htx_wallet_eth - reserve
    # if supplemented_eth > 0:
    #     slack_message.add_message(f'Supplemented supply is {supplemented_eth}')
    #     # slack_message.add_warning('lily', 'tahoe')
    #
    # if polo_wallet_eth > polo_HE_balance:
    #     slack_message.add_message(
    #         f'Poloniex wallet balance is {polo_wallet_eth}, account balance is {polo_HE_balance}'
    #     )
    #     # slack_message.add_warning('lily', 'tahoe')
    # if htx_wallet_eth > htx_HE_balance:
    #     slack_message.add_message(f'HTX wallet balance is {htx_wallet_eth}, account balance is {htx_HE_balance}')
    #     # slack_message.add_warning('lily', 'tahoe')

    slack_service.send_message(channel=channel, message=slack_message)


def monitor_mint_eth():
    redis_key = 'tron_mint_last_block'
    conn = get_redis_connection()
    last_time_stamp = conn.get(redis_key)
    current_time_stamp = int(datetime.timestamp(datetime.now()) * 1000)
    message = SlackMessage()

    try:
        if not last_time_stamp:
            conn.set(redis_key, current_time_stamp)
            message.add_message(f'Get latest block failed.')
            message.add_warning('hosea')
            slack_service.send_message(channel=configuration.TEST, message=message)
            return

        logger.info(f'Monitor mint from {last_time_stamp} to {current_time_stamp}')
        events = client.get_events(contract_address=configuration.ETH.get('TRON_CONTRACT'), event_name='issue',
                                   min_block_timestamp=last_time_stamp, max_block_timestamp=current_time_stamp)

        if events and len(events) > 0:
            headers = ['Transaction_id', 'Amount', 'Time (UTC +8)', 'Operation']
            rows = []
            for event in events:
                packaged_at = datetime.fromtimestamp(int(event.get('block_timestamp')) / 1000,
                                                     pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
                rows.append(
                    [generate_transaction_link('tron', event.get('transaction_id')),
                     convert_to_float(int(event.get('result').get('amount', 0))), packaged_at,
                     event.get('event_name')])
            message.add_table(headers=headers, rows=rows)
            slack_service.send_message(channel=configuration.ETH_MONITOR, message=message)

    except Exception as ex:
        logger.error(f'Monitor eth exception {str(ex)}')

    conn.set(redis_key, current_time_stamp)


def monitor_redemption_eth():
    redis_key = 'tron_redeem_last_block'
    conn = get_redis_connection()
    last_time_stamp = conn.get(redis_key)
    current_time_stamp = int(datetime.timestamp(datetime.now()) * 1000)
    message = SlackMessage()

    try:
        if not last_time_stamp:
            conn.set(redis_key, current_time_stamp)
            message.add_message(f'Get latest block failed.')
            message.add_warning('hosea')
            slack_service.send_message(channel=configuration.TEST, message=message)
            return

        logger.info(f'Monitor redemption from {last_time_stamp} to {current_time_stamp}')
        events = client.get_events(contract_address=configuration.ETH.get('TRON_CONTRACT'), event_name='issue',
                                   min_block_timestamp=last_time_stamp, max_block_timestamp=current_time_stamp)

        if events and len(events) > 0:
            headers = ['Transaction_id', 'redeem', 'Time (UTC +8)', 'Operation']
            rows = []
            for event in events:
                packaged_at = datetime.fromtimestamp(int(event.get('block_timestamp')) / 1000,
                                                     pytz.timezone(TIME_ZONE)).strftime('%Y-%m-%d %H:%M:%S')
                rows.append(
                    [generate_transaction_link('tron', event.get('transaction_id')),
                     convert_to_float(int(event.get('result').get('amount', 0))), packaged_at,
                     event.get('event_name')])
            message.add_table(headers=headers, rows=rows)
            slack_service.send_message(channel=configuration.ETH_MONITOR, message=message)

    except Exception as ex:
        logger.error(f'Monitor eth exception {str(ex)}')

    conn.set(redis_key, current_time_stamp)
