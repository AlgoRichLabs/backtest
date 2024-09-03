"""
File: event
Author: Zhicheng Tang
Created Date: 9/1/24
Description: <>
"""
from pandas import Timestamp

class Event:
    def __init__(self, ts: Timestamp) -> None:
        self.ts = ts

class CashFlowChange(Event):
    def __init__(self, ts: Timestamp, change_amount: float) -> None:
        super().__init__(ts)
        self.change_amount = change_amount