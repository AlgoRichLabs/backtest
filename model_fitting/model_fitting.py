"""
File: model_fitting
Author: Zhicheng Tang
Created Date: 12/21/24
Description: <>
"""
from typing import Dict, List
# No need to use process pool executor as the computations are not conducted in Python.
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from datetime import datetime, timedelta
from sklearn.base import clone
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def slice_dataframe(df: pd.DataFrame, start_time: datetime, end_time: datetime) -> pd.DataFrame:
    sliced_df= df.copy()
    sliced_df["timestamp"] = pd.to_datetime(sliced_df["ts_event"])
    condition = (sliced_df["timestamp"] >= start_time) & (sliced_df["timestamp"] <= end_time)
    return sliced_df[condition]


def prepare_data(df: pd.DataFrame, start_time: datetime, end_time: datetime, retrain_freq: timedelta, test_window: timedelta,
                 validation_window: timedelta, min_training_window: timedelta) -> List[List[pd.Index]]:
    """
    :param df:
    :param start_time: start time of the data set.
    :param end_time: end time of the data set.
    :param retrain_freq: the frequency of the model being trained again to accommodate new data.
    :param test_window: the time window of the data set that is held out for measuring the performance of model only.
    :param validation_window: the time window of the data set that is used for hyperparameters tuning.
    :param min_training_window: minimum size of the training data set.
    :return:

    This method is conducting a rolling training process. The model is trained every certain amount of time. For example,
    the model is trained every year, and will be used for the next year. The test window exactly matches the frequency of
    the model training. In the above example, 1 year of the data will be held to test the performance of the model. Besides,
    validation window is another batch of data, used to tune the hyperparameters of the model. The remaining of the data
    will be used to train the model.

    You cannot use future data to train the model. Then tune and test using the data before. Everything should roll
    forward.

    In production, we could use the most recent data to train the model with predefined hyperparameters.

    This model training process is referenced from here:
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4702406#:~:text=Contrary%20to%20claims%20in%20prior,difficult%2Dto%2Darbitrage%20stocks.

    Example:
    start_time = datetime.fromisoformat(df.iloc[0]["ts_event"])
    end_time = datetime.fromisoformat("2024-12-14 00:00:00+00:00")
    retrained_freq = timedelta(days=180)
    test_window = timedelta(days=180)
    validation_window = timedelta(days=365)
    min_training_window = timedelta(days=365 * 2)
    results = prepare_data(df, start_time, end_time, retrained_freq, test_window, validation_window, min_training_window)
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["ts_event"])
    df.sort_values(by=["timestamp"], inplace=True)
    if start_time is None:
        start_time = df.iloc[0]['timestamp']
    df = df[(df["timestamp"] <= end_time) & (df["timestamp"] >= start_time)]
    batch_indices = []
    while (end_time - validation_window - test_window - df.iloc[0]["timestamp"]) > min_training_window:
        test_start_time = end_time - test_window
        test_index = slice_dataframe(df, test_start_time, end_time).index
        validation_start_time = test_start_time - validation_window
        validation_index = slice_dataframe(df, validation_start_time, test_start_time - timedelta(seconds=1)).index
        train_index = slice_dataframe(df, df.iloc[0]["timestamp"], validation_start_time - timedelta(seconds=1)).index
        batch_indices.append([train_index, validation_index, test_index])
        end_time = end_time - retrain_freq
    return batch_indices[::-1]

def fit_model(input_model, feature_forward: pd.DataFrame, indices: List[List[pd.Index]]) -> (pd.DataFrame, pd.DataFrame):
    """
    :param input_model: machine learning model.
    :param feature_forward: dataframe of features and the forward return.
    :param indices: list of [train idx, validation idx, test idx].
    :return: two dataframes. Each has ts_event, model pred, pred_proba and label.
    """
    validation_results = pd.DataFrame({"ts_event": [], "pred": [], "pred_proba": []})
    test_results = pd.DataFrame({"ts_event": [], "pred": [], "pred_proba": []})

    for idx in indices:
        model = clone(input_model)
        train_index, validation_index, test_index = idx
        df_train = feature_forward.loc[train_index]
        df_validation = feature_forward.loc[validation_index]
        df_test = feature_forward.loc[test_index]

        model.fit(df_train.drop(columns=["ts_event", "return", "label"]), df_train["label"])

        validation_result = df_validation[["ts_event"]]
        validation_result["pred"] = model.predict(df_validation.drop(columns=["ts_event", "return", "label"]))
        validation_result["pred_proba"] = model.predict_proba(
            df_validation.drop(columns=["ts_event", "return", "label"]))[:, 1]
        validation_results = pd.concat([validation_results, validation_result], axis=0)

        test_result = df_test[["ts_event"]]
        test_result["pred"] = model.predict(df_test.drop(columns=["ts_event", "return", "label"]))
        test_result["pred_proba"] = model.predict_proba(df_test.drop(columns=["ts_event", "return", "label"]))[:, 1]
        test_results = pd.concat([test_results, test_result], axis=0)

    return validation_results, test_results


def fit_model_parallel(input_model, feature_forward: pd.DataFrame, indices: List[List[pd.Index]]) -> (pd.DataFrame, pd.DataFrame):
    """
    :param input_model: machine learning model.
    :param feature_forward: dataframe of features and the forward return.
    :param indices: list of [train idx, validation idx, test idx].
    :return: two dataframes. Each has ts_event, model pred, pred_proba and label.
    """

    def train(idx):
        model = clone(input_model)
        train_index, validation_index, test_index = idx
        df_train = feature_forward.loc[train_index]
        df_validation = feature_forward.loc[validation_index]
        df_test = feature_forward.loc[test_index]

        model.fit(df_train.drop(columns=["ts_event", "return", "label"]), df_train["label"])

        validation_result = df_validation[["ts_event"]]
        validation_result["pred"] = model.predict(df_validation.drop(columns=["ts_event", "return", "label"]))
        validation_result["pred_proba"] = model.predict_proba(
            df_validation.drop(columns=["ts_event", "return", "label"]))[:, 1]
        # validation_results = pd.concat([validation_results, validation_result], axis=0)

        test_result = df_test[["ts_event"]]
        test_result["pred"] = model.predict(df_test.drop(columns=["ts_event", "return", "label"]))
        test_result["pred_proba"] = model.predict_proba(df_test.drop(columns=["ts_event", "return", "label"]))[:, 1]
        # test_results = pd.concat([test_results, test_result], axis=0)

        return validation_result, test_result

    validation_results, test_results = [], []

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(train, indices))

        for val_result, test_result in results:
            validation_results.append(val_result)
            test_results.append(test_result)

    validation_results_df = pd.concat(validation_results, axis=0)
    test_results_df = pd.concat(test_results, axis=0)

    return validation_results_df, test_results_df

def validate_binary_model(trained_model, df_v: pd.DataFrame):

    pass


def test_model(trained_model, df_test: pd.DataFrame):
    pass


def model_result(y, y_pred_proba, y_pred):
    print("Accuracy:", accuracy_score(y, y_pred))
    print("Precision:", precision_score(y, y_pred))
    print("Recall:", recall_score(y, y_pred))
    print("F1 Score:", f1_score(y, y_pred))
    print("ROC-AUC Score:", roc_auc_score(y, y_pred_proba))
    return y_pred