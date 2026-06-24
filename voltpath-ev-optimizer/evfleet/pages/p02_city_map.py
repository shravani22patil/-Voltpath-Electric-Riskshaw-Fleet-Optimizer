"""pages/02_city_map.py — Interactive City Map"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def render(fleet: pd.DataFrame, zones: pd.DataFrame, chargers: pd.DataFrame, hubs: pd.DataFrame) -> None:
    st.markdown("## 🗺️ City Intelligence Map")
    st.markdown(
        "<p style='color:#94a3b8;margin-top:-12px;'>Demand zones · Charging stations · Recommended hub locations · Pune, MH</p>",
        unsafe_allow_html=True,
    )

    col_ctrl, _ = st.columns([2, 3])
    with col_ctrl:
        show_chargers = st.checkbox("Show Charging Stations", value=True)
        show_demand = st.checkbox("Show Demand Zones", value=True)
        show_hubs = st.checkbox("Show Recommended Hubs", value=True)

    # Build map
    m = folium.Map(
        location=[18.52, 73.856],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    # Charger stations
    if show_chargers:
        for _, row in chargers.iterrows():
            is_synthetic = "Synthetic" in str(row.get("data_source", ""))
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8,
                color="#63b3ed",
                fill=True,
                fill_color="#63b3ed",
                fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{row['name']}</b><br>Operator: {row.get('operator','—')}<br>"
                    f"Power: {row.get('max_power_kw','—')} kW<br>"
                    f"<i style='color:orange;'>{'⚠ Illustrative' if is_synthetic else '✓ OCM Data'}</i>",
                    max_width=220,
                ),
                tooltip=row["name"],
            ).add_to(m)

    # Demand zone circles
    if show_demand:
        for _, row in zones.iterrows():
            risk = row.get("downtime_risk_score", 0.5)
            color = "#fc8181" if risk > 0.6 else "#f6ad55" if risk > 0.35 else "#48bb78"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=int(20 + row.get("avg_demand_score", 0.5) * 20),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.25,
                weight=2,
                popup=folium.Popup(
                    f"<b>{row['zone']}</b><br>"
                    f"Demand Score: {row.get('avg_demand_score',0):.2f}<br>"
                    f"Downtime Risk: {row.get('downtime_risk_score',0):.2f}<br>"
                    f"Nearest Charger: {row.get('nearest_charger_km','—')} km<br>"
                    f"Accessibility: {row.get('accessibility_score',0):.2f}",
                    max_width=240,
                ),
                tooltip=f"{row['zone']} | Risk: {risk:.2f}",
            ).add_to(m)

    # Recommended hubs
    if show_hubs:
        for _, row in hubs.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                icon=folium.Icon(color="green", icon="bolt", prefix="fa"),
                popup=folium.Popup(
                    f"<b>Recommended Hub #{int(row['priority_rank'])}</b><br>"
                    f"Near: {row['zone_proximity']}<br>"
                    f"Est. Annual Savings: ₹{row.get('estimated_annual_savings',0):,.0f}",
                    max_width=220,
                ),
                tooltip=f"Hub #{int(row['priority_rank'])} · {row['zone_proximity']}",
            ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;left:20px;z-index:9999;
         background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
         border:1px solid rgba(99,179,237,0.3);font-size:13px;color:#e2e8f0;">
        <b style="font-size:14px;">Legend</b><br>
        <span style="color:#63b3ed;">●</span> Charging Station &nbsp;
        <span style="color:#48bb78;">●</span> Low Risk Zone<br>
        <span style="color:#f6ad55;">●</span> Medium Risk Zone &nbsp;
        <span style="color:#fc8181;">●</span> High Risk Zone<br>
        <span style="color:#48bb78;">★</span> Recommended Hub
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=540)

    # Zone table below map
    st.markdown("### Zone Accessibility & Risk Table")
    display_cols = ["zone", "avg_demand_score", "nearest_charger_km", "accessibility_score", "downtime_risk_score", "total_downtime_cost"]
    existing = [c for c in display_cols if c in zones.columns]
    disp = zones[existing].copy()
    disp.columns = [c.replace("_", " ").title() for c in existing]

    def color_risk(val):
        if isinstance(val, float):
            if val > 0.6:
                return "background-color: rgba(252,129,129,0.2); color:#fc8181"
            elif val > 0.35:
                return "background-color: rgba(246,173,85,0.2); color:#f6ad55"
        return ""

    st.dataframe(
       disp.style.map(
          color_risk,
          subset=["Downtime Risk Score"] if "Downtime Risk Score" in disp.columns else []
      ),
      use_container_width=True,
      height=340,
  )
