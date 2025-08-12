import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Oil Price Alert Bot"""
    
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
    
    # Oil Price Monitoring Configuration
    OIL_PRICE_URL = os.getenv('OIL_PRICE_URL', 'https://play.myfly.club/oil-prices')
    
    # Parse POLLING_INTERVAL, handling comments and whitespace
    _polling_raw = os.getenv('POLLING_INTERVAL', '300')
    if _polling_raw:
        # Remove comments and strip whitespace
        _polling_clean = _polling_raw.split('#')[0].strip()
        try:
            POLLING_INTERVAL = int(_polling_clean)
        except ValueError:
            print(f"Warning: Invalid POLLING_INTERVAL '{_polling_raw}', using default 300")
            POLLING_INTERVAL = 300
    else:
        POLLING_INTERVAL = 300
    
    # Bot Configuration
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    BOT_STATUS = os.getenv('BOT_STATUS', 'Monitoring Oil Prices')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = ['DISCORD_TOKEN']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_channel_id(cls):
        """Get the Discord channel ID as an integer"""
        if cls.DISCORD_CHANNEL_ID:
            try:
                return int(cls.DISCORD_CHANNEL_ID)
            except ValueError:
                raise ValueError(f"Invalid DISCORD_CHANNEL_ID: {cls.DISCORD_CHANNEL_ID}")
        return None
