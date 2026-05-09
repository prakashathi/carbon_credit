"""
Carbon Credits Marketplace UI Component
For integration into main dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_carbon_market(carbon_engine, company_id="ECO001", current_emissions=None):
    """Render carbon credits marketplace in dashboard"""
    
    st.markdown("---")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Market Overview Section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); padding: 1.5rem; border-radius: 1rem; margin-bottom: 1.5rem;'>
        <h2 style='color: white; margin: 0;'>🌱 Carbon Credits Marketplace</h2>
        <p style='color: #d8f3dc; margin: 0.5rem 0 0 0;'>Offset your emissions by supporting sustainable farming</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Market Stats
    market_summary = carbon_engine.get_market_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Current Price", f"₹{market_summary['market_price_rs_per_kg']}/kg CO2e",
                 delta=f"₹{market_summary['market_price_rs_per_ton']:,}/ton")
    with col2:
        st.metric("🌾 Available Credits", f"{market_summary['total_credits_available_tons']:.0f} tons",
                 help="Carbon credits available for purchase")
    with col3:
        st.metric("👨‍🌾 Active Farmers", f"{market_summary['active_farmers']:,}",
                 help="Farmers selling verified carbon credits")
    with col4:
        st.metric("🌳 Impact Potential", f"{market_summary['potential_trees']:,.0f} trees",
                 help="Equivalent trees that could be planted")
    
    # Company Credits Needed (if emissions provided)
    if current_emissions:
        st.subheader("📊 Your Carbon Offset Requirement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_reduction = st.slider("Target Emission Reduction", 0, 50, 30, 5,
                                        help="Percentage of emissions you want to offset")
            
            credits_needed = carbon_engine.calculate_company_credits_needed(
                current_emissions, target_reduction
            )
            
            st.info(f"""
            **Your Carbon Footprint Summary:**
            - Annual Emissions: **{credits_needed['current_annual_emissions_tons']:.1f} tons CO2e**
            - Target Reduction: **{target_reduction}%**
            - Credits Needed: **{credits_needed['credits_needed_tons']:.1f} tons**
            - Estimated Cost: **₹{credits_needed['estimated_cost_rs']:,.0f}**
            """)
        
        with col2:
            impact = carbon_engine.calculate_impact(credits_needed['credits_needed_kg'])
            st.markdown(f"""
            <div style='background: #e8f5e9; padding: 1rem; border-radius: 0.5rem;'>
                <h4 style='color: #2e7d32; margin-top: 0;'>🌍 Environmental Impact</h4>
                <p>🌳 Trees Equivalent: <strong>{impact['trees_planted_equivalent']:,.0f}</strong></p>
                <p>🚗 Cars Off Road: <strong>{impact['cars_removed_annual']:.0f}</strong> per year</p>
                <p>🏠 Households Powered: <strong>{impact['households_powered']:.0f}</strong></p>
                <p>👨‍🌾 Farmer Income: <strong>₹{impact['farmer_income_rs']:,.0f}</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Marketplace Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🌾 Browse Farmers", "📈 Market Analytics", "📜 My Credits", "🌿 Impact Stories"])
    
    with tab1:
        st.subheader("🌾 Farmers Selling Carbon Credits")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            farmers_df_all = carbon_engine.get_available_farmers()
            states = farmers_df_all['state'].unique()
            filter_state = st.selectbox("Filter by State", ["All"] + list(states))
        
        with col2:
            practices = farmers_df_all['practice'].unique()
            filter_practice = st.selectbox("Filter by Practice", ["All"] + list(practices))
        
        with col3:
            min_credits = st.number_input("Min Credits (tons)", 0, 100, 0)
        
        with col4:
            max_price = st.number_input("Max Price (₹/kg)", 0, 200, 100)
        
        # Get filtered farmers
        farmers_df = carbon_engine.get_available_farmers(
            state=None if filter_state == "All" else filter_state,
            practice=None if filter_practice == "All" else filter_practice,
            min_credits=min_credits * 1000 if min_credits > 0 else None,
            max_price=max_price if max_price < 100 else None
        )
        
        # Display farmers
        for idx, farmer in farmers_df.head(10).iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1.5])
                
                with col1:
                    st.markdown(f"""
                    **👨‍🌾 {farmer['name']}**  
                    📍 {farmer['state']} - {farmer['district']}  
                    🌾 {farmer['practice']}
                    """)
                
                with col2:
                    st.metric("Available Credits", 
                             f"{farmer['available_credits_kg']/1000:.1f} tons")
                
                with col3:
                    st.metric("Price", f"₹{farmer['price_per_kg']}/kg")
                
                with col4:
                    status = "✅ Verified" if farmer['certified'] else "🔄 Pending"
                    st.metric("Status", status)
                
                with col5:
                    max_buy = int(min(farmer['available_credits_kg'], 10000))
                    credits_kg = st.number_input(f"Buy (kg)", 
                                                key=f"buy_{farmer['farmer_id']}",
                                                min_value=100,
                                                max_value=max_buy,
                                                step=100,
                                                value=min(1000, max_buy))
                    
                    if st.button(f"Purchase", key=f"purchase_{farmer['farmer_id']}"):
                        result = carbon_engine.purchase_credits(
                            company_id, farmer['farmer_id'], credits_kg
                        )
                        if result.get('success'):
                            st.success(f"""
                            ✅ **Purchase Successful!**
                            - Credits: {result['credits_purchased_tons']:.2f} tons CO2e
                            - Cost: ₹{result['total_cost_rs']:,.0f}
                            - Farmer: {result['farmer_name']}
                            - Impact: {result['impact']['trees_planted_equivalent']:.0f} trees equivalent
                            """)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"Purchase failed: {result.get('error', 'Unknown error')}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📈 Carbon Market Analytics")
        
        # Price distribution by practice
        farmers_df = carbon_engine.get_available_farmers()
        fig = px.box(farmers_df, x='practice', y='price_per_kg', 
                    title="Credit Price Distribution by Practice",
                    color='practice')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Credits available by state
        state_credits = farmers_df.groupby('state')['available_credits_kg'].sum().reset_index()
        state_credits['available_tons'] = state_credits['available_credits_kg'] / 1000
        fig = px.bar(state_credits, x='state', y='available_tons',
                    title="Available Credits by State (tons)",
                    color='available_tons', color_continuous_scale='Greens')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Practice distribution
        practice_dist = carbon_engine.get_farmer_summary()['practice_distribution']
        practice_df = pd.DataFrame(list(practice_dist.items()), columns=['Practice', 'Farmers'])
        fig = px.pie(practice_df, values='Farmers', names='Practice',
                    title="Farmer Distribution by Carbon Practice",
                    color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📜 Your Carbon Credit Portfolio")
        
        # Get company credits summary
        company_summary = carbon_engine.get_company_credits_summary(company_id)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Credits Purchased", 
                     f"{company_summary['total_credits_purchased_tons']:.2f} tons")
        with col2:
            st.metric("Total Investment", f"₹{company_summary['total_spent_rs']:,.0f}")
        with col3:
            st.metric("Transactions", company_summary['transaction_count'])
        
        if company_summary['transactions']:
            transactions_df = pd.DataFrame(company_summary['transactions'])
            transactions_df['date'] = pd.to_datetime(transactions_df['timestamp']).dt.date
            display_df = transactions_df[['date', 'farmer_name', 'farmer_state', 
                                         'practice', 'credits_tons', 'total_cost']]
            display_df.columns = ['Date', 'Farmer', 'State', 'Practice', 'Credits (tons)', 'Cost (₹)']
            st.dataframe(display_df, use_container_width=True)
            
            # Total impact
            total_credits = company_summary['total_credits_purchased_kg']
            impact = carbon_engine.calculate_impact(total_credits)
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 1.5rem; border-radius: 1rem; margin-top: 1rem;'>
                <h3 style='color: #1b5e20; margin-top: 0;'>🌍 Your Environmental Impact</h3>
                <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;'>
                    <div><strong>🌳 Trees:</strong> {impact['trees_planted_equivalent']:.0f}</div>
                    <div><strong>🚗 Cars Off Road:</strong> {impact['cars_removed_annual']:.0f}/year</div>
                    <div><strong>🏠 Households:</strong> {impact['households_powered']:.0f}</div>
                    <div><strong>👨‍🌾 Farmers Supported:</strong> {len(transactions_df['farmer_name'].unique())}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("You haven't purchased any carbon credits yet. Browse farmers above to start offsetting your emissions.")
    
    with tab4:
        st.subheader("🌿 Impact Stories from Our Farmers")
        
        # Sample impact stories
        stories = [
            {
                'farmer': 'Rajesh Kumar',
                'state': 'Punjab',
                'practice': 'Tree Plantation',
                'story': 'Planted 5,000 trees on 10 acres, earning ₹2.5L through carbon credits',
                'image': '🌳',
                'impact': '500 tons CO2e sequestered'
            },
            {
                'farmer': 'Savitri Devi',
                'state': 'Karnataka',
                'practice': 'Organic Farming',
                'story': 'Converted 15 acres to organic, reduced chemical fertilizers by 80%',
                'image': '🌾',
                'impact': '300 tons CO2e saved'
            },
            {
                'farmer': 'Mohan Singh',
                'state': 'Uttar Pradesh',
                'practice': 'Agroforestry',
                'story': 'Integrated 2,000 fruit trees with crops, diversified income',
                'image': '🥭',
                'impact': '750 tons CO2e sequestered'
            }
        ]
        
        for story in stories:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"<h1 style='font-size: 4rem;'>{story['image']}</h1>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    **👨‍🌾 {story['farmer']}** - 📍 {story['state']}  
                    *{story['practice']}*  
                    {story['story']}  
                    🌿 **Impact:** {story['impact']}
                    """)
                st.markdown("<hr>", unsafe_allow_html=True)
        
        st.info("""
        💡 **Did You Know?**  
        Every ₹1,000 spent on carbon credits:
        - 🌳 Supports planting of 20+ trees
        - 👨‍🌾 Provides direct income to small farmers
        - 🌍 Offsets 20 kg of CO2e emissions
        - 🏡 Supports rural livelihoods
        """)