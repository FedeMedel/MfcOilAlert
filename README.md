# Oil Price Alert Discord Bot

A Discord bot that monitors oil prices from [play.myfly.club/oil-prices](https://play.myfly.club/oil-prices) and automatically updates Discord channels with price changes and channel renaming.

## Features

- 🔍 **Real-time JSON endpoint monitoring** with smart polling and content change detection
- 📝 **Automatic channel renaming** with current prices and trend indicators (📈/📉)
- 📊 **Price change notifications** with detailed Discord embeds
- ⚡ **Efficient HTTP client** with conditional requests and retry logic
- 🛡️ **Robust error handling** and rate limiting
- ⏰ **UTC timestamps** on all price updates
- 💾 **Local price history storage** with change detection

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord Server with appropriate permissions

## Setup Instructions

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Enable the following bot permissions:
   - Send Messages
   - Manage Channels (for renaming)
   - Read Message History
   - Use Slash Commands

### 2. Invite Bot to Your Server

1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select the permissions mentioned above
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Get Channel ID

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the channel you want the bot to monitor
3. Click "Copy ID"

### 4. Clone and Setup Repository

```bash
git clone <your-repo-url>
cd MfcOilAlert
```

### 5. Create Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

### 7. Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file with your values:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   OIL_PRICE_URL=https://play.myfly.club/oil-prices
   POLLING_INTERVAL=120
   BOT_PREFIX=!
   BOT_STATUS=Monitoring Oil Prices
   ```

### 8. Run the Bot

```bash
python src/bot.py
```

## How It Works

The bot automatically starts monitoring oil prices when it comes online:

1. **Fetches prices** from the JSON endpoint every 2 minutes (configurable)
2. **Detects changes** using content hashing and cycle number comparison
3. **Renames channel** with new price and trend indicator (e.g., `oil-price💲76-28📈`)
4. **Sends notifications** to Discord with price change details and UTC timestamp
5. **Stores history** locally for change detection and statistics

## Testing the Bot

Once running, you can use:
- `!check` - Manually check for price updates and force refresh

## Project Structure

```
OilPriceAlert/
├── src/
│   └── bot.py              # Main Discord bot with passive monitoring
├── config/
│   └── config.py           # Configuration management
├── utils/
│   ├── __init__.py
│   ├── http_client.py      # HTTP client with conditional requests
│   ├── price_monitor.py    # Price monitoring and change detection
│   └── price_parser.py     # JSON response parser
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── price_history.json     # Local price storage (auto-generated)
└── README.md              # This file
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `DISCORD_CHANNEL_ID` | Target channel ID | Required |
| `OIL_PRICE_URL` | Oil price JSON endpoint | `https://play.myfly.club/oil-prices` |
| `POLLING_INTERVAL` | Price check interval (seconds) | `120` (2 minutes) |
| `BOT_PREFIX` | Command prefix | `!` |
| `BOT_STATUS` | Bot status message | `Monitoring Oil Prices` |

## Architecture

- **Bot (src/bot.py)**: Discord integration, passive monitoring, channel management
- **Price Monitor (utils/price_monitor.py)**: Change detection, history storage, event management
- **HTTP Client (utils/http_client.py)**: Efficient endpoint polling with conditional requests
- **Price Parser (utils/price_parser.py)**: JSON response parsing and latest price extraction

## Message Format

All price updates use a unified format:
```
🔄 Oil Price Updated!
Automatic price update detected
💰 Old Price: $72.59
💰 New Price: $76.28
🔄 Cycle: 6548
📊 Change: $+3.69 (+5.08%)
⏰ Time: 14:30 UTC
```

## Troubleshooting

### Bot Won't Connect
- Check if your bot token is correct
- Ensure the bot has proper permissions
- Verify the bot is invited to your server

### Permission Errors
- Make sure the bot has "Manage Channels" permission
- Check if the bot can see the target channel
- Verify the bot has "Send Messages" permission

### Import Errors
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Dependencies

- **discord.py==2.3.2** - Discord API wrapper
- **requests==2.31.0** - HTTP requests with retry logic
- **beautifulsoup4==4.12.2** - HTML parsing (if needed)
- **python-dotenv==1.0.0** - Environment variable management
- **html5lib==1.1** - HTML parsing library

## License

[Add your license here]

## Support

For issues and questions, please [create an issue](link-to-issues) in this repository.