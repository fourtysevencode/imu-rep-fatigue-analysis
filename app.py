import streamlit as st
import pandas as pd
import numpy as np
import datetime
from src.pipeline import run_pipeline

st.set_page_config(page_icon="💪", page_title="Squat Rep Detection")

st.header("Squat Rep & Fatigue Detection")

data = st.file_uploader(label="Upload a csv")

if st.button("Detect"):
    if data:
        with st.spinner("Calculating..."):

            df = run_pipeline(data, 1, "squat", 16, datetime.date.today())
            st.dataframe(df)