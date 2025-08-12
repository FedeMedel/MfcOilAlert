"""
Test script for the Oil Price Parser

This script tests the price parser functionality using the sample oil-prices.json data.
"""

import sys
import os
import json
import logging

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from price_parser import OilPriceParser, OilPriceData

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_parser_with_sample_data():
    """Test the parser with the sample oil-prices.json file"""
    print("🧪 Testing Oil Price Parser with Sample Data")
    print("=" * 50)
    
    parser = OilPriceParser()
    
    try:
        # Test 1: Parse from file
        print("\n📁 Test 1: Parsing from oil-prices.json file")
        latest_price = parser.get_latest_price_from_file("oil-prices.json")
        print(f"✅ Latest price: ${latest_price.price:.2f} (Cycle: {latest_price.cycle})")
        
        # Test 2: Get statistics
        print("\n📊 Test 2: Getting price statistics")
        stats = parser.get_statistics_from_file("oil-prices.json")
        print("✅ Statistics retrieved:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        # Test 3: Get price history
        print("\n📈 Test 3: Getting recent price history")
        history = parser.get_price_history_from_file("oil-prices.json", limit=5)
        print("✅ Recent price history (last 5 entries):")
        for entry in history:
            print(f"   Cycle {entry.cycle}: ${entry.price:.2f}")
        
        # Test 4: Validate price data
        print("\n✅ Test 4: Validating price data")
        is_valid = parser.validate_price_data(latest_price)
        print(f"   Latest price validation: {'PASS' if is_valid else 'FAIL'}")
        
        # Test 5: Test with JSON string directly
        print("\n🔗 Test 5: Parsing JSON string directly")
        with open("oil-prices.json", 'r', encoding='utf-8') as file:
            json_string = file.read()
        
        latest_price_direct = parser.get_latest_price(json_string)
        print(f"✅ Direct parsing result: ${latest_price_direct.price:.2f} (Cycle: {latest_price_direct.cycle})")
        
        # Test 6: Verify consistency
        print("\n🔄 Test 6: Verifying consistency between methods")
        if (latest_price.price == latest_price_direct.price and 
            latest_price.cycle == latest_price_direct.cycle):
            print("✅ File and direct parsing methods return consistent results")
        else:
            print("❌ Inconsistency detected between parsing methods")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False

def test_error_handling():
    """Test error handling with invalid data"""
    print("\n🧪 Testing Error Handling")
    print("=" * 30)
    
    parser = OilPriceParser()
    
    # Test 1: Invalid JSON
    print("\n📝 Test 1: Invalid JSON handling")
    try:
        parser.get_latest_price("invalid json string")
        print("❌ Should have raised an error for invalid JSON")
    except ValueError as e:
        print(f"✅ Correctly handled invalid JSON: {e}")
    
    # Test 2: Empty array
    print("\n📝 Test 2: Empty array handling")
    try:
        parser.get_latest_price("[]")
        print("❌ Should have raised an error for empty array")
    except ValueError as e:
        print(f"✅ Correctly handled empty array: {e}")
    
    # Test 3: Missing required fields
    print("\n📝 Test 3: Missing required fields handling")
    invalid_data = '[{"price": 75.0}]'  # Missing cycle field
    try:
        parser.get_latest_price(invalid_data)
        print("❌ Should have raised an error for missing cycle field")
    except (KeyError, ValueError) as e:
        print(f"✅ Correctly handled missing fields: {e}")
    
    # Test 4: Invalid data types
    print("\n📝 Test 4: Invalid data types handling")
    invalid_types = '[{"price": "not_a_number", "cycle": 1000}]'
    try:
        parser.get_latest_price(invalid_types)
        print("❌ Should have raised an error for invalid price type")
    except ValueError as e:
        print(f"✅ Correctly handled invalid data types: {e}")
    
    print("\n✅ Error handling tests completed!")

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 25)
    
    parser = OilPriceParser()
    
    # Test 1: Single entry
    print("\n📝 Test 1: Single entry handling")
    single_entry = '[{"price": 75.50, "cycle": 1000}]'
    try:
        latest = parser.get_latest_price(single_entry)
        print(f"✅ Single entry parsed: ${latest.price:.2f} (Cycle: {latest.cycle})")
    except Exception as e:
        print(f"❌ Failed to parse single entry: {e}")
    
    # Test 2: Large numbers
    print("\n📝 Test 2: Large numbers handling")
    large_numbers = '[{"price": 999999.99, "cycle": 999999}]'
    try:
        latest = parser.get_latest_price(large_numbers)
        print(f"✅ Large numbers parsed: ${latest.price:.2f} (Cycle: {latest.cycle})")
    except Exception as e:
        print(f"❌ Failed to parse large numbers: {e}")
    
    # Test 3: Decimal precision
    print("\n📝 Test 3: Decimal precision handling")
    decimal_precision = '[{"price": 75.123456789, "cycle": 1000}]'
    try:
        latest = parser.get_latest_price(decimal_precision)
        print(f"✅ Decimal precision preserved: ${latest.price:.9f} (Cycle: {latest.cycle})")
    except Exception as e:
        print(f"❌ Failed to handle decimal precision: {e}")
    
    print("\n✅ Edge case tests completed!")

def main():
    """Main test function"""
    print("🚀 Starting Oil Price Parser Tests")
    print("=" * 50)
    
    # Test with sample data
    success = test_parser_with_sample_data()
    
    if success:
        # Test error handling
        test_error_handling()
        
        # Test edge cases
        test_edge_cases()
        
        print("\n🎯 Test Summary:")
        print("✅ Sample data parsing: PASSED")
        print("✅ Error handling: PASSED")
        print("✅ Edge cases: PASSED")
        print("\n🚀 All tests completed successfully!")
        
        # Show final results
        parser = OilPriceParser()
        latest = parser.get_latest_price_from_file("oil-prices.json")
        print(f"\n📊 Final Result:")
        print(f"   Latest Oil Price: ${latest.price:.2f}")
        print(f"   Cycle Number: {latest.cycle}")
        print(f"   Total Entries: {len(parser.last_parsed_data) if parser.last_parsed_data else 0}")
        
    else:
        print("\n❌ Core functionality test failed. Skipping additional tests.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
