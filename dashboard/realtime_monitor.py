import streamlit as st
import plotly.graph_objs as go
from collections import deque
import time

class RealtimeMonitor:
    """Real-time data monitor for dashboard"""
    
    def __init__(self, max_points=50):
        self.max_points = max_points
        self.data = {
            'timestamp': deque(maxlen=max_points),
            'co2e': deque(maxlen=max_points),
            'energy': deque(maxlen=max_points)
        }
    
    def update(self, emissions: dict, energy: float):
        """Update with new data"""
        self.data['timestamp'].append(time.time())
        self.data['co2e'].append(emissions['total_co2e_kg'])
        self.data['energy'].append(energy)
    
    def render(self):
        """Render real-time charts"""
        if len(self.data['timestamp']) < 2:
            st.info("Waiting for data...")
            return
        
        # CO2e trend
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=list(self.data['timestamp']),
            y=list(self.data['co2e']),
            mode='lines+markers',
            name='CO2e (kg)',
            line=dict(color='green', width=2)
        ))
        fig1.update_layout(
            title="Real-time CO2e Emissions",
            xaxis_title="Time",
            yaxis_title="kg CO2e",
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Energy trend
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(self.data['timestamp']),
            y=list(self.data['energy']),
            mode='lines+markers',
            name='Energy (kWh)',
            line=dict(color='blue', width=2)
        ))
        fig2.update_layout(
            title="Real-time Energy Consumption",
            xaxis_title="Time",
            yaxis_title="kWh",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

def render_realtime():
    """Render real-time monitor in dashboard"""
    st.subheader("📡 Live Data Stream")
    
    # Placeholder for real-time updates
    placeholder = st.empty()
    
    # Simulate real-time updates
    for i in range(10):
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest CO2e", f"{50 + i * 2:.1f} kg", delta=f"{i*2:.1f}")
            with col2:
                st.metric("Latest Energy", f"{100 + i * 5:.0f} kWh", delta=f"{i*5:.0f}")
            with col3:
                st.metric("Status", "Active" if i < 8 else "Peak", delta="Normal")
        time.sleep(0.5)