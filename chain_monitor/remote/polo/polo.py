from chain_monitor.remote.polo.polo_sdk import PoloSDK

headers = {"Content-Type": "application/json"}
host = "https://api.poloniex.com"
method_req = "get"
params_req = {"limit": 10}


def get_account_balance_by_currency(currency):
    client = PoloSDK()
    path_req = "/accounts/balances"
    response = client.sign_req(host, path_req, method_req, params_req, headers)
    balances = [balance for balance in response[0]['balances'] if balance['currency'] == currency]
    if not balances:
        return 0
    return balances[0].get('available') + balances[0].get('hold')
