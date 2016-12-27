
import json

import requests

from oauth2 import Consumer
from oauth2 import Request as OAuthRequest
from oauth2 import SignatureMethod_HMAC_SHA1


class FlowRequest(object):

    request_supported_methods = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'OPTIONS', 'HEAD']
    request_base_url = ''
    request_headers = {}
    request_log_response_codes = [500]
    request_return_response_object = False
    request_session = True
    request_json = True
    request_oauth = None
    request_oauth_signature_method = SignatureMethod_HMAC_SHA1()

    def __init__(
        self,
        supported_methods=None,
        base_url=None,
        headers=None,
        log_response_codes=None,
        return_response_object=False,
        session=None,
        json=None,
        oauth=None
    ):

        if supported_methods:
            self.request_supported_methods = supported_methods

        if base_url:
            self.request_base_url = base_url

        if headers:
            self.request_headers = headers

        if log_response_codes:
            self.request_log_response_codes = log_response_codes

        if return_response_object:
            self.request_return_response_object = return_response_object

        if oauth:
            self.request_oauth = oauth

        # Override settings
        if session is not None:
            self.request_session = session

        if json is not None:
            self.request_json = json

        self.session = requests
        if self.request_session:
            self.session = requests.Session()  # pylint: disable=redefined-variable-type

            # adapter = HTTPAdapter()
            # self.session.mount('http://', adapter)
            # self.session.mount('https://', adapter)

    def _build_oauth_headers(self, method, url, body, parameters):
        oauth_key, oauth_secret = self.request_oauth
        consumer = Consumer(key=oauth_key, secret=oauth_secret)
        oauth_request = OAuthRequest.from_consumer_and_token(
            consumer=consumer,
            token=None,
            http_method=method,
            http_url=url,
            parameters=parameters,
            body=body,
            is_form_encoded=False
        )
        oauth_request.sign_request(
            signature_method=self.request_oauth_signature_method,
            consumer=consumer,
            token=None
        )

        return oauth_request.to_header()

    def _request(self, method, url, data=None, params=None, auth=None):
        if method not in self.request_supported_methods:
            raise IndexError('Only %s are allowed' % self.request_supported_methods)

        method = method.lower()
        url = '%s%s' % (self.request_base_url, url)

        if data and self.request_json:
            data = json.dumps(data)

        if self.request_oauth:
            oauth_headers = self._build_oauth_headers(method=method, url=url, body='', parameters=params)
            self.request_headers.update(oauth_headers)

        response = getattr(self.session, method)(url, data=data, params=params, headers=self.request_headers, auth=auth)
        if self.request_return_response_object:
            return response

        if response is None:
            return None

        # No content anyway, might as well stop here
        if not response:
            return None

        try:
            response_json = response.json()
        except Exception:
            response_json = None

        if not response_json:
            return None

        return response_json

    def get(self, url, data=None, params=None, auth=None):
        return self._request(method='GET', url=url, data=data, params=params, auth=auth)

    def post(self, url, data=None, params=None, auth=None):
        return self._request(method='POST', url=url, data=data, params=params, auth=auth)

    def delete(self, url, data=None, params=None, auth=None):
        return self._request(method='DELETE', url=url, data=data, params=params, auth=auth)

    def put(self, url, data=None, params=None, auth=None):
        return self._request(method='PUT', url=url, data=data, params=params, auth=auth)

    def patch(self, url, data=None, params=None, auth=None):
        return self._request(method='PATCH', url=url, data=data, params=params, auth=auth)

    def head(self, url, auth=None):
        return self._request(method='HEAD', url=url, auth=auth)

    def options(self, url, auth=None):
        return self._request(method='OPTIONS', url=url, auth=auth)
