def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def compute_fatigue(set_df):
    set_df['norm_time'] = normalize(set_df['rep_interval'])
    set_df['norm_range'] = 1 - normalize(set_df['range_a'])
    set_df['fatigue_score'] = set_df['norm_time'] + set_df['norm_range']
    return set_df
