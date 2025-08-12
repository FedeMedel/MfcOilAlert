import os
import sys
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
import asyncio
import time
from datetime import datetime, timezone

# Add the parent directory to Python path to import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from utils.price_monitor import create_monitor, PriceChangeEvent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
# Disable privileged intents that require explicit approval
intents.members = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

# Price monitoring
price_monitor = None
monitoring_task = None

@bot.event
async def on_ready():
    """Event triggered when bot successfully connects to Discord"""
    logger.info(f'Bot connected successfully as {bot.user.name}#{bot.user.discriminator}')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Connected to {len(bot.guilds)} guild(s)')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name=Config.BOT_STATUS))
    
    # Initialize price monitor
    global price_monitor
    price_monitor = create_monitor(polling_interval=Config.POLLING_INTERVAL)
    
    # Log guild information
    for guild in bot.guilds:
        logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')
        
        # Check if configured channel exists in this guild
        if Config.DISCORD_CHANNEL_ID:
            channel = guild.get_channel(Config.get_channel_id())
            if channel:
                logger.info(f'Configured channel found: {channel.name} (ID: {channel.id})')
                logger.info(f'Channel permissions: {channel.permissions_for(guild.me)}')
            else:
                logger.warning(f'Configured channel {Config.DISCORD_CHANNEL_ID} not found in guild {guild.name}')
    
    # Start passive monitoring immediately
    await start_passive_monitoring()

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    # Only handle errors for the !check command
    if ctx.command and ctx.command.name == 'check':
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ **Error:** You don't have permission to use this command.")
            logger.warning(f"Permission denied for command {ctx.command} by {ctx.author}")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"❌ **Error:** I don't have the required permissions to execute this command.")
            logger.error(f"Bot missing permissions for command {ctx.command}: {error}")
        else:
            await ctx.send(f"❌ **Error:** An unexpected error occurred: {str(error)}")
            logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)







@bot.command(name='check')
async def check_price_updates(ctx):
    """Manually check for price updates"""
    if not price_monitor:
        await ctx.send("❌ **Error:** Price monitor not initialized.")
        return
    
    try:
        await ctx.send("🔍 **Checking for price updates...**")
        
        # Check for updates
        change_event = price_monitor.check_for_updates()
        
        if change_event:
            # Use unified message format for consistency
            await send_unified_oil_price_message(price_monitor.get_current_price(), change_event, is_update=True)
            
            # Auto-rename channel if configured
            if Config.DISCORD_CHANNEL_ID:
                await auto_rename_channel(change_event)
        else:
            # Send current price info using unified format
            current_price = price_monitor.get_current_price()
            if current_price:
                await send_unified_oil_price_message(current_price, is_update=False)
            else:
                await ctx.send("✅ **No price updates detected.**")
    
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to check for updates: {str(e)}")
        logger.error(f"Error checking for updates: {e}")





async def auto_rename_channel(change_event):
    """Automatically rename the configured channel with the new oil price and direction indicator"""
    if not Config.DISCORD_CHANNEL_ID:
        return
    
    try:
        channel_id = Config.get_channel_id()
        target_channel = bot.get_channel(channel_id)
        
        if not target_channel:
            logger.error(f"Could not find channel with ID {channel_id} for auto-rename")
            return
        
        # Determine direction emoji based on price change
        if change_event.event_type == 'initial':
            # Initial price - no direction indicator
            direction_emoji = ""
        elif change_event.price_change > 0:
            # Price went up
            direction_emoji = "📈"
        elif change_event.price_change < 0:
            # Price went down
            direction_emoji = "📉"
        else:
            # No change
            direction_emoji = ""
        
        # Create new channel name with 💲 emoji, direction indicator, and dash separator
        price_str = f"{change_event.new_price:.2f}"
        if '.' in price_str:
            dollars, cents = price_str.split('.')
            new_channel_name = f"oil-price {direction_emoji}💲{dollars}-{cents}"
        else:
            new_channel_name = f"oil-price {direction_emoji}💲{price_str}"
        
        # Ensure channel name is within Discord's limits (100 characters)
        if len(new_channel_name) > 100:
            if '.' in price_str:
                dollars, cents = price_str.split('.')
                new_channel_name = f"oil {direction_emoji}💲{dollars}-{cents}"
            else:
                new_channel_name = f"oil {direction_emoji}💲{price_str}"
        
        # Rename the channel
        await target_channel.edit(name=new_channel_name)
        logger.info(f"Auto-renamed channel to: {new_channel_name}")
        
    except discord.Forbidden:
        logger.error(f"Bot lacks permission to rename channel {channel_id}")
    except discord.HTTPException as e:
        logger.error(f"Discord API error while auto-renaming channel: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while auto-renaming channel: {e}")

