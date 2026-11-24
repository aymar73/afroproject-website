# app.py
# The Afro Sandbox — three-zone monetary architecture simulation.
# Deploy: streamlit run app.py

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Afro Sandbox",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS (matching Afro Project brand)
# ============================================================

st.markdown("""
<style>
    .main { background-color: #f4f7fb; }
    h1, h2, h3 { font-family: 'Georgia', serif; color: #0a1128; }
    .zone-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #f5b342;
        box-shadow: 0 4px 20px rgba(10,17,40,0.08);
    }
    .zone-west { border-top-color: #1a4d3a; }
    .zone-east { border-top-color: #2a7ab8; }
    .zone-south { border-top-color: #f5b342; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.title("🌍 The Afro Sandbox")
st.markdown("### Simulating three monetary zones under one continental architecture")

st.markdown("""
This sandbox simulates the Afro Project's three currency zones — West, East, and South —
running in parallel. Adjust the controls on the left to introduce shocks and see how
each zone responds, how the Afro-Index aggregates them, and how the new architecture
compares to the legacy CFA system.
""")

# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("⚙️ Simulation Controls")

st.sidebar.subheader("Global Shocks")
oil_shock = st.sidebar.slider(
    "Oil price shock (%)", -40, 40, 0, 5,
    help="A sudden change in global oil prices affecting all zones"
)

china_shock = st.sidebar.slider(
    "China demand shock (%)", -30, 30, 0, 5,
    help="A change in Chinese demand for African commodities"
)

st.sidebar.subheader("Zone-Specific")
west_fiscal = st.sidebar.slider(
    "West fiscal deficit (% GDP)", 0, 12, 3, 1,
    help="Fiscal deficit in the West African zone"
)

east_fiscal = st.sidebar.slider(
    "East fiscal deficit (% GDP)", 0, 12, 3, 1
)

south_fiscal = st.sidebar.slider(
    "South fiscal deficit (% GDP)", 0, 12, 3, 1
)

st.sidebar.subheader("Architecture Comparison")
regime = st.sidebar.radio(
    "Settlement architecture",
    ["Afro Architecture", "Legacy CFA System"],
    help="Compare the two systems under identical shocks"
)

st.sidebar.subheader("Simulation")
horizon = st.sidebar.slider("Months", 12, 120, 60, 12)

run = st.sidebar.button("▶️ Run Simulation", type="primary", use_container_width=True)

# ============================================================
# SIMULATION ENGINE
# ============================================================

@st.cache_data
def simulate(horizon, oil_shock, china_shock, west_fiscal, east_fiscal, south_fiscal, regime):
    """Run the 3-zone simulation."""
    np.random.seed(42)

    zones = {
        'West': {
            'color': '#1a4d3a',
            'oil_sensitivity': 0.8,
            'china_sensitivity': 0.3,
            'fiscal': west_fiscal,
            'initial_ecm': 0.5,
        },
        'East': {
            'color': '#2a7ab8',
            'oil_sensitivity': 0.2,
            'china_sensitivity': 0.6,
            'fiscal': east_fiscal,
            'initial_ecm': 0.3,
        },
        'South': {
            'color': '#f5b342',
            'oil_sensitivity': 0.4,
            'china_sensitivity': 0.5,
            'fiscal': south_fiscal,
            'initial_ecm': 0.4,
        },
    }

    results = {}
    for name, params in zones.items():
        ecm = params['initial_ecm']
        inflation = 3.0
        reserves = 100.0
        ecm_history = [ecm]
        inflation_history = [inflation]
        reserves_history = [reserves]
        penalty_history = [0]

        for t in range(horizon):
            # Shock contributions
            oil_effect = params['oil_sensitivity'] * (oil_shock / 100) * 2.0
            china_effect = params['china_sensitivity'] * (china_shock / 100) * 1.5
            fiscal_effect = (params['fiscal'] - 3.0) * 0.1

            # Mean reversion
            mean_reversion = -0.25 * ecm

            # Policy response
            if regime == "Afro Architecture":
                # ECM penalty kicks in
                policy_effect = -0.5 * ecm if ecm > 1.0 else 0
                penalty = 1 if ecm > 2.0 else 0
            else:
                # Legacy: no automatic enforcement, slower adjustment
                policy_effect = -0.15 * ecm
                penalty = 0

            # Noise
            noise = np.random.randn() * 0.1

            ecm += mean_reversion + oil_effect + china_effect + fiscal_effect + policy_effect + noise
            ecm = max(0.0, ecm)

            # Inflation follows ECM
            inflation = 3.0 + 0.8 * ecm + np.random.randn() * 0.2
            inflation = max(-2.0, inflation)

            # Reserves
            reserves -= 0.5 * (oil_effect + china_effect) + 0.3 * fiscal_effect
            if regime == "Legacy CFA System":
                # French extraction (0.5% per month on half the reserves)
                reserves -= reserves * 0.005 / 2
            reserves = max(reserves, 20.0)

            ecm_history.append(ecm)
            inflation_history.append(inflation)
            reserves_history.append(reserves)
            penalty_history.append(penalty)

        results[name] = {
            'ecm': ecm_history,
            'inflation': inflation_history,
            'reserves': reserves_history,
            'penalties': penalty_history,
            'color': params['color'],
        }

    # Afro-Index (geometric basket)
    weights = {'West': 0.45, 'East': 0.30, 'South': 0.25}
    afro_index = []
    for t in range(horizon + 1):
        value = 1.0
        for zone_name, weight in weights.items():
            # Price inversely related to inflation
            price = 1.0 / (1.0 + results[zone_name]['inflation'][t] / 100)
            value *= price ** weight
        afro_index.append(value)

    return results, afro_index

# ============================================================
# RUN OR SHOW PLACEHOLDER
# ============================================================

if run:
    with st.spinner("Running simulation..."):
        results, afro_index = simulate(
            horizon, oil_shock, china_shock,
            west_fiscal, east_fiscal, south_fiscal, regime
        )
        st.session_state['results'] = results
        st.session_state['afro_index'] = afro_index
        st.session_state['regime'] = regime

# ============================================================
# DISPLAY RESULTS
# ============================================================

if 'results' in st.session_state:
    results = st.session_state['results']
    afro_index = st.session_state['afro_index']
    regime = st.session_state['regime']

    # ---- Top metrics ----
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    avg_ecm = np.mean([np.mean(results[z]['ecm']) for z in results])
    max_ecm = max([max(results[z]['ecm']) for z in results])
    total_penalties = sum(sum(results[z]['penalties']) for z in results)
    index_change = (afro_index[-1] - 1.0) * 100

    col1.metric("Average ECM Deviation", f"{avg_ecm:.2f}")
    col2.metric("Maximum Deviation", f"{max_ecm:.2f}",
                delta="Above threshold" if max_ecm > 2.0 else "Within bounds")
    col3.metric("Penalties Applied", f"{total_penalties}",
                delta="Automatic" if regime == "Afro Architecture" else "None")
    col4.metric("Afro-Index Change", f"{index_change:+.2f}%",
                delta="Stable" if abs(index_change) < 3 else "Volatile")

    # ---- Zone cards ----
    st.markdown("### Zone Status at End of Simulation")
    zcol1, zcol2, zcol3 = st.columns(3)

    for col, (zone_name, zone_data) in zip([zcol1, zcol2, zcol3], results.items()):
        with col:
            st.markdown(f"""
            <div class="zone-card zone-{zone_name.lower()}">
                <h3 style="margin-top:0; color:{zone_data['color']};">{zone_name} Africa</h3>
                <p style="margin:4px 0;"><strong>Final ECM:</strong> {zone_data['ecm'][-1]:.2f}</p>
                <p style="margin:4px 0;"><strong>Final Inflation:</strong> {zone_data['inflation'][-1]:.1f}%</p>
                <p style="margin:4px 0;"><strong>Reserves:</strong> {zone_data['reserves'][-1]:.0f}</p>
                <p style="margin:4px 0;"><strong>Penalties:</strong> {sum(zone_data['penalties'])}</p>
            </div>
            """, unsafe_allow_html=True)

    # ---- Charts ----
    st.markdown("---")
    st.markdown("### Simulation Results")

    # Chart 1: ECM deviations
    fig1 = go.Figure()
    months = list(range(len(results['West']['ecm'])))
    for zone_name, zone_data in results.items():
        fig1.add_trace(go.Scatter(
            x=months, y=zone_data['ecm'],
            name=zone_name,
            line=dict(color=zone_data['color'], width=2.5)
        ))
    fig1.add_hline(y=2.0, line_dash="dash", line_color="red",
                   annotation_text="ECM penalty threshold")
    fig1.update_layout(
        title="Error Correction Mechanism — Zone Deviations",
        xaxis_title="Month",
        yaxis_title="ECM Deviation (σ)",
        height=350,
        hovermode='x unified',
        plot_bgcolor='white',
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Afro-Index
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=months, y=afro_index,
        name='Afro-Index',
        line=dict(color='#f5b342', width=3),
        fill='tozeroy',
        fillcolor='rgba(245,179,66,0.1)'
    ))
    fig2.add_hline(y=1.0, line_dash="dot", line_color="gray",
                   annotation_text="Base value")
    fig2.update_layout(
        title="Afro-Index — Continental Unit of Account",
        xaxis_title="Month",
        yaxis_title="Index Value (base = 1.0)",
        height=350,
        plot_bgcolor='white',
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Reserve trajectories (with extraction if legacy)
    fig3 = go.Figure()
    for zone_name, zone_data in results.items():
        fig3.add_trace(go.Scatter(
            x=months, y=zone_data['reserves'],
            name=zone_name,
            line=dict(color=zone_data['color'], width=2.5)
        ))
    fig3.update_layout(
        title="Reserve Trajectories" + (" (with French extraction)" if regime == "Legacy CFA System" else ""),
        xaxis_title="Month",
        yaxis_title="Reserves (index)",
        height=350,
        hovermode='x unified',
        plot_bgcolor='white',
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---- Interpretation ----
    st.markdown("---")
    st.markdown("### Interpretation")

    if regime == "Afro Architecture":
        st.success(f"""
        **Afro Architecture Results:**
        - ECM penalties were applied **{total_penalties} times** automatically
        - Maximum deviation was **{max_ecm:.2f}σ** — {"above" if max_ecm > 2.0 else "within"} threshold
        - The Afro-Index moved **{index_change:+.2f}%** over the period
        - No reserves were extracted by any external treasury
        """)
    else:
        st.warning(f"""
        **Legacy CFA System Results:**
        - **No automatic penalties** were applied (political enforcement only)
        - Maximum deviation was **{max_ecm:.2f}σ** — {"above" if max_ecm > 2.0 else "within"} threshold
        - The Afro-Index moved **{index_change:+.2f}%** over the period
        - Reserves were continuously extracted to an external treasury
        """)

else:
    st.info("👈 Adjust the controls in the sidebar and click **Run Simulation** to begin.")

    # Preview the architecture
    st.markdown("---")
    st.markdown("### The Architecture You Are Simulating")
    st.markdown("""
    - **Three independent zones** — West, East, Southern Africa
    - **Three currencies** — Afro-W, Afro-E, Afro-S — each pegged to the Afro-Index
    - **One continental index** — geometric basket, weighted by GDP and trade
    - **Automatic enforcement** — ECM penalties applied by smart contract
    - **No external extraction** — reserves stay in the zone
    """)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8899b0; font-size:0.85rem;">
    The Afro Sandbox · A research initiative by <a href="https://consilium-cfa.com">Consilium-CFA</a><br>
    <a href="https://afroproject.africa">afroproject.africa</a>
</div>
""", unsafe_allow_html=True)
