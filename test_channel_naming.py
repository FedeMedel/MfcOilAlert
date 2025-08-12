#!/usr/bin/env python3
"""
Test script for the new channel naming functionality with direction emojis
"""

from utils.price_monitor import PriceChangeEvent
import time

def test_channel_naming():
    """Test the channel naming logic with different price change scenarios"""
    
    print("🧪 Testing Channel Naming with Direction Emojis")
    print("=" * 50)
    
    # Test 1: Price increase
    print("\n📈 Test 1: Price Increase")
    increase_event = PriceChangeEvent(
        timestamp=time.time(),
        old_price=72.59,
        new_price=76.28,
        old_cycle=6547,
        new_cycle=6548,
        price_change=3.69,
        price_change_percent=5.08,
        event_type='update'
    )
    
    # Simulate the channel naming logic
    if increase_event.event_type == 'initial':
        direction_emoji = ""
    elif increase_event.price_change > 0:
        direction_emoji = "📈"
    elif increase_event.price_change < 0:
        direction_emoji = "📉"
    else:
        direction_emoji = ""
    
    price_str = f"{increase_event.new_price:.2f}"
    dollars, cents = price_str.split('.')
    channel_name = f"oil-price💲{dollars}-{cents}{direction_emoji}"
    
    print(f"Old Price: ${increase_event.old_price:.2f}")
    print(f"New Price: ${increase_event.new_price:.2f}")
    print(f"Change: ${increase_event.price_change:+.2f}")
    print(f"Direction Emoji: {direction_emoji}")
    print(f"Channel Name: {channel_name}")
    
    # Test 2: Price decrease
    print("\n📉 Test 2: Price Decrease")
    decrease_event = PriceChangeEvent(
        timestamp=time.time(),
        old_price=76.28,
        new_price=72.59,
        old_cycle=6548,
        new_cycle=6549,
        price_change=-3.69,
        price_change_percent=-4.84,
        event_type='update'
    )
    
    # Simulate the channel naming logic
    if decrease_event.event_type == 'initial':
        direction_emoji = ""
    elif decrease_event.price_change > 0:
        direction_emoji = "📈"
    elif decrease_event.price_change < 0:
        direction_emoji = "📉"
    else:
        direction_emoji = ""
    
    price_str = f"{decrease_event.new_price:.2f}"
    dollars, cents = price_str.split('.')
    channel_name = f"oil-price💲{dollars}-{cents}{direction_emoji}"
    
    print(f"Old Price: ${decrease_event.old_price:.2f}")
    print(f"New Price: ${decrease_event.new_price:.2f}")
    print(f"Change: ${decrease_event.price_change:+.2f}")
    print(f"Direction Emoji: {direction_emoji}")
    print(f"Channel Name: {channel_name}")
    
    # Test 3: Initial price (no change)
    print("\n📝 Test 3: Initial Price")
    initial_event = PriceChangeEvent(
        timestamp=time.time(),
        old_price=None,
        new_price=72.59,
        old_cycle=None,
        new_cycle=6547,
        price_change=0.0,
        price_change_percent=0.0,
        event_type='initial'
    )
    
    # Simulate the channel naming logic
    if initial_event.event_type == 'initial':
        direction_emoji = ""
    elif initial_event.price_change > 0:
        direction_emoji = "📈"
    elif initial_event.price_change < 0:
        direction_emoji = "📉"
    else:
        direction_emoji = ""
    
    price_str = f"{initial_event.new_price:.2f}"
    dollars, cents = price_str.split('.')
    channel_name = f"oil-price💲{dollars}-{cents}{direction_emoji}"
    
    print(f"New Price: ${initial_event.new_price:.2f}")
    print(f"Event Type: {initial_event.event_type}")
    print(f"Direction Emoji: {direction_emoji}")
    print(f"Channel Name: {channel_name}")
    
    # Test 4: No change (same price)
    print("\n➡️ Test 4: No Price Change")
    no_change_event = PriceChangeEvent(
        timestamp=time.time(),
        old_price=72.59,
        new_price=72.59,
        old_cycle=6547,
        new_cycle=6548,
        price_change=0.0,
        price_change_percent=0.0,
        event_type='update'
    )
    
    # Simulate the channel naming logic
    if no_change_event.event_type == 'initial':
        direction_emoji = ""
    elif no_change_event.price_change > 0:
        direction_emoji = "📈"
    elif no_change_event.price_change < 0:
        direction_emoji = "📉"
    else:
        direction_emoji = ""
    
    price_str = f"{no_change_event.new_price:.2f}"
    dollars, cents = price_str.split('.')
    channel_name = f"oil-price💲{dollars}-{cents}{direction_emoji}"
    
    print(f"Old Price: ${no_change_event.old_price:.2f}")
    print(f"New Price: ${no_change_event.new_price:.2f}")
    print(f"Change: ${no_change_event.price_change:+.2f}")
    print(f"Direction Emoji: {direction_emoji}")
    print(f"Channel Name: {channel_name}")
    
    print("\n" + "=" * 50)
    print("✅ Channel naming tests completed!")
    print("\n📋 Summary of Channel Name Formats:")
    print("• Price Increase: oil-price💲76-28📈")
    print("• Price Decrease: oil-price💲72-59📉")
    print("• Initial Price: oil-price💲72-59")
    print("• No Change: oil-price💲72-59")

if __name__ == "__main__":
    test_channel_naming()
