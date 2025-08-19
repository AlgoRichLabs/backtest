"""
File: position.py
Author: Zhicheng Tang
Created Date: 8/23/24
Description: <>
"""
from .utils.constant import SIDE
from .utils.instrument import Instrument, InstrumentType
from backtest.event import FilledOrder

class Position(object):
    def __init__(self, instrument: Instrument) -> None:
        self.instrument = instrument
        # amount is the number of shares for stocks or number of contracts for options.
        self.amount = 0
        self.position_value = 0
        self.unrealized_pnl = 0
        self.average_entry_price = 0

    @property
    def symbol(self) -> str:
        return self.instrument.symbol

    def fill_order(self, order: FilledOrder) -> None:
        """
        Update the position with a filled order.
        :param order: a filled order.
        :return: None.
        """
        if order.instrument.symbol != self.instrument.symbol:
            raise ValueError(
                f"Order instrument '{order.instrument.symbol}' does not match "
                f"position instrument '{self.instrument.symbol}'"
            )

        old_amount = self.amount
        if order.side == SIDE.SELL:
            self.amount -= order.quantity
        elif order.side == SIDE.BUY:
            self.amount += order.quantity

        if self.instrument.type == InstrumentType.STOCK and self.amount < 0:
            raise ValueError(f"Shorting stock '{self.symbol}' is not supported.")
        
        is_opening_position = abs(self.amount) > abs(old_amount)

        if is_opening_position:
            if old_amount == 0:
                self.average_entry_price = order.filled_price
            # If we are adding to an existing position (long or short)
            else:
                old_total_value = self.average_entry_price * abs(old_amount)
                new_order_value = order.filled_price * order.quantity
                self.average_entry_price = (old_total_value + new_order_value) / abs(self.amount)

        if self.amount == 0:
            self.average_entry_price = 0.0
            self.unrealized_pnl = 0.0
            self.position_value = 0.0
        self.update_position(order.filled_price)

    def update_position(self, price: float) -> None:
        """
        Update the position with a price.
        :param price: current market price.
        :return: None.
        """
        if self.amount == 0:
            return
        
        self.unrealized_pnl = (price - self.average_entry_price) * self.amount * self.instrument.multiplier
        self.position_value = self.amount * price * self.instrument.multiplier

