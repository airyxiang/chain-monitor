import re


def generate_transaction_link(chain, transaction_hash):
    if chain == 'tron':
        return f'<https://tronscan.org/#/transaction/{transaction_hash}|{transaction_hash}>'
    elif chain == 'eth':
        return f'<https://etherscan.io/tx/{transaction_hash}|{transaction_hash}>'
    else:
        return transaction_hash


def get_text(text):
    text = str(text)
    match = re.match(r'^<(.*)\|(.*)>$', text)
    return match.group(2) if match else text
