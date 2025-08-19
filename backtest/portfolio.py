"""
File: portfolio.py
Author: Zhicheng Tang
Created Date: 8/24/24
Description: <>
"""
from typing import Dict
from backtest.position import Position
from backtest.event import FilledOrder, OptionAssigned, OptionExpired
from .utils.logger import logger
from .utils.constant import SIDE


class Portfolio(object):
    def __init__(self, initial_cash_balance: float = 0) -> None:
        self.cash_balance = initial_cash_balance
        self.positions: Dict[str, Position] = {}
        self.portfolio_value = self.cash_balance

    def add_cash_flow(self, value: float) -> float:
        self.cash_balance += value
        self.update_portfolio()
        return self.cash_balance

    def fill_order(self, order: FilledOrder) -> None:
        commission = abs(order.order_value) * order.commission_rate
        self.cash_balance -= (order.order_value + commission)
        if self.cash_balance < 0:
            print(order.filled_date)
            raise Exception("Negative cash balance.")
        logger.info(f"Symbol: {order.symbol}: {order.side} order filled at {order.filled_price}, quantity {order.quantity}, multiplier {order.instrument.multiplier}, Timestamp: {order.ts}")

        instrument_symbol = order.instrument.symbol
        if instrument_symbol not in self.positions:
            self.positions[instrument_symbol] = Position(order.instrument)

        self.positions[instrument_symbol].fill_order(order)

    def option_expired(self, option_expired_event: OptionExpired):
        """
        Remove the option position and no further calculations required.
        """
        del self.positions[option_expired_event.instrument.symbol]

    def option_assigned(self, option_assigned_event: OptionAssigned):
        """
        Execute trades for assigned option.
        """
        position = self.positions[option_assigned_event.instrument.symbol]
        side = SIDE.BUY if position.amount > 0 else SIDE.SELL
        filled_order = option_assigned_event.get_filled_order(side, position.amount)
        self.fill_order(filled_order)
        del self.positions[option_assigned_event.instrument.symbol]


    def get_snapshot(self) -> Dict:
        return {"portfolio_value": self.portfolio_value, "cash_balance": self.cash_balance, "positions": self.positions}

    def update_portfolio(self, prices: Dict[str, float] = None) -> None:
        """
        Updates the portfolio value.
        :param prices: dictionary with symbol as keys and price as values.
        :return: None.
        """
        if prices:
            for symbol, price in prices.items():
                if symbol in self.positions:
                    self.positions[symbol].update_position(price)

        self.portfolio_value = sum([position.position_value for position in self.positions.values()]) + self.cash_balance



