import pandas as pd
import numpy as np

def compute_magnitude(df):
    df["a_mag"] = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)
    return df

def load_csv(path):
    return pd.read_csv(path)

def trim_edges(df, seconds = 1.0):
    time = df['time'].values
    mask = (time>= seconds) & (time <= time[-1] - seconds) # removes 'seconds' from beginning and end
    return df[mask].reset_index(drop=True)

def smooth_signal(signal, window = 5):
    return np.convolve(signal, np.ones(window)/window, mode = 'same')

