from preprocessing import load_csv, compute_magnitude, trim_edges, smooth_signal
from rep_detection import detect_valleys
from feature_extraction import compute_rep_intervals, compute_range
from fatigue_model import compute_fatigue
import pandas as pd

def run_pipeline(path, set_id, exercise, age, date):
    df = load_csv(path)
    #df = compute_magnitude(df)   -- uncomment if a_mag not present in df
    df = trim_edges(df)

    df["a_smooth"] = smooth_signal(df["a_mag"])

    valleys = detect_valleys(df["a_smooth"])

    intervals = compute_rep_intervals(df["time"].values, valleys)

    ranges = compute_range(valleys, df['a_smooth'.values])

    intervals = intervals[:-1] #drop last interval, last valley doesn't correspond to any range

    rep_df = pd.DataFrame({
        # metadata
        "set_id": set_id,
        "set_size": len(ranges),
        "exercise": exercise,
        "age": age,
        "date": pd.to_datetime(date, dayfirst = True),
        #features
        "rep_in_set": range(1, len(intervals)+1),
        "rep_interval": intervals[:-1], 
        "rep_depth": df['a_smooth'][valleys],
        "range_a": ranges
    })

    rep_df = compute_fatigue(rep_df)

    return rep_df