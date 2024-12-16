"""
File: sampling
Author: Zhicheng Tang
Created Date: 12/14/24
Description: <This file includes sampling methods for machine learning models.>
"""
from datetime import datetime

import numpy as np
import pandas as pd


def exponential_time_weighted_samping(df: pd.DataFrame, exp_weight: float) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["ts_event"]).dt.tz_localize(None)
    current_time = datetime.now()
    t_diff = (current_time - df["timestamp"]).dt.total_seconds() // (24 * 60 * 60)

    df["weight"] = exponential_weight(t_diff, exp_weight)
    sample_size = int(df["weight"].sum())
    return df.sample(sample_size, weights="weight").sort_values(by="ts_event", ascending=True).drop(columns=["weight", "timestamp"], axis=1)


def exponential_weight(time_delta: pd.Series, alpha: float) -> pd.Series:
    return np.exp(-alpha * time_delta)
