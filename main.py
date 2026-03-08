import os
import asyncio
import traceback
import discord
from dotenv import load_dotenv
from bot.config_manager import ConfigManager
from bot.tts_client import TTSClient
from bot.client import TTSBot
from bot.logger import get_logger

load_dotenv()

# Enable discord.py logging
discord.utils.setup_logging()

logger = get_logger("Main")

async def main():
    logger.info("Starting bot initialization...")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables or .env file.")
        return

    try:
        config_manager = ConfigManager()
        tts_client = TTSClient(config_manager)
        bot = TTSBot(config_manager, tts_client)
        
        logger.info("Attempting to connect to Discord...")
        async with bot:
            await bot.start(token)
            
    except Exception as e:
        logger.error("A critical error occurred during bot execution:")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        # Check for FFmpeg first
        import subprocess
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            logger.info("FFmpeg found and verified.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found! Audio playback will fail. Please install FFmpeg and add it to PATH.")

        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutting down (KeyboardInterrupt)...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()
