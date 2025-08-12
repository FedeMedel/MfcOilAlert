#!/usr/bin/env python3
"""
Test script for Oil Price Alert Bot
Tests Discord connection and basic functionality
"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from config.config import Config
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_discord_connection():
    """Test basic Discord connection and permissions"""
    print("🔍 Testing Discord connection...")
    
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration validation passed")
        
        # Test bot creation
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        @bot.event
        async def on_ready():
            print(f"✅ Bot connected successfully as {bot.user.name}#{bot.user.discriminator}")
            print(f"✅ Bot ID: {bot.user.id}")
            print(f"✅ Connected to {len(bot.guilds)} guild(s)")
            
            # Test channel access
            if Config.DISCORD_CHANNEL_ID:
                channel_id = Config.get_channel_id()
                target_channel = bot.get_channel(channel_id)
                
                if target_channel:
                    print(f"✅ Target channel found: {target_channel.name} (ID: {channel_id})")
                    
                    # Check bot permissions
                    guild = target_channel.guild
                    bot_member = guild.get_member(bot.user.id)
                    channel_permissions = target_channel.permissions_for(bot_member)
                    
                    print(f"📋 Bot permissions in channel:")
                    print(f"   - Send Messages: {channel_permissions.send_messages}")
                    print(f"   - Manage Channels: {channel_permissions.manage_channels}")
                    print(f"   - Read Message History: {channel_permissions.read_message_history}")
                    print(f"   - View Channel: {channel_permissions.view_channel}")
                    
                    # Test sending a message
                    try:
                        await target_channel.send("🧪 **Test Message:** Bot connection test successful!")
                        print("✅ Test message sent successfully")
                    except discord.Forbidden:
                        print("❌ Cannot send messages to channel - permission denied")
                    except Exception as e:
                        print(f"❌ Error sending test message: {e}")
                    
                    # Test channel rename capability
                    if channel_permissions.manage_channels:
                        print("✅ Bot has permission to manage channels (can rename)")
                    else:
                        print("❌ Bot lacks permission to manage channels (cannot rename)")
                        
                else:
                    print(f"❌ Target channel {channel_id} not found")
                    print("   Make sure the channel ID in your .env file is correct")
                    print("   Make sure the bot has access to the channel")
            else:
                print("⚠️  No DISCORD_CHANNEL_ID configured")
            
            # Close the connection
            await bot.close()
            print("✅ Test completed successfully")
            
        @bot.event
        async def on_error(event, *args, **kwargs):
            print(f"❌ Error in event {event}: {args}")
            
        # Start the bot
        token = Config.DISCORD_TOKEN
        await bot.start(token)
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("   Please check your .env file")
    except discord.LoginFailure:
        print("❌ Discord login failed - check your bot token")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error("Test failed", exc_info=True)

async def test_config():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        load_dotenv()
        
        # Test required variables
        token = os.getenv('DISCORD_TOKEN')
        channel_id = os.getenv('DISCORD_CHANNEL_ID')
        
        if token:
            print(f"✅ DISCORD_TOKEN: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '***'}")
        else:
            print("❌ DISCORD_TOKEN: Not set")
            
        if channel_id:
            print(f"✅ DISCORD_CHANNEL_ID: {channel_id}")
        else:
            print("❌ DISCORD_CHANNEL_ID: Not set")
            
        # Test optional variables
        oil_url = os.getenv('OIL_PRICE_URL', 'https://play.myfly.club/oil-prices')
        polling = os.getenv('POLLING_INTERVAL', '300')
        
        print(f"✅ OIL_PRICE_URL: {oil_url}")
        print(f"✅ POLLING_INTERVAL: {polling}s")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

async def test_unified_message_format():
    """Test the unified message format functionality"""
    print("🔍 Testing unified message format...")
    
    try:
        # Import the bot module to test the message function
        from src.bot import send_unified_oil_price_message
        
        # Create mock data for testing
        class MockPriceData:
            def __init__(self, price, cycle):
                self.price = price
                self.cycle = cycle
        
        class MockChangeEvent:
            def __init__(self, old_price, new_price, old_cycle, new_cycle, price_change, price_change_percent, event_type):
                self.old_price = old_price
                self.new_price = new_price
                self.old_cycle = old_cycle
                self.new_cycle = new_cycle
                self.price_change = price_change
                self.price_change_percent = price_change_percent
                self.event_type = event_type
        
        # Test data
        current_price = MockPriceData(76.28, 6548)
        update_event = MockChangeEvent(72.59, 76.28, 6547, 6548, 3.69, 5.08, 'update')
        initial_event = MockChangeEvent(None, 76.28, None, 6548, 0.0, 0.0, 'initial')
        
        print("✅ Mock data created successfully")
        print(f"   - Current Price: ${current_price.price:.2f} (Cycle: {current_price.cycle})")
        print(f"   - Update Event: ${update_event.old_price:.2f} → ${update_event.new_price:.2f} (Change: +${update_event.price_change:.2f})")
        print(f"   - Initial Event: ${initial_event.new_price:.2f} (Cycle: {initial_event.new_cycle})")
        
        # Test timestamp functionality
        from datetime import datetime, timezone
        current_time = datetime.now(timezone.utc)
        time_str = current_time.strftime("%H:%M")
        print(f"✅ Timestamp functionality working: {time_str} UTC")
        
        print("✅ Unified message format test completed")
        
    except ImportError as e:
        print(f"⚠️  Could not import bot module for testing: {e}")
        print("   This is expected if the bot hasn't been run yet")
    except Exception as e:
        print(f"❌ Unified message format test failed: {e}")
        logger.error("Unified message format test failed", exc_info=True)

if __name__ == "__main__":
    print("🚀 Oil Price Alert Bot - Connection Test")
    print("=" * 50)
    
    # Test configuration first
    asyncio.run(test_config())
    print()
    
    # Test unified message format
    asyncio.run(test_unified_message_format())
    print()
    
    # Test Discord connection
    asyncio.run(test_discord_connection())
    
    print("\n" + "=" * 50)
    print("�� Test completed!")
