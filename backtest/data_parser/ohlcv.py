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
        Get the most recent OHLCV record for a given ts. If end_timestamp is provided, it returns all records
        within the range.
        :param timestamp: If end_timestamp is provided, it's a snapshot ts, otherwise it's the start ts.
        :param end_timestamp: It's the end ts if provided.
        :return: OHLCV dataframe.
        """
        raise NotImplementedError

    def get_ohlcv_by_date_string(self, date_string: str, end_date_string: str = None) -> pd.DataFrame:
        """
        Get the most recent OHLCV record for a given filled_date string. If end_date_string is provided, it returns all records
        within the range. date_string should be in YYYY-MM-DD or YYYY-MM-DD HH format. Currently, only support day and
        hour level. Range is [start, end).
        :param date_string: If end_date_string is provided, it's a snapshot filled_date string, otherwise it's the start filled_date
        string.
        :param end_date_string: It's the end filled_date string if provided.
        :return:
        """
        start_ts = pd.to_datetime(date_string, utc=True)
        end_ts = pd.to_datetime(end_date_string, utc=True) if end_date_string else None

        if end_ts:
            condition = (self.data["ts_event"] >= start_ts) & (self.data["ts_event"] < end_ts)
            return self.data[condition]
        else:
            condition = self.data["ts_event"] >= start_ts
            if sum(condition) > 0:
                return self.data[condition].iloc[0]
            else:
                raise Exception("No data found.")

    def _get_symbol(self) -> str:
        """
        Get the symbol of the ticker.
        :return: symbol string.
        """
        return self.data.iloc[0]["symbol"]