import numpy as np

def compute_rep_intervals(time_array, valleys):
    time_stamp = time_array[valleys]
    intervals = []
    for i in range(len(time_stamp)):
        intervals.append(time_stamp.iloc[0] if i==0 else time_stamp.iloc[i] - time_stamp.iloc[i-1])
        return intervals

def compute_range(valleys, a_smooth):

    '''one rep is valley to  then next valley, 
       a peak is the max value between the two valleys, 
       range is the difference of that peak and the inital valley.'''

    ranges = []
    for i in range(len(valleys) - 1): # last valley correspons to no peak
        start = valleys[i]
        end = valleys[i+1]
        segment = a_smooth[start:end] # segment of a_smooth values from one valley to the other
        peak = np.max(segment) # max +ve value
        ranges.append(float(peak - a_smooth[start])) # to avoid conficts in position of peaks and valleys
    return ranges