async def start_passive_monitoring():
    """Start passive monitoring immediately on bot startup"""
    if not price_monitor:
        logger.error("Price monitor not initialized")
        return
    
    try:
        # Start monitoring
        price_monitor.start_monitoring()
        start_monitoring_task()
        
        # Immediately fetch and send current price
        await fetch_and_send_current_price()
        
        logger.info("Passive monitoring started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start passive monitoring: {e}")

async def fetch_and_send_current_price():
    """Fetch current price and send update to Discord channel"""
    if not Config.DISCORD_CHANNEL_ID:
        return
    
    try:
        # Force a price check to get the latest data
        change_event = price_monitor.check_for_updates()
        
        if change_event:
            # Send price update notification
            await send_unified_oil_price_message(price_monitor.get_current_price(), change_event, is_update=True)
            
            # Auto-rename channel if configured
            await auto_rename_channel(change_event)
            
            logger.info(f"Initial price update sent: ${change_event.new_price:.2f}")
        else:
            # If no change event, still send current price info
            current_price = price_monitor.get_current_price()
            if current_price:
                await send_unified_oil_price_message(current_price, is_update=False)
                logger.info(f"Current price info sent: ${current_price.price:.2f}")
        
    except Exception as e:
        logger.error(f"Error fetching and sending current price: {e}")

async def send_unified_oil_price_message(price_data, change_event=None, is_update=False):
    """Unified function to send oil price information in consistent format"""
    if not Config.DISCORD_CHANNEL_ID:
        return
    
    try:
        channel_id = Config.get_channel_id()
        target_channel = bot.get_channel(channel_id)
        
        if not target_channel:
            logger.error(f"Could not find channel with ID {channel_id}")
            return
        
        # Create unified embed with consistent "🔄 Oil Price Updated!" format
        embed = discord.Embed(
            title="🔄 Oil Price Updated!",
            description="Automatic price update detected" if is_update else "Current price information",
            color=discord.Color.green()
        )
        
        if change_event and change_event.event_type != 'initial':
            # Update scenario: show old price, new price, cycle, and change
            embed.add_field(name="💰 Old Price", value=f"${change_event.old_price:.2f}", inline=True)
            embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
            embed.add_field(name="📊 Change", value=f"${change_event.price_change:+.2f} ({change_event.price_change_percent:+.2f}%)", inline=True)
        elif change_event and change_event.event_type == 'initial':
            # Initial price scenario
            embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
            embed.add_field(name="📝 Type", value="Initial Price", inline=True)
        else:
            # Info scenario: show current price and cycle only
            embed.add_field(name="💰 Current Price", value=f"${price_data.price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{price_data.cycle}", inline=True)
            embed.add_field(name="📊 Status", value="No price change detected", inline=True)
        
        # Add UTC timestamp to all message scenarios
        current_time = datetime.now(timezone.utc)
        time_str = current_time.strftime("%H:%M")
        embed.add_field(name="⏰ Time", value=f"{time_str} UTC", inline=True)
        
        await target_channel.send(embed=embed)
        logger.info(f"Unified oil price message sent to channel {channel_id}")
        
    except Exception as e:
        logger.error(f"Error sending unified oil price message: {e}")

def start_monitoring_task():
    """Start the background monitoring task"""
    global monitoring_task
    if monitoring_task and not monitoring_task.done():
        return
    
    monitoring_task = asyncio.create_task(background_monitoring())

def stop_monitoring_task():
    """Stop the background monitoring task"""
    global monitoring_task
    if monitoring_task and not monitoring_task.done():
        monitoring_task.cancel()

async def background_monitoring():
    """Background task for automatic price monitoring"""
    if not price_monitor:
        return
    
    logger.info("Background monitoring task started")
    
    try:
        while price_monitor.monitoring_active:
            try:
                # Check for updates
                change_event = price_monitor.check_for_updates()
                
                if change_event:
                    logger.info(f"Price update detected in background: ${change_event.new_price:.2f}")
                    
                    # Auto-rename channel
                    await auto_rename_channel(change_event)
                    
                    # Send notification to configured channel
                    if Config.DISCORD_CHANNEL_ID:
                        await send_unified_oil_price_message(price_monitor.get_current_price(), change_event, is_update=True)
                
                # Wait for next check (use monitor's polling interval)
                next_poll = price_monitor.http_client.get_next_poll_time()
                wait_time = max(0, next_poll - time.time())
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                else:
                    await asyncio.sleep(Config.POLLING_INTERVAL)  # Use config value instead of hardcoded
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    except asyncio.CancelledError:
        logger.info("Background monitoring task cancelled")
    except Exception as e:
        logger.error(f"Background monitoring task failed: {e}")
    finally:
        logger.info("Background monitoring task stopped")

async def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validation passed")
        
        # Get bot token
        token = Config.DISCORD_TOKEN
        if not token:
            raise ValueError("DISCORD_TOKEN not found in environment variables")
        
        logger.info("Starting Discord bot...")
        await bot.start(token)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure DISCORD_TOKEN is set.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


