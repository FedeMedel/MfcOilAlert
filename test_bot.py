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

if __name__ == "__main__":
    print("🚀 Oil Price Alert Bot - Connection Test")
    print("=" * 50)
    
    # Test configuration first
    asyncio.run(test_config())
    print()
    
    # Test Discord connection
    asyncio.run(test_discord_connection())
    
    print("\n" + "=" * 50)
    print("�� Test completed!")
