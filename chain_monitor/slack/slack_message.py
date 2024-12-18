# import re
from collections import OrderedDict

from chain_monitor.configurations.configuration import slack_members
from chain_monitor.utils.formatter import get_text


class SlackMessage:
    def __init__(self):
        # O(1)
        self.messages = OrderedDict()

    def add_message(self, message):
        if message not in self.messages:
            self.messages[message] = None

    def get_messages(self):
        return list(self.messages.keys())

    def add_code_block_message(self, message):
        self.add_message(f'```{message}```')

    def add_table(self, headers, rows):
        self.add_message(self._create_table(headers=headers, rows=rows))

    def add_warning(self, *members):
        message = ''.join(f"<@{slack_members.get(member, '')}>" for member in members)
        self.add_message(message=message)

    # <url | text>
    @staticmethod
    def _create_table(headers, rows):
        col_widths = [max(len(get_text(item)) for item in col) for col in zip(*rows, headers)]
        header_row = ' | '.join(header.ljust(w) for header, w in zip(headers, col_widths))
        separator = '-+-'.join('-' * w for w in col_widths)
        table = f"{header_row}\n{separator}\n"
        for row in rows:
            data_row = ' | '.join(
                str(item).ljust(w) if idx < len(col_widths) - 4 else str(item).rjust(w)
                for idx, (item, w) in enumerate(zip(row, col_widths))
            )
            table = f'{table}{data_row}\n'

        return f'```{table}```'
        # split_point = table[:len(table) // 2].rfind('\n')
        # return [f'```\n{table[:split_point]}\n```', f'```\n{table[split_point + 1:]}\n```']
