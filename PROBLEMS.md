# PROBLEMS

Known problems in `imu-rep-fatigue-analysis`, found by reading the code and running `run_pipeline` on the three datasets in `Data/`. Ordered roughly by impact.

Sampling rate across all three recordings is about 394 Hz (derived from the `time` column).

---

## 1. Rep detection over-counts (critical)

Because fatigue features are computed per detected rep, wrong rep counts make every downstream number unreliable.

| Dataset | Expected reps | Pipeline reports | Typical gap between "reps" |
|---|---|---|---|
| `30 squat reps, male, 16.csv` | 30 (from filename) | 71 | about 0.2 s |
| `Squa_mother_49.csv` | 25 (from notebook name) | 38 | mixed, 0.2 to 3.3 s |
| `squats_phone.csv` | unknown | 20 | mixed |

A 0.2 s gap is not physically plausible for squats, so the friend dataset is being double and triple counted.

### 1a. Parameters are in samples, not seconds
- `smooth_signal(window=5)` is about 13 ms at 394 Hz, which barely smooths anything.
- `detect_valleys(distance=70)` is about 0.18 s, so the refractory period is far shorter than a squat.
- The code never reads the sampling rate from the data, so results change if the device or sample rate changes.
- Quick test on the friend file: a ~0.06 s smoothing window with a 0.5 to 0.8 s minimum spacing gives 25 to 27 reps, much closer to 30.

### 1b. `src/` does not match the notebooks it came from
| Setting | Notebooks | `src/` |
|---|---|---|
| Smoothing window | 25 | 5 |
| Edge trim | first 3 s, last 2 s | 1 s each side |
| Height filter on valleys | yes (`-8.0` or `-7.0`) | none (`height=None`) |
| Peak distance | 10 or 70 | 70 |

The tuning from the notebooks was lost in the refactor. The notebooks also disagree with each other.

### 1c. Prominence threshold is tuned to one dataset
- `prominence=5.4` is absolute. The friend signal has a standard deviation of about 7.8, while the mother and self signals are about 1.6.
- On the quieter recordings the threshold is close to the signal's own spread, so counts swing a lot with small parameter changes. On the self file, counts ranged from 10 to 21 across reasonable settings.
- It should scale with each set's spread instead of being a constant.

### 1d. Smoothing choice
- A moving average (`np.convolve(..., mode='same')`) has edge artifacts and a poor frequency response.
- A zero-phase Butterworth low-pass (`scipy.signal.butter` and `sosfiltfilt`) would be better.

### 1e. Magnitude discards direction
- `a_mag` includes gravity and loses which axis the squat moves along.
- Using the vertical or gravity-projected axis would likely separate descent and ascent more cleanly.

---

## 2. Fatigue score shows no usable signal

Correlation of `fatigue_score` with `rep_in_set`:

| Dataset | Correlation |
|---|---|
| friend | 0.01 |
| self | -0.06 |
| mother | 0.42 |

- The mother result is driven by a jump in `rep_interval` around rep 10, from about 0.5 s to 2+ s. That looks like a pause or tempo change, not fatigue.
- Because reps are miscounted (problem 1), this cannot be judged yet. Fixing detection comes first.
- There is no ground truth (RPE, reps-in-reserve, or rep-failure labels), so the score cannot be validated against anything.

---

## 3. Feature extraction bugs and design issues

### 3a. First `rep_interval` is an absolute timestamp
`compute_rep_intervals` sets the first interval to `time_stamp.iloc[0]`, which is the time since recording start (including setup time and the trimmed offset), not a rep duration. It is then included in min-max normalization, so it can distort the whole `norm_time` column. In the friend set it is 1.13 s against a typical 0.2 to 0.3 s.

### 3b. Interval and range are misaligned
- `rep_interval[i]` is the gap before valley `i`.
- `range_a[i]` covers the movement from valley `i` to valley `i+1`, which is after it.
- The pipeline drops the last interval and the last valley to make the lengths match, but each row still combines "time before this rep" with "range after this rep".

### 3c. Valley-to-valley time is not rep duration
It includes rest between reps. In the mother and self data, long gaps are likely rests or pauses and get scored as fatigue.

### 3d. `rep_depth` is not used in the score
It is computed and returned but never contributes to `fatigue_score`.

