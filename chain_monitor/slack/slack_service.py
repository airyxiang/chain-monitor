import threading

from chain_monitor.configurations.logger import get_logger
from chain_monitor.slack.slack_client import SlackClient
from chain_monitor.slack.slack_message import SlackMessage

logger = get_logger(__name__)

slack_client = SlackClient()
lock = threading.Lock()


def send(channel, messages):
    with lock:
        for message in messages:
            slack_client.post(channel=channel, message=message)


def send_direct_message(channel, message: str):
    send(channel=channel, messages=[message])


def send_warning(channel, *members):
    messages = [f'<@{member}>' for member in members]
    send(channel=channel, messages=messages)


def send_message(channel, message: SlackMessage):
    messages = message.get_messages()
    send(channel=channel, messages=messages)
