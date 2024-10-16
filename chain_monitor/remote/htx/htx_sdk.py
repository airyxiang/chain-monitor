import datetime
import hashlib
import time
import hmac
import base64
import urllib
from urllib import parse

from huobi.exception.huobi_api_exception import HuobiApiException
from huobi.utils import UrlParamsBuilder, utc_now, create_signature

from chain_monitor.configurations.configuration import HTX_WALLET_API_KEY, HTX_WALLET_API_SECRET_KEY, HTX_API_KEY, \
    HTX_API_SECRET_KEY


class HtxSDK:
    def __init__(self):
        self.__time = utc_now()

    def create_wallet_sign(self, api_key, secret_key, method, url, builder):
        if api_key is None or secret_key is None or api_key == "" or secret_key == "":
            raise HuobiApiException(HuobiApiException.KEY_MISSING, "API key and secret key are required")

        builder.put_url("AWSAccessKeyId", api_key)
        builder.put_url("SignatureVersion", "2")
        builder.put_url("SignatureMethod", "HmacSHA256")
        builder.put_url("Timestamp", self.__time)

        host = urllib.parse.urlparse(url).hostname
        path = urllib.parse.urlparse(url).path

        keys = sorted(builder.param_map.keys())
        qs0 = '&'.join(['%s=%s' % (key, parse.quote(builder.param_map[key], safe='')) for key in keys])
        payload0 = '%s\n%s\n%s\n%s' % (method, host, path, qs0)
        dig = hmac.new(secret_key.encode('utf-8'), msg=payload0.encode('utf-8'), digestmod=hashlib.sha256).digest()
        s = base64.b64encode(dig).decode()
        builder.put_url("Signature", s)

    def wallet_request(self, host, path, method):
        builder = UrlParamsBuilder()
        builder.put_url("currency", "trc20eth")
        builder.put_url("walletType", "hot")
        self.create_wallet_sign(api_key=HTX_WALLET_API_KEY, secret_key=HTX_WALLET_API_SECRET_KEY, method=method,
                                url=f'{host}{path}', builder=builder)
        request_url = f'{host}{path}{builder.build_url()}'
        return request_url

    def api_request(self, host, path, method):
        builder = UrlParamsBuilder()
        self.create_wallet_sign(api_key=HTX_API_KEY, secret_key=HTX_API_SECRET_KEY, method=method, url=f'{host}{path}',
                                builder=builder)
        request_url = f'{host}{path}{builder.build_url()}'
        return request_url
