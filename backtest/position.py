"""
File: position.py
Author: Zhicheng Tang
Created Date: 8/23/24
Description: <>
"""
from backtest.order import FilledOrder
from utils.constant import SIDE


class Position(object):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.amount = 0
        self.position_value = 0
        self.unrealized_pnl = 0
        self.average_entry_price = None

    def fill_order(self, order: FilledOrder) -> None:
        """
        Update the position with a filled order.
        :param order: a filled order.
        :return: None.
        """
        if order.side == SIDE.SELL:
            self.amount -= order.quantity
            if self.amount < 0:
                raise Exception("Does not support shorting a position.")
        elif order.side == SIDE.BUY:
            if not self.average_entry_price:
                self.average_entry_price = order.filled_price
            else:
                self.average_entry_price = (
                    (self.amount * self.average_entry_price + order.quantity * order.filled_price) /
                    (self.amount + order.quantity)
                )
            self.amount += order.quantity

        self.update_position(order.filled_price)

    def update_position(self, price: float) -> None:
        """
        Update the position with a price.
        :param price: current market price.
        :return: None.
        """
        self.unrealized_pnl = (self.average_entry_price - price) * self.amount
        self.position_value = self.amount * price

