import pytest
import time

from upbit import UPBitClient
from upbit.exceptions import APIException

MARKET_CODE = 'KRW-BTC'


def test_get_markets_not_none():
    assert UPBitClient.get_markets() is not None
    assert UPBitClient.get_markets(True) is not None


def test_get_candle_tickers_not_none():
    assert UPBitClient.get_candles('min1', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min3', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min5', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min15', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min10', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min30', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min60', MARKET_CODE) is not None
    assert UPBitClient.get_candles('min240', MARKET_CODE) is not None
    assert UPBitClient.get_candles('week', MARKET_CODE) is not None
    assert UPBitClient.get_candles('day', MARKET_CODE) is not None
    assert UPBitClient.get_candles('day', MARKET_CODE, price_unit='KRW')
    assert UPBitClient.get_candles('month', MARKET_CODE) is not None


def test_get_candle_tickers_wrong_code():
    with pytest.raises(APIException):
        UPBitClient.get_candles('min1', '')
        UPBitClient.get_candles('m', '')


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
