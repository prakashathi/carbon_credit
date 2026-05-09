import numpy as np
from collections import deque
from typing import Dict, List, Tuple

class EdgeProcessor:
    """Edge computing for anomaly detection and data compression"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.buffers = {}
        self.anomalies = []
        
    def detect_anomaly(self, value: float, sensor_type: str) -> Tuple[bool, float]:
        """Detect anomalies using moving average"""
        if sensor_type not in self.buffers:
            self.buffers[sensor_type] = deque(maxlen=self.window_size)
            self.buffers[sensor_type].append(value)
            return False, 0.0
        
        buffer = self.buffers[sensor_type]
        if len(buffer) < 10:
            buffer.append(value)
            return False, 0.0
        
        mean = np.mean(buffer)
        std = np.std(buffer) + 0.001
        z_score = abs(value - mean) / std
        
        buffer.append(value)
        
        if z_score > 2.5:
            self.anomalies.append({
                'timestamp': pd.Timestamp.now(),
                'sensor_type': sensor_type,
                'value': value,
                'z_score': z_score
            })
            return True, z_score
        
        return False, z_score
    
    def compress_batch(self, readings: List[Dict], ratio: int = 10) -> List[Dict]:
        """Compress data by keeping only anomalies and periodic samples"""
        compressed = []
        for i, reading in enumerate(readings):
            is_anomaly, z_score = self.detect_anomaly(reading['value'], reading['sensor_type'])
            if is_anomaly or i % ratio == 0:
                compressed.append({
                    **reading,
                    'edge_processed': True,
                    'z_score': round(z_score, 2)
                })
        return compressed
    
    def get_stats(self) -> Dict:
        """Get edge processing statistics"""
        return {
            'sensors_monitored': len(self.buffers),
            'total_anomalies': len(self.anomalies),
            'buffer_sizes': {k: len(v) for k, v in self.buffers.items()}
        }

import pandas as pd  # For timestamp