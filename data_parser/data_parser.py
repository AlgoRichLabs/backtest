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
            df["timestamp"] = pd.to_datetime(df["ts_event"])
            condition = ((df['timestamp'].dt.hour >= 13) & (df['timestamp'].dt.hour <= 20))
            df = df.loc[condition].drop(columns=["timestamp"])
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
        if original_freq == FREQUENCY.HOUR and target_freq == FREQUENCY.DAY:
            resampled_df = df.copy()
            resampled_df["datetime"] = pd.to_datetime(resampled_df["ts_event"])
            resampled_df.set_index('datetime', inplace=True)
            resampled_df = resampled_df.resample("D").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum"
            }).dropna()

            resampled_df["symbol"] = df["symbol"].iloc[0]
            resampled_df["rtype"] = df["rtype"].iloc[0]
            resampled_df["instrument_id"] = df["instrument_id"].iloc[0]
            resampled_df["publisher_id"] = df["publisher_id"].iloc[0]
            resampled_df = resampled_df.reset_index().rename(columns={"datetime": "ts_event"})
            resampled_df["ts_event"] = resampled_df["ts_event"].astype(str)
            return resampled_df


        raise NotImplementedError("Not implemented yet")


