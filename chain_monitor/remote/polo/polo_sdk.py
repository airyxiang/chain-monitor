import hashlib
import requests
import time
import hmac
import base64
from urllib import parse
from chain_monitor.configurations.configuration import POLO_API_KEY, POLO_API_SECRET_KEY


class PoloSDK:
    def __init__(self):
        self.__access_key = POLO_API_KEY
        self.__secret_key = POLO_API_SECRET_KEY
        self.__time = int(time.time() * 1000)

    def __create_sign(self, params, method, path):
        timestamp = self.__time
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

    def sign_req(self, host, path, method, params, headers):
        sign = self.__create_sign(params=params, method=method, path=path)
        headers.update(
            {
                "key": self.__access_key,
                "signTimestamp": str(self.__time),
                "signature": sign,
            }
        )
        params = parse.urlencode(params)
        if params == "":
            request_url = "{host}{path}".format(host=host, path=path)
        else:
            request_url = "{host}{path}?{params}".format(host=host, path=path, params=params)
        response = requests.get(request_url, params={}, headers=headers)
        return response.json()
