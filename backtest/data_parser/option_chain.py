"""
File: option_chain.py
Author: Zhicheng Tang
Created Date: 08/12/25
Description: a wrapper for an option chain dataframe, providing convenient query methods.
"""
import pandas as pd


class OptionChain:
    def __init__(self, data: pd.DataFrame):
        data["quote_date"] = pd.to_datetime(data["quote_date"])
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