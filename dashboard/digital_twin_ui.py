import streamlit as st
import plotly.graph_objects as go
from digital_twin.twin_engine import DigitalTwin

def render_digital_twin(twin: DigitalTwin):
    """Render digital twin interface"""
    st.subheader("🏗️ Digital Twin Dashboard")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        occupancy_factor = st.slider("Occupancy Factor", 0.0, 1.0, 0.7, 0.1)
    with col2:
        if st.button("Run Simulation"):
            result = twin.simulate(occupancy_factor)
            st.session_state.twin_result = result
    
    # Display results
    if 'twin_result' in st.session_state:
        result = st.session_state.twin_result
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Power", f"{result['total_power_kw']:.1f} kW")
        with col2:
            st.metric("Energy This Hour", f"{result['energy_kwh']:.1f} kWh")
        with col3:
            st.metric("Cumulative Energy", f"{result['cumulative_energy_kwh']:.1f} kWh")
        
        # Zone breakdown
        st.write("**Zone Breakdown**")
        zone_df = pd.DataFrame(result['zones'])
        st.dataframe(zone_df, use_container_width=True)
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result['total_power_kw'],
            title={'text': "Current Power (kW)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [None, 300]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

import pandas as pd