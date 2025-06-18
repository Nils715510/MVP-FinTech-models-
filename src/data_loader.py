import pandas as pd

def load_borrowers(path='data/sample_borrowers.csv'):
    return pd.read_csv(path)

def load_lenders(path='data/sample_lenders.csv'):
    return pd.read_csv(path)
