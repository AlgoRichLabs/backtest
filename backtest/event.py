"""
File: event
Author: Zhicheng Tang
Created Date: 9/1/24
Description: <>
"""
from pandas import Timestamp
from typing import Dict

from backtest.backtest.order import FilledOrder
from backtest.utils.instrument import Instrument, OptionType, Option
from backtest.utils.constant import SIDE


class Event:
    _id_counter = 0

    def __init__(self, ts: Timestamp) -> None:
        Event._id_counter += 1
        self.ts = ts
        self.id = Event._id_counter


class CashFlowChange(Event):
    def __init__(self, ts: Timestamp, change_amount: float) -> None:
        super().__init__(ts)
        self.change_amount = change_amount


class UpdatePortfolio(Event):
    def __init__(self, ts: Timestamp, prices: Dict[str, float] = None) -> None:
        super().__init__(ts)
        self.prices = prices


class OptionExpired(Event):
    def __init__(self, ts: Timestamp, instrument: Instrument) -> None:
        super().__init__(ts)
        self.instrument = instrument


class OptionAssigned(Event):
    """
    Do not consider the situation of partial position is early assigned.
    """
    def __init__(self, ts: Timestamp, instrument: Option) -> None:
        super().__init__(ts)
        self.instrument = instrument
        self.ts = ts

    def get_filled_order(self, side: SIDE, quantity: int) -> FilledOrder:
        """
        Convert an assigned option position to a filled order.
        Args:
            side: side of the option position.
            quantity: number of contracts.

        Returns:
            A filled order to execute the option.
        """
        underlying_stock = self.instrument.get_underlying()

        if side == SIDE.BUY:
            # Assign a long option position.
            if self.instrument.option_type == OptionType.CALL:
                order_side = SIDE.BUY
            elif self.instrument.option_type == OptionType.PUT:
                order_side = SIDE.SELL
        elif side == SIDE.SELL:
            if self.instrument.option_type == OptionType.CALL:
                order_side = SIDE.SELL
            elif self.instrument.option_type == OptionType.PUT:
                order_side = SIDE.BUY

        return FilledOrder(
            underlying_stock,
            self.ts, # Usually the execution date is one trading day after the expiration day. Just assgined ts for convenience
            order_side,
            quantity * self.instrument.multiplier,
            self.instrument.strike_price,
            self.ts)
