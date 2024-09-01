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
            raise NotImplementedError("Not implemented yet")
        elif frequency == FREQUENCY.MINUTE:
            print("Does not support minute level data.")
            raise NotImplementedError("Not implemented yet")
        elif frequency == FREQUENCY.SECOND:
            print("Does not support second level data.")
            raise NotImplementedError("Not implemented yet")
        else:
            raise ValueError(f"Invalid frequency: {frequency}.")

        return df

    @staticmethod
    def resample_ohlcv(df: pd.DataFrame, original_freq: FREQUENCY, target_freq: FREQUENCY) -> pd.DataFrame:
        """
        Resamples ohlcv from higher frequency to lower frequency.
        :param df: dataframe to be resampled.
        :param original_freq: original frequency.
        :param target_freq: target frequency
        :return: resampled dataframe.
        """
        raise NotImplementedError("Not implemented yet")


