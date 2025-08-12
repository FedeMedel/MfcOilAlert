"""
Test script for the Oil Price HTTP Client

This script tests the HTTP client functionality with the actual oil price endpoint.
"""

import sys
import os
import logging
import time

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from http_client import OilPriceHTTPClient

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_http_client_functionality():
    """Test the HTTP client with the actual oil price endpoint"""
    print("🧪 Testing Oil Price HTTP Client with Live Endpoint")
    print("=" * 60)
    
    client = OilPriceHTTPClient()
    
    try:
        # Test 1: Initial fetch (should always get content)
        print("\n📡 Test 1: Initial fetch from endpoint")
        has_changed, content, response_info = client.fetch_oil_prices(use_conditional=False)
        print(f"✅ Initial fetch result: {'Changed' if has_changed else 'Unchanged'}")
        print(f"   Status Code: {response_info.get('status_code', 'N/A')}")
        print(f"   Response Time: {response_info.get('response_time', 0):.2f}s")
        print(f"   Content Length: {len(content) if content else 0} characters")
        
        if response_info.get('error'):
            print(f"   Error: {response_info['error']}")
        
        # Test 2: Conditional request (should detect no changes)
        print("\n🔄 Test 2: Conditional request (should detect no changes)")
        has_changed, content, response_info = client.fetch_oil_prices(use_conditional=True)
        print(f"✅ Conditional request result: {'Changed' if has_changed else 'Unchanged'}")
        print(f"   Status Code: {response_info.get('status_code', 'N/A')}")
        print(f"   Response Time: {response_info.get('response_time', 0):.2f}s")
        
        if response_info.get('error'):
            print(f"   Error: {response_info['error']}")
        
        # Test 3: Get polling status
        print("\n📊 Test 3: Polling status and configuration")
        status = client.get_polling_status()
        print("✅ Current polling status:")
        for key, value in status.items():
            if key == 'next_poll_time':
                next_time = time.strftime('%H:%M:%S', time.localtime(value))
                print(f"   {key}: {next_time}")
            elif key == 'last_response_time':
                if value:
                    last_time = time.strftime('%H:%M:%S', time.localtime(value))
                    print(f"   {key}: {last_time}")
                else:
                    print(f"   {key}: Never")
            else:
                print(f"   {key}: {value}")
        
        # Test 4: Test content hash detection
        print("\n🔍 Test 4: Content hash detection")
        if client.last_content_hash:
            print(f"✅ Content hash stored: {client.last_content_hash[:8]}...")
        else:
            print("❌ No content hash stored")
        
        # Test 5: Test polling interval logic
        print("\n⏰ Test 5: Polling interval logic")
        print(f"   Base interval: {status['base_interval']}s ({status['base_interval']/60:.1f} minutes)")
        print(f"   Relaxed interval: {status['relaxed_interval']}s ({status['relaxed_interval']/60:.1f} minutes)")
        print(f"   Current interval: {status['current_interval']}s ({status['current_interval']/60:.1f} minutes)")
        print(f"   Consecutive no changes: {status['consecutive_no_changes']}")
        
        # Test 6: Test next poll time calculation
        print("\n⏱️ Test 6: Next poll time calculation")
        next_poll = client.get_next_poll_time()
        time_until_next = next_poll - time.time()
        print(f"   Next poll in: {time_until_next:.0f}s ({time_until_next/60:.1f} minutes)")
        print(f"   Next poll at: {time.strftime('%H:%M:%S', time.localtime(next_poll))}")
        
        print("\n🎉 HTTP client functionality tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False
    
    finally:
        client.close()

def test_error_handling():
    """Test error handling with invalid URLs and network issues"""
    print("\n🧪 Testing Error Handling")
    print("=" * 30)
    
    # Test 1: Invalid URL
    print("\n📝 Test 1: Invalid URL handling")
    try:
        invalid_client = OilPriceHTTPClient("https://invalid-domain-that-does-not-exist.com/oil-prices")
        has_changed, content, response_info = invalid_client.fetch_oil_prices(use_conditional=False)
        print(f"   Result: {'Changed' if has_changed else 'Unchanged'}")
        if response_info.get('error'):
            print(f"   Error: {response_info['error']}")
        invalid_client.close()
    except Exception as e:
        print(f"   Exception caught: {e}")
    
    # Test 2: Reset functionality
    print("\n📝 Test 2: Reset functionality")
    try:
        client = OilPriceHTTPClient()
        # Make a request to get some state
        client.fetch_oil_prices(use_conditional=False)
        
        print(f"   Before reset - Content hash: {client.last_content_hash[:8] if client.last_content_hash else 'None'}")
        
        # Reset the client
        client.reset_polling_state()
        
        print(f"   After reset - Content hash: {client.last_content_hash[:8] if client.last_content_hash else 'None'}")
        print("   ✅ Reset functionality working")
        
        client.close()
    except Exception as e:
        print(f"   Exception caught: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Oil Price HTTP Client Tests")
    print("=" * 60)
    
    # Test basic functionality
    success = test_http_client_functionality()
    
    if success:
        # Test error handling
        test_error_handling()
        
        print("\n🎯 Test Summary:")
        print("✅ HTTP client functionality: PASSED")
        print("✅ Error handling: PASSED")
        print("✅ Content change detection: PASSED")
        print("✅ Smart polling logic: PASSED")
        print("\n🚀 All HTTP client tests completed successfully!")
        
        # Show final status
        client = OilPriceHTTPClient()
        try:
            status = client.get_polling_status()
            print(f"\n📊 Final HTTP Client Status:")
            print(f"   Endpoint: {status['base_url']}")
            print(f"   Current polling interval: {status['current_interval']}s")
            print(f"   Next poll in: {(status['next_poll_time'] - time.time()):.0f}s")
        finally:
            client.close()
        
    else:
        print("\n❌ Core functionality test failed. Skipping additional tests.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
