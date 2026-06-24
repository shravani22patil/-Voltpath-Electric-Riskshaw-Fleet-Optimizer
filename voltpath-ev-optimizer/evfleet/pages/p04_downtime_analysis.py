"""pages/04_downtime_analysis.py — Downtime & Revenue Loss Intelligence"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def render(fleet: pd.DataFrame, zones: pd.DataFrame) -> None:
    st.markdown("## ⏱️ Downtime & Revenue Loss Intelligence")
    st.markdown(
        "<p style='color:#94a3b8;margin-top:-12px;'>Charging wait times, accessibility gaps, and lost earnings by zone</p>",
        unsafe_allow_html=True,
    )

    # Top KPIs
    total_wait_hours = fleet["downtime_wait_minutes"].sum() / 60
    total_loss = fleet["downtime_cost"].sum()
    worst_zone = zones.nlargest(1, "downtime_risk_score")["zone"].values[0]
    worst_risk = zones["downtime_risk_score"].max()
    avg_dist = fleet["charger_distance_km"].mean()

    cols = st.columns(4)
    cards = [
        ("Total Downtime Hours", f"{total_wait_hours:,.0f} hrs", "#fc8181"),
        ("Total Revenue Lost", f"₹{total_loss/1e5:.2f}L", "#f6ad55"),
        ("Highest Risk Zone", worst_zone, "#b794f4"),
        ("Avg Charger Distance", f"{avg_dist:.1f} km", "#63b3ed"),
    ]
    card_css = "background:rgba(15,23,42,0.7);border:1px solid rgba(252,129,129,0.2);border-radius:10px;padding:16px;text-align:center;"
    for col, (label, val, color) in zip(cols, cards):
        with col:
            st.markdown(f"<div style='{card_css}'><p style='color:#94a3b8;font-size:11px;margin:0;text-transform:uppercase;'>{label}</p><p style='color:{color};font-size:22px;font-weight:700;margin:6px 0 0;'>{val}</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # Downtime cost by zone - bar
    with col_a:
        zone_loss = (
            fleet.groupby("zone")
            .agg(downtime_cost=("downtime_cost","sum"), revenue=("total_revenue","sum"))
            .reset_index()
        )
        zone_loss["loss_pct"] = (zone_loss["downtime_cost"] / zone_loss["revenue"] * 100).round(1)
        zone_loss = zone_loss.sort_values("downtime_cost", ascending=True)
        fig = px.bar(
            zone_loss, y="zone", x="downtime_cost", orientation="h",
            color="loss_pct",
            color_continuous_scale=["#48bb78", "#f6ad55", "#fc8181"],
            title="Downtime Cost by Zone (INR)",
            labels={"downtime_cost": "Downtime Cost (₹)", "loss_pct": "Loss %"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=340,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: charger distance vs downtime wait
    with col_b:
        fig2 = px.scatter(
            zones,
            x="nearest_charger_km",
            y="avg_downtime_wait",
            size="total_downtime_cost",
            color="downtime_risk_score",
            color_continuous_scale=["#48bb78", "#f6ad55", "#fc8181"],
            text="zone",
            title="Charger Distance vs Avg Downtime Wait",
            labels={
                "nearest_charger_km": "Nearest Charger (km)",
                "avg_downtime_wait": "Avg Wait (min)",
                "downtime_risk_score": "Risk Score",
            },
        )
        fig2.update_traces(textposition="top center", textfont_size=10)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0", height=340,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Weekly downtime pattern
    fleet["dow"] = pd.to_datetime(fleet["date"]).dt.day_name()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    daily_pattern = fleet.groupby("dow")["downtime_wait_minutes"].mean().reindex(day_order).reset_index()
    fig3 = go.Figure(go.Bar(
        x=daily_pattern["dow"],
        y=daily_pattern["downtime_wait_minutes"],
        marker_color=["#fc8181" if v > 40 else "#f6ad55" if v > 30 else "#48bb78" for v in daily_pattern["downtime_wait_minutes"]],
    ))
    fig3.update_layout(
        title="Average Downtime Wait by Day of Week",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0", height=280,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Avg Wait (min)"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Risk score table
    st.markdown("### Zone Risk & Accessibility Scores")
    risk_table = zones[["zone","avg_demand_score","nearest_charger_km","accessibility_score","downtime_risk_score","total_downtime_cost"]].copy()
    risk_table = risk_table.sort_values("downtime_risk_score", ascending=False)
    risk_table["total_downtime_cost"] = risk_table["total_downtime_cost"].apply(lambda x: f"₹{x:,.0f}")
    risk_table.columns = ["Zone","Demand Score","Nearest Charger (km)","Accessibility","Risk Score","Downtime Cost"]

    def highlight_risk(val):
        try:
            v = float(val)
            if v > 0.6: return "color: #fc8181"
            if v > 0.35: return "color: #f6ad55"
            return "color: #48bb78"
        except:
            return ""

    st.dataframe(
        risk_table.style.map(highlight_risk, subset=["Risk Score","Accessibility"]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown(
        """**📌 Metric Definitions**
        - **Accessibility Score**: Composite score (0–1) penalizing charger distance and wait time. Higher = better access.
        - **Downtime Risk Score**: Composite (0–1) combining cost, wait, and distance weights. Higher = more revenue at risk.
        - **Charger Distance**: Average km from fleet vehicle positions to nearest charger in that zone (simulated for synthetic data).
        """
    )
