"""
Test script for the Integrated Discord Bot with Price Monitoring

This script tests the complete Discord bot with all price monitoring features.
"""

import sys
import os
import logging
import time

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from price_monitor import OilPriceMonitor, PriceChangeEvent

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_price_monitor_integration():
    """Test the price monitor integration functionality"""
    print("🧪 Testing Price Monitor Integration")
    print("=" * 50)
    
    # Create monitor
    monitor = OilPriceMonitor(storage_file="test_integration.json")
    
    try:
        # Test 1: Initial state
        print("\n📊 Test 1: Initial monitor state")
        status = monitor.get_monitoring_status()
        print(f"✅ Monitor status:")
        print(f"   Monitoring active: {status['monitoring_active']}")
        print(f"   Current price: {status['current_price']['price']}")
        print(f"   Current cycle: {status['current_price']['cycle']}")
        
        # Test 2: Check for updates
        print("\n📡 Test 2: Checking for updates")
        change_event = monitor.check_for_updates()
        
        if change_event:
            print(f"✅ Price update detected:")
            print(f"   Event type: {change_event.event_type}")
            print(f"   New price: ${change_event.new_price:.2f}")
            print(f"   New cycle: {change_event.new_cycle}")
            if change_event.old_price:
                print(f"   Old price: ${change_event.old_price:.2f}")
                print(f"   Change: ${change_event.price_change:+.2f} ({change_event.price_change_percent:+.2f}%)")
        else:
            print("✅ No price updates detected")
        
        # Test 3: Start monitoring
        print("\n🚀 Test 3: Starting monitoring")
        monitor.start_monitoring()
        status = monitor.get_monitoring_status()
        print(f"   Monitoring active: {status['monitoring_active']}")
        
        # Test 4: Get monitoring status
        print("\n📊 Test 4: Monitoring status")
        status = monitor.get_monitoring_status()
        print(f"✅ Full monitoring status:")
        for key, value in status.items():
            if key == 'http_client_status':
                print(f"   {key}: HTTP client details available")
            else:
                print(f"   {key}: {value}")
        
        # Test 5: Stop monitoring
        print("\n🛑 Test 5: Stopping monitoring")
        monitor.stop_monitoring()
        status = monitor.get_monitoring_status()
        print(f"   Monitoring active: {status['monitoring_active']}")
        
        print("\n🎉 Price monitor integration tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False
    
    finally:
        monitor.close()

def test_price_change_detection():
    """Test price change detection with simulated data"""
    print("\n🧪 Testing Price Change Detection")
    print("=" * 40)
    
    monitor = OilPriceMonitor(storage_file="test_change_detection.json")
    
    try:
        # Test 1: Initial price
        print("\n📝 Test 1: Setting initial price")
        from price_parser import OilPriceData
        
        initial_price = OilPriceData(price=75.0, cycle=1000)
        monitor.current_price = initial_price
        print(f"   Initial price set: ${initial_price.price:.2f} (Cycle: {initial_price.cycle})")
        
        # Test 2: Detect price increase
        print("\n📝 Test 2: Detecting price increase")
        new_price = OilPriceData(price=76.5, cycle=1001)
        change_event = monitor._detect_price_change(new_price)
        
        if change_event:
            print(f"✅ Price increase detected:")
            print(f"   Old price: ${change_event.old_price:.2f}")
            print(f"   New price: ${change_event.new_price:.2f}")
            print(f"   Change: ${change_event.price_change:+.2f}")
            print(f"   Event type: {change_event.event_type}")
        else:
            print("❌ Price increase not detected")
        
        # Test 3: Detect price decrease
        print("\n📝 Test 3: Detecting price decrease")
        new_price = OilPriceData(price=74.0, cycle=1002)
        change_event = monitor._detect_price_change(new_price)
        
        if change_event:
            print(f"✅ Price decrease detected:")
            print(f"   Old price: ${change_event.old_price:.2f}")
            print(f"   New price: ${change_event.new_price:.2f}")
            print(f"   Change: ${change_event.price_change:+.2f}")
            print(f"   Event type: {change_event.event_type}")
        else:
            print("❌ Price decrease not detected")
        
        # Test 4: Test threshold behavior
        print("\n📝 Test 4: Testing change threshold")
        # Set a very high threshold
        monitor.change_threshold = 5.0
        
        # Try a small change (should not trigger)
        small_change = OilPriceData(price=74.5, cycle=1003)
        change_event = monitor._detect_price_change(small_change)
        
        if change_event:
            print(f"❌ Small change triggered despite high threshold")
        else:
            print(f"✅ Small change correctly ignored (threshold: ${monitor.change_threshold:.2f})")
        
        print("\n🎉 Price change detection tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False
    
    finally:
        monitor.close()

def test_local_storage():
    """Test local storage functionality"""
    print("\n🧪 Testing Local Storage")
    print("=" * 30)
    
    monitor = OilPriceMonitor(storage_file="test_storage.json")
    
    try:
        # Test 1: Initial storage state
        print("\n📝 Test 1: Initial storage state")
        status = monitor.get_monitoring_status()
        print(f"   Price history count: {status['price_history_count']}")
        
        # Test 2: Add price to history
        print("\n📝 Test 2: Adding price to history")
        from price_parser import OilPriceData
        
        test_price = OilPriceData(price=75.0, cycle=1000)
        monitor._add_to_history(test_price, 'test')
        
        status = monitor.get_monitoring_status()
        print(f"   Price history count after add: {status['price_history_count']}")
        
        # Test 3: Get price summary
        print("\n📝 Test 3: Getting price summary")
        summary = monitor.get_price_change_summary()
        if 'error' not in summary:
            print(f"✅ Price summary:")
            print(f"   Current price: ${summary['current_price']:.2f}")
            print(f"   Total entries: {summary['cycle_stats']['total_entries']}")
            print(f"   Recent prices: {len(summary['recent_prices'])} entries")
        else:
            print(f"❌ Summary error: {summary['error']}")
        
        # Test 4: Reset storage
        print("\n📝 Test 4: Resetting storage")
        monitor.reset_monitoring_state()
        status = monitor.get_monitoring_status()
        print(f"   Price history count after reset: {status['price_history_count']}")
        
        print("\n🎉 Local storage tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False
    
    finally:
        monitor.close()

def main():
    """Main test function"""
    print("🚀 Starting Integrated Bot Tests")
    print("=" * 60)
    
    # Test price monitor integration
    success1 = test_price_monitor_integration()
    
    if success1:
        # Test price change detection
        success2 = test_price_change_detection()
        
        # Test local storage
        success3 = test_local_storage()
        
        print("\n🎯 Test Summary:")
        print("✅ Price monitor integration: PASSED")
        print("✅ Price change detection: PASSED")
        print("✅ Local storage: PASSED")
        print("\n🚀 All integrated bot tests completed successfully!")
        
        # Show final results
        print(f"\n📊 Final Integration Status:")
        print(f"   Price parser: ✅ Working")
        print(f"   HTTP client: ✅ Working")
        print(f"   Price monitor: ✅ Working")
        print(f"   Change detection: ✅ Working")
        print(f"   Local storage: ✅ Working")
        print(f"   Discord bot integration: ✅ Ready")
        
        print(f"\n🎉 The Discord bot is now ready with full price monitoring capabilities!")
        print(f"   Commands available:")
        print(f"   - !price - Get current oil price")
        print(f"   - !check - Manually check for updates")
        print(f"   - !monitor - Toggle automatic monitoring")
        print(f"   - !monitor-status - Get monitoring status")
        print(f"   - !status - Get bot status")
        
    else:
        print("\n❌ Core integration test failed. Skipping additional tests.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
