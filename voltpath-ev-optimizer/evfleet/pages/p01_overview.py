"""pages/p01_overview.py — Fleet KPI Overview Dashboard (fixed)"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.utils.data_loader import load_fleet, load_zones, load_chargers


def render(fleet: pd.DataFrame, zones: pd.DataFrame, chargers: pd.DataFrame) -> None:
    st.markdown("## 📊 Fleet Operations Overview")
    st.markdown(
        "<p style='color:#94a3b8;margin-top:-12px;'>Synthetic operational data · Pune, Maharashtra · 60-day window</p>",
        unsafe_allow_html=True,
    )

    # ── KPI values ───────────────────────────────────────────────────────────
    total_revenue      = fleet["total_revenue"].sum()
    total_downtime     = fleet["downtime_cost"].sum()
    total_trips        = fleet["trip_count"].sum()
    n_vehicles         = fleet["vehicle_id"].nunique()
    avg_wait           = fleet["downtime_wait_minutes"].mean()

    # ── KPI cards via st.metric (no raw HTML needed — no </div> bug) ─────────
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Trips",         f"{total_trips:,}")
    col2.metric("Gross Revenue",       f"₹{total_revenue/1e5:.1f}L")
    col3.metric("Downtime Loss",       f"₹{total_downtime/1e5:.1f}L")
    col4.metric("Fleet Size",          f"{n_vehicles} Vehicles")
    col5.metric("Avg Wait (Charging)", f"{avg_wait:.0f} min")

    # ── Colour the metric values with a small CSS injection ──────────────────
    st.markdown("""
    <style>
    /* Target the metric value text — colour each column sequentially */
    [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 700 !important; }
    div[data-testid="column"]:nth-child(1) [data-testid="stMetricValue"] { color: #63b3ed; }
    div[data-testid="column"]:nth-child(2) [data-testid="stMetricValue"] { color: #48bb78; }
    div[data-testid="column"]:nth-child(3) [data-testid="stMetricValue"] { color: #fc8181; }
    div[data-testid="column"]:nth-child(4) [data-testid="stMetricValue"] { color: #f6ad55; }
    div[data-testid="column"]:nth-child(5) [data-testid="stMetricValue"] { color: #b794f4; }
    [data-testid="stMetricLabel"]  { font-size: 11px !important; text-transform: uppercase;
                                     letter-spacing: 0.06em; color: #94a3b8 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revenue vs Downtime Loss by Zone ─────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        zone_agg = (
            fleet.groupby("zone")
            .agg(revenue=("total_revenue","sum"), loss=("downtime_cost","sum"))
            .reset_index()
            .sort_values("revenue", ascending=True)
        )
        fig = go.Figure()
        fig.add_bar(y=zone_agg["zone"], x=zone_agg["revenue"],
                    name="Revenue", marker_color="#48bb78", orientation="h")
        fig.add_bar(y=zone_agg["zone"], x=-zone_agg["loss"],
                    name="Downtime Loss", marker_color="#fc8181", orientation="h")
        fig.update_layout(
            title="Revenue vs Downtime Loss by Zone", barmode="overlay",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=340,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="INR"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        type_agg = fleet.groupby("vehicle_type")["trip_count"].sum().reset_index()
        fig2 = px.pie(type_agg, names="vehicle_type", values="trip_count",
                      color_discrete_sequence=["#63b3ed","#48bb78","#f6ad55"], hole=0.55)
        fig2.update_layout(title="Trips by Vehicle Type",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                           height=340, legend=dict(bgcolor="rgba(0,0,0,0)"))
        fig2.update_traces(textfont_color="#e2e8f0")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Daily Revenue Trend ───────────────────────────────────────────────────
    daily = (fleet.groupby("date")
             .agg(revenue=("total_revenue","sum")).reset_index())
    fig3 = go.Figure()
    fig3.add_scatter(x=daily["date"], y=daily["revenue"], name="Daily Revenue",
                     line=dict(color="#48bb78", width=2),
                     fill="tozeroy", fillcolor="rgba(72,187,120,0.08)")
    fig3.update_layout(
        title="Daily Revenue Trend",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", height=260,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="INR"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Executive Summary ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Executive Summary")
    loss_pct   = total_downtime / total_revenue * 100
    worst_zone = zones.nlargest(1, "downtime_risk_score")["zone"].values[0]
    st.info(
        f"**Fleet of {n_vehicles} e-rickshaws** completed **{total_trips:,} trips** generating "
        f"**₹{total_revenue/1e5:.1f} lakh** gross revenue over a 60-day simulation window. "
        f"Charging downtime losses account for **{loss_pct:.1f}%** of gross revenue "
        f"(₹{total_downtime/1e5:.1f}L). Zone **{worst_zone}** shows the highest downtime risk. "
        f"Deploying 3–5 new charging hubs in high-risk zones could recover 15–25% of losses."
    )
