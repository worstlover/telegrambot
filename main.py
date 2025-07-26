#!/usr/bin/env python3
"""
Telegram Anonymous Channel Management Bot
Main entry point for the bot application
"""

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.handlers import (
    start_handler, message_handler, set_display_name_handler, 
    help_handler, button_callback_handler
)
from bot.admin_handlers import (
    admin_panel_handler, approve_media_handler, reject_media_handler,
    add_admin_handler, remove_admin_handler, add_profanity_handler,
    remove_profanity_handler, toggle_approval_handler, set_rate_limit_handler,
    set_activity_hours_handler, list_settings_handler, list_admins_handler,
    list_profanity_handler
)
from bot.database import init_database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("setname", set_display_name_handler))
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin", admin_panel_handler))
    application.add_handler(CommandHandler("addadmin", add_admin_handler))
    application.add_handler(CommandHandler("removeadmin", remove_admin_handler))
    application.add_handler(CommandHandler("addprofanity", add_profanity_handler))
    application.add_handler(CommandHandler("removeprofanity", remove_profanity_handler))
    application.add_handler(CommandHandler("toggleapproval", toggle_approval_handler))
    application.add_handler(CommandHandler("setratelimit", set_rate_limit_handler))
    application.add_handler(CommandHandler("setactivityhours", set_activity_hours_handler))
    application.add_handler(CommandHandler("settings", list_settings_handler))
    application.add_handler(CommandHandler("listadmins", list_admins_handler))
    application.add_handler(CommandHandler("listprofanity", list_profanity_handler))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(button_callback_handler, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(button_callback_handler, pattern="^reject_"))
    
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
