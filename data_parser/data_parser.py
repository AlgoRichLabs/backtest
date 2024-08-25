"""
File: data_parser.py
Author: Zhicheng Tang
Created Date: 8/24/24
Description: <This class parses the raw data into the format that strategy and backtest could use.>
"""
import pandas as pd
from utils.constant import FREQUENCY


class DataParser(object):
    @staticmethod
    def read_ohlcv(data_path: str, frequency: FREQUENCY) -> pd.DataFrame:
        if frequency == FREQUENCY.HOUR:
            df = pd.read_csv(f'{data_path}/ohlcv-{frequency.value}.csv')
        elif frequency == FREQUENCY.DAY:
            print("Resampling methods not implemented.")
            raise Exception("Not implemented yet")
        elif frequency == FREQUENCY.MINUTE:
            print("Does not support minute level data.")
            raise Exception("Not implemented yet")
        elif frequency == FREQUENCY.SECOND:
            print("Does not support second level data.")
            raise Exception("Not implemented yet")
        else:
            raise ValueError(f"Invalid frequency: {frequency}.")

        return df


