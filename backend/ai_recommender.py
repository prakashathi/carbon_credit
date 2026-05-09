import numpy as np
from typing import Dict, List
from datetime import datetime

class AIRecommender:
    """AI-powered emission reduction recommendations"""
    
    def __init__(self):
        self.recommendations_history = []
    
    def generate(self, current_data: Dict) -> List[Dict]:
        """Generate recommendations based on current data"""
        recommendations = []
        
        energy = current_data.get('energy_kwh', 500)
        gas = current_data.get('gas_therm', 100)
        fuel = current_data.get('fuel_l', 50)
        
        # Energy efficiency
        if energy > 600:
            recommendations.append({
                'id': 'E001',
                'title': 'Reduce Energy Consumption',
                'description': 'Install VFDs on motors and optimize compressed air',
                'savings_percent': 18,
                'co2e_reduction_kg': energy * 0.45 * 0.18,
                'investment_rs': 250000,
                'payback_months': 8,
                'priority': 'High'
            })
        
        # Lighting
        recommendations.append({
            'id': 'L001',
            'title': 'LED Lighting Retrofit',
            'description': 'Replace all lighting with energy-efficient LEDs',
            'savings_percent': 65,
            'co2e_reduction_kg': energy * 0.45 * 0.65 * 0.3,
            'investment_rs': 150000,
            'payback_months': 6,
            'priority': 'Medium'
        })
        
        # Solar
        if energy > 1000:
            recommendations.append({
                'id': 'S001',
                'title': 'Solar PV Installation',
                'description': 'Install rooftop solar system',
                'savings_percent': 40,
                'co2e_reduction_kg': energy * 0.45 * 0.40,
                'investment_rs': 800000,
                'payback_months': 36,
                'priority': 'Medium'
            })
        
        # Gas optimization
        if gas > 150:
            recommendations.append({
                'id': 'G001',
                'title': 'Natural Gas Optimization',
                'description': 'Tune boiler and recover waste heat',
                'savings_percent': 15,
                'co2e_reduction_kg': gas * 5.3 * 0.15,
                'investment_rs': 85000,
                'payback_months': 5,
                'priority': 'High'
            })
        
        # Behavioral
        recommendations.append({
            'id': 'B001',
            'title': 'Employee Awareness Program',
            'description': 'Train staff on energy conservation',
            'savings_percent': 8,
            'co2e_reduction_kg': energy * 0.45 * 0.08,
            'investment_rs': 35000,
            'payback_months': 2,
            'priority': 'Low'
        })
        
        # Sort by CO2e reduction
        recommendations.sort(key=lambda x: x['co2e_reduction_kg'], reverse=True)
        
        # Add rank and timestamp
        for i, rec in enumerate(recommendations[:5], 1):
            rec['rank'] = i
            rec['timestamp'] = datetime.now().isoformat()
        
        self.recommendations_history.extend(recommendations[:5])
        return recommendations[:5]
    
    def get_summary(self) -> Dict:
        """Get summary of all recommendations"""
        if not self.recommendations_history:
            return {'total_recommendations': 0}
        
        total_savings = sum(r['co2e_reduction_kg'] for r in self.recommendations_history)
        total_investment = sum(r['investment_rs'] for r in self.recommendations_history)
        
        return {
            'total_recommendations': len(self.recommendations_history),
            'total_co2e_savings_kg': round(total_savings, 2),
            'total_investment_rs': round(total_investment, 2),
            'avg_payback_months': round(np.mean([r['payback_months'] for r in self.recommendations_history]), 1)
        }