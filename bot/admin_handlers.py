"""
Admin command handlers for the bot
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import (
    is_admin, add_admin, remove_admin, add_profanity_word, remove_profanity_word,
    get_setting, set_setting, get_all_admins, get_profanity_words
)
from bot.config import MESSAGES

logger = logging.getLogger(__name__)

async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin panel"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    await update.message.reply_text(MESSAGES['admin_panel'])

async def add_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addadmin command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if not context.args:
        await update.message.reply_text("❌ لطفاً ID کاربر را وارد کنید.\nمثال: /addadmin 123456789")
        return
    
    try:
        new_admin_id = int(context.args[0])
        if add_admin(new_admin_id, update.effective_user.id):
            await update.message.reply_text(MESSAGES['admin_added'])
        else:
            await update.message.reply_text("❌ خطا در افزودن مدیر.")
    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_command'])

async def remove_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeadmin command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if not context.args:
        await update.message.reply_text("❌ لطفاً ID کاربر را وارد کنید.\nمثال: /removeadmin 123456789")
        return
    
    try:
        admin_id = int(context.args[0])
        if remove_admin(admin_id):
            await update.message.reply_text(MESSAGES['admin_removed'])
        else:
            await update.message.reply_text(MESSAGES['admin_not_found'])
    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_command'])

async def add_profanity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addprofanity command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if not context.args:
        await update.message.reply_text("❌ لطفاً کلمه نامناسب را وارد کنید.\nمثال: /addprofanity کلمه_نامناسب")
        return
    
    word = ' '.join(context.args).strip().lower()
    if add_profanity_word(word, update.effective_user.id):
        await update.message.reply_text(MESSAGES['profanity_added'])
    else:
        await update.message.reply_text("❌ خطا در افزودن کلمه.")

async def remove_profanity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeprofanity command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if not context.args:
        await update.message.reply_text("❌ لطفاً کلمه نامناسب را وارد کنید.\nمثال: /removeprofanity کلمه_نامناسب")
        return
    
    word = ' '.join(context.args).strip().lower()
    if remove_profanity_word(word):
        await update.message.reply_text(MESSAGES['profanity_removed'])
    else:
        await update.message.reply_text(MESSAGES['profanity_not_found'])

async def toggle_approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /toggleapproval command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    current_setting = get_setting('require_approval')
    new_setting = 'false' if current_setting == 'true' else 'true'
    
    if set_setting('require_approval', new_setting):
        if new_setting == 'true':
            await update.message.reply_text(MESSAGES['approval_enabled'])
        else:
            await update.message.reply_text(MESSAGES['approval_disabled'])
    else:
        await update.message.reply_text("❌ خطا در تغییر تنظیمات.")

async def set_rate_limit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setratelimit command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if not context.args:
        await update.message.reply_text("❌ لطفاً تعداد دقیقه را وارد کنید.\nمثال: /setratelimit 5")
        return
    
    try:
        minutes = int(context.args[0])
        if minutes < 0:
            await update.message.reply_text("❌ تعداد دقیقه باید مثبت باشد.")
            return
        
        if set_setting('rate_limit_minutes', str(minutes)):
            await update.message.reply_text(MESSAGES['rate_limit_set'].format(minutes))
        else:
            await update.message.reply_text("❌ خطا در تنظیم محدودیت زمانی.")
    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_command'])

async def set_activity_hours_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setactivityhours command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    if len(context.args) != 2:
        await update.message.reply_text("❌ لطفاً ساعت شروع و پایان را وارد کنید.\nمثال: /setactivityhours 8 22")
        return
    
    try:
        start_hour = int(context.args[0])
        end_hour = int(context.args[1])
        
        if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
            await update.message.reply_text("❌ ساعت باید بین 0 تا 23 باشد.")
            return
        
        if set_setting('activity_start_hour', str(start_hour)) and set_setting('activity_end_hour', str(end_hour)):
            await update.message.reply_text(MESSAGES['activity_hours_set'].format(start_hour, end_hour))
        else:
            await update.message.reply_text("❌ خطا در تنظیم ساعات فعالیت.")
    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_command'])

async def list_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    # Get all settings
    require_approval = get_setting('require_approval')
    rate_limit = get_setting('rate_limit_minutes')
    start_hour = get_setting('activity_start_hour')
    end_hour = get_setting('activity_end_hour')
    
    settings_text = "⚙️ تنظیمات فعلی:\n\n"
    settings_text += f"📋 تأیید رسانه: {'فعال' if require_approval == 'true' else 'غیرفعال'}\n"
    settings_text += f"⏰ محدودیت زمانی: {rate_limit} دقیقه\n"
    settings_text += f"🕐 ساعات فعالیت: {start_hour}:00 - {end_hour}:00\n"
    
    # Count admins and profanity words
    admins_count = len(get_all_admins())
    profanity_count = len(get_profanity_words())
    
    settings_text += f"👥 تعداد مدیران: {admins_count}\n"
    settings_text += f"🚫 تعداد کلمات نامناسب: {profanity_count}"
    
    await update.message.reply_text(settings_text)

async def list_admins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listadmins command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    admins = get_all_admins()
    if not admins:
        await update.message.reply_text("👥 هیچ مدیری یافت نشد.")
        return
    
    admins_text = "👥 لیست مدیران:\n\n"
    for i, admin_id in enumerate(admins, 1):
        admins_text += f"{i}. {admin_id}\n"
    
    await update.message.reply_text(admins_text)

async def list_profanity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listprofanity command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    words = get_profanity_words()
    if not words:
        await update.message.reply_text("🚫 هیچ کلمه نامناسبی یافت نشد.")
        return
    
    # Split words into chunks to avoid message length limits
    chunk_size = 20
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        words_text = f"🚫 لیست کلمات نامناسب (قسمت {i + 1}):\n\n"
        for j, word in enumerate(chunk, 1):
            words_text += f"{j + (i * chunk_size)}. {word}\n"
        
        await update.message.reply_text(words_text)

async def approve_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual media approval (if needed)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    # This could be used for manual approval commands
    await update.message.reply_text("✅ برای تأیید رسانه از دکمه‌های inline استفاده کنید.")

async def reject_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual media rejection (if needed)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    # This could be used for manual rejection commands
    await update.message.reply_text("❌ برای رد رسانه از دکمه‌های inline استفاده کنید.")

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries (approve/reject buttons)"""
    if not update.callback_query:
        return
        
    query = update.callback_query
    
    # Check if user is admin
    if not is_admin(query.from_user.id):
        await query.answer("❌ شما مجاز به انجام این عمل نیستید.")
        return
    
    # Handle approval
    if query.data.startswith("approve_"):
        await handle_media_approval(query, context)
    elif query.data.startswith("reject_"):
        await handle_media_rejection(query, context)
    else:
        await query.answer("❌ عملیات نامشخص.")

