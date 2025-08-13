"""
File: portfolio.py
Author: Zhicheng Tang
Created Date: 8/24/24
Description: <>
"""
from typing import Dict
from backtest.position import Position
from backtest.order import FilledOrder
from .utils.logger import logger


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
        logger.info(f"Symbol: {order.symbol}: {order.side} order filled at {order.filled_price}, quantity {order.quantity}. Timestamp: {order.ts}")

        instrument_symbol = order.instrument.symbol
        if instrument_symbol not in self.positions:
            self.positions[instrument_symbol] = Position(order.instrument)

        self.positions[instrument_symbol].fill_order(order)

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



