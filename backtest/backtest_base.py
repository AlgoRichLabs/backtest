"""
File: backtest_base.py
Author: Zhicheng Tang
Created Date: 8/23/24
Description: <This is a general backtest class that includes the essential methods required to backtest a strategy.>
"""
from typing import List, Dict
from order import FilledOrder
from portfolio import Portfolio
from position import Position


class BacktestBase(object):
    def __init__(self, history_data_path: Dict[str, str], time_sorted_orders: List[FilledOrder], start_date: str,
                 end_date: str, **kwargs) -> None:
        """
        It only supports daily close price backtest.
        :param history_data_path: dictionary with symbol as keys and data paths as values
        :param time_sorted_orders: list of FilledOrder.
        :param start_date: start date string in format YYYY-MM-DD and it's inclusive.
        :param end_date: end date string in format YYYY-MM-DD and it's inclusive.
        :param kwargs: other potential configs.
        """
        self.history_data_path = history_data_path
        self.time_sorted_orders = time_sorted_orders
        self.start_date = start_date
        self.end_date = end_date
        initial_cash_balance = kwargs.get('initial_cash_balance', 0)
        self.portfolio = Portfolio(initial_cash_balance)

    def run(self) -> None:
        # TODO: actual backtest process.
        """
        1. Record the backtest start time
        2. Load all history data to the memory. Since it's daily close price data, it won't use too much memory.
        3. Iterate every trading day in the range of start_date and end_date.
            1. Load filled orders and get a portfolio snapshot.
            2. Save the portfolio snapshot.
        4. Record the backtest end time and compute the time consumption.
        5. Print out the time consumption for backtesting.
        :return: None.
        """
        pass








