
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from typing import Dict
from .utils import (
    load_local_csvs,
    detect_numeric_columns,
    standardize_column_names,
    compute_zscores,
    summarize_metric,
    guess_region_column,
)

st.set_page_config(page_title="Solar Data Dashboard", page_icon="🔆", layout="wide")

@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, pd.DataFrame]:
    # Load from local data/ if present
    local = load_local_csvs(Path(__file__).resolve().parents[1] / "data")
    return {k: standardize_column_names(v) for k, v in local.items()}

def load_uploaded(uploaded_files) -> Dict[str, pd.DataFrame]:
    frames = {}
    for uf in uploaded_files:
        try:
            df = pd.read_csv(uf)
            frames[Path(uf.name).stem.lower()] = standardize_column_names(df)
        except Exception as e:
            st.warning(f"Failed to read {uf.name}: {e}")
    return frames

def sidebar_sources(local_frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    st.sidebar.header("Data Sources")
    st.sidebar.caption("• Place CSVs in the `data/` folder **or** upload here.\n• Columns such as `ghi`, `dni`, `dhi`, `moda`, `modb`, `ws`, `wsgust` are supported.")
    uploaded = st.sidebar.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)
    frames = dict(local_frames)
    frames.update(load_uploaded(uploaded) if uploaded else {})
    if not frames:
        st.info("No datasets found. Add CSVs to the `data/` folder or upload them from the sidebar.")
    return frames

def main():
    st.title("🔆 Solar Data Interactive Dashboard")
    st.write("Analyze and compare solar datasets across countries. Select a dataset, choose a metric, and interact with the plots and tables.")

    local_frames = load_data()
    frames = sidebar_sources(local_frames)

    if not frames:
        st.stop()

    country = st.selectbox("Dataset", options=sorted(frames.keys()))
    df = frames[country].copy()

    numeric_cols = detect_numeric_columns(df)
    default_metric = None
    for pref in ["ghi","dni","dhi","moda","modb","ws","wsgust"]:
        if pref in df.columns:
            default_metric = pref
            break

    metric = st.selectbox("Metric", options=numeric_cols, index=(numeric_cols.index(default_metric) if default_metric in numeric_cols else 0))

    region_col_guess = guess_region_column(df)
    group_choice = st.selectbox("Group by (optional)", options=["(none)"] + [c for c in df.columns if c != metric],
                                index=(0 if region_col_guess is None else (1 + [c for c in df.columns if c != metric].index(region_col_guess))))

    # Basic cleaning options
    st.subheader("Cleaning & Outliers")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        dropna = st.checkbox("Drop rows with NA in selected metric", value=True)
    with col2:
        zcut = st.slider("Outlier threshold (|z| > ...)", min_value=2.0, max_value=5.0, value=3.0, step=0.5)
    with col3:
        show_outliers = st.checkbox("Highlight outliers", value=True)

    if dropna:
        df = df[df[metric].notna()]

    dfz = compute_zscores(df, [metric], zcut=zcut)

    # Box plot
    st.subheader("Distribution")
    if group_choice != "(none)":
        fig = px.box(dfz, x=group_choice, y=metric, points="suspectedoutliers" if show_outliers else False,
                     title=f"Distribution of {metric} by {group_choice}")
    else:
        fig = px.box(dfz, y=metric, points="suspectedoutliers" if show_outliers else False,
                     title=f"Distribution of {metric}")
    st.plotly_chart(fig, use_container_width=True)

    # Summary stats / Top regions
    st.subheader("Summary & Top Regions")
    groupby = None if group_choice == "(none)" else group_choice
    top = summarize_metric(dfz, metric, groupby=groupby, top_n=20)
    if not top.empty:
        st.dataframe(top, use_container_width=True)
    else:
        st.info("No summary available for the current selection.")

    # Raw preview
    with st.expander("Preview cleaned data"):
        st.write(dfz.head(50))

    st.caption("Tip: add more CSVs to the `data/` folder or upload them from the sidebar to compare additional countries.")

if __name__ == '__main__':
    main()
