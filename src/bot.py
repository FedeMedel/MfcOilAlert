import os
import sys
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
import asyncio
import time

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
    price_monitor = create_monitor()
    
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

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ **Error:** You don't have permission to use this command.")
        logger.warning(f"Permission denied for command {ctx.command} by {ctx.author}")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"❌ **Error:** I don't have the required permissions to execute this command.")
        logger.error(f"Bot missing permissions for command {ctx.command}: {error}")
    else:
        await ctx.send(f"❌ **Error:** An unexpected error occurred: {str(error)}")
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)

@bot.command(name='ping')
async def ping(ctx):
    """Test command to verify bot is responsive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 **Pong!** Latency: {latency}ms')

@bot.command(name='rename')
async def rename_channel(ctx, *, new_name: str):
    """Rename the configured Discord channel (Admin only)"""
    # Check if user has manage channels permission
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ **Error:** You need 'Manage Channels' permission to use this command.")
        return
    
    # Check if bot has manage channels permission
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ **Error:** I don't have permission to manage channels.")
        return
    
    try:
        # Get the configured channel
        if not Config.DISCORD_CHANNEL_ID:
            await ctx.send("❌ **Error:** No channel ID configured in environment variables.")
            return
        
        channel_id = Config.get_channel_id()
        target_channel = bot.get_channel(channel_id)
        
        if not target_channel:
            await ctx.send(f"❌ **Error:** Could not find channel with ID {channel_id}")
            return
        
        # Store old name for logging
        old_name = target_channel.name
        
        # Attempt to rename the channel
        await target_channel.edit(name=new_name)
        
        # Send success message
        await ctx.send(f"✅ **Channel renamed successfully!**\n"
                      f"**Old name:** {old_name}\n"
                      f"**New name:** {new_name}")
        
        logger.info(f"Channel renamed from '{old_name}' to '{new_name}' by {ctx.author}")
        
    except discord.Forbidden:
        await ctx.send("❌ **Error:** I don't have permission to rename this channel.")
        logger.error(f"Bot lacks permission to rename channel {channel_id}")
    except discord.HTTPException as e:
        await ctx.send(f"❌ **Error:** Failed to rename channel. Discord API error: {e}")
        logger.error(f"Discord API error while renaming channel: {e}")
    except Exception as e:
        await ctx.send(f"❌ **Error:** An unexpected error occurred: {str(e)}")
        logger.error(f"Unexpected error while renaming channel: {e}", exc_info=True)

@bot.command(name='price')
async def get_current_price(ctx):
    """Get the current oil price"""
    if not price_monitor:
        await ctx.send("❌ **Error:** Price monitor not initialized.")
        return
    
    try:
        current_price = price_monitor.get_current_price()
        if current_price:
            # Create price embed
            embed = discord.Embed(
                title="🛢️ Current Oil Price",
                description=f"Latest oil price information",
                color=discord.Color.green()
            )
            
            embed.add_field(name="💰 Price", value=f"${current_price.price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{current_price.cycle}", inline=True)
            if current_price.timestamp:
                embed.add_field(name="⏰ Last Updated", value=current_price.timestamp, inline=True)
            
            # Add price history summary
            summary = price_monitor.get_price_change_summary()
            if 'error' not in summary and summary.get('price_stats'):
                embed.add_field(name="📊 Recent Statistics", value="", inline=False)
                embed.add_field(name="📈 Average", value=f"${summary['price_stats']['avg_price']:.2f}", inline=True)
                embed.add_field(name="📉 Range", value=f"${summary['price_stats']['min_price']:.2f} - ${summary['price_stats']['max_price']:.2f}", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ **Error:** No current price available. Try running a price check first.")
    
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to get current price: {str(e)}")
        logger.error(f"Error getting current price: {e}")

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
            # Create update embed
            embed = discord.Embed(
                title="🔄 Oil Price Update Detected!",
                description="A new oil price has been detected",
                color=discord.Color.blue()
            )
            
            if change_event.event_type == 'initial':
                embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
                embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
                embed.add_field(name="📝 Type", value="Initial Price", inline=True)
            else:
                embed.add_field(name="💰 Old Price", value=f"${change_event.old_price:.2f}", inline=True)
                embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
                embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
                embed.add_field(name="📊 Change", value=f"${change_event.price_change:+.2f} ({change_event.price_change_percent:+.2f}%)", inline=True)
            
            await ctx.send(embed=embed)
            
            # Auto-rename channel if configured
            if Config.DISCORD_CHANNEL_ID:
                await auto_rename_channel(change_event.new_price)
        else:
            await ctx.send("✅ **No price updates detected.**")
    
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to check for updates: {str(e)}")
        logger.error(f"Error checking for updates: {e}")

@bot.command(name='monitor')
async def toggle_monitoring(ctx):
    """Toggle automatic price monitoring on/off (Admin only)"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ **Error:** You need 'Manage Channels' permission to use this command.")
        return
    
    if not price_monitor:
        await ctx.send("❌ **Error:** Price monitor not initialized.")
        return
    
    try:
        if price_monitor.monitoring_active:
            price_monitor.stop_monitoring()
            stop_monitoring_task()
            await ctx.send("🛑 **Price monitoring stopped.**")
        else:
            price_monitor.start_monitoring()
            start_monitoring_task()
            await ctx.send("🚀 **Price monitoring started.**")
    
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to toggle monitoring: {str(e)}")
        logger.error(f"Error toggling monitoring: {e}")

