from pandas import Timestamp

from backtest.event import Event
from utils.constant import SIDE


class Order(Event):
    def __init__(self, symbol: str, ts: Timestamp, side: SIDE, quantity: int, commission_rate: float = 0) -> None:
        """
        :param symbol: ticker symbol.
        :param side: side of the trade.
        :param quantity: the quantity of the underlying asset.
        :param commission_rate: the commission rate.
        """
        super().__init__(ts)
        self.symbol = symbol
        if not isinstance(side, SIDE):
            raise ValueError(f'Invalid side type: {side}')
        self.side = side
        self.quantity = quantity
        self.commission_rate = commission_rate


class FilledOrder(Order):
    def __init__(self, symbol: str, ts: Timestamp, side: SIDE, quantity: int, filled_price: float,
                 filled_date: str, commission_rate: float = 0) -> None:
        """
        :param filled_price: filled price of the order.
        """
        super().__init__(symbol, ts, side, quantity, commission_rate)
        self.filled_price = filled_price
        self.filled_date = filled_date
        if self.side == SIDE.SELL:
            self.order_value = -filled_price * quantity
        elif self.side == SIDE.BUY:
            self.order_value = filled_price * quantity
