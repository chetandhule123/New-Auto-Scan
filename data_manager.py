import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading

class DataManager:
    def __init__(self):
        self.current_scan_data = None
        self.scan_history = []
        self.last_scan_time = None
        self.next_scan_time = None
        self.data_lock = threading.Lock()
        self.max_history_items = 100
        
    def store_scan_data(self, stock_data: List[Dict], scan_time: datetime):
        """Store the latest scan data"""
        with self.data_lock:
            self.current_scan_data = pd.DataFrame(stock_data)
            self.last_scan_time = scan_time
            self.next_scan_time = scan_time + timedelta(minutes=15)
    
    def get_latest_scan_data(self) -> Optional[pd.DataFrame]:
        """Get the latest scan data"""
        with self.data_lock:
            return self.current_scan_data.copy() if self.current_scan_data is not None else None
    
    def get_last_scan_time(self) -> Optional[datetime]:
        """Get the timestamp of the last scan"""
        return self.last_scan_time
    
    def get_next_scan_time(self) -> Optional[datetime]:
        """Get the timestamp of the next scheduled scan"""
        return self.next_scan_time
    
    def add_scan_history(self, scan_info: Dict):
        """Add a scan record to history"""
        with self.data_lock:
            self.scan_history.append(scan_info)
            
            # Keep only the last N items to prevent memory issues
            if len(self.scan_history) > self.max_history_items:
                self.scan_history = self.scan_history[-self.max_history_items:]
    
    def get_scan_history(self) -> List[Dict]:
        """Get the scan history"""
        with self.data_lock:
            return self.scan_history.copy()
    
    def get_filtered_data(self, market_cap_filter: str = "All", 
                         sector_filter: str = "All", 
                         price_range: tuple = (0, 10000)) -> Optional[pd.DataFrame]:
        """Get filtered scan data based on criteria"""
        data = self.get_latest_scan_data()
        
        if data is None or data.empty:
            return None
        
        filtered_data = data.copy()
        
        if market_cap_filter != "All":
            filtered_data = filtered_data[filtered_data['market_cap'] == market_cap_filter]
        
        if sector_filter != "All":
            filtered_data = filtered_data[filtered_data['sector'] == sector_filter]
        
        # Apply price range filter
        filtered_data = filtered_data[
            (filtered_data['price'] >= price_range[0]) & 
            (filtered_data['price'] <= price_range[1])
        ]
        
        return filtered_data
    
    def get_statistics(self) -> Dict:
        """Get statistics about the current scan data"""
        data = self.get_latest_scan_data()
        
        if data is None or data.empty:
            return {
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'avg_volume': 0,
                'top_gainer': None,
                'top_loser': None
            }
        
        stats = {
            'total_stocks': len(data),
            'gainers': len(data[data['change_percent'] > 0]),
            'losers': len(data[data['change_percent'] < 0]),
            'avg_volume': data['volume'].mean(),
            'top_gainer': data.loc[data['change_percent'].idxmax()] if len(data) > 0 else None,
            'top_loser': data.loc[data['change_percent'].idxmin()] if len(data) > 0 else None
        }
        
        return stats
    
    def clear_data(self):
        """Clear all stored data"""
        with self.data_lock:
            self.current_scan_data = None
            self.scan_history = []
            self.last_scan_time = None
            self.next_scan_time = None
