"""
File: backtest_dca
Author: Zhicheng Tang
Created Date: 9/2/24
Description: <>
"""
from typing import Dict, List
import pandas as pd

from backtest.backtest_base import BacktestBase
from backtest.event import Event, CashFlowChange
from backtest.order import *
from utils.constant import FREQUENCY


class BacktestDCA(BacktestBase):
    def __init__(self, history_data_path: Dict[str, str], frequency: FREQUENCY, start_date: str,
                 end_date: str, **kwargs) -> None:
        super().__init__(history_data_path, frequency, start_date, end_date, **kwargs)

    def run_backtest(self, time_ordered_events: List[Event]) -> None:
        """
        Simulate the portfolio performance based on the time sorted events.
        :param time_ordered_events:
        :return: None
        """
        last_value: float | None = None
        open_orders: Dict[str, LimitOrder] = {}
        self.events = time_ordered_events
        for event in time_ordered_events:
            if isinstance(event, FilledOrder):
                filled_order: FilledOrder = event
                self.portfolio.fill_order(filled_order)
                self.portfolio.update_portfolio({filled_order.symbol: filled_order.filled_price})
                self.portfolio_snapshots.append(self.portfolio.get_snapshot())
            elif isinstance(event, LimitOrder):
                open_orders[event.order_id] = event
            elif isinstance(event, CanceledOrder):
                del open_orders[event.order_id]
            elif isinstance(event, CashFlowChange):
                if last_value:
                    prices = {}
                    for symbol in self.portfolio.positions.keys():
                        end_of_day = event.ts.normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
                        intraday_prices = self.ohlcv_data[symbol].get_ohlcv_by_date_string(event.ts, end_of_day)
                        try:
                            close_price = intraday_prices.iloc[-1].close
                        except IndexError:
                            print(f"{event.ts} data not exist")
                            continue
                        prices[symbol] = close_price
                    self.portfolio.update_portfolio(prices)
                    period_return = self.get_simple_return(last_value, self.portfolio.portfolio_value)
                    self.period_returns.append(period_return)

                self.portfolio.add_cash_flow(event.change_amount)
                self.net_cash_flow += event.change_amount
                last_value = self.portfolio.portfolio_value
            elif isinstance(event, Event):
                raise NotImplementedError(f"{event} not supported.")
            else:
                raise ValueError(f"Invalid event type: {type(event)}.")