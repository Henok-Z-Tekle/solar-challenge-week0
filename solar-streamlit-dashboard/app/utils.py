
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

def load_local_csvs(data_dir: str | Path) -> Dict[str, pd.DataFrame]:
    """Load all CSVs under data_dir into a dict keyed by stem (e.g., 'benin')."""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return {}
    csvs = list(data_dir.glob("*.csv"))
    frames: Dict[str, pd.DataFrame] = {}
    for p in csvs:
        try:
            df = pd.read_csv(p)
            frames[p.stem.lower()] = df
        except Exception as e:
            # Skip unreadable files but continue
            print(f"Failed reading {p}: {e}")
    return frames

def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return numeric columns; used to auto-detect metrics like GHI, DNI, etc."""
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip spaces/illegal chars for consistency."""
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w_]+", "", regex=True)
        .str.lower()
    )
    return df

def compute_zscores(df: pd.DataFrame, cols: List[str], zcut: float = 3.0) -> pd.DataFrame:
    """Compute z-scores for selected columns and flag outliers with |z| > zcut."""
    out = df.copy()
    for c in cols:
        if c not in out.columns or not pd.api.types.is_numeric_dtype(out[c]):
            continue
        mu = out[c].mean()
        sd = out[c].std(ddof=0)
        if sd == 0 or np.isnan(sd):
            out[f"{c}_z"] = np.nan
            out[f"{c}_is_outlier"] = False
        else:
            z = (out[c] - mu) / sd
            out[f"{c}_z"] = z
            out[f"{c}_is_outlier"] = z.abs() > zcut
    return out

def summarize_metric(df: pd.DataFrame, metric: str, groupby: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    """Return a table of top groups by mean metric (descending)."""
    if metric not in df.columns:
        return pd.DataFrame()
    if groupby and groupby in df.columns:
        agg = (df.groupby(groupby)[metric]
               .agg(['count','mean','median','std','min','max'])
               .sort_values('mean', ascending=False)
               .head(top_n)
               .reset_index())
    else:
        # no grouping, just overall stats in one row
        agg = df[metric].agg(['count','mean','median','std','min','max']).to_frame().T
    return agg

COMMON_REGION_KEYS = ["region", "state", "province", "zone", "area", "subregion", "city", "location"]

def guess_region_column(df: pd.DataFrame) -> Optional[str]:
    for key in COMMON_REGION_KEYS:
        if key in df.columns:
            return key
    # try fuzzy match for typical naming like 'region_name'
    for c in df.columns:
        if any(k in c for k in COMMON_REGION_KEYS):
            return c
    return None
