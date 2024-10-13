"""
File: constant.py
Author: Zhicheng Tang
Created Date: 8/23/24
Description: <>
"""
from enum import Enum


class SIDE(Enum):
    LONG = "long"
    SHORT = "short"
    BUY = "buy"
    SELL = "sell"


class FREQUENCY(Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"


class STRATEGY(Enum):
    DCA = "dca"
    DCA_LIMIT_DIP = "dca_limit_dip"

class ORDER_STATUS(Enum):
    OPEN = "open"
    CANCELED = "canceled"
    FILLED = "filled"

