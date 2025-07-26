"""
Main message handlers for the bot
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from bot.database import (
    get_or_create_user, set_user_display_name, update_last_message_time,
    can_user_send_message, is_channel_active, add_pending_media, log_message,
    get_setting, is_admin, get_all_admins
)
from bot.filters import contains_profanity
from bot.utils import (
    get_rate_limit_minutes, get_activity_hours, requires_approval,
    format_time_remaining, is_valid_display_name, sanitize_text,
    get_file_type_name
)
from bot.config import MESSAGES, CHANNEL_ID, CHANNEL_USERNAME, CHANNEL_FOOTER

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not update.effective_user or not update.message:
        return
        
    user = get_or_create_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دسترسی به پایگاه داده.")
        return
    
    from bot.keyboards import get_main_menu, get_admin_menu
    
    # Show appropriate menu based on admin status
    if is_admin(update.effective_user.id):
        keyboard = get_admin_menu()
        welcome_msg = "🤖 خوش آمدید! شما به عنوان مدیر وارد شده‌اید.\n\n" + MESSAGES['welcome']
    else:
        keyboard = get_main_menu()
        welcome_msg = MESSAGES['welcome']
    
    await update.message.reply_text(welcome_msg, reply_markup=keyboard)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not update.message:
        return
        
    rate_limit = get_rate_limit_minutes()
    help_msg = MESSAGES['help'].format(rate_limit)
    await update.message.reply_text(help_msg)

async def set_display_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setname command"""
    if not update.effective_user or not update.message:
        return
        
    user = get_or_create_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دسترسی به پایگاه داده.")
        return
    
    # Check if user already set name
    if user.get('display_name_set'):
        await update.message.reply_text(MESSAGES['name_already_set'])
        return
    
    # Check if name is provided
    if not context.args:
        await update.message.reply_text("❌ لطفاً نام نمایشی خود را وارد کنید.\nمثال: /setname نام_من")
        return
    
    new_name = ' '.join(context.args).strip()
    
    # Validate name
    if not is_valid_display_name(new_name):
        await update.message.reply_text(MESSAGES['name_invalid'])
        return
    
    # Try to set name
    if set_user_display_name(update.effective_user.id, new_name):
        await update.message.reply_text(MESSAGES['name_set'].format(new_name))
    else:
        await update.message.reply_text(MESSAGES['name_taken'])

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text and media messages"""
    if not update.effective_user or not update.message:
        return
        
    # Check if this is a keyboard button press
    from bot.menu_handlers import handle_keyboard_input, handle_user_state_input
    
    if update.message.text:
        # First check if user is in a specific state (waiting for input)
        if await handle_user_state_input(update, context):
            return
        
        # Then check if it's a keyboard button
        if update.message.text in ["📝 ارسال پیام", "📷 ارسال رسانه", "✏️ تنظیم نام نمایشی", 
                                 "❓ راهنما", "🔗 لینک کانال", "🔄 شروع مجدد",
                                 "👥 مدیریت ادمین‌ها", "🚫 مدیریت کلمات نامناسب", "⚙️ تنظیمات سیستم",
                                 "📊 آمار و گزارش", "📋 تأیید رسانه‌ها", "🔙 بازگشت به منوی کاربر",
                                 "➕ افزودن ادمین", "➖ حذف ادمین", "📋 لیست ادمین‌ها",
                                 "➕ افزودن کلمه", "➖ حذف کلمه", "📋 لیست کلمات",
                                 "⏰ تنظیم محدودیت زمانی", "🕐 تنظیم ساعات فعالیت",
                                 "📋 تغییر وضعیت تأیید", "📊 مشاهده تنظیمات", "🔙 بازگشت"]:
            await handle_keyboard_input(update, context)
            return
    
    user = get_or_create_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ خطا در دسترسی به پایگاه داده.")
        return
    
    # Check rate limiting
    if not can_user_send_message(update.effective_user.id):
        rate_limit = get_rate_limit_minutes()
        await update.message.reply_text(MESSAGES['rate_limited'].format(rate_limit))
        return
    
    # Check channel activity hours
    if not is_channel_active():
        start_hour, end_hour = get_activity_hours()
        await update.message.reply_text(MESSAGES['channel_inactive'].format(start_hour, end_hour))
        return
    
    # Update last message time
    update_last_message_time(update.effective_user.id)
    
    # Handle text messages
    if update.message.text:
        await handle_text_message(update, context, user)
    
    # Handle media messages
    elif (update.message.photo or update.message.video or update.message.audio or 
          update.message.voice or update.message.document):
        await handle_media_message(update, context, user)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict):
    """Handle text messages"""
    text = update.message.text
    
    # Check for profanity
    if contains_profanity(text):
        await update.message.reply_text(MESSAGES['message_filtered'])
        log_message(user['telegram_id'], 'text', 'filtered', 'profanity')
        return
    
    # Prepare message for channel
    display_name = user['display_name']
    channel_message = f"📝 {sanitize_text(text)}\n\n👤 {display_name}{CHANNEL_FOOTER}"
    
    try:
        # Send to channel
        if CHANNEL_ID:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=channel_message,
                parse_mode='HTML'
            )
        
        # Notify user
        await update.message.reply_text(MESSAGES['message_sent'].format(CHANNEL_USERNAME))
        log_message(user['telegram_id'], 'text', 'sent')
        
        # Open channel for user
        if CHANNEL_USERNAME:
            keyboard = [[InlineKeyboardButton("🔗 مشاهده در کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🔗 کانال:", reply_markup=reply_markup)
        
    except TelegramError as e:
        logger.error(f"Error sending message to channel: {e}")
        await update.message.reply_text("❌ خطا در ارسال پیام به کانال.")
        log_message(user['telegram_id'], 'text', 'error', str(e))

async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict):
    """Handle media messages"""
    # Determine file type and get file info
    file_info = None
    file_type = None
    caption = update.message.caption or ""
    
    if update.message.photo:
        file_info = update.message.photo[-1]  # Get highest resolution
        file_type = 'photo'
    elif update.message.video:
        file_info = update.message.video
        file_type = 'video'
    elif update.message.audio:
        file_info = update.message.audio
        file_type = 'audio'
    elif update.message.voice:
        file_info = update.message.voice
        file_type = 'voice'
    elif update.message.document:
        file_info = update.message.document
        file_type = 'document'
    
    if not file_info:
        await update.message.reply_text("❌ نوع فایل پشتیبانی نمی‌شود.")
        return
    
    # Check if approval is required
    if not requires_approval():
        # Send directly to channel
        await send_media_to_channel(update, context, user, file_info, file_type, caption)
        return
    
    # Add to pending media for approval
    media_id = add_pending_media(
        user['telegram_id'],
        update.message.message_id,
        file_info.file_id,
        file_type,
        caption
    )
    
    if media_id:
        await update.message.reply_text(MESSAGES['media_sent_for_review'])
        log_message(user['telegram_id'], file_type, 'pending')
        
        # Notify admins
        await notify_admins_for_approval(context, media_id, user, file_type, caption)
    else:
        await update.message.reply_text("❌ خطا در ارسال رسانه برای بررسی.")
        log_message(user['telegram_id'], file_type, 'error', 'database error')

async def send_media_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               user: dict, file_info, file_type: str, caption: str = ""):
    """Send media directly to channel"""
    display_name = user['display_name']
    
    # Prepare caption
    if caption and contains_profanity(caption):
        caption = ""  # Remove profane caption
    
    channel_caption = f"{sanitize_text(caption)}\n\n👤 {display_name}{CHANNEL_FOOTER}" if caption else f"👤 {display_name}{CHANNEL_FOOTER}"
    
    try:
        # Send to channel based on file type
        if file_type == 'photo':
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=file_info.file_id,
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif file_type == 'video':
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=file_info.file_id,
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif file_type == 'audio':
            await context.bot.send_audio(
                chat_id=CHANNEL_ID,
                audio=file_info.file_id,
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif file_type == 'voice':
            await context.bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=file_info.file_id,
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif file_type == 'document':
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=file_info.file_id,
                caption=channel_caption,
                parse_mode='HTML'
            )
        
        # Notify user
        await update.message.reply_text(MESSAGES['message_sent'].format(CHANNEL_USERNAME))
        log_message(user['telegram_id'], file_type, 'sent')
        
        # Open channel for user
        if CHANNEL_USERNAME:
            keyboard = [[InlineKeyboardButton("🔗 مشاهده در کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🔗 کانال:", reply_markup=reply_markup)
            
    except TelegramError as e:
        logger.error(f"Error sending media to channel: {e}")
        await update.message.reply_text("❌ خطا در ارسال رسانه به کانال.")
        log_message(user['telegram_id'], file_type, 'error', str(e))

async def notify_admins_for_approval(context: ContextTypes.DEFAULT_TYPE, media_id: int, 
                                   user: dict, file_type: str, caption: str):
    """Notify admins about pending media"""
    admins = get_all_admins()
    if not admins:
        logger.warning("No admins found to notify")
        return
    
    file_type_name = get_file_type_name(file_type)
    message = f"📋 درخواست تأیید {file_type_name}\n\n"
    message += f"👤 از: {user['display_name']}\n"
    if caption:
        message += f"📝 توضیحات: {sanitize_text(caption)}\n"
    message += f"\n⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create approval buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f"approve_{media_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{media_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send to all admins
    for admin_id in admins:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=message,
                reply_markup=reply_markup
            )
        except TelegramError as e:
            logger.error(f"Error notifying admin {admin_id}: {e}")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    # Check if user is admin
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما مجوز دسترسی به این بخش را ندارید.")
        return
    
    data = query.data
    
    if data.startswith("approve_"):
        media_id = int(data.split("_")[1])
        await approve_media_callback(query, context, media_id)
    elif data.startswith("reject_"):
        media_id = int(data.split("_")[1])
        await reject_media_callback(query, context, media_id)

async def approve_media_callback(query, context: ContextTypes.DEFAULT_TYPE, media_id: int):
    """Handle media approval"""
    from bot.database import get_pending_media, remove_pending_media
    
    # Get pending media
    media = get_pending_media(media_id)
    if not media:
        await query.edit_message_text("❌ رسانه یافت نشد.")
        return
    
    # Get user info
    user = get_or_create_user(media['user_telegram_id'])
    if not user:
        await query.edit_message_text("❌ خطا در دسترسی به اطلاعات کاربر.")
        return
    
    try:
        # Send media to channel
        display_name = user['display_name']
        caption = media['caption'] if media['caption'] else ""
        
        # Check caption for profanity
        if caption and contains_profanity(caption):
            caption = ""
        
        channel_caption = f"{sanitize_text(caption)}\n\n👤 {display_name}{CHANNEL_FOOTER}" if caption else f"👤 {display_name}{CHANNEL_FOOTER}"
        
        # Send based on file type
        if media['file_type'] == 'photo':
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=media['file_id'],
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif media['file_type'] == 'video':
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=media['file_id'],
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif media['file_type'] == 'audio':
            await context.bot.send_audio(
                chat_id=CHANNEL_ID,
                audio=media['file_id'],
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif media['file_type'] == 'voice':
            await context.bot.send_voice(
                chat_id=CHANNEL_ID,
                voice=media['file_id'],
                caption=channel_caption,
                parse_mode='HTML'
            )
        elif media['file_type'] == 'document':
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=media['file_id'],
                caption=channel_caption,
                parse_mode='HTML'
            )
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=media['user_telegram_id'],
                text=MESSAGES['media_approved'].format(CHANNEL_USERNAME)
            )
            
            # Send channel link
            if CHANNEL_USERNAME:
                keyboard = [[InlineKeyboardButton("🔗 مشاهده در کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=media['user_telegram_id'],
                    text="🔗 کانال:",
                    reply_markup=reply_markup
                )
        except TelegramError as e:
            logger.error(f"Error notifying user about approval: {e}")
        
        # Remove from pending
        remove_pending_media(media_id)
        log_message(media['user_telegram_id'], media['file_type'], 'approved')
        
        # Update admin message
        await query.edit_message_text(f"✅ رسانه تأیید و در کانال منتشر شد.\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
    except TelegramError as e:
        logger.error(f"Error approving media: {e}")
        await query.edit_message_text(f"❌ خطا در ارسال رسانه به کانال: {str(e)}")

async def reject_media_callback(query, context: ContextTypes.DEFAULT_TYPE, media_id: int):
    """Handle media rejection - ask for reason"""
    # For simplicity, we'll use a default reason
    # In a more advanced implementation, you could ask for custom reason
    reason = "محتوای نامناسب"
    
    from bot.database import get_pending_media, remove_pending_media
    
    # Get pending media
    media = get_pending_media(media_id)
    if not media:
        await query.edit_message_text("❌ رسانه یافت نشد.")
        return
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=media['user_telegram_id'],
            text=MESSAGES['media_rejected'].format(reason)
        )
    except TelegramError as e:
        logger.error(f"Error notifying user about rejection: {e}")
    
    # Remove from pending
    remove_pending_media(media_id)
    log_message(media['user_telegram_id'], media['file_type'], 'rejected', reason)
    
    # Update admin message
    await query.edit_message_text(f"❌ رسانه رد شد.\n📝 دلیل: {reason}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
