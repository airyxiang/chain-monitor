from chain_monitor.configurations.configuration import USDT, TEST
from chain_monitor.configurations.logger import get_logger
from chain_monitor.slack import slack_service, SlackMessage
from chain_monitor.web3.contract.contract_factory import USDTContract

logger = get_logger(__name__)

contract_address = USDT.get('ETH_CONTRACT')
contract = USDTContract(contract_address)
monitor_address = '0xcC2BcF5f274595cb71fA0F5609cBA6e4b602E2D7'


def monitoring_blacklisted():
    try:
        is_black_listed = contract.isBlackListed(monitor_address)
    except Exception as ex:
        err_msg = f'Get balance failed. {str(ex)}'
        logger.error(err_msg)
        slack_service.send_message(err_msg, TEST)
        slack_service.send_warning('hosea')
        return

    if not is_black_listed:
        message = SlackMessage()
        message.add_message(f'{monitor_address} has been blacklisted!')
        message.add_warning('hosea', 'lily', 'tahoe')
        slack_service.send_message(message=message, channel=TEST)
