from abc import ABC, abstractmethod
from enum import Enum
from datetime import date


class InstrumentType(Enum):
    STOCK = "stock"
    OPTION = "option"


class OptionType(Enum):
    CALL = "C"
    PUT = "P"


class Instrument(ABC):
    """
    Abstract base class for a tradable instrument.
    """

    @property
    @abstractmethod
    def symbol(self) -> str:
        # Unique trading symbol for the instrument.
        raise NotImplementedError

    @property
    @abstractmethod
    def type(self) -> InstrumentType:
        # Type of instrument (e.g., stock, option, future, etc).
        raise NotImplementedError

    @property
    @abstractmethod
    def multiplier(self) -> int:
        # Contract multiplier. For stocks, it's 1. For standard options, it's 100.
        raise NotImplementedError
    

class Stock(Instrument):
    def __init__(self, ticker: str) -> None:
        self._ticker = ticker

    @property
    def symbol(self) -> str:
        return self._ticker

    @property
    def type(self) -> InstrumentType:
        return InstrumentType.STOCK

    @property
    def multiplier(self) -> int:
        return 1
    
    def __repr__(self):
        return f"Stock(ticker='{self.symbol}')"



class Option(Instrument):
    def __init__(self, underlying_symbol: str, expiration_date: date, strike_price: float, option_type: OptionType) -> None:
        self.underlying_symbol = underlying_symbol
        self.expiration_date = expiration_date
        self.strike_price = strike_price
        self.option_type = option_type
    
    @property
    def symbol(self) -> str:
        """
        Generates the standard OCC (Options Clearing Corporation) symbol.
        Example: SPY241220C00450000
        """
        return (
            f"{self.underlying_symbol.ljust(6)}"
            f"{self.expiration_date.strftime('%y%m%d')}"
            f"{self.option_type.value}"
            f"{int(self.strike_price * 1000):08d}"
        )

    @property
    def type(self) -> InstrumentType:
        return InstrumentType.OPTION

    @property
    def multiplier(self) -> int:
        # Standard US equity options control 100 shares
        return 100

    def __repr__(self):
        return (f"Option(underlying='{self.underlying_symbol}', expiry='{self.expiration_date}', "
                f"strike={self.strike_price}, type='{self.option_type.name}')")


        