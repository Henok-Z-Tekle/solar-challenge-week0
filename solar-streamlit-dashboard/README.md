# Solar Data Interactive Dashboard (Streamlit)

A **code-only** Streamlit dashboard that reads CSVs from a local `data/` folder (git-ignored) or via file upload at runtime. 
It visualizes common solar metrics such as **GHI, DNI, DHI**, module sensors (**ModA**, **ModB**), and wind (**WS, WSgust**).
Includes:
- Dataset selector (per CSV file)
- Metric picker
- Optional grouping (e.g., by `region`)
- Box plot distribution
- Summary table (count/mean/median/std/min/max) and “Top regions” by mean
- Outlier detection via z-scores (|z| > threshold)

## Folder Structure
```
.
├── app
│   ├── __init__.py
│   ├── main.py          # Streamlit UI
│   └── utils.py         # Data helpers (loading, cleaning, z-scores, summaries)
├── data/                # Put your CSVs here (ignored by git)
├── scripts
│   ├── __init__.py
│   └── README.md
├── .gitignore
├── requirements.txt
└── README.md
```

## Local Run
```bash
# 1) (optional) create & activate venv
python -m venv .venv
# Windows PowerShell:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 2) install deps
pip install -r requirements.txt

# 3) (optional) add your CSVs under data/
#    or just upload via the sidebar when the app is running

# 4) start the app
streamlit run app/main.py
```

## Expected CSV Columns
The app will auto-detect numeric columns and guess a region column, but for best results keep column names simple:
```
date, region, ghi, dni, dhi, moda, modb, ws, wsgust
```
Column names are normalized (lowercased, spaces removed) on load.

## Deploy to Streamlit Community Cloud
1. Push this folder as a GitHub repo (e.g., `solar-dashboard`).
2. Go to **https://share.streamlit.io** (or *New app* in Streamlit Community Cloud).
3. Select your repo and set **Main file path** to `app/main.py`.
4. Ensure **Python version** >= 3.10 and `requirements.txt` is present.
5. Deploy. On first run, upload your CSVs from the sidebar, or add them to the repo later if you’re fine committing sample data.

## KPIs Check
- **Dashboard Usability:** clear labels, sidebar data uploader, and simple defaults.
- **Interactive Elements:** dataset & metric selectors, grouping, outlier toggle, dynamic tables.
- **Visual Appeal:** modern Plotly charts and wide layout.
- **Deployment Success:** designed for Streamlit Community Cloud; no private data required.

## Notes
- Data is intentionally **not** included. Keep your proprietary CSVs locally under `data/`.
- If you need reproducible demo data, add a small anonymized CSV to `data/` on a dev branch (do not include sensitive info).