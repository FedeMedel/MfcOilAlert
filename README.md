# Oil Price Alert Discord Bot

A Discord bot that monitors oil prices from [play.myfly.club/oil-prices](https://play.myfly.club/oil-prices) and automatically updates a Discord channel with price changes.

## Features

- 🔍 **Real-time monitoring** of oil prices
- 📝 **Automatic channel renaming** with current prices
- 📊 **Price change logging** in Discord channels
- ⚡ **Fast response** with Discord slash commands
- 🛡️ **Error handling** and rate limiting

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
cd OilPriceAlert
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
   POLLING_INTERVAL=300
   BOT_PREFIX=!
   BOT_STATUS=Monitoring Oil Prices
   ```

### 8. Test Connection

```bash
python test_connection.py
```

### 9. Run the Bot

```bash
python src/bot.py
```

## Testing the Bot

Once the bot is running, you can test it with these commands:

- `!!check` - Check bot responsiveness

## Project Structure

```
OilPriceAlert/
├── src/
│   └── bot.py              # Main bot file
├── config/
│   └── config.py           # Configuration management
├── utils/                   # Utility functions (future)
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── test_connection.py      # Connection test script
└── README.md               # This file
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `DISCORD_CHANNEL_ID` | Target channel ID | Required |
| `OIL_PRICE_URL` | Oil price website URL | `https://play.myfly.club/oil-prices` |
| `POLLING_INTERVAL` | Price check interval (seconds) | `180` (3 minutes) |
| `BOT_PREFIX` | Command prefix | `!` |
| `BOT_STATUS` | Bot status message | `Monitoring Oil Prices` |

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

## Development

This bot is built with:
- **discord.py** - Discord API wrapper
- **requests** - HTTP requests for web scraping
- **beautifulsoup4** - HTML parsing
- **python-dotenv** - Environment variable management

## License

[Add your license here]

## Support

For issues and questions, please [create an issue](link-to-issues) in this repository.
