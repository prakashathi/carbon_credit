import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BuildingZone:
    name: str
    area: float  # sq m
    occupancy: int
    equipment_kw: float
    lighting_kw: float

class DigitalTwin:
    """Digital twin for building simulation"""
    
    def __init__(self):
        self.zones = [
            BuildingZone("Production", 500, 25, 120, 15),
            BuildingZone("Office", 150, 15, 20, 8),
            BuildingZone("Warehouse", 300, 5, 10, 5)
        ]
        self.total_energy = 0
        self.simulation_history = []
    
    def simulate(self, occupancy_factor: float = 0.7) -> Dict:
        """Run simulation for current timestep"""
        total_power = 0
        zone_details = []
        
        for zone in self.zones:
            current_occupancy = zone.occupancy * occupancy_factor
            power = (zone.equipment_kw * occupancy_factor + 
                    zone.lighting_kw * (0.5 + 0.5 * occupancy_factor))
            total_power += power
            
            zone_details.append({
                'name': zone.name,
                'power_kw': round(power, 2),
                'occupancy': round(current_occupancy, 1)
            })
        
        # Convert to energy (kWh per hour)
        energy_hour = total_power
        self.total_energy += energy_hour
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_power_kw': round(total_power, 2),
            'energy_kwh': round(energy_hour, 2),
            'cumulative_energy_kwh': round(self.total_energy, 2),
            'zones': zone_details
        }
        
        self.simulation_history.append(result)
        return result
    
    def get_hvac_load(self) -> float:
        """Calculate HVAC load based on occupancy and outdoor temp"""
        total_load = 0
        for zone in self.zones:
            # Simplified HVAC model
            load = zone.area * 0.05 + zone.occupancy * 0.5
            total_load += load
        return round(total_load, 2)
    
    def reset(self):
        """Reset simulation"""
        self.total_energy = 0
        self.simulation_history = []