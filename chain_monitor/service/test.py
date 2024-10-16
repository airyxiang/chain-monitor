from chain_monitor.remote.htx.htx_sdk import HtxSDK

htx_sdk = HtxSDK()

print(htx_sdk.wallet_request(host='https://wallet-tron.huobi.com', path='/openapi/balance', method='GET'))

# print(htx_sdk.api_request(host='https://api.huobi.pro', path='/v1/account/accounts', method='GET'))
