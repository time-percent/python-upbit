import pytest
import time

from upbit import UPBitClient
from upbit.exceptions import APIException

MARKET_CODE = 'KRW-BTC'


def test_get_markets_not_none():
    assert UPBitClient.get_markets() is not None
    assert UPBitClient.get_markets(True) is not None


def test_get_candle_tickers_not_none():
    assert UPBitClient.get_candle_tickers('min1', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min3', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min5', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min15', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min10', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min30', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min60', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('min240', MARKET_CODE) is not None
    time.sleep(1)
    assert UPBitClient.get_candle_tickers('week', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('day', MARKET_CODE) is not None
    assert UPBitClient.get_candle_tickers('day', MARKET_CODE, price_unit='KRW')
    assert UPBitClient.get_candle_tickers('month', MARKET_CODE) is not None


def test_get_candle_tickers_wrong_code():
    with pytest.raises(APIException):
        UPBitClient.get_candle_tickers('min1', '')
        UPBitClient.get_candle_tickers('m', '')


def test_get_recent_trade_ticks():
    assert UPBitClient.get_recent_trade_ticks(MARKET_CODE) is not None
    with pytest.raises(APIException):
        UPBitClient.get_recent_trade_ticks('')


def test_get_ticker():
    assert UPBitClient.get_ticker(MARKET_CODE) is not None
    with pytest.raises(APIException):
        UPBitClient.get_ticker('')


def test_get_order_book():
    assert UPBitClient.get_order_book(MARKET_CODE) is not None
    with pytest.raises(APIException):
        UPBitClient.get_order_book('')
