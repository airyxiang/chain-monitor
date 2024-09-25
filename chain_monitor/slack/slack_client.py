import requests

from chain_monitor.configurations.logger import get_logger

logger = get_logger(__name__)


class SlackClient:
    def __init__(self):
        self.session = requests.Session()

    def post(self, message, channel):
        if not message or not channel:
            logger.info('Message body or channel can not be none.')

        logger.info(f'Send message {message} to {channel}')

        data = {"text": message}
        response = self.session.post(channel, json=data)
        return response
