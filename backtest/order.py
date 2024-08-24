from utils.constant import SIDE


class Order(object):
    def __init__(self, symbol: str, side: SIDE, quantity: int) -> None:
        """
        :param symbol: ticker symbol.
        :param side: side of the trade.
        :param quantity: the quantity of the underlying asset.
        """
        self.symbol = symbol
        if not isinstance(side, SIDE):
            raise ValueError(f'Invalid side type: {side}')
        self.side = side
        self.quantity = quantity


class FilledOrder(Order):
    def __init__(self, symbol: str, side: SIDE, quantity: int, filled_price: float, date: str) -> None:
        """
        :param filled_price: filled price of the order.
        """
        super().__init__(symbol, side, quantity)
        self.filled_price = filled_price
        self.date = date
        if self.side == SIDE.SELL:
            self.order_value = -filled_price * quantity
        elif self.side == SIDE.BUY:
            self.order_value = filled_price * quantity
