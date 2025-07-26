#!/usr/bin/env python3
"""
Telegram Anonymous Channel Management Bot
Main entry point for the bot application
"""

import os
import logging
import asyncio
import threading
import time
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.handlers import start_handler, message_handler
from bot.admin_handlers import admin_callback_handler
from bot.database import init_database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def keep_alive():
    """Keep the program alive by periodically logging status"""
    while True:
        time.sleep(300)  # Every 5 minutes
        logger.info("Bot is running and active")

def main():
    """Start the bot"""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Initialize database
    init_database()
    
    # Start keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    
    # Callback query handlers for admin approval
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        message_handler
    ))
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL | filters.VOICE) & ~filters.COMMAND,
        message_handler
    ))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
