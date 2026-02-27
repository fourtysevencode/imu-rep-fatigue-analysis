# IMU Rep Fatigue Analysis

Automated rep segmentation and fatigue scoring from smartphone IMU data.

This repository provides a complete signal processing pipeline that
takes accelerometer data from a phone, detects exercise repetitions
(reps), extracts meaningful features per rep, and computes a fatigue
score for each rep in a workout set.

It is designed to serve as a modular foundation for research, wearable
fitness analytics, and future machine learning integration.

------------------------------------------------------------------------

## Motivation

Repetition-based workouts (e.g., squats, push-ups) exhibit measurable
changes in motion patterns as fatigue increases. With only IMU data from
a device (such as a phone or smartwatch), we can quantify these changes
and produce fatigue indicators without relying on manual labeling or
subjective input.

This repository aims to:

-   Provide a reusable signal processing pipeline\
-   Extract interpretable features for each rep\
-   Produce a deterministic fatigue score per rep\
-   Serve as a foundation for future ML models or real-time systems

------------------------------------------------------------------------

## Core Functionality

-   Removes unstable start/end seconds from raw motion data
-   Smooths noisy accelerometer signals
-   Detects rep boundaries using valleys in motion magnitude
-   Computes features per rep:
    -   Rep interval (time between reps)
    -   Rep range (bottom → top movement magnitude)
    -   Rep depth (minimum acceleration magnitude)
-   Normalizes features
-   Computes a simple fatigue score

------------------------------------------------------------------------

## Repository Structure

    imu-rep-fatigue-analysis/
    │
    ├── src/
    │   ├── preprocessing.py           # signal cleanup functions
    │   ├── rep_detection.py           # rep valley detection
    │   ├── feature_extraction.py      # rep feature engineering
    │   ├── fatigue_model.py           # scoring
    │   └── pipeline.py                # single entry point pipeline
    │
    ├── notebooks/                     # experiments and 
    ├── data/                          # example input datasets
    ├── results/                       # generated plots & outputs
    ├── tests/                         # automated unit tests
    ├── requirements.txt               # needed Python libraries
    └── README.md

------------------------------------------------------------------------

## Usage

### 1. Install dependencies

``` bash
pip install -r requirements.txt
```

### 2. Run the pipeline

``` python
from src.pipeline import run_pipeline

rep_df = run_pipeline(
    path="data/squat_25_reps.csv",
    set_id=1,
    exercise="squat",
    age=28,
    date="24-02-2026"
)

print(rep_df.head())
```

This returns a DataFrame with one row per rep, including:


  rep_in_set |  rep_interval |  rep_depth |  range_a  |  norm_time  | norm_range |  fatigue

------------------------------------------------------------------------

## Output Interpretation

-   rep_interval --- time duration between consecutive reps
-   rep_depth --- acceleration magnitude at the bottom of the rep
-   range_a --- acceleration range (bottom → maximum)
-   norm_time / norm_range --- normalized features
-   fatigue --- combined indicator that tends to increase as reps
    progress

A typical plot may show gradual increases in normalized features,
indicating growing fatigue.

------------------------------------------------------------------------

## Testing

Automated tests ensure correct feature extraction and stable behavior:

``` 
pytest
```

Tested modules include:

-   compute_range\
-   compute_rep_intervals\
-   Rep detection sanity checks\
-   Pipeline integration

------------------------------------------------------------------------

## Future Directions

This system is intentionally modular and can be extended in several
directions.

### Machine Learning

Train models to classify fatigue levels, rep failure, etc instead of using a hand-built
formula.

### Wearable Integration

Port feature extraction to a real-time Wear OS or smartwatch
application. -- in progress*

### Personalization

Adapt fatigue scoring per user based on body metrics or historical
performance.

### Visualization

Add dashboards (e.g., Streamlit or Plotly) for interactive performance
analytics.

------------------------------------------------------------------------

## Contributing

Contributions are welcome. Possible improvements include:

-   Supporting additional exercises
-   Improving segmentation robustness
-   Adding new fatigue indicators
-   Integrating ML-based classification

------------------------------------------------------------------------

## License

MIT License --- open for academic and personal use.

------------------------------------------------------------------------

This project focuses on clear signal processing, reproducibility, and
extensibility. It is intended as a foundation for wearable motion
analysis and fatigue estimation systems.

** AI aided in the writing of only this README