@bot.command(name='monitor-status')
async def get_monitoring_status(ctx):
    """Get the current monitoring status"""
    if not price_monitor:
        await ctx.send("❌ **Error:** Price monitor not initialized.")
        return
    
    try:
        status = price_monitor.get_monitoring_status()
        
        # Create status embed
        embed = discord.Embed(
            title="📊 Price Monitoring Status",
            description="Current monitoring system status",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🔄 Monitoring", value="Active" if status['monitoring_active'] else "Inactive", inline=True)
        embed.add_field(name="💰 Current Price", value=f"${status['current_price']['price']:.2f}" if status['current_price']['price'] else "None", inline=True)
        embed.add_field(name="🔄 Current Cycle", value=status['current_price']['cycle'] or "None", inline=True)
        embed.add_field(name="📈 History Entries", value=status['price_history_count'], inline=True)
        embed.add_field(name="⚖️ Change Threshold", value=f"${status['change_threshold']:.2f}", inline=True)
        
        # Add HTTP client status
        http_status = status['http_client_status']
        embed.add_field(name="🌐 HTTP Status", value=f"Status: {http_status.get('status', 'Unknown')}", inline=False)
        embed.add_field(name="⏰ Next Poll", value=f"<t:{int(http_status['next_poll_time'])}:R>", inline=True)
        embed.add_field(name="📡 Poll Interval", value=f"{http_status['current_interval']}s", inline=True)
        
        embed.set_footer(text="Oil Price Alert Bot")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to get monitoring status: {str(e)}")
        logger.error(f"Error getting monitoring status: {e}")

async def auto_rename_channel(new_price: float):
    """Automatically rename the configured channel with the new oil price"""
    if not Config.DISCORD_CHANNEL_ID:
        return
    
    try:
        channel_id = Config.get_channel_id()
        target_channel = bot.get_channel(channel_id)
        
        if not target_channel:
            logger.error(f"Could not find channel with ID {channel_id} for auto-rename")
            return
        
        # Create new channel name with ︲ separator and 💰 emoji
        price_str = f"{new_price:.2f}"
        if '.' in price_str:
            dollars, cents = price_str.split('.')
            new_channel_name = f"oil-price-💰{dollars}︲{cents}"
        else:
            new_channel_name = f"oil-price-💰{price_str}"
        
        # Ensure channel name is within Discord's limits (100 characters)
        if len(new_channel_name) > 100:
            if '.' in price_str:
                dollars, cents = price_str.split('.')
                new_channel_name = f"oil-💰{dollars}︲{cents}"
            else:
                new_channel_name = f"oil-💰{price_str}"
        
        # Rename the channel
        await target_channel.edit(name=new_channel_name)
        logger.info(f"Auto-renamed channel to: {new_channel_name}")
        
    except discord.Forbidden:
        logger.error(f"Bot lacks permission to rename channel {channel_id}")
    except discord.HTTPException as e:
        logger.error(f"Discord API error while auto-renaming channel: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while auto-renaming channel: {e}")

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
                    await auto_rename_channel(change_event.new_price)
                    
                    # Send notification to configured channel
                    if Config.DISCORD_CHANNEL_ID:
                        await send_price_update_notification(change_event)
                
                # Wait for next check (use monitor's polling interval)
                next_poll = price_monitor.http_client.get_next_poll_time()
                wait_time = max(0, next_poll - time.time())
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                else:
                    await asyncio.sleep(300)  # Default 5 minutes
                    
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

async def send_price_update_notification(change_event: PriceChangeEvent):
    """Send price update notification to the configured channel"""
    if not Config.DISCORD_CHANNEL_ID:
        return
    
    try:
        channel_id = Config.get_channel_id()
        target_channel = bot.get_channel(channel_id)
        
        if not target_channel:
            logger.error(f"Could not find channel with ID {channel_id} for notification")
            return
        
        # Create notification embed
        embed = discord.Embed(
            title="🔄 Oil Price Updated!",
            description="Automatic price update detected",
            color=discord.Color.green()
        )
        
        if change_event.event_type == 'initial':
            embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
            embed.add_field(name="📝 Type", value="Initial Price", inline=True)
        else:
            embed.add_field(name="💰 Old Price", value=f"${change_event.old_price:.2f}", inline=True)
            embed.add_field(name="💰 New Price", value=f"${change_event.new_price:.2f}", inline=True)
            embed.add_field(name="🔄 Cycle", value=f"{change_event.new_cycle}", inline=True)
            embed.add_field(name="📊 Change", value=f"${change_event.price_change:+.2f} ({change_event.price_change_percent:+.2f}%)", inline=True)
        
        await target_channel.send(embed=embed)
        logger.info(f"Price update notification sent to channel {channel_id}")
        
    except Exception as e:
        logger.error(f"Error sending price update notification: {e}")

@bot.command(name='status')
async def bot_status(ctx):
    """Show current bot status and configuration"""
    try:
        # Get bot latency
        latency = round(bot.latency * 1000)
        
        # Get configured channel info
        channel_info = "Not configured"
        if Config.DISCORD_CHANNEL_ID:
            channel_id = Config.get_channel_id()
            target_channel = bot.get_channel(channel_id)
            if target_channel:
                channel_info = f"{target_channel.name} (ID: {channel_id})"
            else:
                channel_info = f"Channel not found (ID: {channel_id})"
        
        # Create status embed
        embed = discord.Embed(
            title="🤖 Bot Status",
            description="Current bot configuration and status",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🟢 Status", value="Online", inline=True)
        embed.add_field(name="📡 Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="🏠 Guilds", value=len(bot.guilds), inline=True)
        embed.add_field(name="📺 Target Channel", value=channel_info, inline=False)
        embed.add_field(name="⏰ Polling Interval", value=f"{Config.POLLING_INTERVAL}s", inline=True)
        embed.add_field(name="🔗 Oil Price URL", value=Config.OIL_PRICE_URL, inline=False)
        
        # Add price monitoring status if available
        if price_monitor:
            monitor_status = price_monitor.get_monitoring_status()
            embed.add_field(name="🛢️ Price Monitor", value="Active" if monitor_status['monitoring_active'] else "Inactive", inline=True)
            if monitor_status['current_price']['price']:
                embed.add_field(name="💰 Current Price", value=f"${monitor_status['current_price']['price']:.2f}", inline=True)
        
        embed.set_footer(text=f"Bot ID: {bot.user.id}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ **Error:** Failed to get bot status: {str(e)}")
        logger.error(f"Error getting bot status: {e}")

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


