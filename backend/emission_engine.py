import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime

class EmissionEngine:
    """CO2e calculation using standard emission factors"""
    
    def __init__(self):
        self.factors = {
            'electricity': 0.45,    # kg CO2e per kWh
            'natural_gas': 5.3,     # kg CO2e per therm
            'diesel': 2.68,         # kg CO2e per liter
            'occupancy': 0.1        # kg CO2e per person-hour
        }
        
        self.scope_mapping = {
            'electricity': 'Scope 2',
            'natural_gas': 'Scope 1',
            'diesel': 'Scope 1',
            'occupancy': 'Scope 3'
        }
    
    def calculate(self, readings: List[Dict]) -> Dict:
        """Calculate emissions from sensor readings"""
        total = 0
        breakdown = {'Scope 1': 0, 'Scope 2': 0, 'Scope 3': 0}
        details = {}
        
        for reading in readings:
            sensor = reading['sensor_type']
            value = reading['value']
            
            if sensor == 'energy':
                co2e = value * self.factors['electricity']
                breakdown['Scope 2'] += co2e
                details['Electricity'] = co2e
            elif sensor == 'gas':
                co2e = value * self.factors['natural_gas']
                breakdown['Scope 1'] += co2e
                details['Natural Gas'] = co2e
            elif sensor == 'fuel':
                co2e = value * self.factors['diesel']
                breakdown['Scope 1'] += co2e
                details['Fuel'] = co2e
            elif sensor == 'occupancy':
                co2e = value * self.factors['occupancy']
                breakdown['Scope 3'] += co2e
                details['Occupancy'] = co2e
            else:
                co2e = 0
            
            total += co2e
        
        return {
            'total_co2e_kg': round(total, 3),
            'breakdown': breakdown,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'readings_processed': len(readings)
        }
    
    def daily_aggregate(self, hourly_data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate to daily totals"""
        if hourly_data.empty:
            return pd.DataFrame()
        
        daily = hourly_data.resample('D').agg({
            'co2e_kg': 'sum',
            'energy_kwh': 'sum',
            'gas_therm': 'sum',
            'fuel_l': 'sum'
        }).reset_index()
        
        daily['co2e_per_employee'] = daily['co2e_kg'] / 25  # Assumed average occupancy
        return daily
    
    def validate(self, calculated: float, reference: float) -> Dict:
        """Validate calculation accuracy"""
        error = abs(calculated - reference)
        error_pct = (error / reference) * 100 if reference > 0 else 0
        
        return {
            'calculated': round(calculated, 2),
            'reference': round(reference, 2),
            'error_abs': round(error, 2),
            'error_percent': round(error_pct, 2),
            'grade': 'A' if error_pct < 5 else 'B' if error_pct < 10 else 'C',
            'passed': error_pct < 10
        }