### 3e. Eccentric and concentric phases are not separated
Related work found that eccentric rep time was the strongest predictor of perceived exertion. Splitting each rep into down and up phases would likely be more informative than one interval.

---

## 4. Fatigue model design (`src/fatigue_model.py`)

- **Per-set min-max normalization.** Every set is stretched to span 0 to 1 per feature, so a set with no real fatigue still shows a "least fatigued" and "most fatigued" rep. Scores cannot be compared between sets or users.
- **Divide by zero.** `normalize` has no guard when `max == min`, which gives NaN or inf (for example, a very short set or constant feature).
- **Unbounded meaning.** The score is a plain sum of two normalized features, so it ranges 0 to 2 with no justification for equal weights.
- **Not a trend measure.** It scores each rep independently. A slope or rolling trend of rep time and range across the set would be more meaningful than comparing to the set's own min and max.
- **No smoothing.** One noisy rep can dominate.

---

## 5. Pipeline and code issues (`src/`)

- `run_pipeline` re-reads the CSV itself and ignores `load_csv` from `preprocessing.py`.
- `compute_magnitude`, `load_csv`, and `detect_peaks` are unused. `compute_magnitude` is commented out in the pipeline and is only needed if `a_mag` is absent; the pipeline crashes with `KeyError` in that case unless the user edits the code.
- `trim_edges` assumes the `time` column starts near 0, and returns an empty DataFrame for recordings shorter than 2 s, which then fails in later steps.
- `set_size`, `age`, `exercise`, and `date` are metadata that nothing uses. Age is hard-coded in the app.
- `pd.to_datetime(date, dayfirst=True)` is applied to whatever is passed in, including a `datetime.date` from the app, which is inconsistent.
- No input validation: missing columns, empty files, or zero detected valleys all produce confusing errors rather than clear messages.
- No type hints or docstrings on most public functions.
- Column naming drifts: the code returns `fatigue_score` but the README documents `fatigue`.

---

## 6. App problems (`app.py`)

- Age is hard-coded to 16 and set id to 1, regardless of who uploaded the data.
- Clicking **Detect** with no file uploaded does nothing, with no message.
- No error handling around `run_pipeline`; a malformed CSV shows a raw traceback.
- No plot of the signal and detected valleys, so a user cannot see whether detection worked.
- The file extension is not checked.

---

## 7. README does not match the repo

- Refers to `data/`, `results/`, and `tests/`; the repo has `Data/` and no `results/` or `tests/`.
- Says automated tests exist and lists tested modules (`compute_range`, `compute_rep_intervals`, and so on), but there are no tests. `pytest` will find nothing.
- The usage example points to `data/squat_25_reps.csv`, which does not exist.
- Documents a `fatigue` column, but the code produces `fatigue_score`.
- Describes "removes unstable start/end seconds" and other behavior without stating the parameters used or that they differ from the notebooks.
- The stated claim that the score "tends to increase as reps progress" is not supported by the results above.
- The Wear OS / wearable integration is listed as "in progress" with no code in the repo.

---

## 8. Reproducibility and project hygiene

- `requirements.txt` has no version pins (and the README mentions Plotly, which is not listed).
- `.gitignore` only covers `__pycache__`.
- Notebooks use Colab paths (`/content/drive/MyDrive/Gym tracker/...`) and will not run elsewhere.
- Notebook outputs are committed (the notebook files are about 0.2 to 0.7 MB each), which makes diffs noisy.
- There is no LICENSE file, even though the README states MIT.
- Raw recordings from named individuals (including family members, with ages and sex in filenames or notebooks) are committed to the repo. Consider whether consent and privacy are covered before making the repo public.
- Three datasets with no documented protocol: no description of phone placement, exercise load, rest instructions, or how the "expected" rep counts were obtained.
- The data has only three recordings from three people, so the pipeline has no real test set.

---

## Suggested fix order

1. Convert all parameters to seconds, read the sampling rate from `time`, and use a zero-phase low-pass filter.
2. Make prominence relative to each set's spread.
3. Add ground-truth rep counts per file and a test that fails if the detected count is off by more than one or two.
4. Fix the first-interval bug and the interval/range alignment.
5. Replace min-max sums with a trend-based score, and guard against zero range.
6. Collect labelled data (RPE or reps-in-reserve) to validate the score.
7. Bring the README, requirements, notebooks, and app in line with the code.
