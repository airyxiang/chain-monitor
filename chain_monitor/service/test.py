import re
# from chain_monitor.remote.htx.htx_sdk import HtxSDK
# from chain_monitor.service.monitor_stu_balackelist import monitoring_blacklisted, monitoring_user_status
# from chain_monitor.slack import SlackMessage

# htx_sdk = HtxSDK()

# htx_sdk.wallet_request(host='https://wallet-tron.huobi.com', path='/openapi/balance', method='GET')

# htx_sdk.api_request(host='https://api.huobi.pro', path='/v1/account/accounts', method='GET')

# monitoring_blacklisted()

# monitoring_user_status()

c = [
    ['TRX- A', '123123', '12312312', '123123123'],
    ['TRX- B', '123123', '12312312', '123123123'],
    ['TRX- C', '123123', '12312312', '123123123'],
    ['sTRX', '123123', '12312312', '123123123'],
    ['USDT', '123123', '12312312', '123123123']
]

h = ['拍卖总CDP数量', '拍卖的抵押品数量', '实际拍卖价值-总拍卖的债务价值-拍卖的清算奖励金']


def test(headers, rows):
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

    print(f'```{table}```')


def get_text(text):
    text = str(text)
    match = re.match(r'^<(.*)\|(.*)>$', text)
    return match.group(2) if match else text


test(h, c)
