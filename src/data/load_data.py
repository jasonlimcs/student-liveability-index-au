import pandas as pd
import os

def load_csv(filepath):
    return pd.read_csv(filepath)

def save_csv(df, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)