async def handle_media_approval(query, context):
    """Handle media approval"""
    try:
        media_id = query.data.split("_")[1]
        
        # Get media info from database
        from bot.database import get_connection
        conn = get_connection()
        if not conn:
            await query.answer("❌ خطا در دسترسی به پایگاه داده.")
            return
            
        media_info = conn.execute('''
            SELECT user_id, media_type, file_id, caption, message_id 
            FROM pending_media WHERE id = ?
        ''', (int(media_id),)).fetchone()
        
        if not media_info:
            await query.answer("❌ رسانه یافت نشد.")
            return
        
        # Post to channel
        from bot.config import CHANNEL_ID, CHANNEL_FOOTER
        from bot.database import get_user_display_name
        
        display_name = get_user_display_name(media_info['user_id'])
        caption = media_info['caption'] or ""
        full_caption = f"{caption}\n\n{CHANNEL_FOOTER.format(display_name)}"
        
        # Send based on media type
        if media_info['media_type'] == 'photo':
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=media_info['file_id'],
                caption=full_caption
            )
        elif media_info['media_type'] == 'video':
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=media_info['file_id'],
                caption=full_caption
            )
        elif media_info['media_type'] == 'document':
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=media_info['file_id'],
                caption=full_caption
            )
        
        # Remove from pending
        conn.execute('DELETE FROM pending_media WHERE id = ?', (int(media_id),))
        conn.commit()
        
        # Notify user
        await context.bot.send_message(
            chat_id=media_info['user_id'],
            text="✅ رسانه شما تأیید و در کانال منتشر شد!"
        )
        
        # Update admin message
        await query.edit_message_text(
            text="✅ رسانه تأیید و منتشر شد.",
            reply_markup=None
        )
        
        await query.answer("✅ رسانه تأیید شد.")
        
    except Exception as e:
        logger.error(f"Error approving media: {e}")
        await query.answer("❌ خطا در تأیید رسانه.")

async def handle_media_rejection(query, context):
    """Handle media rejection"""
    try:
        media_id = query.data.split("_")[1]
        
        # Get media info from database
        from bot.database import get_connection
        conn = get_connection()
        if not conn:
            await query.answer("❌ خطا در دسترسی به پایگاه داده.")
            return
            
        media_info = conn.execute('''
            SELECT user_id FROM pending_media WHERE id = ?
        ''', (int(media_id),)).fetchone()
        
        if not media_info:
            await query.answer("❌ رسانه یافت نشد.")
            return
        
        # Remove from pending
        conn.execute('DELETE FROM pending_media WHERE id = ?', (int(media_id),))
        conn.commit()
        
        # Notify user
        await context.bot.send_message(
            chat_id=media_info['user_id'],
            text="❌ رسانه شما رد شد. لطفاً محتوای مناسب‌تری ارسال کنید."
        )
        
        # Update admin message
        await query.edit_message_text(
            text="❌ رسانه رد شد.",
            reply_markup=None
        )
        
        await query.answer("❌ رسانه رد شد.")
        
    except Exception as e:
        logger.error(f"Error rejecting media: {e}")
        await query.answer("❌ خطا در رد رسانه.")
