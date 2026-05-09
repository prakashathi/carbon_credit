import numpy as np
import asyncio
import random
from datetime import datetime
from typing import Dict, List

class IoTSensorGateway:
    """Simulates IoT sensors for SME facilities"""
    
    def __init__(self, facility_id="SME_001"):
        self.facility_id = facility_id
        self.sensors = {
            'energy': {'base': 50, 'unit': 'kWh', 'current': 0},
            'gas': {'base': 10, 'unit': 'therm', 'current': 0},
            'fuel': {'base': 5, 'unit': 'L', 'current': 0},
            'occupancy': {'base': 25, 'unit': 'people', 'current': 0},
            'temperature': {'base': 22, 'unit': '°C', 'current': 0},
            'humidity': {'base': 45, 'unit': '%', 'current': 0}
        }
        self.history = []
    
    async def read_sensor(self, sensor_type: str) -> Dict:
        """Read a single sensor value"""
        now = datetime.now()
        hour = now.hour
        is_weekend = now.weekday() >= 5
        
        # Work hours pattern (9 AM - 6 PM)
        work_factor = 1.5 if 9 <= hour <= 18 else 0.6
        if is_weekend:
            work_factor *= 0.3
        
        base = self.sensors[sensor_type]['base']
        
        if sensor_type == 'energy':
            value = base * work_factor * (1 + 0.2 * np.sin(hour/12 * np.pi))
        elif sensor_type == 'gas':
            value = base * (0.7 + 0.5 * work_factor)
        elif sensor_type == 'fuel':
            shift_spike = 1.5 if hour in [8, 12, 17] else 1.0
            value = base * work_factor * shift_spike
        elif sensor_type == 'occupancy':
            value = base * work_factor + random.gauss(0, 3)
            value = max(0, min(100, value))
        else:
            value = base + random.gauss(0, base * 0.1)
        
        # Add random anomaly (2% chance)
        if random.random() < 0.02:
            value *= random.uniform(2, 4)
        
        self.sensors[sensor_type]['current'] = round(value, 2)
        
        reading = {
            'timestamp': now.isoformat(),
            'facility_id': self.facility_id,
            'sensor_type': sensor_type,
            'value': round(value, 2),
            'unit': self.sensors[sensor_type]['unit']
        }
        
        self.history.append(reading)
        return reading
    
    async def read_all_sensors(self) -> List[Dict]:
        """Read all sensors"""
        readings = []
        for sensor_type in self.sensors.keys():
            reading = await self.read_sensor(sensor_type)
            readings.append(reading)
        return readings
    
    def get_history(self, n: int = 100) -> List[Dict]:
        """Get recent history"""
        return self.history[-n:]