from datetime import datetime

import pytz

from chain_monitor.configurations import configuration
from chain_monitor.configurations.logger import get_logger
from chain_monitor.configurations.redis import get_redis_connection
from chain_monitor.slack import slack_service, SlackMessage
from chain_monitor.utils.formatter import generate_transaction_link
from chain_monitor.utils.money import convert_to_float
from chain_monitor.web3.blockchains.tron import TrongridClient

logger = get_logger(__name__)

client = TrongridClient()
redis_key = 'tron_mint_last_block'


def monitor_mint_eth():
    conn = get_redis_connection()
    last_time_stamp = conn.get(redis_key)
    current_time_stamp = int(datetime.timestamp(datetime.now()) * 1000)

    message = SlackMessage()

    if not last_time_stamp:
        conn.set(redis_key, current_time_stamp)
        message.add_message(f'Get latest block failed.')
        message.add_warning('hosea')
        slack_service.send_message(channel=configuration.TEST, message=message)
        return

    logger.info(f'{last_time_stamp} to {current_time_stamp}')
    events = client.get_events(contract_address=configuration.ETH.get('TRON_CONTRACT'), event_name='issue',
                               min_block_timestamp=last_time_stamp, max_block_timestamp=current_time_stamp)

    if events and len(events) > 0:
        headers = ['Transaction_id', 'Amount', 'Time (UTC +8)', 'Operation']
        rows = []
        for event in events:
            packaged_at = datetime.fromtimestamp(int(event.get('block_timestamp')) / 1000,
                                                 pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            rows.append(
                [generate_transaction_link('tron', event.get('transaction_id')),
                 convert_to_float(int(event.get('result').get('amount', 0))), packaged_at,
                 event.get('event_name')])
        message.add_table(headers=headers, rows=rows)
        slack_service.send_message(channel=configuration.TEST, message=message)

    conn.set(redis_key, current_time_stamp)
