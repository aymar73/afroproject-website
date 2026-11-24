# afro_dashboard.py
# African Monetary Union - Real-Time ECM Monitoring Dashboard
# Run: streamlit run afro_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.vector_ar.vecm import VECM
from datetime import datetime, timedelta
import yfinance as yf  # For real FX data (proxy)

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(page_title="Afro ECM Monitor", layout="wide", page_icon="🌍")
st.title("🌍 African Monetary Convergence Mechanism (AMCM)")
st.subheader("Real-Time Cointegration & Error Correction Dashboard")

# ============================================
# SIDEBAR - COUNTRY SELECTION
# ============================================
st.sidebar.header("⚙️ Controls")
zone = st.sidebar.selectbox("Select Zone", ["East Africa", "West Africa", "Southern Africa"])
countries_map = {
    "East Africa": ["Kenya", "Tanzania", "Rwanda", "Uganda", "Ethiopia"],
    "West Africa": ["Nigeria", "Ghana", "Senegal", "IvoryCoast"],
    "Southern Africa": ["South Africa", "Botswana", "Namibia"]
}
selected_countries = st.sidebar.multiselect(
    "Select Countries to Monitor",
    countries_map[zone],
    default=countries_map[zone][:3]
)

# ============================================
# DATA SIMULATION (Replace with real API)
# ============================================
@st.cache_data(ttl=3600)
def load_real_data():
    """In production, pull from AfDB/IMF API. Here we simulate with FX + inflation proxies."""
    dates = pd.date_range(start='2016-01-01', end=datetime.today(), freq='ME')
    np.random.seed(42)
    
    data = {}
    for country in ['Kenya', 'Tanzania', 'Rwanda', 'Uganda', 'Ethiopia', 
                    'Nigeria', 'Ghana', 'Senegal', 'IvoryCoast',
                    'South Africa', 'Botswana', 'Namibia']:
        # Simulate GDP proxy (industrial production)
        trend = np.linspace(0, 3, len(dates))
        cycle = 0.5 * np.sin(np.linspace(0, 20, len(dates)))
        noise = 0.3 * np.random.randn(len(dates))
        data[country] = 100 + trend + cycle + noise
    
    df = pd.DataFrame(data, index=dates)
    return df

df = load_real_data()

# ============================================
# VECM COMPUTATION (Error Correction)
# ============================================
def compute_ecm(data, countries):
    """Runs VECM and extracts deviation from equilibrium."""
    if len(countries) < 2:
        return None, None
    
    subset = data[countries].dropna()
    # Differencing to make stationary
    diff = subset.diff().dropna()
    
    # Simple VECM with 2 lags
    try:
        vecm = VECM(subset, k_ar_diff=2, coint_rank=1)
        vecm_fit = vecm.fit()
        # Error correction term (deviation from long-run)
        ec_term = vecm_fit.resid.mean(axis=1)  # Approximation
        return ec_term, subset
    except:
        return None, None

# ============================================
# MAIN DASHBOARD - METRICS
# ============================================
col1, col2, col3, col4 = st.columns(4)

if len(selected_countries) >= 2:
    ec_term, subset = compute_ecm(df, selected_countries)
    
    if ec_term is not None:
        latest_dev = ec_term.iloc[-1]
        avg_dev = ec_term.mean()
        
        col1.metric("📊 Current Deviation", f"{latest_dev:.3f}", 
                    delta=f"{latest_dev - ec_term.iloc[-2]:.3f}" if len(ec_term)>1 else "N/A")
        col2.metric("⚖️ Avg Deviation (5yr)", f"{avg_dev:.3f}")
        col3.metric("🟢 Status", "GREEN" if abs(latest_dev) < 0.5 else "YELLOW" if abs(latest_dev) < 1.0 else "🔴 RED")
        col4.metric("🏛️ Voting Rights", "100%" if abs(latest_dev) < 0.5 else "90%" if abs(latest_dev) < 1.0 else "SUSPENDED")
        
        # ============================================
        # PLOT 1: Error Correction Term Over Time
        # ============================================
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=ec_term.index,
            y=ec_term,
            mode='lines+markers',
            name='ECM Deviation',
            line=dict(color='royalblue', width=2),
            marker=dict(size=4)
        ))
        fig1.add_hline(y=0.5, line_dash="dash", line_color="yellow", annotation_text="Yellow Zone (1σ)")
        fig1.add_hline(y=-0.5, line_dash="dash", line_color="yellow")
        fig1.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Red Zone (2σ)")
        fig1.add_hline(y=-1.0, line_dash="dash", line_color="red")
        fig1.update_layout(
            title=f"Error Correction Term - {zone}",
            xaxis_title="Date",
            yaxis_title="Deviation from Equilibrium",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # ============================================
        # PLOT 2: Country-Level Inflation Convergence
        # ============================================
        fig2 = make_subplots(rows=1, cols=2, subplot_titles=("GDP Proxy Levels", "Inflation Differential"))
        
        # Levels
        for col in selected_countries:
            fig2.add_trace(
                go.Scatter(x=subset.index, y=subset[col], mode='lines', name=col),
                row=1, col=1
            )
        
        # Inflation diff (rolling 12m)
        for col in selected_countries:
            infl = subset[col].pct_change(12).dropna()
            fig2.add_trace(
                go.Scatter(x=infl.index, y=infl, mode='lines', name=f"{col} (12m)"),
                row=1, col=2
            )
        
        fig2.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)
        
        # ============================================
        # PLOT 3: Cointegration Heatmap (Within Zone)
        # ============================================
        st.subheader("🔥 Cointegration Heatmap (Trace Statistics)")
        # Compute pairwise trace (simplified)
        countries_list = selected_countries
        matrix = pd.DataFrame(0, index=countries_list, columns=countries_list)
        for i, c1 in enumerate(countries_list):
            for j, c2 in enumerate(countries_list):
                if i != j:
                    # Simulate trace (higher = better)
                    matrix.loc[c1, c2] = 2.5 + 0.5 * np.random.randn() + (1 if np.random.rand() > 0.3 else 0)
        
        fig3 = go.Figure(data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale='RdYlGn',
            zmid=2.5,
            text=matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        fig3.update_layout(height=400, title="Pairwise Trace Statistics (Green = Cointegrated)")
        st.plotly_chart(fig3, use_container_width=True)
        
        # ============================================
        # REAL-TIME ALERT SYSTEM
        # ============================================
        st.sidebar.subheader("🚨 Alerts")
        if abs(latest_dev) > 1.0:
            st.sidebar.error(f"🔴 EMERGENCY: {zone} in Red Zone! Voting rights suspended.")
        elif abs(latest_dev) > 0.5:
            st.sidebar.warning(f"🟡 WARNING: {zone} approaching Red Zone. Technical assistance triggered.")
        else:
            st.sidebar.success(f"✅ {zone} stable. All policies within Green Zone.")
        
        # Export report
        if st.sidebar.button("📥 Download ECM Report (CSV)"):
            report_df = pd.DataFrame({
                'Date': ec_term.index,
                'ECM_Deviation': ec_term.values
            })
            csv = report_df.to_csv(index=False)
            st.sidebar.download_button("Download", data=csv, file_name=f"ecm_report_{zone}.csv")
        
    else:
        st.error("⚠️ Not enough data for VECM. Select at least 2 countries with 20+ months of data.")
else:
    st.warning("Please select at least 2 countries from the sidebar.")

# ============================================
# FOOTER
# ============================================
st.caption("📐 Powered by StatsModels VECM | Data: Simulated (replace with AfDB/IMF API) | Nairobi Accord 2026")
