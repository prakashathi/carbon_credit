import asyncio
import json
from typing import Callable, Dict, List
from .sensor_gateway import IoTSensorGateway
from .edge_processor import EdgeProcessor

class DataStream:
    """Manages real-time data streaming"""
    
    def __init__(self):
        self.sensor = IoTSensorGateway()
        self.edge = EdgeProcessor()
        self.subscribers = []
        self.is_streaming = False
        
    def subscribe(self, callback: Callable):
        """Add a subscriber for real-time data"""
        self.subscribers.append(callback)
        
    async def start_streaming(self, interval_seconds: float = 2.0):
        """Start streaming data to all subscribers"""
        self.is_streaming = True
        while self.is_streaming:
            readings = await self.sensor.read_all_sensors()
            compressed = self.edge.compress_batch(readings)
            
            for callback in self.subscribers:
                await callback(compressed)
            
            await asyncio.sleep(interval_seconds)
    
    def stop_streaming(self):
        """Stop the data stream"""
        self.is_streaming = False
    
    async def get_latest_batch(self, n_sensors: int = 6) -> List[Dict]:
        """Get a single batch of readings"""
        readings = await self.sensor.read_all_sensors()
        return readings[:n_sensors]