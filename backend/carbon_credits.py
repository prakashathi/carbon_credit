"""
Carbon Credits Marketplace Engine
Connects SME buyers with farmer sellers
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import os
from pathlib import Path

class CarbonCreditsEngine:
    """Carbon credits calculation, trading, and marketplace management"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.credits_file = self.data_dir / "carbon_credits.json"
        self.farmers_file = self.data_dir / "farmers_data.csv"
        self.transactions_file = self.data_dir / "transactions.csv"
        self._initialize_data()
        
    def _initialize_data(self):
        """Initialize carbon credits data structures"""
        # Current market price (₹ per kg CO2e)
        self.market_price = 50  # ₹50 per kg CO2e (typical Indian carbon market)
        
        # Load or create farmers data
        if not self.farmers_file.exists():
            self._generate_farmers_data()
        
        # Load or create credits data
        if not self.credits_file.exists():
            self._initialize_credits_data()
    
    def _generate_farmers_data(self):
        """Generate synthetic farmer data for carbon credit sellers"""
        farmers = []
        states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 
                  'Telangana', 'Tamil Nadu', 'Madhya Pradesh', 'Gujarat', 'Rajasthan']
        practices = ['Organic Farming', 'Tree Plantation', 'Soil Carbon Sequestration', 
                    'Agroforestry', 'Cover Cropping', 'No-Till Farming', 'Methane Capture']
        
        np.random.seed(42)
        for i in range(200):
            farmer_id = f"FRM{i+1:04d}"
            name = f"Farmer {i+1}"
            state = np.random.choice(states)
            district = f"District_{np.random.randint(1, 50)}"
            practice = np.random.choice(practices)
            land_area = np.random.uniform(1, 50)  # hectares
            
            # Carbon sequestration capacity (kg CO2e per hectare per year)
            sequestration_rates = {
                'Organic Farming': 8000,
                'Tree Plantation': 12000,
                'Soil Carbon Sequestration': 5000,
                'Agroforestry': 10000,
                'Cover Cropping': 4000,
                'No-Till Farming': 3000,
                'Methane Capture': 15000
            }
            
            rate = sequestration_rates[practice]
            total_credits = land_area * rate * np.random.uniform(0.8, 1.2)
            
            # Available credits (percentage of total)
            available_pct = np.random.uniform(0.3, 0.9)
            available_credits = total_credits * available_pct
            
            farmers.append({
                'farmer_id': farmer_id,
                'name': name,
                'state': state,
                'district': district,
                'practice': practice,
                'land_area_hectares': round(land_area, 2),
                'total_credits_kg': round(total_credits, 0),
                'available_credits_kg': round(available_credits, 0),
                'price_per_kg': round(self.market_price * np.random.uniform(0.8, 1.2), 2),
                'certified': np.random.choice([True, False], p=[0.7, 0.3]),
                'verification_status': np.random.choice(['Verified', 'Pending', 'Audited'], p=[0.6, 0.2, 0.2])
            })
        
        df = pd.DataFrame(farmers)
        df.to_csv(self.farmers_file, index=False)
    
    def _initialize_credits_data(self):
        """Initialize carbon credits data"""
        credits_data = {
            'total_credits_issued': 0,
            'total_credits_purchased': 0,
            'total_credits_retired': 0,
            'market_price_history': [],
            'transactions': []
        }
        with open(self.credits_file, 'w') as f:
            json.dump(credits_data, f)
    
    def calculate_company_credits_needed(self, current_emissions: float, target_reduction: float = 30) -> Dict:
        """
        Calculate how many carbon credits a company needs to buy
        current_emissions: kg CO2e per day
        target_reduction: percentage reduction target (default 30%)
        """
        annual_emissions = current_emissions * 365
        target_emissions = annual_emissions * (1 - target_reduction / 100)
        credits_needed = annual_emissions - target_emissions
        
        # Cost calculation
        total_cost = credits_needed * self.market_price
        
        return {
            'current_annual_emissions_kg': round(annual_emissions, 2),
            'current_annual_emissions_tons': round(annual_emissions / 1000, 2),
            'target_reduction_percent': target_reduction,
            'target_emissions_kg': round(target_emissions, 2),
            'credits_needed_kg': round(credits_needed, 2),
            'credits_needed_tons': round(credits_needed / 1000, 2),
            'estimated_cost_rs': round(total_cost, 2),
            'market_price_per_kg': self.market_price,
            'carbon_price_per_ton': self.market_price * 1000
        }
    
    def get_available_farmers(self, state: str = None, practice: str = None, 
                               min_credits: float = None, max_price: float = None) -> pd.DataFrame:
        """Get list of farmers selling carbon credits with filters"""
        farmers_df = pd.read_csv(self.farmers_file)
        
        # Apply filters
        if state:
            farmers_df = farmers_df[farmers_df['state'] == state]
        if practice:
            farmers_df = farmers_df[farmers_df['practice'] == practice]
        if min_credits:
            farmers_df = farmers_df[farmers_df['available_credits_kg'] >= min_credits]
        if max_price:
            farmers_df = farmers_df[farmers_df['price_per_kg'] <= max_price]
        
        # Sort by price (lowest first) and then by available credits
        farmers_df = farmers_df.sort_values(['price_per_kg', 'available_credits_kg'], ascending=[True, False])
        
        return farmers_df
    
    def purchase_credits(self, company_id: str, farmer_id: str, credits_kg: float) -> Dict:
        """
        Execute purchase of carbon credits from farmer
        """
        # Load current data
        farmers_df = pd.read_csv(self.farmers_file)
        with open(self.credits_file, 'r') as f:
            credits_data = json.load(f)
        
        # Find farmer
        farmer = farmers_df[farmers_df['farmer_id'] == farmer_id]
        if farmer.empty:
            return {'error': 'Farmer not found'}
        
        farmer = farmer.iloc[0]
        available = farmer['available_credits_kg']
        
        if credits_kg > available:
            return {'error': f'Insufficient credits. Only {available} kg available'}
        
        # Calculate cost
        price_per_kg = farmer['price_per_kg']
        total_cost = credits_kg * price_per_kg
        
        # Update farmer's available credits
        new_available = available - credits_kg
        farmers_df.loc[farmers_df['farmer_id'] == farmer_id, 'available_credits_kg'] = new_available
        farmers_df.to_csv(self.farmers_file, index=False)
        
        # Record transaction
        transaction = {
            'transaction_id': f'TXN{len(credits_data["transactions"]) + 1:06d}',
            'company_id': company_id,
            'farmer_id': farmer_id,
            'farmer_name': farmer['name'],
            'farmer_state': farmer['state'],
            'practice': farmer['practice'],
            'credits_kg': round(credits_kg, 2),
            'credits_tons': round(credits_kg / 1000, 2),
            'price_per_kg': price_per_kg,
            'total_cost': round(total_cost, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'Completed'
        }
        
        credits_data['transactions'].append(transaction)
        credits_data['total_credits_purchased'] += credits_kg
        credits_data['total_credits_issued'] += credits_kg
        
        # Update market price history
        credits_data['market_price_history'].append({
            'timestamp': datetime.now().isoformat(),
            'price': self.market_price,
            'volume': credits_kg
        })
        
        with open(self.credits_file, 'w') as f:
            json.dump(credits_data, f)
        
        # Also save to CSV for easy access
        transactions_df = pd.DataFrame(credits_data['transactions'])
        transactions_df.to_csv(self.transactions_file, index=False)
        
        # Calculate impact
        impact = self.calculate_impact(credits_kg)
        
        return {
            'success': True,
            'transaction_id': transaction['transaction_id'],
            'credits_purchased_kg': round(credits_kg, 2),
            'credits_purchased_tons': round(credits_kg / 1000, 2),
            'total_cost_rs': round(total_cost, 2),
            'farmer_name': farmer['name'],
            'farmer_state': farmer['state'],
            'practice': farmer['practice'],
            'price_per_kg': price_per_kg,
            'impact': impact
        }
    
    def calculate_impact(self, credits_kg: float) -> Dict:
        """Calculate environmental and social impact of carbon credits"""
        # Trees equivalent (1 tree absorbs ~21 kg CO2 per year)
        trees_equivalent = credits_kg / 21
        
        # Cars off the road (1 car emits ~4,600 kg CO2 per year)
        cars_off_road = credits_kg / 4600
        
        # Household energy equivalent (1 household ~5,000 kg CO2 per year)
        households_equivalent = credits_kg / 5000
        
        # Farmer income generated
        farmer_income = credits_kg * self.market_price * 0.8  # 80% goes to farmer
        
        return {
            'trees_planted_equivalent': round(trees_equivalent, 0),
            'cars_removed_annual': round(cars_off_road, 2),
            'households_powered': round(households_equivalent, 2),
            'farmer_income_rs': round(farmer_income, 2),
            'co2_offset_kg': round(credits_kg, 2),
            'co2_offset_tons': round(credits_kg / 1000, 2)
        }
    
    def get_company_credits_summary(self, company_id: str) -> Dict:
        """Get summary of company's carbon credit purchases"""
        if not self.transactions_file.exists():
            return {
                'total_credits_purchased_kg': 0,
                'total_credits_purchased_tons': 0,
                'total_spent_rs': 0,
                'transactions': [],
                'offset_percentage': 0,
                'transaction_count': 0
            }
        
        transactions_df = pd.read_csv(self.transactions_file)
        company_txns = transactions_df[transactions_df['company_id'] == company_id]
        
        if company_txns.empty:
            return {
                'total_credits_purchased_kg': 0,
                'total_credits_purchased_tons': 0,
                'total_spent_rs': 0,
                'transactions': [],
                'offset_percentage': 0,
                'transaction_count': 0
            }
        
        total_credits = company_txns['credits_kg'].sum()
        total_cost = company_txns['total_cost'].sum()
        
        return {
            'total_credits_purchased_kg': round(total_credits, 2),
            'total_credits_purchased_tons': round(total_credits / 1000, 2),
            'total_spent_rs': round(total_cost, 2),
            'transactions': company_txns.to_dict('records'),
            'transaction_count': len(company_txns)
        }
    
    def get_farmer_summary(self, farmer_id: str = None) -> Dict:
        """Get summary of farmer earnings and impact"""
        farmers_df = pd.read_csv(self.farmers_file)
        
        if farmer_id:
            farmer = farmers_df[farmers_df['farmer_id'] == farmer_id]
            if farmer.empty:
                return {'error': 'Farmer not found'}
            farmer = farmer.iloc[0]
            
            # Calculate earnings from transactions
            if self.transactions_file.exists():
                transactions_df = pd.read_csv(self.transactions_file)
                farmer_txns = transactions_df[transactions_df['farmer_id'] == farmer_id]
                total_sold = farmer_txns['credits_kg'].sum() if not farmer_txns.empty else 0
                total_earned = farmer_txns['total_cost'].sum() if not farmer_txns.empty else 0
            else:
                total_sold = 0
                total_earned = 0
            
            return {
                'farmer_id': farmer['farmer_id'],
                'name': farmer['name'],
                'state': farmer['state'],
                'practice': farmer['practice'],
                'land_area': farmer['land_area_hectares'],
                'available_credits_kg': farmer['available_credits_kg'],
                'total_credits_issued_kg': farmer['total_credits_kg'],
                'total_credits_sold_kg': round(total_sold, 2),
                'total_earned_rs': round(total_earned, 2),
                'price_per_kg': farmer['price_per_kg']
            }
        else:
            # Aggregate all farmers
            total_available = farmers_df['available_credits_kg'].sum()
            total_issued = farmers_df['total_credits_kg'].sum()
            avg_price = farmers_df['price_per_kg'].mean()
            
            return {
                'total_farmers': len(farmers_df),
                'total_available_credits_kg': round(total_available, 2),
                'total_available_credits_tons': round(total_available / 1000, 2),
                'total_issued_credits_kg': round(total_issued, 2),
                'average_price_rs': round(avg_price, 2),
                'practice_distribution': farmers_df['practice'].value_counts().to_dict()
            }
    
    def get_market_summary(self) -> Dict:
        """Get overall carbon market summary"""
        farmers_df = pd.read_csv(self.farmers_file)
        
        if self.credits_file.exists():
            with open(self.credits_file, 'r') as f:
                credits_data = json.load(f)
            total_purchased = credits_data.get('total_credits_purchased', 0)
        else:
            total_purchased = 0
        
        total_available = farmers_df['available_credits_kg'].sum()
        total_issued = farmers_df['total_credits_kg'].sum()
        
        # Calculate carbon offset impact
        trees_planted = total_available / 21
        
        return {
            'market_price_rs_per_kg': self.market_price,
            'market_price_rs_per_ton': self.market_price * 1000,
            'total_credits_available_kg': round(total_available, 2),
            'total_credits_available_tons': round(total_available / 1000, 2),
            'total_credits_issued_kg': round(total_issued, 2),
            'total_credits_purchased_kg': round(total_purchased, 2),
            'active_farmers': len(farmers_df),
            'potential_trees': round(trees_planted, 0),
            'total_market_value_rs': round(total_available * self.market_price, 2)
        }