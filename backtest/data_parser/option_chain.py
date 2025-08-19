"""
File: option_chain.py
Author: Zhicheng Tang
Created Date: 08/12/25
Description: a wrapper for an option chain dataframe, providing convenient query methods.
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional
from ..utils.instrument import Option


class OptionChain:
    def __init__(self, data: pd.DataFrame):
        data["quote_date"] = pd.to_datetime(data["quote_date"])
        data["expiration"] = pd.to_datetime(data["expiration"])
        data["DTE"] = (data["expiration"] - data["quote_date"]).dt.days

        self.data = data
        self.underlying_symbol = self.data.iloc[0]["underlying_symbol"]

    def get_chain_by_date(self, date_string: str) -> pd.DataFrame:
        """
        Gets the full option chain for a specific trading day.
        :param date_string: The date to retrieve, in 'YYYY-MM-DD' format.
        :return: A DataFrame containing all options for that day.
        """
        target_date = pd.to_datetime(date_string)
        # We use .dt.date to compare only the date part, ignoring time
        condition = self.data['quote_date'].dt.date == target_date.date()
        result = self.data[condition]
        
        if result.empty:
            print(f"Warning: No data found for date {date_string}. Check if it's a trading day.")
            
        return result
    
    def get_full_chain(self) -> pd.DataFrame:
        """
        Returns the entire underlying DataFrame.
        """
        return self.data

    def get_instrument_price(self, date_string: str, instrument: Option) -> float:
        target_date = pd.to_datetime(date_string)
        daily_chain = self.get_chain_by_date(date_string)
        if daily_chain.empty:
            if target_date > instrument.expiration_date:
                close_price = 0
            else:
                print(f"Warning: No option chain data for {self.underlying_symbol} on {target_date}.")
        else:
            target_expiry = pd.to_datetime(instrument.expiration_date)
            option_row = daily_chain
            specific_option_row = daily_chain[
                (daily_chain['strike'] == instrument.strike_price) &
                (daily_chain['expiration'] == target_expiry) &
                (daily_chain['option_type'] == instrument.option_type.value)
                ]
            if not specific_option_row.empty:
                return (specific_option_row.iloc[0]['ask_eod'] + specific_option_row.iloc[0]['bid_eod']) / 2
            else:
                print(f"Warning: Could not find specific contract in data on {target_date}, strike "
                      f"{instrument.strike_price}, expiry: {target_expiry}, type: {instrument.option_type.value}")

        return None

