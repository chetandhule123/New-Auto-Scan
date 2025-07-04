import threading
import time
import schedule
from datetime import datetime, timedelta
import pandas as pd
import random
import requests
from typing import Dict, List, Optional

class StockScanner:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.scanning_thread = None
        self.is_running = False
        self.total_scans = 0
        self.last_scan_time = None
        self.next_scan_time = None
        self.scan_interval_minutes = 15
        
    def start_background_scanning(self):
        """Start the background scanning thread"""
        if not self.is_running:
            self.is_running = True
            self.scanning_thread = threading.Thread(target=self._background_scan_loop, daemon=True)
            self.scanning_thread.start()
            
            # Schedule the scanning job
            schedule.every(self.scan_interval_minutes).minutes.do(self._perform_scan)
            
            # Perform initial scan
            self._perform_scan()
    
    def _background_scan_loop(self):
        """Background loop that runs the scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _perform_scan(self):
        """Perform the actual stock scanning"""
        try:
            scan_start_time = datetime.now()
            print(f"Starting scan at {scan_start_time}")
            
            # Get stock data
            stock_data = self._fetch_stock_data()
            
            if stock_data:
                # Store the scan results
                self.data_manager.store_scan_data(stock_data, scan_start_time)
                
                # Update scan statistics
                self.total_scans += 1
                self.last_scan_time = scan_start_time
                self.next_scan_time = scan_start_time + timedelta(minutes=self.scan_interval_minutes)
                
                # Store scan history
                self.data_manager.add_scan_history({
                    'scan_time': scan_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_stocks': len(stock_data),
                    'gainers': len([s for s in stock_data if s['change_percent'] > 0]),
                    'losers': len([s for s in stock_data if s['change_percent'] < 0]),
                    'status': 'Success'
                })
                
                print(f"Scan completed successfully. Found {len(stock_data)} stocks.")
            else:
                print("No data received from scan")
                
        except Exception as e:
            print(f"Error during scan: {e}")
            self.data_manager.add_scan_history({
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'status': f'Error: {str(e)}'
            })
    
    def _fetch_stock_data(self) -> List[Dict]:
        """Fetch stock data from NSE or other sources"""
        # In a real implementation, this would connect to NSE API or other data sources
        # For now, we'll simulate realistic stock data
        
        # Sample NSE stocks with realistic data patterns
        sample_stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd', 'sector': 'Energy', 'market_cap': 'Large Cap'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'sector': 'IT', 'market_cap': 'Large Cap'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd', 'sector': 'Banking', 'market_cap': 'Large Cap'},
            {'symbol': 'INFY', 'name': 'Infosys Ltd', 'sector': 'IT', 'market_cap': 'Large Cap'},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd', 'sector': 'FMCG', 'market_cap': 'Large Cap'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd', 'sector': 'Banking', 'market_cap': 'Large Cap'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank', 'sector': 'Banking', 'market_cap': 'Large Cap'},
            {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance Ltd', 'sector': 'Banking', 'market_cap': 'Large Cap'},
            {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd', 'sector': 'Auto', 'market_cap': 'Large Cap'},
            {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical Industries', 'sector': 'Pharma', 'market_cap': 'Large Cap'},
            {'symbol': 'WIPRO', 'name': 'Wipro Ltd', 'sector': 'IT', 'market_cap': 'Large Cap'},
            {'symbol': 'TECHM', 'name': 'Tech Mahindra Ltd', 'sector': 'IT', 'market_cap': 'Large Cap'},
            {'symbol': 'HCLTECH', 'name': 'HCL Technologies Ltd', 'sector': 'IT', 'market_cap': 'Large Cap'},
            {'symbol': 'DRREDDY', 'name': 'Dr Reddys Laboratories', 'sector': 'Pharma', 'market_cap': 'Large Cap'},
            {'symbol': 'CIPLA', 'name': 'Cipla Ltd', 'sector': 'Pharma', 'market_cap': 'Large Cap'},
            {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Ltd', 'sector': 'Auto', 'market_cap': 'Large Cap'},
            {'symbol': 'BAJAJFINSV', 'name': 'Bajaj Finserv Ltd', 'sector': 'Banking', 'market_cap': 'Large Cap'},
            {'symbol': 'NESTLEIND', 'name': 'Nestle India Ltd', 'sector': 'FMCG', 'market_cap': 'Large Cap'},
            {'symbol': 'TITAN', 'name': 'Titan Company Ltd', 'sector': 'FMCG', 'market_cap': 'Large Cap'},
            {'symbol': 'ASIANPAINT', 'name': 'Asian Paints Ltd', 'sector': 'FMCG', 'market_cap': 'Large Cap'},
        ]
        
        current_time = datetime.now()
        stock_data = []
        
        for stock in sample_stocks:
            # Generate realistic stock data
            base_price = random.uniform(100, 3000)
            change_percent = random.uniform(-5, 5)
            volume = random.randint(100000, 10000000)
            
            stock_data.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'price': round(base_price, 2),
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'market_cap': stock['market_cap'],
                'sector': stock['sector'],
                'scan_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return stock_data
    
    def trigger_manual_scan(self):
        """Trigger a manual scan immediately"""
        threading.Thread(target=self._perform_scan, daemon=True).start()
    
    def get_status(self) -> Dict:
        """Get current scanner status"""
        return {
            'running': self.is_running,
            'total_scans': self.total_scans,
            'last_scan_time': self.last_scan_time,
            'next_scan_time': self.next_scan_time
        }
    
    def stop_scanning(self):
        """Stop the background scanning"""
        self.is_running = False
        schedule.clear()
        if self.scanning_thread:
            self.scanning_thread.join(timeout=1)
