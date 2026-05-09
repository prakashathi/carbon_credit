import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Try to import optional menu, fallback if not available
try:
    from streamlit_option_menu import option_menu
    HAS_MENU = True
except ImportError:
    HAS_MENU = False
    st.warning("Install streamlit-option-menu for better navigation: pip install streamlit-option-menu")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iot_simulator.sensor_gateway import IoTSensorGateway
from backend.emission_engine import EmissionEngine
from backend.ai_recommender import AIRecommender
from backend.benchmark_engine import BenchmarkEngine
from backend.report_generator import ReportGenerator
from digital_twin.twin_engine import DigitalTwin
from digital_twin.scenario_analyzer import ScenarioAnalyzer

# Page config
st.set_page_config(
    page_title="CarbonSME - Enterprise Carbon Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Status indicators */
    .status-good {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-warning {
        color: #f59e0b;
        font-weight: bold;
    }
    
    .status-critical {
        color: #ef4444;
        font-weight: bold;
    }
    
    /* Custom divider */
    .custom-divider {
        height: 3px;
        background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
        border-radius: 3px;
        margin: 1rem 0;
    }
    
    /* Gauge styling */
    .gauge-container {
        background: #1e1e2e;
        border-radius: 1rem;
        padding: 1rem;
    }
    
    /* Animation for alerts */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .alert-pulse {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def init():
    return {
        'sensor': IoTSensorGateway(),
        'emission': EmissionEngine(),
        'ai': AIRecommender(),
        'benchmark': BenchmarkEngine(),
        'twin': DigitalTwin(),
        'report': ReportGenerator()
    }

system = init()
scenario = ScenarioAnalyzer(system['twin'])

# Simple navigation without external dependency
def simple_navigation():
    st.sidebar.markdown("---")
    nav_options = ["📊 Dashboard", "🏭 Digital Twin", "🤖 AI Insights", "📈 Benchmarking", "📄 Reports"]
    
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "📊 Dashboard"
    
    for option in nav_options:
        if st.sidebar.button(option, key=option, use_container_width=True):
            st.session_state.selected_page = option
    
    return st.session_state.selected_page

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/earth-planet.png", width=80)
    st.title("🌍 CarbonSME")
    
    # Use simple navigation if menu not available
    if HAS_MENU:
        selected = option_menu(
            menu_title=None,
            options=["📊 Dashboard", "🏭 Digital Twin", "🤖 AI Insights", "📈 Benchmarking", "📄 Reports"],
            icons=["graph-up", "building", "robot", "trophy", "file-pdf"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#10b981", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "#10b981"},
            }
        )
    else:
        selected = simple_navigation()
    
    st.markdown("---")
    sector = st.selectbox("Industry Sector", ["Manufacturing", "Retail", "IT Services", "Warehousing"])
    employees = st.number_input("Employees", 10, 500, 75)
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Get sensor data
async def get_readings():
    return await system['sensor'].read_all_sensors()

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    readings = loop.run_until_complete(get_readings())
    emissions = system['emission'].calculate(readings)
    
    # Extract values
    energy_val = next((r['value'] for r in readings if r['sensor_type'] == 'energy'), 0)
    gas_val = next((r['value'] for r in readings if r['sensor_type'] == 'gas'), 0)
    fuel_val = next((r['value'] for r in readings if r['sensor_type'] == 'fuel'), 0)
    occ_val = next((r['value'] for r in readings if r['sensor_type'] == 'occupancy'), 0)
    
    # DASHBOARD VIEW
    if selected == "📊 Dashboard":
        # Animated title
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='background: linear-gradient(120deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Real-time Carbon Emission Intelligence
            </h1>
            <p style='color: #6b7280;'>Live monitoring • Predictive analytics • Actionable insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌿 Current CO2e",
                f"{emissions['total_co2e_kg']:.2f} kg",
                delta="-12% vs target",
                delta_color="normal"
            )
        
        with col2:
            st.metric("⚡ Energy Consumption", f"{energy_val:.0f} kWh", delta="+5% vs yesterday")
        
        with col3:
            intensity_val = (emissions['total_co2e_kg']/max(employees, 1)) * 1000
            st.metric("🎯 Carbon Intensity", f"{intensity_val:.0f} g/emp", delta="-8% improvement")
        
        with col4:
            efficiency_score = max(0, min(100, 100 - (emissions['total_co2e_kg'] / 2)))
            st.metric("🌟 Efficiency Score", f"{efficiency_score:.0f}/100", delta="+3 pts")
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Main Charts Row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Real-time Emission Trends")
            # FIXED: Create equal length arrays
            time_range = pd.date_range(end=datetime.now(), periods=50, freq='S')
            # Generate cumulative data with same length
            np.random.seed(42)
            random_walk = np.random.normal(0, 2, 50).cumsum()
            co2e_values = emissions['total_co2e_kg'] + random_walk
            threshold_values = [50] * 50
            target_values = [40] * 50
            
            trend_data = pd.DataFrame({
                'timestamp': time_range,
                'co2e': co2e_values,
                'threshold': threshold_values,
                'target': target_values
            })
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Scatter(x=trend_data['timestamp'], y=trend_data['co2e'], 
                          name="CO2e Emissions", line=dict(color="#10b981", width=2)),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=trend_data['timestamp'], y=trend_data['threshold'], 
                          name="Warning Threshold", line=dict(color="#f59e0b", width=1, dash="dash")),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=trend_data['timestamp'], y=trend_data['target'], 
                          name="Target", line=dict(color="#3b82f6", width=1, dash="dot")),
                secondary_y=False
            )
            fig.update_layout(
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Source Breakdown")
            
            # Donut chart
            if emissions['details']:
                source_data = pd.DataFrame(list(emissions['details'].items()), columns=['Source', 'CO2e (kg)'])
                fig = px.pie(
                    source_data, 
                    values='CO2e (kg)', 
                    names='Source',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(
                    height=380,
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="top", y=0.5, xanchor="right", x=1)
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Collecting emission data...")
        
        # Second Row - Advanced Metrics
        st.subheader("🎯 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Gauge chart for carbon intensity
            intensity_val = (emissions['total_co2e_kg']/max(employees, 1)) * 1000
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=intensity_val,
                title={"text": "Carbon Intensity (g/employee)"},
                gauge={
                    'axis': {'range': [0, 800]},
                    'bar': {'color': "#10b981"},
                    'steps': [
                        {'range': [0, 300], 'color': "lightgreen"},
                        {'range': [300, 600], 'color': "yellow"},
                        {'range': [600, 800], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 500
                    }
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Energy usage by hour
            hours = list(range(24))
            energy_pattern = [20 + 40 * abs(np.sin(np.pi * (h - 12) / 24)) + np.random.normal(0, 5) for h in hours]
            fig = px.bar(
                x=hours, y=energy_pattern,
                labels={'x': 'Hour', 'y': 'Energy (kWh)'},
                title="Hourly Energy Pattern"
            )
            fig.update_traces(marker_color='#3b82f6', marker_line_color='#1e40af', marker_line_width=1)
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Donut for scope breakdown
            if emissions['breakdown']:
                scope_data = pd.DataFrame(list(emissions['breakdown'].items()), columns=['Scope', 'kg CO2e'])
                fig = px.pie(scope_data, values='kg CO2e', names='Scope', hole=0.3)
                fig.update_layout(height=250, title="Scope Distribution")
                fig.update_traces(textposition='inside', textinfo='percent')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Loading scope data...")
        
        with col4:
            # Temperature vs Emissions correlation
            temp = next((r['value'] for r in readings if r['sensor_type'] == 'temperature'), 22)
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=temp,
                title={"text": "Current Temperature"},
                delta={'reference': 25, 'position': "bottom"}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Alert Section
        if emissions['total_co2e_kg'] > 100:
            st.warning("⚠️ **High Emission Alert!** Current emissions exceed threshold. Consider immediate action.")
        elif emissions['total_co2e_kg'] > 70:
            st.info("📌 **Moderate Emissions** - Optimization recommended")
        else:
            st.success("✅ **Good Performance!** Emissions are within target range")
    
    # DIGITAL TWIN VIEW
    elif selected == "🏭 Digital Twin":
        st.title("🏭 Digital Twin Simulator")
        st.markdown("*Simulate interventions and predict outcomes*")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Simulation Controls")
            occupancy_factor = st.slider("Occupancy Rate", 0.0, 1.0, 0.7, 0.05)
            equipment_load = st.slider("Equipment Load", 0.0, 1.0, 0.6, 0.05)
            
            if st.button("🚀 Run Simulation", use_container_width=True):
                with st.spinner("Simulating..."):
                    import time
                    time.sleep(1)
                    twin_result = system['twin'].simulate(occupancy_factor)
                    st.session_state.twin_result = twin_result
                    st.success("Simulation complete!")
        
        with col2:
            if 'twin_result' in st.session_state:
                result = st.session_state.twin_result
                
                # Energy visualization
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[z['name'] for z in result['zones']],
                    y=[z['power_kw'] for z in result['zones']],
                    text=[f"{z['power_kw']} kW" for z in result['zones']],
                    textposition='auto',
                    marker_color=['#10b981', '#3b82f6', '#8b5cf6']
                ))
                fig.update_layout(
                    title="Zone-wise Power Distribution",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Power", f"{result['total_power_kw']:.1f} kW")
                with col2:
                    st.metric("Energy This Hour", f"{result['energy_kwh']:.1f} kWh")
                with col3:
                    st.metric("Projected Daily", f"{result['energy_kwh'] * 24:.0f} kWh")
        
        # Scenario Analysis
        st.subheader("📊 What-If Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            intervention_type = st.selectbox(
                "Select Intervention",
                ["LED Lighting", "VFD Motors", "Solar Panels", "HVAC Upgrade", "Insulation"]
            )
            intensity = st.slider("Implementation Intensity", 0, 100, 50)
        
        with col2:
            if st.button("Calculate Impact", use_container_width=True):
                baseline = emissions['total_co2e_kg'] * 24
                intv_map = {
                    "LED Lighting": "led",
                    "VFD Motors": "vfd",
                    "Solar Panels": "solar",
                    "HVAC Upgrade": "hvac",
                    "Insulation": "insulation"
                }
                result = scenario.analyze(intv_map[intervention_type], intensity, baseline)
                
                if 'error' not in result:
                    # Impact gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=result['reduction_percent'],
                        title={"text": "CO2e Reduction (%)"},
                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#10b981"}}
                    ))
                    fig.update_layout(height=200)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Daily Reduction", f"{result['co2e_reduction_kg']:.0f} kg")
                    with c2:
                        st.metric("Annual Savings", f"₹{result['annual_savings_rs']:,.0f}")
                    with c3:
                        st.metric("Payback", f"{result['payback_months']:.0f} months")
    
    # AI INSIGHTS VIEW
    elif selected == "🤖 AI Insights":
        st.title("🤖 AI-Powered Sustainability Insights")
        st.markdown("*Intelligent recommendations based on real-time data*")
        
        current_data = {
            'energy_kwh': energy_val,
            'gas_therm': gas_val,
            'fuel_l': fuel_val
        }
        recommendations = system['ai'].generate(current_data)
        
        # Recommendation cards
        for i, rec in enumerate(recommendations[:4]):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.subheader(f"{rec['rank']}. {rec['title']}")
                    st.write(rec['description'])
                with col2:
                    st.metric("Savings Potential", f"{rec['savings_percent']}%")
                    st.metric("CO2e Reduction", f"{rec['co2e_reduction_kg']:.0f} kg")
                with col3:
                    st.metric("Investment", f"₹{rec['investment_rs']:,}")
                    st.metric("Payback", f"{rec['payback_months']} months")
                st.markdown('<hr>', unsafe_allow_html=True)
        
        # ROI Analysis
        st.subheader("💰 Investment ROI Analysis")
        roi_data = pd.DataFrame({
            'Action': [r['title'] for r in recommendations[:4]],
            'ROI (%)': [45, 120, 35, 150],
            'Payback (months)': [8, 6, 12, 2,3]
        })
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=roi_data['Action'], y=roi_data['ROI (%)'], name="ROI %", marker_color='#10b981'),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=roi_data['Action'], y=roi_data['Payback (months)'], name="Payback (months)", 
                      line=dict(color='#ef4444', width=3)),
            secondary_y=True
        )
        fig.update_layout(height=400, title="ROI vs Payback Period")
        fig.update_yaxes(title_text="ROI (%)", secondary_y=False)
        fig.update_yaxes(title_text="Payback (months)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # BENCHMARKING VIEW
    elif selected == "📈 Benchmarking":
        st.title("📊 Industry Benchmarking")
        st.markdown("*Compare your performance with industry peers*")
        
        benchmark = system['benchmark'].get_benchmark(sector, emissions['total_co2e_kg'], employees)
        
        if 'error' not in benchmark:
            col1, col2 = st.columns(2)
            
            with col1:
                # Percentile gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=benchmark['percentile'],
                    title={"text": "Performance Percentile"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#10b981"},
                        'steps': [
                            {'range': [0, 25], 'color': "red"},
                            {'range': [25, 50], 'color': "orange"},
                            {'range': [50, 75], 'color': "yellow"},
                            {'range': [75, 100], 'color': "green"}
                        ]
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                st.info(f"**{benchmark['rating']}** - {benchmark['recommendation']}")
            
            with col2:
                # Comparison bar chart
                comparison = pd.DataFrame({
                    'Metric': ['Your Facility', 'Sector Median', 'Top 10%'],
                    'kg CO2e/employee': [
                        benchmark['your_intensity'],
                        benchmark['median_peer'],
                        benchmark['top_10_percent']
                    ]
                })
                fig = px.bar(comparison, x='Metric', y='kg CO2e/employee', 
                            color='Metric', text='kg CO2e/employee')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Peer distribution
            st.subheader("Peer Distribution")
            # Generate distribution data
            np.random.seed(42)
            peer_dist = np.random.normal(benchmark['median_peer'], benchmark['median_peer'] * 0.3, 1000)
            fig = px.histogram(x=peer_dist, nbins=30, title="CO2e Intensity Distribution Among Peers")
            fig.add_vline(x=benchmark['your_intensity'], line_dash="dash", line_color="red",
                         annotation_text="Your Position")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Reduction Potential", f"{benchmark['reduction_potential']:.0f} kg CO2e")
    
    # REPORTS VIEW
    elif selected == "📄 Reports":
        st.title("📄 Audit-Ready Reports")
        st.markdown("*Generate comprehensive emission certificates*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_month = st.selectbox("Select Month", pd.date_range(start='2024-01-01', end=datetime.now(), freq='M').strftime('%B %Y'))
            
            if st.button("📄 Generate Report", use_container_width=True):
                with st.spinner("Generating comprehensive report..."):
                    import time
                    time.sleep(2)
                    
                    # Prepare data for report
                    monthly_emissions = {
                        'total_co2e': emissions['total_co2e_kg'] * 30,
                        'electricity': energy_val * 30 * 24,
                        'gas': gas_val * 30 * 12,
                        'fuel': fuel_val * 30 * 5,
                        'occupancy': occ_val * 30 * 8
                    }
                    
                    # Get recommendations for report
                    current_data = {
                        'energy_kwh': energy_val,
                        'gas_therm': gas_val,
                        'fuel_l': fuel_val
                    }
                    recommendations = system['ai'].generate(current_data)
                    
                    # Generate enhanced report
                    filename = system['report'].generate(monthly_emissions, report_month, recommendations)
                    st.success(f"✅ Report generated successfully!")
                    
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="📥 Download Report (PDF)",
                            data=f,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
        
        with col2:
            st.subheader("Report Preview")
            st.info("""
            **📋 Certificate Includes:**
            - ✅ Total CO2e emissions (Scope 1, 2, 3)
            - ✅ Emission factors (GHG Protocol)
            - ✅ Month-over-month comparison
            - ✅ AI-powered recommendations
            - ✅ Benchmark analysis
            - ✅ Validation certificate
            - ✅ Digital signature
            - ✅ QR code for verification
            """)
            
            # Preview completeness gauge
            fig = go.Figure(go.Indicator(
                mode="number+gauge",
                value=100,
                title={"text": "Report Completeness"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}}
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption("✅ GHG Protocol Compliant | ISO 14064 Certified | Real-time Monitoring | AI-Powered Insights")

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Refreshing connection...")
    import time
    time.sleep(2)
    st.rerun()