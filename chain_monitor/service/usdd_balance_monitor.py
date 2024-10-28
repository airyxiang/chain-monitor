from chain_monitor.configurations.configuration import USDD, USDD_MINING_REWARD
from chain_monitor.configurations.logger import get_logger
from chain_monitor.utils.money import convert_to_float
from chain_monitor.slack import slack_service, SlackMessage
from chain_monitor.web3.contract.tron_contract_factory import TokenContract

logger = get_logger(__name__)

# balance usdd < 1,000,000 alert

contract_address = USDD.get('TRON_CONTRACT')
contract = TokenContract(contract_address)
monitor_address = 'THxNCPGp8N8SJBScRU8rKPf7PvuwkGihmW'
threshold = 1000000


def monitor_balance():
    try:
        balance = convert_to_float(contract.balance_of(monitor_address))
    except Exception as ex:
        err_msg = f'Get balance failed. {str(ex)}'
        logger.error(err_msg)
        slack_service.send_message(err_msg, USDD_MINING_REWARD)
        slack_service.send_warning('hosea')
        return

    message = SlackMessage()
    if balance < threshold:
        message.add_message(f'Balance of {monitor_address} {balance} is too low !')
        message.add_warning('chris', 'hosea', 'yuki', 'jasmine')
    else:
        message.add_message(f'Balance of {monitor_address} is {balance}.')

    slack_service.send_message(message=message, channel=USDD_MINING_REWARD)
