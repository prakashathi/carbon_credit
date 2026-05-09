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
from PIL import Image
import base64
from io import BytesIO

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
    page_title="EcoPlus AI - Carbon Intelligence Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Company Branding
COMPANY_NAME = "EcoPlus AI"
COMPANY_TAGLINE = "Intelligent Carbon Management for Sustainable Enterprises"

# Custom CSS for Professional UI
st.markdown(f"""
<style>
    /* Main container */
    .main {{
        padding: 0rem 1rem;
    }}
    
    /* Header styling */
    .header {{
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
        padding: 1rem 2rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        color: white;
    }}
    
    /* Footer styling */
    .footer {{
        background: #1f2937;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-top: 2rem;
        color: #9ca3af;
        text-align: center;
    }}
    
    /* Custom divider */
    .custom-divider {{
        height: 3px;
        background: linear-gradient(90deg, #14b8a6, #0f766e, #0d9488);
        border-radius: 3px;
        margin: 1rem 0;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 1rem;
        border-left: 4px solid #10b981;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    /* Status indicators */
    .status-good {{
        color: #10b981;
        font-weight: bold;
    }}
    
    .status-warning {{
        color: #f59e0b;
        font-weight: bold;
    }}
    
    .status-critical {{
        color: #ef4444;
        font-weight: bold;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: #f8fafc;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15,118,110,0.3);
    }}
    
    /* Industry selector highlight */
    .industry-selector {{
        background: #e0f2fe;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }}
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

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("https://img.icons8.com/color/96/000000/earth-planet.png", width=70)
with col2:
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1 style='color: #0f766e; margin-bottom: 0;'>{COMPANY_NAME}</h1>
        <p style='color: #6b7280; margin-top: 0;'>{COMPANY_TAGLINE}</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("<div style='text-align: right; font-size: 0.8rem; color: #6b7280;'>v3.0 | Enterprise</div>", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Simple navigation with icons
def render_navigation():
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 1rem 0;'>
        <h3 style='color: #0f766e;'>🌿 {COMPANY_NAME}</h3>
        <p style='font-size: 0.8rem; color: #6b7280;'>Carbon Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "📊 Executive Dashboard"
    
    nav_options = {
        "📊 Executive Dashboard": "Dashboard",
        "🏭 Digital Twin": "Digital Twin", 
        "🤖 AI Sustainability Advisor": "AI Insights",
        "📈 Industry Benchmarking": "Benchmarking",
        "📄 Audit Reports": "Reports"
    }
    
    for display, key in nav_options.items():
        button_style = "primary" if st.session_state.selected_page == display else "secondary"
        if st.sidebar.button(display, key=key, use_container_width=True):
            st.session_state.selected_page = display
    
    return st.session_state.selected_page

# Sidebar with industry selector
with st.sidebar:
    selected = render_navigation()
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 🏭 Facility Profile")
    sector = st.selectbox(
        "Industry Sector",
        ["Manufacturing", "Retail", "IT Services", "Warehousing", "FoodProcessing", "Logistics"],
        help="Select your primary industry sector for accurate benchmarking"
    )
    
    # Sub-sector options based on sector
    sub_sector_options = {
        "Manufacturing": ["Textile", "Automotive", "Electronics", "Chemical", "Pharma", "Metal", "Plastics"],
        "Retail": ["Apparel", "Grocery", "Electronics", "Furniture", "Pharmacy", "DepartmentStore"],
        "IT Services": ["Software", "Cloud", "Consulting", "DataCenter", "SaaS", "Cybersecurity", "FinTech"],
        "Warehousing": ["Logistics", "ColdStorage", "Distribution", "Fulfillment", "CrossDock", "AutomotiveParts", "Ecommerce"],
        "FoodProcessing": ["Dairy", "Bakery", "Beverages", "Meat", "Grain", "Snacks"],
        "Logistics": ["Trucking", "Shipping", "Rail", "AirCargo", "LastMile", "Courier"]
    }
    
    sub_sector = st.selectbox("Sub-Sector", sub_sector_options.get(sector, ["General"]))
    employees = st.number_input("👥 Employees", 10, 500, 75, step=5)
    region = st.selectbox("📍 Region", ["North", "South", "East", "West", "Central"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Live Controls")
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
    energy_val = next((r['value'] for r in readings if r['sensor_type'] == 'energy'), 50)
    gas_val = next((r['value'] for r in readings if r['sensor_type'] == 'gas'), 10)
    fuel_val = next((r['value'] for r in readings if r['sensor_type'] == 'fuel'), 5)
    occ_val = next((r['value'] for r in readings if r['sensor_type'] == 'occupancy'), 25)
    
    # Get benchmark data
    benchmark = system['benchmark'].get_benchmark(sector, emissions['total_co2e_kg'], employees, sub_sector, region)
    
    # EXECUTIVE DASHBOARD VIEW
    if selected == "📊 Executive Dashboard":
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%); padding: 1.5rem; border-radius: 1rem; margin-bottom: 1.5rem;'>
            <h2 style='color: white; margin: 0;'>Executive Carbon Dashboard</h2>
            <p style='color: #ccfbf1; margin: 0.5rem 0 0 0;'>{sector} | {sub_sector} | {region} | {employees} employees</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top KPIs Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🌿 Current CO2e", f"{emissions['total_co2e_kg']:.2f} kg", 
                     delta=f"{benchmark.get('reduction_percentage', 0):.0f}% vs target")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("⚡ Energy Intensity", f"{energy_val:.0f} kWh", 
                     delta=f"{benchmark.get('avg_efficiency_score', 0):.0f} efficiency score")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            intensity_val = (emissions['total_co2e_kg']/max(employees, 1)) * 1000
            st.metric("🎯 Carbon Intensity", f"{intensity_val:.0f} g/employee", 
                     delta=f"vs {benchmark.get('median_peer', 0):.0f} g industry avg")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            efficiency_score = benchmark.get('avg_efficiency_score', 65)
            st.metric("🌟 Eco Rating", f"{efficiency_score:.0f}/100", 
                     delta=f"{benchmark.get('percentile', 0):.0f}th percentile")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Main Charts Row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Real-time Emission Intelligence")
            time_range = pd.date_range(end=datetime.now(), periods=50, freq='s')
            np.random.seed(42)
            co2e_values = emissions['total_co2e_kg'] + np.cumsum(np.random.normal(0, 0.3, 50))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_range, y=np.maximum(co2e_values, 0), 
                      name="Current CO2e", line=dict(color="#14b8a6", width=2),
                      fill='tozeroy', fillcolor='rgba(20,184,166,0.1)'))
            fig.add_trace(go.Scatter(x=time_range, y=[75] * 50, 
                      name="Warning Threshold", line=dict(color="#f59e0b", width=1.5, dash="dash")))
            fig.add_trace(go.Scatter(x=time_range, y=[benchmark.get('median_peer', 60)] * 50, 
                      name="Industry Median", line=dict(color="#8b5cf6", width=1.5, dash="dot")))
            fig.update_layout(
                height=400,
                hovermode='x unified',
                yaxis_title="CO2e (kg)",
                xaxis_title="Time",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Emission Breakdown")
            if emissions['details']:
                source_data = pd.DataFrame(list(emissions['details'].items()), columns=['Source', 'CO2e (kg)'])
                fig = px.pie(source_data, values='CO2e (kg)', names='Source', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Teal_r)
                fig.update_layout(height=380, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        # Industry Comparison Section
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.subheader("🏭 Industry Benchmarking Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=benchmark['percentile'],
                title={"text": "Your Industry Percentile"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#14b8a6"},
                    'steps': [
                        {'range': [0, 25], 'color': "#fee2e2"},
                        {'range': [25, 50], 'color': "#fed7aa"},
                        {'range': [50, 75], 'color': "#d9f99d"},
                        {'range': [75, 100], 'color': "#a7f3d0"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            comparison_data = pd.DataFrame({
                'Metric': ['Your Facility', f'{sector} Median', 'Top 10%'],
                'kg CO2e/employee': [
                    benchmark['your_intensity'],
                    benchmark['median_peer'],
                    benchmark['top_10_percent']
                ]
            })
            fig = px.bar(comparison_data, x='Metric', y='kg CO2e/employee', 
                        color='Metric', text='kg CO2e/employee',
                        color_discrete_sequence=['#0f766e', '#94a3b8', '#10b981'])
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: #f0fdf4; padding: 1rem; border-radius: 1rem;'>
                <h4 style='color: #0f766e; margin-top: 0;'>Performance Summary</h4>
                <p><strong>Rating:</strong> {benchmark['rating']}</p>
                <p><strong>Better than:</strong> {100 - benchmark['percentile']:.0f}% of peers</p>
                <p><strong>Reduction Potential:</strong> {benchmark['reduction_potential']:.0f} kg CO2e</p>
                <p><strong>Recommendation:</strong> {benchmark['recommendation'][:80]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional Industry Insights
        if benchmark.get('sub_sector_data') or benchmark.get('region_data'):
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.subheader("📊 Granular Benchmarking")
            
            col1, col2 = st.columns(2)
            
            if benchmark.get('sub_sector_data'):
                with col1:
                    sub_data = benchmark['sub_sector_data']
                    st.markdown(f"""
                    <div style='background: #e0f2fe; padding: 1rem; border-radius: 0.5rem;'>
                        <h4>🎯 {sub_data['sub_sector']} Sub-Sector</h4>
                        <p>Your Percentile: <strong>{sub_data['percentile']}th</strong></p>
                        <p>Median Intensity: <strong>{sub_data['median_intensity']} kg/employee</strong></p>
                        <p>Peer Count: <strong>{sub_data['peer_count']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if benchmark.get('region_data'):
                with col2:
                    reg_data = benchmark['region_data']
                    st.markdown(f"""
                    <div style='background: #fce7f3; padding: 1rem; border-radius: 0.5rem;'>
                        <h4>📍 {reg_data['region']} Region</h4>
                        <p>Your Percentile: <strong>{reg_data['percentile']}th</strong></p>
                        <p>Median Intensity: <strong>{reg_data['median_intensity']} kg/employee</strong></p>
                        <p>Peer Count: <strong>{reg_data['peer_count']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Alert Section
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        if emissions['total_co2e_kg'] > 100:
            st.warning("⚠️ **High Emission Alert!** Current emissions exceed threshold by 25%. Consider immediate action from AI recommendations.")
        elif emissions['total_co2e_kg'] > 70:
            st.info("📌 **Moderate Emissions Detected** - Optimization recommended. Check AI Sustainability Advisor for insights.")
        else:
            st.success("✅ **Excellent Performance!** Emissions are well within target range. Continue best practices.")
    
    # DIGITAL TWIN VIEW (Keep existing)
    elif selected == "🏭 Digital Twin":
        st.markdown(f"<h2 style='color: #0f766e;'>🏭 Digital Twin Simulator</h2>", unsafe_allow_html=True)
        st.markdown(f"<p><i>Simulate interventions for {sector} | {sub_sector} facility</i></p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            occupancy_factor = st.slider("Occupancy Rate", 0.0, 1.0, 0.7, 0.05)
            if st.button("🚀 Run Simulation", use_container_width=True):
                with st.spinner("Simulating building physics..."):
                    import time
                    time.sleep(1)
                    twin_result = system['twin'].simulate(occupancy_factor)
                    st.session_state.twin_result = twin_result
                    st.success("Simulation complete!")
        
        with col2:
            if 'twin_result' in st.session_state:
                result = st.session_state.twin_result
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[z['name'] for z in result['zones']],
                    y=[z['power_kw'] for z in result['zones']],
                    text=[f"{z['power_kw']} kW" for z in result['zones']],
                    textposition='auto',
                    marker_color=['#14b8a6', '#0d9488', '#0f766e']
                ))
                fig.update_layout(height=300, title="Zone-wise Power Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Total Power", f"{result['total_power_kw']:.1f} kW")
                with c2:
                    st.metric("Energy/Hour", f"{result['energy_kwh']:.1f} kWh")
                with c3:
                    st.metric("Projected Daily", f"{result['energy_kwh'] * 24:.0f} kWh")
    
    # AI INSIGHTS VIEW (Keep existing)
    elif selected == "🤖 AI Sustainability Advisor":
        st.markdown(f"<h2 style='color: #0f766e;'>🤖 AI Sustainability Advisor</h2>", unsafe_allow_html=True)
        st.markdown(f"<p><i>Intelligent recommendations for {sector} | {sub_sector}</i></p>", unsafe_allow_html=True)
        
        current_data = {'energy_kwh': energy_val, 'gas_therm': gas_val, 'fuel_l': fuel_val}
        recommendations = system['ai'].generate(current_data)
        
        for i, rec in enumerate(recommendations[:4]):
            with st.expander(f"🎯 #{i+1}: {rec['title']} - {rec['priority']} Priority", expanded=(i==0)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Savings Potential", f"{rec['savings_percent']}%")
                    st.metric("CO2e Reduction", f"{rec['co2e_reduction_kg']:.0f} kg")
                with col2:
                    st.metric("Investment", f"₹{rec['investment_rs']:,}")
                    st.metric("Payback", f"{rec['payback_months']} months")
                with col3:
                    st.metric("Industry Impact", f"Top {benchmark.get('percentile', 50):.0f}%")
                st.write(f"📝 {rec['description']}")
    
    # BENCHMARKING VIEW - Enhanced with Industry Comparison
    elif selected == "📈 Industry Benchmarking":
        st.markdown(f"<h2 style='color: #0f766e;'>📈 Industry Benchmarking Report</h2>", unsafe_allow_html=True)
        st.markdown(f"<p><i>{sector} | {sub_sector} | {region} - Compared with {benchmark['peers_count']:,} industry peers</i></p>", unsafe_allow_html=True)
        
        if 'error' not in benchmark:
            # Industry Comparison Chart
            industry_comparison = system['benchmark'].get_industry_comparison()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(industry_comparison, x='Industry', y='Median (kg/emp)',
                            title="CO2e Intensity by Industry (kg CO2e per employee)",
                            color='Median (kg/emp)', color_continuous_scale='Tealgrn')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(industry_comparison, x='Avg Efficiency', y='Median (kg/emp)',
                                size='Companies', color='Industry', text='Industry',
                                title="Efficiency vs Emissions by Industry")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Your Position
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.subheader("Your Industry Position")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Your Percentile", f"{benchmark['percentile']:.0f}th",
                         delta=f"Better than {100-benchmark['percentile']:.0f}%")
            with c2:
                st.metric("Your Intensity", f"{benchmark['your_intensity']:.1f} kg/emp",
                         delta=f"vs {benchmark['median_peer']:.1f} median")
            with c3:
                st.metric("Reduction Potential", f"{benchmark['reduction_potential']:.0f} kg",
                         delta=f"{benchmark['reduction_percentage']:.0f}% improvement")
            with c4:
                st.metric("Industry Rank", f"{min(100, int(benchmark['percentile'])+1)}th",
                         delta=f"out of {benchmark['peers_count']:,}")
            
            # Distribution Chart
            np.random.seed(42)
            peer_dist = np.random.normal(benchmark['median_peer'], benchmark['median_peer'] * 0.3, 1000)
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=peer_dist, nbinsx=40, name=f'{sector} Peers',
                                      marker_color='#99f6e4', opacity=0.7))
            fig.add_vline(x=benchmark['your_intensity'], line_dash="dash", line_color="#0d9488",
                         line_width=3, annotation_text="Your Facility", annotation_position="top")
            fig.add_vline(x=benchmark['median_peer'], line_dash="dot", line_color="#f59e0b",
                         line_width=2, annotation_text="Industry Median")
            fig.update_layout(height=400, title=f"CO2e Intensity Distribution - {sector} Industry",
                             xaxis_title="kg CO2e per Employee", yaxis_title="Number of Companies")
            st.plotly_chart(fig, use_container_width=True)
            
            # Industry Trends
            st.subheader("Industry Insights")
            trends = benchmark['industry_trends']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Industry Average", f"{trends['avg_intensity']:.1f} kg/emp")
            with col2:
                st.metric("Top Performers", f"{trends['top_decile']:.1f} kg/emp")
            with col3:
                st.metric("Certification Rate", f"{benchmark['certification_rate']:.0f}%")
            with col4:
                st.metric("Avg Renewable", f"{benchmark['avg_renewable_pct']:.0f}%")
    
    # REPORTS VIEW (Keep existing)
    elif selected == "📄 Audit Reports":
        st.markdown(f"<h2 style='color: #0f766e;'>📄 Audit-Ready Reports</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_month = st.selectbox("Select Reporting Month",
                                       pd.date_range(start='2023-01-01', end=datetime.now(), freq='ME').strftime('%B %Y'))
            
            if st.button("📄 Generate Certificate", use_container_width=True):
                with st.spinner("Generating comprehensive report..."):
                    import time
                    time.sleep(2)
                    
                    monthly_emissions = {
                        'total_co2e': emissions['total_co2e_kg'] * 30,
                        'electricity': energy_val * 30 * 8,
                        'gas': gas_val * 30 * 4,
                        'fuel': fuel_val * 30 * 2,
                        'occupancy': occ_val * 30 * 8,
                        'details': emissions['details']
                    }
                    
                    current_data = {'energy_kwh': energy_val, 'gas_therm': gas_val, 'fuel_l': fuel_val}
                    recommendations = system['ai'].generate(current_data)
                    
                    filename = system['report'].generate(monthly_emissions, report_month, recommendations)
                    st.success(f"✅ Report generated!")
                    
                    with open(filename, "rb") as f:
                        st.download_button("📥 Download PDF", data=f, file_name=filename.split('/')[-1], use_container_width=True)
        
        with col2:
            st.info(f"""
            **📋 {COMPANY_NAME} Report Includes:**
            - 🏭 **Executive Summary** with key metrics
            - 📊 **Scope 1, 2, 3** emission breakdown
            - 🎯 **Industry Benchmarking** against {benchmark.get('peers_count', 2000):,}+ peers
            - 🤖 **AI Recommendations** with ROI analysis
            - ✅ **GHG Protocol** compliance certificate
            - 🔐 **Digital signature** for audit trail
            - 📈 **Trend analysis** with 12-month projection
            """)
    
    # FOOTER
    st.markdown("""
    <div class='footer'>
        <p>© 2024 EcoPlus AI - Intelligent Carbon Management Platform</p>
        <p style='font-size: 0.75rem;'>GHG Protocol Compliant | ISO 14064 Certified | Real-time Monitoring | AI-Powered</p>
        <p style='font-size: 0.7rem; margin-top: 0.5rem;'>Empowering SMEs for a Sustainable Future 🌍</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"System Alert: {str(e)}")
    st.info("🔄 Please refresh the page or contact support@ecoplus.ai")

# Sidebar Footer
with st.sidebar:
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; font-size: 0.7rem; color: #6b7280;'>
        <p>© 2024 {COMPANY_NAME}</p>
        <p>v3.0 | Enterprise</p>
        <p>support@ecoplus.ai</p>
    </div>
    """, unsafe_allow_html=True)