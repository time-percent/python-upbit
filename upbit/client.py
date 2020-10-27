import collections.abc
import hashlib
import jwt
import uuid
import requests

from typing import Mapping, Sequence
from urllib.parse import urlencode

from .exceptions import APIException, RequestException


class UPBitClient:
    API_URL = 'https://api.upbit.com'
    API_VERSION = 'v1'

    def __init__(self, api_key: str, api_secret: str = None):
        """
        :param api_key: API Key
        :param api_secret: Secret Key
        :param requests_params: optional - Mapping of requests params to use for all calls
        """
        self.API_KEY = api_key
        self.API_SECRET = api_secret

    def _urlencode_sequence(self, key, seq: Sequence[str]):
        return '&'.join([f'{key}={item}' for item in seq])

    def _urlencode(self, query: Mapping):
        encoded = {}
        encoded_seq = []
        for k, v in query.items():
            if not isinstance(v, str) and isinstance(v, collections.abc.Iterable):
                encoded_seq.append(self._urlencode_sequence(k + '[]', v))
            else:
                encoded[k] = v

        return f"{urlencode(encoded)}&{'&'.join(encoded_seq)}"

    def _generate_payload(self, query: Mapping = None):
        payload = {
            'access_key': self.API_KEY,
            'nonce': str(uuid.uuid4())
        }

        if query:
            query_string = self._urlencode(query).encode()
            m = hashlib.sha512()
            m.update(query_string)
            payload['query_hash'] = m.hexdigest()
            payload['query_hash_alg'] = 'SHA512'

        return payload

    def _generate_auth_header(self, payload):
        jwt_token = jwt.encode(payload, self.API_SECRET).decode('utf-8')
        authorize_token = f'Bearer {jwt_token}'
        headers = {'Authorization': authorize_token}

        return headers

    @staticmethod
    def _handle_response(response):
        if not str(response.status_code).startswith('2'):
            raise APIException(response)

        try:
            return response.json()
        except ValueError:
            raise RequestException(f'Invalid Response: {response.text}')

    def _request(self, method, path, query: Mapping = None, headers: Mapping=None, **kwargs):
        if headers is None:
            headers = {}
        payload = self._generate_payload(query)
        headers.update(self._generate_auth_header(payload))
        uri = f"{self.API_URL}/{self.API_VERSION}/{path}"

        response = getattr(requests, method)(uri, headers=headers, **kwargs)

        return self._handle_response(response)

    @classmethod
    def _public_request(cls, method: str, path: str, query: Mapping = None):
        uri = f"{cls.API_URL}/{cls.API_VERSION}/{path}"
        response = requests.request(method, uri, params=query)
        return cls._handle_response(response)

    # Exchange API

    def accounts(self):
        return self._request('get', 'accounts')

    def order_chance(self, market: str):
        """

        :type market: object
        """
        query = {
            'market': market
        }
        return self._request('get', "orders/chance", query=query)

    def get_order(self, uuid_: str = None, identifier: str = None):
        """

        :param uuid_: Order UUID
        :param identifier:
        :return:
        """
        if not uuid_ and not identifier:
            raise TypeError('order() needs at least one argument  (0 given)')

        query = {}
        if uuid_:
            query['uuid'] = uuid_
        if identifier:
            query['identifier'] = identifier

        return self._request('get', 'order', query=query)

    def get_recent_trades(self, market: str, states: Sequence[str], uuids: Sequence[str], identifiers: Sequence[str],
                          kind: str, state: str = 'wait', page: int = 1, limit: int = 100, order_by: str = 'desc'):
        query = {
            'market': market,
            'states': states,
            'uuids[]': uuids,
            'identifiers[]': identifiers,
            'state': state,
            'page': page,
            'limit': limit,
            'order_by': order_by
        }
        return self._request('get', 'orders', query=query)

    def cancel_order(self, uuid_: str = None, identifier: str = None):
        if not uuid_ and not identifier:
            raise TypeError('cancel_order() needs at least one argument (0 given)')

        query = {
            'uuid': uuid_,
            'identifier': identifier
        }

        return self._request('delete', 'order', query=query)

    def _order(self, side: str, **kwargs):
        return self._request('post', 'orders', query=kwargs.update({'side': side}))

    def purchase(self, market: str, volume: int, price: int, ord_type: str, identifier: str):
        return self._order(side='bid', market=market, volume=volume, price=price,
                           ord_type=ord_type, identifier=identifier)

    def sell(self, market: str, volume: int, price: int, ord_type: str, identifier: str):
        return self._order(side='ask', market=market, volume=volume, price=price,
                           ord_type=ord_type, identifier=identifier)

    def get_withdraws(self, **kwargs):
        """

        :param currency: Currency Code
        :param state:
            - 'submitting'
            - 'submitted'
            - 'almost_accepted': awaiting withdraw
            - 'rejected'
            - 'accepted'
            - 'processing'
            - 'done'
            - 'canceled'
        :param uuids: list of withdraw UUIDs
        :param txids: list of withdraw TXID
        :param limit: defaults to 100, maximum 100
        :param page: defaults to 1
        :param order_by: 'desc' or 'asc'

        :return: API response

        .. code-block:: python
            [
                {
                    "type": "withdraw",
                    "uuid": "35a4f1dc-1db5-4d6b-89b5-7ec137875956",
                    "currency": "XRP",
                    "txid": "98c15999f0bdc4ae0e8a-ed35868bb0c204fe6ec29e4058a3451e-88636d1040f4baddf943274ce37cf9cc",
                    "state": "DONE",
                    "created_at": "2019-02-28T15:17:51+09:00",
                    "done_at": "2019-02-28T15:22:12+09:00",
                    "amount": "1.00",
                    "fee": "0.0",
                    "transaction_type": "default"
                }
                # ....
            ]

        :raises: APIException, RequestException

        """
        return self._request('get', 'withdraws', query=kwargs)

    def get_withdraw(self, uuid_: str, txid: str, currency: str):
        query = {}
        if uuid_:
            query['uuid'] = uuid_
        if txid:
            query['txid'] = txid
        if currency:
            query['currency'] = currency
        return self._request('get', 'withdraw', query=query)

    def widthdraws_chance(self, currency):
        query = {}
        if currency:
            query['currency'] = currency

        return self._request('get', 'widthraws/chance', query=query)

    def withdraw_in_coin(self, currency: str, amount: int, address: str, secondary_address: str, transaction_type):
        query = {
            'currency': currency,
            'amount': amount,
            'address': address
        }
        if secondary_address:
            query['secondary_address'] = secondary_address
        if transaction_type:
            query['transaction_type'] = transaction_type

        return self._request('post', 'withdraws/coin', query=query)

    def withdraw_in_krw(self, amount: int):
        query = {'amount': amount}
        return self._request('post', 'withdraws/krw', query=query)

    def get_deposits(self, currency: str, state: str, uuids: Sequence[str], txids: Sequence[str],
                     limit: int, page: int, order_by: str):
        query = {
            'currency': currency,
            'state': state,
            'uuids': uuids,
            'txids': txids,
            'limit': limit,
            'page': page,
            'order_by': order_by
        }

        return self._request('get', 'deposits', query=query)

    def get_deposit(self, uuid: str, txid: str, currency: str):
        query = {
            'uuid': uuid,
            'txid': txid,
            'currency': currency
        }

        return self._request('get', 'deposit', query=query)

    def generate_coin_address(self, currency: str):
        query = {
            'currency': currency
        }

        return self._request('post', 'deposits/generate_coin_address', query=query)

    def get_coin_addresses(self):
        return self._request('get', 'deposits/coin_addresses')

    def get_coin_address(self, currency):
        query = {
            'currency': currency
        }
        return self._request('get', 'deposits/coin_address', query=query)

    def wallet_status(self):
        return self._request('get', 'status/wallet')

    def api_keys(self):
        return self._request('get', 'api_keys')

    # Quotation API

    @staticmethod
    def get_markets(detail: bool = False):
        query = {
            'detail': str(detail).lower()
        }

        return UPBitClient._public_request('get', 'market/all', query=query)

    @staticmethod
    def get_candle_tickers(period: str,  market: str, to: str = None, count: int = 200, price_unit: str = None):
        query = {
            'count': count,
            'market': market,
            'to': to
        }
        if price_unit:
            query['convertingPriceUnit'] = price_unit

        unit = ''.join(filter(lambda x: x.isnumeric(), period))
        path = 'candles/'
        if period.startswith('min'):
            path += 'minutes/'
            path += unit
        elif period == 'week':
            path += 'weeks'
        elif period == 'day':
            path += 'days'
        elif period == 'month':
            path += 'months'

        return UPBitClient._public_request('get', path, query=query)

    @staticmethod
    def get_recent_trade_ticks(market: str,  count: int = None, cursor: str = None,
                               days_ago: int = None, to: str = None):
        query = {
            'market': market,
            'to': to,
            'count': count,
            'cursor': cursor,
            'days_ago': days_ago
        }

        return UPBitClient._public_request('get', 'trades/ticks', query=query)

    @staticmethod
    def get_ticker(market_code: str):
        return UPBitClient._public_request('get', 'ticker', query={'markets': market_code})

    @staticmethod
    def get_order_book(markets: Sequence[str]):
        return UPBitClient._public_request('get', 'orderbook', query={'markets': markets})
