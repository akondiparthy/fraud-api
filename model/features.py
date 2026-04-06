import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    features = df.copy()
    features['amount_log'] = np.log1p(features['Amount'])
    features['hour_of_day'] = (features['Time'] % 86400) / 3600
    features['is_night'] = (
        (features['hour_of_day'] < 5) | (features['hour_of_day'] > 22)
    ).astype(int)
    features['is_round_amount'] = (features['Amount'] % 10 < 0.01).astype(int)
    features['is_micro_txn'] = (features['Amount'] < 1.0).astype(int)
    features['is_high_value'] = (features['Amount'] > 500).astype(int)
    features = features.drop(columns=['Time', 'Amount'])
    return features