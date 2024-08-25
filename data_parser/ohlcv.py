"""
File: ohlcv.py
Author: Zhicheng Tang
Created Date: 8/24/24
Description: <>
"""
import pandas as pd


class OHLCV(object):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.symbol = self._get_symbol()

    def get_ohlcv_by_timestamp(self, timestamp: int, end_timestamp: int = None) -> pd.DataFrame:
        """
        Get the most recent OHLCV record for a given timestamp. If end_timestamp is provided, it returns all records
        within the range.
        :param timestamp: If end_timestamp is provided, it's a snapshot timestamp, otherwise it's the start timestamp.
        :param end_timestamp: It's the end timestamp if provided.
        :return: OHLCV dataframe.
        """
        pass

    def get_ohlcv_by_date_string(self, date_string: str, end_date_string: str = None) -> pd.DataFrame:
        """
        Get the most recent OHLCV record for a given date string. If end_date_string is provided, it returns all records
        within the range. date_string should be in YYYY-MM-DD or YYYY-MM-DD HH format. Currently, only support day and
        hour level.
        :param date_string: If end_date_string is provided, it's a snapshot date string, otherwise it's the start date
        string.
        :param end_date_string: It's the end date string if provided.
        :return:
        """
        pass

    def _get_symbol(self) -> str:
        """
        Get the symbol of the ticker.
        :return: symbol string.
        """
        pass
