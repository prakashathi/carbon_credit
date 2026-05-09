from typing import Dict, List

class ScenarioAnalyzer:
    """What-if analysis for emission reduction"""
    
    def __init__(self, digital_twin):
        self.digital_twin = digital_twin
        self.interventions = {
            'led': {
                'name': 'LED Lighting Retrofit',
                'reduction': 0.65,
                'cost': 150000,
                'co2_per_kwh': 0.45
            },
            'vfd': {
                'name': 'VFD Installation',
                'reduction': 0.30,
                'cost': 350000,
                'co2_per_kwh': 0.45
            },
            'solar': {
                'name': 'Solar Panels',
                'reduction': 0.40,
                'cost': 800000,
                'co2_per_kwh': 0.45
            },
            'hvac': {
                'name': 'HVAC Optimization',
                'reduction': 0.25,
                'cost': 200000,
                'co2_per_kwh': 0.45
            },
            'insulation': {
                'name': 'Building Insulation',
                'reduction': 0.18,
                'cost': 180000,
                'co2_per_kwh': 0.45
            }
        }
    
    def analyze(self, intervention_id: str, intensity: float, baseline_emissions: float) -> Dict:
        """Analyze a single intervention"""
        if intervention_id not in self.interventions:
            return {'error': f'Unknown intervention: {intervention_id}'}
        
        intv = self.interventions[intervention_id]
        reduction = baseline_emissions * intv['reduction'] * (intensity / 100)
        
        annual_savings = reduction * 365 * 5  # ₹5 per kg CO2e
        payback_months = (intv['cost'] / annual_savings) * 12 if annual_savings > 0 else 999
        
        return {
            'name': intv['name'],
            'co2e_reduction_kg': round(reduction, 2),
            'reduction_percent': round(intv['reduction'] * intensity, 1),
            'cost_rs': intv['cost'],
            'annual_savings_rs': round(annual_savings, 2),
            'payback_months': round(payback_months, 1),
            'roi_percent': round((annual_savings / intv['cost']) * 100, 1)
        }
    
    def optimize(self, baseline_emissions: float, budget: float) -> Dict:
        """Find optimal combination of interventions"""
        candidates = []
        for intv_id in self.interventions:
            result = self.analyze(intv_id, 100, baseline_emissions)
            if result['cost_rs'] <= budget:
                candidates.append(result)
        
        # Sort by reduction per rupee
        candidates.sort(key=lambda x: x['co2e_reduction_kg'] / x['cost_rs'], reverse=True)
        
        selected = []
        remaining = budget
        total_reduction = 0
        
        for candidate in candidates:
            if candidate['cost_rs'] <= remaining:
                selected.append(candidate)
                remaining -= candidate['cost_rs']
                total_reduction += candidate['co2e_reduction_kg']
        
        return {
            'portfolio': selected,
            'total_reduction_kg': round(total_reduction, 2),
            'total_cost_rs': round(budget - remaining, 2),
            'remaining_budget_rs': round(remaining, 2),
            'recommendations_count': len(selected)
        }