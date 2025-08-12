"""
Oil Price Monitor Module

This module integrates the price parser and HTTP client to create a complete
oil price monitoring system with change detection and local storage.
"""

import json
import logging
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from .price_parser import OilPriceParser, OilPriceData
from .http_client import OilPriceHTTPClient

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class PriceChangeEvent:
    """Data class for price change events"""
    timestamp: float
    old_price: Optional[float]
    new_price: float
    old_cycle: Optional[int]
    new_cycle: int
    price_change: float
    price_change_percent: float
    event_type: str  # 'initial', 'update', 'reset'

class OilPriceMonitor:
    """Main monitoring system for oil prices"""
    
    def __init__(self, 
                 base_url: str = "https://play.myfly.club/oil-prices",
                 storage_file: str = "price_history.json",
                 change_threshold: float = 0.01):  # 1 cent threshold
        self.parser = OilPriceParser()
        self.http_client = OilPriceHTTPClient(base_url)
        self.storage_file = storage_file
        self.change_threshold = change_threshold
        
        # Current state
        self.current_price: Optional[OilPriceData] = None
        self.last_change_event: Optional[PriceChangeEvent] = None
        self.price_history: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        # Load existing price history
        self._load_price_history()
        
        # Initialize with current price if available
        self._initialize_current_price()
    
    def _load_price_history(self):
        """Load price history from storage file"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.price_history = data.get('history', [])
                logger.info(f"Loaded {len(self.price_history)} price history entries")
        except FileNotFoundError:
            logger.info("No existing price history found, starting fresh")
            self.price_history = []
        except Exception as e:
            logger.error(f"Error loading price history: {e}")
            self.price_history = []
    
    def _save_price_history(self):
        """Save price history to storage file"""
        try:
            data = {
                'last_updated': time.time(),
                'total_entries': len(self.price_history),
                'history': self.price_history
            }
            with open(self.storage_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)
            logger.debug(f"Saved {len(self.price_history)} price history entries")
        except Exception as e:
            logger.error(f"Error saving price history: {e}")
    
    def _initialize_current_price(self):
        """Initialize current price from storage or fetch from endpoint"""
        if self.price_history:
            # Get the most recent entry
            latest_entry = max(self.price_history, key=lambda x: x['timestamp'])
            self.current_price = OilPriceData(
                price=latest_entry['price'],
                cycle=latest_entry['cycle'],
                timestamp=latest_entry.get('timestamp_str')
            )
            logger.info(f"Initialized current price: ${self.current_price.price:.2f} (Cycle: {self.current_price.cycle})")
        else:
            logger.info("No price history available, will fetch on first check")
    
    def _add_to_history(self, price_data: OilPriceData, event_type: str = 'update'):
        """Add price data to history"""
        entry = {
            'timestamp': time.time(),
            'timestamp_str': datetime.fromtimestamp(time.time(), tz=timezone.utc).isoformat(),
            'price': price_data.price,
            'cycle': price_data.cycle,
            'event_type': event_type
        }
        
        self.price_history.append(entry)
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
            logger.debug("Trimmed price history to 1000 entries")
        
        # Save to file
        self._save_price_history()
    
    def _detect_price_change(self, new_price_data: OilPriceData) -> Optional[PriceChangeEvent]:
        """Detect if there's a meaningful price change"""
        if self.current_price is None:
            # First price check
            event = PriceChangeEvent(
                timestamp=time.time(),
                old_price=None,
                new_price=new_price_data.price,
                old_cycle=None,
                new_cycle=new_price_data.cycle,
                price_change=0.0,
                price_change_percent=0.0,
                event_type='initial'
            )
            logger.info(f"Initial price detected: ${new_price_data.price:.2f} (Cycle: {new_price_data.cycle})")
            return event
        
        # Check if cycle has changed (indicating new data)
        if new_price_data.cycle > self.current_price.cycle:
            price_change = new_price_data.price - self.current_price.price
            price_change_percent = (price_change / self.current_price.price) * 100
            
            # Check if change exceeds threshold
            if abs(price_change) >= self.change_threshold:
                event = PriceChangeEvent(
                    timestamp=time.time(),
                    old_price=self.current_price.price,
                    new_price=new_price_data.price,
                    old_cycle=self.current_price.cycle,
                    new_cycle=new_price_data.cycle,
                    price_change=price_change,
                    price_change_percent=price_change_percent,
                    event_type='update'
                )
                
                logger.info(f"Price change detected: ${self.current_price.price:.2f} → ${new_price_data.price:.2f} "
                          f"(Change: ${price_change:+.2f}, {price_change_percent:+.2f}%)")
                return event
            else:
                logger.debug(f"Price change below threshold: ${price_change:.2f} (threshold: ${self.change_threshold:.2f})")
                return None
        else:
            logger.debug(f"No new cycle data (current: {self.current_price.cycle}, new: {new_price_data.cycle})")
            return None
    
    def check_for_updates(self) -> Optional[PriceChangeEvent]:
        """
        Check for oil price updates
        
        Returns:
            PriceChangeEvent if a change was detected, None otherwise
        """
        try:
            # Fetch latest prices from endpoint
            has_changed, content, response_info = self.http_client.fetch_oil_prices()
            
            if not has_changed:
                logger.debug("No content changes detected")
                return None
            
            if not content:
                logger.warning("No content received despite change detection")
                return None
            
            # Parse the new content
            new_price_data = self.parser.get_latest_price(content)
            
            # Detect price changes
            change_event = self._detect_price_change(new_price_data)
            
            if change_event:
                # Update current price
                self.current_price = new_price_data
                self.last_change_event = change_event
                
                # Add to history
                self._add_to_history(new_price_data, change_event.event_type)
                
                logger.info(f"Price update processed: {change_event.event_type}")
                return change_event
            else:
                # Even if no meaningful change, update current price if cycle is newer
                if (self.current_price is None or 
                    new_price_data.cycle > self.current_price.cycle):
                    self.current_price = new_price_data
                    self._add_to_history(new_price_data, 'update')
                    logger.debug(f"Price updated without significant change: ${new_price_data.price:.2f}")
                
                return None
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def get_current_price(self) -> Optional[OilPriceData]:
        """Get the current oil price"""
        return self.current_price
    
    def get_price_change_summary(self) -> Dict[str, Any]:
        """Get a summary of recent price changes"""
        if not self.price_history:
            return {'error': 'No price history available'}
        
        # Get last 10 entries
        recent_history = self.price_history[-10:]
        
        # Calculate basic statistics
        prices = [entry['price'] for entry in recent_history]
        cycles = [entry['cycle'] for entry in recent_history]
        
        summary = {
            'current_price': self.current_price.price if self.current_price else None,
            'current_cycle': self.current_price.cycle if self.current_price else None,
            'last_update': self.last_change_event.timestamp if self.last_change_event else None,
            'recent_prices': recent_history,
            'price_stats': {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'price_range': max(prices) - min(prices)
            },
            'cycle_stats': {
                'min_cycle': min(cycles),
                'max_cycle': max(cycles),
                'total_entries': len(self.price_history)
            }
        }
        
        return summary
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get the current monitoring status"""
        http_status = self.http_client.get_polling_status()
        
        status = {
            'monitoring_active': self.monitoring_active,
            'current_price': {
                'price': self.current_price.price if self.current_price else None,
                'cycle': self.current_price.cycle if self.current_price else None,
                'timestamp': self.current_price.timestamp if self.current_price else None
            },
            'last_change_event': asdict(self.last_change_event) if self.last_change_event else None,
            'price_history_count': len(self.price_history),
            'change_threshold': self.change_threshold,
            'http_client_status': http_status
        }
        
        return status
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info("Oil price monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if not self.monitoring_active:
            logger.warning("Monitoring is not active")
            return
        
        self.monitoring_active = False
        logger.info("Oil price monitoring stopped")
    
    def reset_monitoring_state(self):
        """Reset the monitoring state (useful for testing)"""
        self.current_price = None
        self.last_change_event = None
        self.price_history = []
        self.monitoring_active = False
        self.http_client.reset_polling_state()
        
        # Clear storage file
        try:
            import os
            if os.path.exists(self.storage_file):
                os.remove(self.storage_file)
                logger.info(f"Removed storage file: {self.storage_file}")
        except Exception as e:
            logger.error(f"Error removing storage file: {e}")
        
        logger.info("Monitoring state reset")
    
    def close(self):
        """Clean up resources"""
        self.http_client.close()
        logger.info("Oil price monitor closed")


def create_monitor(base_url: str = "https://play.myfly.club/oil-prices",
                  storage_file: str = "price_history.json") -> OilPriceMonitor:
    """Factory function to create a new monitor instance"""
    return OilPriceMonitor(base_url, storage_file)


# Example usage and testing
if __name__ == "__main__":
    # Test the price monitor
    monitor = create_monitor()
    
    try:
        print("🧪 Testing Oil Price Monitor")
        print("=" * 40)
        
        # Test 1: Check for updates
        print("\n📡 Test 1: Checking for updates")
        change_event = monitor.check_for_updates()
        
        if change_event:
            print(f"✅ Price change detected:")
            print(f"   Old price: ${change_event.old_price:.2f}" if change_event.old_price else "   Old price: None")
            print(f"   New price: ${change_event.new_price:.2f}")
            print(f"   Change: ${change_event.price_change:+.2f} ({change_event.price_change_percent:+.2f}%)")
            print(f"   Event type: {change_event.event_type}")
        else:
            print("✅ No significant price changes detected")
        
        # Test 2: Get current price
        print("\n💰 Test 2: Current price")
        current_price = monitor.get_current_price()
        if current_price:
            print(f"✅ Current price: ${current_price.price:.2f} (Cycle: {current_price.cycle})")
        else:
            print("❌ No current price available")
        
        # Test 3: Get monitoring status
        print("\n📊 Test 3: Monitoring status")
        status = monitor.get_monitoring_status()
        print("✅ Monitoring status:")
        for key, value in status.items():
            if key == 'http_client_status':
                print(f"   {key}: HTTP client details available")
            else:
                print(f"   {key}: {value}")
        
        # Test 4: Get price change summary
        print("\n📈 Test 4: Price change summary")
        summary = monitor.get_price_change_summary()
        if 'error' not in summary:
            print(f"✅ Price summary:")
            print(f"   Current price: ${summary['current_price']:.2f}")
            print(f"   Current cycle: {summary['current_cycle']}")
            print(f"   Total history entries: {summary['cycle_stats']['total_entries']}")
            print(f"   Recent price range: ${summary['price_stats']['min_price']:.2f} - ${summary['price_stats']['max_price']:.2f}")
        else:
            print(f"❌ Summary error: {summary['error']}")
        
        print("\n🎉 Price monitor tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
    
    finally:
        monitor.close()
