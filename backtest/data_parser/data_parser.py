"""
File: data_parser.py
Author: Zhicheng Tang
Created Date: 8/24/24
Description: <This class parses the raw data into the format that strategy and backtest could use.>
"""
from typing import List
import pandas as pd
import os

from ..utils.constant import FREQUENCY


class DataParser(object):
    """
    A collection of static methos to parse and process financial data.
    """


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

    @staticmethod
    def align_return(alpha_close: pd.DataFrame, forward_periods: int) -> pd.DataFrame:
        """
        :param alpha_close: feature with the close price.
        :param forward_periods: the forward period used to compute return.
        :return: dataframe of ts_event, feature and return.
        """
        df = alpha_close.copy()
        factor_name = alpha_close.columns[1]
        df["return"] = df["close"].pct_change(periods=forward_periods)
        df["return"] = df["return"].shift(-forward_periods)
        return df.dropna().loc[:, ["ts_event", factor_name, "return"]]

    @staticmethod
    def merge_features_binary(feature_lst: List[pd.DataFrame], df: pd.DataFrame, forward_periods: int) -> pd.DataFrame:
        """
        :param feature_lst: list of features in dataframe format.
        :param df: the original ohlcv dataframe.
        :param forward_periods: period of the forward return.
        :return: features and the target.
        """
        feature_lst = feature_lst.copy()
        for i in range(len(feature_lst)):
            feature_lst[i] = DataParser.align_return(feature_lst[i].merge(df, on="ts_event", how="inner"), forward_periods)

        results = feature_lst.pop()

        for feature in feature_lst:
            results = results.merge(feature, on=["ts_event", "return"], how="inner")

        positive_return = results["return"] > 0
        results.loc[positive_return, "label"] = 1
        results.loc[~positive_return, "label"] = 0

        cols = ["ts_event"] + list(results.drop(columns=["ts_event", "return", "label"]).columns) + ["return", "label"]
        results = results.loc[:, cols]
        print("Feature with forward return range:")
        print(results.head(1)["ts_event"].values[0], results.tail(1)["ts_event"].values[0])
        return results

    @staticmethod
    def process_option_chain(data_path: str, underlying_symbol: str) -> pd.DataFrame:
        """
        Reads all option chain CSVs for a specific symbol from a directory,
        merge and reformats them to a CBOE-like option EOD summary schema.
        https://datashop.cboe.com/option-eod-summary

        This function is not used by any backtest class. It is used manually to process the raw option
        chain data which is not in CBOE format. It only needs to be used once.
        """
        print(f"Starting to parse option data for {underlying_symbol} from {data_path}")

        COLUMN_MAPPING = {
            'Trade Date': 'quote_date',
            'Strike': 'strike',
            'Expiry Date': 'expiration',
            'Call/Put': 'option_type',
            'Last Trade Price': 'close',
            'Bid Price': 'bid_eod',
            'Ask Price': 'ask_eod',
            'Bid Implied Volatility': 'bid_iv', # Temp name before averaging
            'Ask Implied Volatility': 'ask_iv', # Temp name before averaging
            'Open Interest': 'open_interest',
            'Volume': 'trade_volume',
            'Delta': 'delta_eod',
            'Gamma': 'gamma_eod',
            'Vega': 'vega_eod',
            'Theta': 'theta_eod',
            'Rho': 'rho_eod'
        }

        # Define the final column order, matching the CBOE structure
        FINAL_COLUMNS = [
            'underlying_symbol', 'quote_date', 'expiration', 'strike', 'option_type',
            'open', 'high', 'low', 'close', 'trade_volume', 'vwap',
            'bid_eod', 'ask_eod', 'bid_size_eod', 'ask_size_eod',
            'implied_volatility_eod', 'delta_eod', 'gamma_eod', 'theta_eod', 'vega_eod', 'rho_eod',
            'open_interest'
        ]
        resolved_path = os.path.expanduser(data_path)
        if not os.path.isdir(resolved_path):
            raise FileNotFoundError(f"Directory not found at the specified path: {os.path.abspath(resolved_path)}")

        all_files_in_dir = os.listdir(resolved_path)
        pattern_start = f'{underlying_symbol}_'.lower()
        pattern_end = '_option_chain.csv'.lower()
        
        matched_files = []
        for filename in all_files_in_dir:
            if filename.lower().startswith(pattern_start) and filename.lower().endswith(pattern_end):
                # If it matches, create the full path to the file
                matched_files.append(os.path.join(resolved_path, filename))

        if not matched_files:
            raise FileNotFoundError("No option data found")

        processed_dfs = []

        for file_path in matched_files:
            df = pd.read_csv(file_path)

            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])

            df.rename(columns=COLUMN_MAPPING, inplace=True)
            df['quote_date'] = pd.to_datetime(df['quote_date'])
            df['expiration'] = pd.to_datetime(df['expiration'])

            df['option_type'] = df['option_type'].str.upper().str[0]

            df["underlying_symbol"] = underlying_symbol

            # --- Create CBOE columns that are missing from the current data source ---
            df['open'] = pd.NA
            df['high'] = pd.NA
            df['low'] = pd.NA
            df['vwap'] = pd.NA
            df['bid_size_eod'] = pd.NA
            df['ask_size_eod'] = pd.NA


            # Create a single 'implied_volatility_eod' from the bid/ask IV by taking the midpoint.
            df['implied_volatility_eod'] = df[['bid_iv', 'ask_iv']].mean(axis=1)
            df = df[FINAL_COLUMNS]
            processed_dfs.append(df)

        final_df = pd.concat(processed_dfs, ignore_index=True)
        final_df.sort_values(by=['quote_date', 'expiration', 'strike'], inplace=True)
        return final_df

    @staticmethod
    def read_option_chain(path: str) -> pd.DataFrame:
        """
        Currently, do not expect to read higher frequency option data in the near future.
        """
        return pd.read_csv(f"{path}/option-day.csv")
