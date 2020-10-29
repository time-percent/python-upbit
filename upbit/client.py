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
        """UPBit API Client constructor

        :param api_key: API Key
        :param api_secret: Secret Key
        :param requests_params: optional - Mapping of requests params to use for all calls
        """
        self.API_KEY = api_key
        self.API_SECRET = api_secret

    def _urlencode_sequence(self, key, seq: Sequence[str]):
        """Transform a sequence to a query string

        :param key: a name of parameter
        :param seq: sequence data
        :return: a query string
        """
        return '&'.join([f'{key}={item}' for item in seq])

    def _urlencode(self, query: Mapping):
        """Generate a query string.

        :param query:
        :return: a query string
        """
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
        """Internal helper for handling API responses from the UPBit server.
        Raises the appropriate exceptions when necessary; otherwise, returns the response.

        :param response:
        :return: the API response from the UPBit server
        """
        if not str(response.status_code).startswith('2'):
            raise APIException(response)

        try:
            return response.json()
        except ValueError:
            raise RequestException(f'Invalid Response: {response.text}')

    def _request(self, method, path, query: Mapping = None, headers: Mapping = None, **kwargs):
        """Used for private(exchange) API requests

        :param method: a request method
        :param path: target endpoint
        :param query:
        :param headers:
        :param kwargs:
        :return:
        """
        if headers is None:
            headers = {}
        payload = self._generate_payload(query)
        headers.update(self._generate_auth_header(payload))
        uri = f"{self.API_URL}/{self.API_VERSION}/{path}"

        response = requests.request(method, uri, headers=headers, params=kwargs)

        return self._handle_response(response)

    @classmethod
    def _public_request(cls, method: str, path: str, query: Mapping = None):
        """Used for public(quotation) API requests

        :param method: a request method
        :param path: target endpoint
        :param query: request params
        :return:
        """
        uri = f"{cls.API_URL}/{cls.API_VERSION}/{path}"
        response = requests.request(method, uri, params=query)
        return cls._handle_response(response)

    # Exchange API

    def accounts(self):
        """Get current account information.

        https://docs.upbit.com/reference#전체-계좌-조회

        :return: API response

        .. code-block:: python
            [
                {
                    "currency":"KRW",
                    "balance":"1000000.0",
                    "locked":"0.0",
                    "avg_buy_price":"0",
                    "avg_buy_price_modified":false,
                    "unit_currency": "KRW",
                },
                {
                    "currency":"BTC",
                    "balance":"2.0",
                    "locked":"0.0",
                    "avg_buy_price":"101000",
                    "avg_buy_price_modified":false,
                    "unit_currency": "KRW",
                }
            ]

        :raises: APIException, RequestException
        """
        return self._request('get', 'accounts')

    def order_chance(self, market: str):
        """List possible orders by market

        https://docs.upbit.com/reference#주문-가능-정보

        :type market: market ID
        """
        query = {
            'market': market
        }
        return self._request('get', "orders/chance", query=query)

    def get_order_info(self, uuid_: str = None, identifier: str = None):
        """Get order information. uuid_ or identifier must be provided.

        https://docs.upbit.com/reference#개별-주문-조회

        :param uuid_: Order UUID
        :param identifier:
        :return: API response

        .. code-block:: python
            {
                "uuid": "9ca023a5-851b-4fec-9f0a-48cd83c2eaae",
                "side": "ask",
                "ord_type": "limit",
                "price": "4280000.0",
                "state": "done",
                "market": "KRW-BTC",
                "created_at": "2019-01-04T13:48:09+09:00",
                "volume": "1.0",
                "remaining_volume": "0.0",
                "reserved_fee": "0.0",
                "remaining_fee": "0.0",
                "paid_fee": "2140.0",
                "locked": "0.0",
                "executed_volume": "1.0",
                "trades_count": 1,
                "trades": [
                    {
                        "market": "KRW-BTC",
                        "uuid": "9e8f8eba-7050-4837-8969-cfc272cbe083",
                        "price": "4280000.0",
                        "volume": "1.0",
                        "funds": "4280000.0",
                        "side": "ask"
                    }
                ]
            }
            # ....

        :raises: TypeError, APIException, RequestException

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
        """Get a list of recent trades.

        https://docs.upbit.com/reference#주문-리스트-조회

        :param market: market ID
        :param states: list of order status
        :param uuids: list of order UUIDs
        :param identifiers: order identifier
        :param kind: can be set to 'normal' or 'watch'
        :param state:
        :param page: defaults to 1
        :param limit: defaults to 100
        :param order_by: can be set to 'asc' or 'desc'. defaults to 'desc'
        :return: API response

        .. code-block:: python
            [
                {
                    "uuid": "9ca023a5-851b-4fec-9f0a-48cd83c2eaae",
                    "side": "ask",
                    "ord_type": "limit",
                    "price": "4280000.0",
                    "state": "done",
                    "market": "KRW-BTC",
                    "created_at": "2019-01-04T13:48:09+09:00",
                    "volume": "1.0",
                    "remaining_volume": "0.0",
                    "reserved_fee": "0.0",
                    "remaining_fee": "0.0",
                    "paid_fee": "2140.0",
                    "locked": "0.0",
                    "executed_volume": "1.0",
                    "trades_count": 1,
                }
                # ....
            ]

        :raises: APIException, RequestException
        """
        query = {
            'market': market,
            'states': states,
            'uuids': uuids,
            'identifiers': identifiers,
            'kind': kind,
            'state': state,
            'page': page,
            'limit': limit,
            'order_by': order_by
        }
        return self._request('get', 'orders', query=query)

    def cancel_order(self, uuid_: str = None, identifier: str = None):
        """uuid_ or identifier must be provided.

        :param uuid_:
        :param identifier:
        :return: API response

        .. code-block:: python
            {
                "uuid":"cdd92199-2897-4e14-9448-f923320408ad",
                "side":"bid",
                "ord_type":"limit",
                "price":"100.0",
                "state":"wait",
                "market":"KRW-BTC",
                "created_at":"2018-04-10T15:42:23+09:00",
                "volume":"0.01",
                "remaining_volume":"0.01",
                "reserved_fee":"0.0015",
                "remaining_fee":"0.0015",
                "paid_fee":"0.0",
                "locked":"1.0015",
                "executed_volume":"0.0",
                "trades_count":0
            }

        :raises: TypeError, APIException, RequestException
        """
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
        """

        :param volume:
        :param price:
        :param ord_type:
        :param identifier:
        :return: API response

        .. code-block:: python
            {
                "uuid":"cdd92199-2897-4e14-9448-f923320408ad",
                "side":"bid",
                "ord_type":"limit",
                "price":"100.0",
                "avg_price":"0.0",
                "state":"wait",
                "market":"KRW-BTC",
                "created_at":"2018-04-10T15:42:23+09:00",
                "volume":"0.01",
                "remaining_volume":"0.01",
                "reserved_fee":"0.0015",
                "remaining_fee":"0.0015",
                "paid_fee":"0.0",
                "locked":"1.0015",
                "executed_volume":"0.0",
                "trades_count":00
            }

        :raises: APIException, RequestException
        """
        return self._order(side='bid', market=market, volume=volume, price=price,
                           ord_type=ord_type, identifier=identifier)

    def sell(self, market: str, volume: int, price: int, ord_type: str, identifier: str):
        """

        :param volume:
        :param price:
        :param ord_type:
        :param identifier:
        :return: API response

        .. code-block:: python
            {
                "uuid":"cdd92199-2897-4e14-9448-f923320408ad",
                "side":"ask",
                "ord_type":"limit",
                "price":"100.0",
                "avg_price":"0.0",
                "state":"wait",
                "market":"KRW-BTC",
                "created_at":"2018-04-10T15:42:23+09:00",
                "volume":"0.01",
                "remaining_volume":"0.01",
                "reserved_fee":"0.0015",
                "remaining_fee":"0.0015",
                "paid_fee":"0.0",
                "locked":"1.0015",
                "executed_volume":"0.0",
                "trades_count":00
            }

        :raises: APIException, RequestException
        """
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
        :param txids: list of withdraw TXIDs
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
        """

        :param uuid_:
        :param txid:
        :param currency:
        :return: API response

        .. code-block:: python
            {
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec8b42b79",
                "currency": "BTC",
                "txid": null,
                "state": "processing",
                "created_at": "2018-04-13T11:24:01+09:00",
                "done_at": null,
                "amount": "0.01",
                "fee": "0.0",
                "transaction_type": "default"
            }

        :raises: APIException, RequestException
        """
        query = {}
        if uuid_:
            query['uuid'] = uuid_
        if txid:
            query['txid'] = txid
        if currency:
            query['currency'] = currency
        return self._request('get', 'withdraw', query=query)

    def widthdraws_chance(self, currency):
        """

        :param currency:
        :return: API response

        .. code-block:: python
            {
                "member_level": {
                    "security_level": 3,
                    "fee_level": 0,
                    "email_verified": true,
                    "identity_auth_verified": true,
                    "bank_account_verified": true,
                    "kakao_pay_auth_verified": false,
                    "locked": false,
                    "wallet_locked": false
                },
                "currency": {
                    "code": "BTC",
                    "withdraw_fee": "0.0005",
                    "is_coin": true,
                    "wallet_state": "working",
                    "wallet_support": [
                        "deposit",
                        "withdraw"
                    ]
                },
                "account": {
                    "currency": "BTC",
                    "balance": "10.0",
                    "locked": "0.0",
                    "avg_buy_price": "8042000",
                    "avg_buy_price_modified": false,
                    "unit_currency": "KRW",
                },
                "withdraw_limit": {
                    "currency": "BTC",
                    "minimum": null,
                    "onetime": null,
                    "daily": "10.0",
                    "remaining_daily": "10.0",
                    "remaining_daily_krw": "0.0",
                    "fixed": null,
                    "can_withdraw": true
                }
            }

        :raises: APIException, RequestException
        """
        query = {}
        if currency:
            query['currency'] = currency

        return self._request('get', 'widthraws/chance', query=query)

    def withdraw_in_coin(self, currency: str, amount: int, address: str, secondary_address: str, transaction_type):
        """

        :param currency:
        :param amount:
        :param address:
        :param secondary_address:
        :param transaction_type:
        :return: API response

        .. code-block:: python
            {
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec8b42b79",
                "currency": "BTC",
                "txid": "ebe6937b-130e-4066-8ac6-4b0e67f28adc",
                "state": "processing",
                "created_at": "2018-04-13T11:24:01+09:00",
                "done_at": null,
                "amount": "0.01",
                "fee": "0.0",
                "krw_amount": "80420.0",
                "transaction_type": "default"
            }

        :raises: APIException, RequestException
        """
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
        """

        :param amount:
        :return: API response

        .. code-block:: python
            {
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec8b42b79",
                "currency": "KRW",
                "txid": "ebe6937b-130e-4066-8ac6-4b0e67f28adc",
                "state": "processing",
                "created_at": "2018-04-13T11:24:01+09:00",
                "done_at": null,
                "amount": "10000",
                "fee": "0.0",
                "transaction_type": "default"
            }

        :raises: APIException, RequestException
        """
        query = {'amount': amount}
        return self._request('post', 'withdraws/krw', query=query)

    def get_deposits(self, currency: str, state: str, uuids: Sequence[str], txids: Sequence[str],
                     limit: int, page: int, order_by: str):
        """

        :param currency:
        :param state:
        :param uuids:
        :param txids:
        :param limit:
        :param page:
        :param order_by:
        :return: API response

        .. code-block:: python
            {
                [
                    {
                        "type": "deposit",
                        "uuid": "94332e99-3a87-4a35-ad98-28b0c969f830",
                        "currency": "KRW",
                        "txid": "9e37c537-6849-4c8b-a134-57313f5dfc5a",
                        "state": "ACCEPTED",
                        "created_at": "2017-12-08T15:38:02+09:00",
                        "done_at": "2017-12-08T15:38:02+09:00",
                        "amount": "100000.0",
                        "fee": "0.0",
                        "transaction_type": "default"
                    }
                    #....
                ]
            }

        :raises: APIException, RequestException
        """
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
        """

        :param uuid:
        :param txid:
        :param currency:
        :return: API response

        .. code-block:: python
            {
                "type": "deposit",
                "uuid": "94332e99-3a87-4a35-ad98-28b0c969f830",
                "currency": "KRW",
                "txid": "9e37c537-6849-4c8b-a134-57313f5dfc5a",
                "state": "ACCEPTED",
                "created_at": "2017-12-08T15:38:02+09:00",
                "done_at": "2017-12-08T15:38:02+09:00",
                "amount": "100000.0",
                "fee": "0.0",
                "transaction_type": "default"
            }

        :raises: APIException, RequestException
        """
        query = {
            'uuid': uuid,
            'txid': txid,
            'currency': currency
        }

        return self._request('get', 'deposit', query=query)

    def generate_coin_address(self, currency: str):
        """https://docs.upbit.com/reference#입금-주소-생성-요청

        :param currency:
        :return: API response

        .. code-block:: python
            {
                "success": true,
                "message": "BTC 입금주소를 생성중입니다."
            }

        :raises: APIException, RequestException
        """
        query = {
            'currency': currency
        }

        return self._request('post', 'deposits/generate_coin_address', query=query)

    def get_coin_addresses(self):
        """

        :return: API response

        .. code-block:: python
            [
                {
                    "currency": "BTC",
                    "deposit_address": "3EusRwybuZUhVDeHL7gh3HSLmbhLcy7NqD",
                    "secondary_address": null
                },
                {
                    "currency": "ETH",
                    "deposit_address": "0x0d73e0a482b8cf568976d2e8688f4a899d29301c",
                    "secondary_address": null
                },
                {
                    "currency": "XRP",
                    "deposit_address": "rN9qNpgnBaZwqCg8CvUZRPqCcPPY7wfWep",
                    "secondary_address": "3057887915"
                }
            ]

        :raises: APIException, RequestException
        """
        return self._request('get', 'deposits/coin_addresses')

    def get_coin_address(self, currency):
        """

        :param currency:
        :return: API response

        .. code-block:: python
            {
                "currency": "BTC",
                "deposit_address": "3EusRwybuZUhVDeHL7gh3HSLmbhLcy7NqD",
                "secondary_address": null
            }

        :raises: APIException, RequestException
        """
        query = {
            'currency': currency
        }
        return self._request('get', 'deposits/coin_address', query=query)

    def wallet_status(self):
        """

        :return: API response

        .. code-block:: python
            [
                {
                    "currency": "BTC",
                    "wallet_state": "working",
                    "block_state": "normal",
                    "block_height": 637432,
                    "block_updated_at": "2020-07-03T02:04:45.523+00:00"
                }
            ]

        :raises: APIException, RequestException
        """
        return self._request('get', 'status/wallet')

    def api_keys(self):
        """

        :return: API response

        .. code-block:: python
            [
                {
                    "access_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                    "expire_at": "2021-03-09T12:39:39+00:00"
                }
            ]
        :raises: APIException, RequestException
        """
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
