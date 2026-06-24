# ⚡ VoltPath — Electric Rickshaw Fleet Optimizer

> **Charging, Demand, and Downtime Intelligence for Urban Mobility Operators**

A portfolio-grade analytics product simulating how EV fleet operators, infrastructure startups, and city mobility planners can reduce downtime and optimize charging station placement for electric rickshaw fleets in Indian cities.

**Live Demo:** [Voltpath](https://akssyhpky6mnuymtwsce7c.streamlit.app/)

---

## 📸 Screenshots

> _Screenshots below are representative placeholders. Run the app locally to see live visuals._

| Overview Dashboard | City Intelligence Map |
|---|---|
| `<img width="1920" height="877" alt="DA1" src="https://github.com/user-attachments/assets/2c72901b-38c2-46e8-a07a-237bb4d0d4fe" /> |` <img width="1017" height="836" alt="DA3" src="https://github.com/user-attachments/assets/186768ff-8c7f-4f17-9a8d-5675280fc8e8" />
`<img width="1920" height="879" alt="DA2" src="https://github.com/user-attachments/assets/78fc0518-25a6-43cc-be4a-23ab9c2cdf6a" /> |` <img width="1401" height="629" alt="DA10" src="https://github.com/user-attachments/assets/4fb0bdd9-ec4d-4883-8df7-3275f32c406b" /> |


| Fleet Performance | Scenario Simulator |
|---|---|
| `<img width="1470" height="882" alt="DA4" src="https://github.com/user-attachments/assets/dd2a5e27-8f4e-4fba-9b4a-7b44802c1dd2" /> |` <img width="1501" height="858" alt="DA6" src="https://github.com/user-attachments/assets/84eccaf9-fad0-49c0-a6a5-6872f3b4cbd6" />
`<img width="1914" height="860" alt="DA7" src="https://github.com/user-attachments/assets/f6c4daca-8734-457e-801b-bcef9f2d62a3" /> |` <img width="1914" height="873" alt="DA8" src="https://github.com/user-attachments/assets/c02997c3-92d9-4cb7-b198-7188dad76f6b" /> |



---

## 🎯 Business Problem

Electric rickshaw fleets in Indian cities lose **15–25% of potential revenue** to charging-related downtime. The core issues are:

1. **Charger Access Gaps** — Charging stations are concentrated near highways or commercial zones, not near high-demand residential or transit corridors.
2. **Unoptimized Charging Windows** — Vehicles charge during peak earning hours, compounding revenue loss.
3. **No Predictive Visibility** — Fleet operators lack data tools to anticipate which zones will face the worst downtime on a given day.

**VoltPath** addresses these problems through spatial analytics, risk scoring, and ROI-based recommendation logic.

---

## 🏗️ Architecture

```
app.py (Streamlit Entry Point)
├── src/
│   ├── ingestion/
│   │   ├── fetch_chargers.py       # Open Charge Map API + synthetic fallback
│   │   └── generate_synthetic_data.py  # Realistic fleet simulation
│   ├── analysis/
│   │   └── analysis.py             # Scoring, clustering, ROI simulation
│   └── utils/
│       ├── data_loader.py          # Cached Streamlit data loaders
│       └── db_utils.py             # SQLite schema + query helpers
├── pages/
│   ├── p01_overview.py             # KPI dashboard
│   ├── p02_city_map.py             # Folium city map
│   ├── p03_fleet_performance.py    # Vehicle analytics
│   ├── p04_downtime_analysis.py    # Downtime & loss analysis
│   ├── p05_scenario_simulator.py   # ROI simulator
│   └── p06_recommendations.py     # Business recommendations
├── data/
│   ├── processed/                  # Generated CSVs
│   └── sql/                        # SQLite database
├── run_pipeline.py                 # One-command data setup
└── .streamlit/config.toml          # Theme + server config
```

---

## 📊 Data Sources

| Layer | Source | Notes |
|---|---|---|
| EV Charger Locations | [Open Charge Map API](https://openchargemap.org/) | Real API; auto-fallbacks to synthetic if sparse |
| Fleet Operations | Synthetic simulation | Labeled clearly; no real operator data |
| Demand Zones | Manually defined Pune zone centroids | Based on OSM neighborhoods |

**⚠️ Data Disclaimer:** All fleet data is synthetic and generated for educational/portfolio purposes. No real fleet operator, partnership, or live deployment is implied or claimed.

---

## 🔬 Methodology

### Metrics Explained

| Metric | Formula | Interpretation |
|---|---|---|
| **Accessibility Score** | `1 - (0.6×norm_dist + 0.4×norm_wait)` | 0=no access, 1=excellent |
| **Downtime Risk Score** | `0.4×cost + 0.35×wait + 0.25×dist` (normalized) | 0=safe, 1=critical |
| **Revenue Recovered** | `(downtime_wait × 0.40 × vehicles × days) / 60 × avg_rev` | Conservative estimate |
| **Payback Period** | `CapEx ÷ (Annual Revenue Recovered ÷ 2)` | Safety-adjusted |

### Analysis Pipeline
1. Generate 60-day synthetic fleet ops (60 vehicles × 10 Pune zones)
2. Fetch OCM charger data for Pune (fallback to 8 curated illustrative stations)
3. Compute haversine distances: each zone → nearest charger
4. Score each zone on accessibility + downtime risk
5. KMeans cluster high-demand, high-wait vehicle positions → hub recommendations
6. ROI simulation for 1–10 new charging points with adjustable parameters

---

## ✨ Features

- **📊 Overview** — 5 KPI cards, revenue vs loss by zone, daily trend, executive summary
- **🗺️ City Map** — Dark-theme Folium map with chargers, demand zones (color by risk), recommended hubs
- **🚗 Fleet Performance** — Battery distribution, trip efficiency, demand heatmap, top vehicle leaderboard
- **⏱️ Downtime Analysis** — Zone risk table, charger distance scatter, day-of-week pattern
- **🧮 Scenario Simulator** — Adjustable sliders for chargers, cost, coverage; ROI comparison table
- **💡 Recommendations** — Prioritized hub cards, action quadrant scatter, 5 strategic recommendations

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- pip

### Step 1 — Clone & Install
```bash
git clone https://github.com/shravani22patil/voltpath-ev-optimizer.git
cd voltpath-ev-optimizer
pip install -r requirements.txt
```

### Step 2 — (Optional) Add OCM API Key
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your key
# Free key: https://openchargemap.org/site/developerinfo
```
Or set as environment variable:
```bash
export OCM_API_KEY="your_key_here"
```

### Step 3 — Run Data Pipeline
```bash
python run_pipeline.py
```
This generates all CSVs and the SQLite database in `data/`. Takes ~10 seconds.

### Step 4 — Launch App
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub (ensure `data/processed/` is NOT in `.gitignore` — or run pipeline before push)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path**: `app.py`
5. In **Secrets**, add (optional):
   ```toml
   OCM_API_KEY = "your_key_here"
   ```
6. Click **Deploy**

The app auto-generates data on first load if CSVs are missing.

> **Tip:** To avoid cold-start data generation, commit the generated `data/processed/*.csv` files to the repo.

---

## 📁 Full Folder Structure

```
voltpath-ev-optimizer/
├── app.py
├── run_pipeline.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml          ← not committed
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── fetch_chargers.py
│   │   └── generate_synthetic_data.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── analysis.py
│   └── utils/
│       ├── __init__.py
│       ├── data_loader.py
│       └── db_utils.py
├── pages/
│   ├── p01_overview.py
│   ├── p02_city_map.py
│   ├── p03_fleet_performance.py
│   ├── p04_downtime_analysis.py
│   ├── p05_scenario_simulator.py
│   └── p06_recommendations.py
├── data/
│   ├── processed/
│   │   ├── fleet_operations.csv
│   │   ├── zone_summary.csv
│   │   ├── chargers.csv
│   │   └── recommended_hubs.csv
│   └── sql/
│       └── evfleet.db
└── notebooks/
    └── exploration.ipynb     ← optional
```

---

## 🔮 Future Improvements

1. **Real-time GTFS / ATPCO data** — Integrate actual transit demand signals from city bus APIs
2. **Driver App Integration** — REST API layer so drivers receive push alerts for nearest charger when battery drops below 25%
3. **Dynamic Pricing Model** — ML model to predict revenue loss risk by hour, enabling smarter charging scheduling
4. **Multi-city Support** — Parameterize the pipeline for Mumbai, Delhi, Hyderabad using OCM country/city filters
5. **3D Kepler.gl Map** — Replace Folium with Kepler.gl for GPU-accelerated trip flow visualizations

---

## 📄 SQL Schema (Key Tables)

```sql
-- fleet_operations: one row per vehicle per day
CREATE TABLE fleet_operations (
    vehicle_id TEXT, vehicle_type TEXT, date TEXT, zone TEXT,
    demand_score REAL, trip_count INTEGER, battery_level_end REAL,
    charge_minutes INTEGER, downtime_wait_minutes INTEGER,
    charger_distance_km REAL, revenue_per_trip REAL,
    downtime_cost REAL, total_revenue REAL, net_revenue REAL
);

-- zone_summary: aggregated zone-level KPIs + scores
CREATE TABLE zone_summary (
    zone TEXT PRIMARY KEY, lat REAL, lon REAL,
    avg_demand_score REAL, avg_downtime_wait REAL,
    nearest_charger_km REAL, accessibility_score REAL,
    downtime_risk_score REAL, total_downtime_cost REAL
);

-- chargers: OCM or synthetic station data
CREATE TABLE chargers (
    charger_id TEXT, name TEXT, lat REAL, lon REAL,
    operator TEXT, max_power_kw REAL, data_source TEXT
);

-- recommended_hubs: KMeans cluster centers ranked by savings
CREATE TABLE recommended_hubs (
    hub_id INTEGER, lat REAL, lon REAL,
    zone_proximity TEXT, estimated_annual_savings REAL, priority_rank INTEGER
);
```



---

## 🛠️ Tech Stack

`Python 3.11` · `Pandas` · `NumPy` · `GeoPandas` · `Shapely` · `scikit-learn` · `Streamlit` · `Folium` · `streamlit-folium` · `Plotly` · `SQLite` · `SQLAlchemy` · `Open Charge Map API` · `SciPy`

---

*VoltPath is a student portfolio project. All data is synthetic. No real-world operator, EV company, or government agency is affiliated with or endorses this project.*
