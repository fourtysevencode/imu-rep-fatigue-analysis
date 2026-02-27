from scipy.signal import find_peaks

def detect_valleys(a_smooth, distance = 70, height = None, prominence = 5.4):
    valleys,_ = find_peaks(-a_smooth, distance = distance, height = height, prominence = prominence) # peaks to valleys with -ve
    return valleys

def detect_peaks(a_smooth, distance = 70, height = None, prominence = 5.4):
    peaks,_ = find_peaks(a_smooth, distance = distance, height = height, prominence = prominence) # peaks to valleys with +ve
    return peaks