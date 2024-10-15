import datetime
import hashlib
import time
import hmac
import base64
import urllib
from urllib import parse
from chain_monitor.configurations.configuration import HTX_WALLET_API_KEY, HTX_WALLET_API_SECRET_KEY


class HtxSDK:
    def __init__(self):
        self.__access_key = HTX_WALLET_API_KEY
        self.__secret_key = HTX_WALLET_API_SECRET_KEY
        self.__time = time.time()

    def __create_sign(self, params, method, path):
        timestamp = int(self.__time * 1000)
        params.update({"signTimestamp": timestamp})
        sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        encode_params = parse.urlencode(sorted_params)
        del params["signTimestamp"]
        sign_params_first = [method.upper(), path, encode_params]
        sign_params_second = "\n".join(sign_params_first)
        sign_params = sign_params_second.encode(encoding="UTF8")
        secret_key = self.__secret_key.encode(encoding="UTF8")
        digest = hmac.new(secret_key, sign_params, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature

    def get_time_stamp(self):
        return datetime.datetime.fromtimestamp(self.__time).strftime('%Y-%m-%dT%H:%M:%S')

    def sign_req(self, host, path, method, params):
        signature = self.__create_sign(method=method, path=path, params=params)

        signature_encoded = urllib.parse.quote(signature, safe='')
        time_stamp_encoded = urllib.parse.quote(self.get_time_stamp(), safe=':')

        request_url = (f"{host}{path}?AWSAccessKeyId={HTX_WALLET_API_KEY}&Signature={signature_encoded}"
                       f"&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp={time_stamp_encoded}"
                       f"&currency=trc20eth&walletType=hot")

        return request_url
