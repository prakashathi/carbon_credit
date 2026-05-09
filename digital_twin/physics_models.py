import numpy as np
from typing import Dict

class PhysicsModels:
    """Physics-based thermal and energy models"""
    
    @staticmethod
    def thermal_dynamics(indoor_temp: float, outdoor_temp: float, 
                        wall_u_value: float, area: float) -> float:
        """Calculate heat transfer through walls"""
        return wall_u_value * area * (indoor_temp - outdoor_temp)
    
    @staticmethod
    def hvac_efficiency(cop: float = 3.5, cooling_load: float = 100) -> float:
        """Calculate HVAC power consumption"""
        return cooling_load / cop
    
    @staticmethod
    def solar_gain(irradiance: float, window_area: float, 
                   shgc: float = 0.6) -> float:
        """Calculate solar heat gain"""
        return irradiance * window_area * shgc
    
    @staticmethod
    def lighting_energy(area: float, lux_target: float, 
                       efficacy: float = 100) -> float:
        """Calculate lighting energy consumption"""
        return (area * lux_target) / efficacy / 1000  # kW
    
    @staticmethod
    def equipment_energy(power_rating: float, load_factor: float, 
                        hours: float = 1.0) -> float:
        """Calculate equipment energy consumption"""
        return power_rating * load_factor * hours
    
    @staticmethod
    def occupancy_impact(people_count: int, hours: float = 1.0) -> float:
        """Calculate energy impact of occupancy"""
        # Sensible heat gain per person: ~75W
        return people_count * 0.075 * hours  # kWh