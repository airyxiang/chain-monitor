import requests
from easydict import EasyDict

from chain_monitor.configurations.logger import get_logger
from chain_monitor.exceptions import *

logger = get_logger(__name__)


class SigningServiceError(Exception):
    pass


class TronSigningServiceError(SigningServiceError):
    pass


class RESTClient:
    def __init__(self, base_url, enabled=True):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.enabled = enabled

    def build_url(self, url):
        full_url = '{}/{}'.format(self.base_url, url.lstrip('/'))
        return full_url

    def _get_auth_header(self):
        return {}

    def get(self, url, data=None, timeout=None):
        if not self.enabled:
            return

        full_url = self.build_url(url)
        headers = self._get_auth_header()
        response = self.session.get(full_url, params=data, headers=headers, timeout=timeout)
        return self._handle_response(response)

    def post(self, url, data=None, timeout=None):
        if not self.enabled:
            return

        full_url = self.build_url(url)
        headers = self._get_auth_header()
        response = self.session.post(full_url, json=data, headers=headers, timeout=timeout)
        return self._handle_response(response)

    def patch(self, url, data=None, timeout=None):
        if not self.enabled:
            return

        full_url = self.build_url(url)
        headers = self._get_auth_header()
        response = self.session.patch(full_url, json=data, headers=headers, timeout=timeout)
        return self._handle_response(response)

    def delete(self, url, data=None, timeout=None):
        if not self.enabled:
            return

        full_url = self.build_url(url)
        headers = self._get_auth_header()
        response = self.session.delete(full_url, json=data, headers=headers, timeout=timeout)
        return self._handle_response(response)

    def _handle_response(self, response):
        return response


class RESTServiceClient(RESTClient):
    def __init__(self, api_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key

    def _get_auth_header(self):
        if self.api_key:
            return {'Authorization': 'Bearer {}'.format(self.api_key)}
        else:
            return {}

    def _handle_response(self, response):
        status_code = response.status_code
        if status_code in (200, 201):
            json_data = response.json()
            return EasyDict(json_data)
        if status_code == 404:
            raise NotFoundError()
        elif 400 <= status_code < 500:
            # expecting an error object with message, code
            data = response.json()
            error_message = data.get('message', None)
            error_code = data.get('code', None)
            raise BadRequestError(message=error_message, code=error_code, )
        elif status_code >= 500:
            raise ServerError(
                message='Server error',
            )
