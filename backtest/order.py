from pandas import Timestamp

from backtest.event import Event
from .utils.constant import SIDE, ORDER_STATUS
from .utils.instrument import Instrument


class Order(Event):
    def __init__(self, instrument: Instrument, ts: Timestamp, side: SIDE, quantity: int, commission_rate: float = 0) -> None:
        """
        :param symbol: ticker symbol.
        :param ts: timestamp when the order is created.
        :param side: side of the trade.
        :param quantity: the quantity of the underlying asset.
        :param commission_rate: the commission rate.
        """
        super().__init__(ts)
        self.instrument = instrument
        if not isinstance(side, SIDE):
            raise ValueError(f'Invalid side type: {side}')
        self.side = side
        self.quantity = quantity
        self.commission_rate = commission_rate

    @property
    def symbol(self) -> str:
        """
        This is to maintain backward compatibility for now. Now delegates getting symbol to the instrument.symbol.
        """
        return self.instrument.symbol


class LimitOrder(Order):
    """

    """
    def __init__(self, instrument: Instrument, ts: Timestamp, side: SIDE, quantity: int, limit_price: float,
                 commission_rate: float = 0) -> None:
        """
        :param limit_price: bid/ask price.
        """
        super().__init__(instrument, ts, side, quantity, commission_rate)
        self.filled_price = None
        self.filled_date = None # Timestamp when the order is filled. Currently, don't consider partially filled cases.
        self.limit_price = limit_price
        self.status = ORDER_STATUS.OPEN
        self.order_id = self.id # Order id equals the event id when it's initially created.

        base_value = limit_price * quantity * self.instrument.multiplier

        if self.side == SIDE.SELL:
            self.order_value = -base_value
        elif self.side == SIDE.BUY:
            self.order_value = base_value

    def fill(self, filled_date: Timestamp, filled_price: float):
        self.status = ORDER_STATUS.FILLED
        self.filled_date = filled_date
        self.filled_price = filled_price


class FilledOrder(Order):
    def __init__(self, instrument: Instrument, ts: Timestamp, side: SIDE, quantity: int, filled_price: float,
                 filled_date: Timestamp, commission_rate: float = 0) -> None:
        """
        :param filled_price: filled price of the order.
        """
        super().__init__(instrument, ts, side, quantity, commission_rate)
        self.filled_price = filled_price
        self.filled_date = filled_date
        self.status = ORDER_STATUS.FILLED
        self.order_id = None

        base_value = filled_price * quantity * self.instrument.multiplier
        if self.side == SIDE.SELL:
            self.order_value = -base_value
        elif self.side == SIDE.BUY:
            self.order_value = base_value

    @classmethod
    def from_order(cls, limit_order: LimitOrder):
        if limit_order.status != ORDER_STATUS.FILLED:
            raise ValueError(f'Invalid order status: {limit_order.status}')

        cls_to_return = cls(limit_order.instrument, limit_order.ts, limit_order.side, limit_order.quantity,
                             limit_order.filled_price, limit_order.filled_date, limit_order.commission_rate)
        cls_to_return.order_id = limit_order.order_id
        return cls_to_return


class CanceledOrder(Order):
    def __init__(self, order: LimitOrder, canceled_date: Timestamp) -> None:
        super().__init__(order.instrument, order.ts, order.side, order.quantity, order.commission_rate)
        self.status = ORDER_STATUS.CANCELED
        self.canceled_date = canceled_date
        self.order_value = order.order_value
        self.order_id = order.id
