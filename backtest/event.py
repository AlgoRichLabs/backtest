"""
File: event
Author: Zhicheng Tang
Created Date: 9/1/24
Description: <>
"""
from pandas import Timestamp

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