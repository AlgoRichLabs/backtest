"""
File: backtest_base.py
Author: Zhicheng Tang
Created Date: 8/23/24
Description: <This is a general backtest class that includes the essential methods required to backtest a strategy.>
"""
from typing import List, Dict
import pandas as pd
import numpy as np

from backtest.event import Event
from backtest.portfolio import Portfolio
from .data_parser.ohlcv import OHLCV
from .data_parser.option_chain import OptionChain
from .data_parser.data_parser import DataParser
from .utils.constant import FREQUENCY
from .utils.instrument import InstrumentType


class BacktestBase(object):
    def __init__(self, history_data_path: Dict[str, str], frequency: FREQUENCY, start_date: str, end_date: str,
                 **kwargs) -> None:
        """
        :param history_data_path: dictionary with symbol as keys and data paths as values.
        :param frequency: frequency of the backtest data.
        :param start_date: start date string in format YYYY-MM-DD and it's inclusive.
        :param end_date: end date string in format YYYY-MM-DD and it's inclusive.
        :param kwargs: other potential configs.
        """
        self.history_data_path = history_data_path
        self.start_date = start_date
        self.end_date = end_date
        initial_cash_balance = kwargs.get('initial_cash_balance', 0)
        self.portfolio = Portfolio(initial_cash_balance)
        self.frequency = frequency
        self.portfolio_snapshots: List[Dict] = []
        self.net_cash_flow = initial_cash_balance
        self.period_returns: List[float] = []

    def run_backtest(self, time_sorted_events: List[Event]) -> None:
        raise NotImplementedError("Run backtest method is not implemented.")

    @staticmethod
    def get_simple_return(start_value: float, end_value: float) -> float:
        return end_value / start_value - 1

    @staticmethod
    def get_time_weighted_return(returns: List[float], period: FREQUENCY) -> float:
        """
        Computes the annualized time weighted rate of return.
        :param returns: a list of returns for each sub-period.
        :param period: the frequency of the periods.
        :return: annualized time weighted rate of return.
        """
        if period == FREQUENCY.DAY:
            years = len(returns) / 365
            return (np.prod([(1 + r) for r in returns]) - 1) ** (1 / years) - 1
        elif period == FREQUENCY.WEEK:
            avg_week_num_yearly = 52.1429
            years = len(returns) / avg_week_num_yearly
            return (np.prod([(1 + r) for r in returns]) - 1) ** (1 / years) - 1
        elif period == FREQUENCY.MONTH:
            years = len(returns) / 12
            return (np.prod([(1 + r) for r in returns]) - 1) ** (1 / years) - 1
        elif isinstance(period, FREQUENCY):
            raise NotImplementedError(f"{period} is not supported for get_time_weighted_return.")
        else:
            raise ValueError(f"Invalid period {period}.")

    def get_maximum_drawdown(self) -> float:
        pass

    def _load_data(self) -> None:
        instruments = self.config.get("instrument", {})
        if InstrumentType.OPTION.value in instruments:
            self.ohlcv_data = self._load_option_data(instruments[InstrumentType.OPTION.value])

        if InstrumentType.STOCK.value in instruments:
            self.option_data = self._load_stock_data(instruments[InstrumentType.STOCK.value])

    def _load_stock_data(self, symbols: List[str]) -> Dict[str, OHLCV]:
        """
        Initialize OHLCV objects for each symbol. Data ts is in UTC timezone.
        :param symbols: a list of stock instrument symbols
        :return: A dictionary of OHLCV objects.
        """
        ohlcv_data = {}
        for symbol in symbols:
            path = f"{self.history_data_path}/{symbol}"
            df = DataParser.read_ohlcv(path, self.frequency)
            df["ts_event"] = pd.to_datetime(df["ts_event"], utc=True)
            df.rename(columns={"ts_event": "ts"})
            ohlcv_data[symbol] = OHLCV(df)

        return ohlcv_data

    def _load_option_data(self, symbols: List[str]) -> Dict[str, OptionChain]:
        """
        Initialize OptionChain objects for each symbol.
        :param symbols: a list of option instrument underlying symbols
        :return: A dictionary of OptionChain objects.
        """
        option_data = {}
        for symbol in symbols:
            path = f"{self.history_data_path}/{symbol}"
            df = DataParser.read_option_chain(path)
            option_data[symbol] = OptionChain(df)

        return option_data










