"""
Menu handlers for keyboard interactions
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import (
    get_or_create_user, is_admin, get_setting, set_setting,
    add_admin, remove_admin, get_all_admins,
    add_profanity_word, remove_profanity_word, get_profanity_words
)
from bot.keyboards import (
    get_main_menu, get_admin_menu, get_admin_management_menu,
    get_profanity_menu, get_settings_menu, get_channel_link_keyboard
)
from bot.config import MESSAGES, CHANNEL_USERNAME
from bot.utils import get_rate_limit_minutes, get_activity_hours

logger = logging.getLogger(__name__)

# User states for multi-step operations
user_states = {}

async def handle_keyboard_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle keyboard button presses"""
    if not update.message or not update.effective_user:
        return
    
    text = update.message.text
    user_id = update.effective_user.id
    
    # Get or create user
    user = get_or_create_user(user_id)
    if not user:
        await update.message.reply_text("❌ خطا در دسترسی به پایگاه داده.")
        return
    
    # Handle different button presses
    if text == "📝 ارسال پیام":
        await handle_send_message_button(update, context)
    elif text == "📷 ارسال رسانه":
        await handle_send_media_button(update, context)
    elif text == "✏️ تنظیم نام نمایشی":
        await handle_set_display_name_button(update, context)
    elif text == "❓ راهنما":
        await handle_help_button(update, context)
    elif text == "🔗 لینک کانال":
        await handle_channel_link_button(update, context)
    elif text == "🔄 شروع مجدد":
        await handle_restart_button(update, context)
    
    # Admin menu buttons
    elif text == "👥 مدیریت ادمین‌ها" and is_admin(user_id):
        await handle_admin_management_button(update, context)
    elif text == "🚫 مدیریت کلمات نامناسب" and is_admin(user_id):
        await handle_profanity_management_button(update, context)
    elif text == "⚙️ تنظیمات سیستم" and is_admin(user_id):
        await handle_settings_button(update, context)
    elif text == "📊 آمار و گزارش" and is_admin(user_id):
        await handle_stats_button(update, context)
    elif text == "📋 تأیید رسانه‌ها" and is_admin(user_id):
        await handle_media_approval_button(update, context)
    elif text == "🔙 بازگشت به منوی کاربر":
        await handle_back_to_user_menu(update, context)
    
    # Admin management submenu
    elif text == "➕ افزودن ادمین" and is_admin(user_id):
        await handle_add_admin_button(update, context)
    elif text == "➖ حذف ادمین" and is_admin(user_id):
        await handle_remove_admin_button(update, context)
    elif text == "📋 لیست ادمین‌ها" and is_admin(user_id):
        await handle_list_admins_button(update, context)
    
    # Profanity management submenu
    elif text == "➕ افزودن کلمه" and is_admin(user_id):
        await handle_add_profanity_button(update, context)
    elif text == "➖ حذف کلمه" and is_admin(user_id):
        await handle_remove_profanity_button(update, context)
    elif text == "📋 لیست کلمات" and is_admin(user_id):
        await handle_list_profanity_button(update, context)
    
    # Settings submenu
    elif text == "⏰ تنظیم محدودیت زمانی" and is_admin(user_id):
        await handle_set_rate_limit_button(update, context)
    elif text == "🕐 تنظیم ساعات فعالیت" and is_admin(user_id):
        await handle_set_activity_hours_button(update, context)
    elif text == "📋 تغییر وضعیت تأیید" and is_admin(user_id):
        await handle_toggle_approval_button(update, context)
    elif text == "📊 مشاهده تنظیمات" and is_admin(user_id):
        await handle_view_settings_button(update, context)
    
    # Back button
    elif text == "🔙 بازگشت":
        await handle_back_button(update, context)

async def handle_send_message_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle send message button"""
    await update.message.reply_text(
        "📝 لطفاً پیام متنی خود را ارسال کنید:\n\n"
        "⚠️ توجه: پیام باید عاری از کلمات نامناسب باشد تا در کانال منتشر شود."
    )

async def handle_send_media_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle send media button"""
    require_approval = get_setting('require_approval') == 'true'
    approval_text = "و پس از تأیید مدیر" if require_approval else ""
    
    await update.message.reply_text(
        f"📷 لطفاً رسانه خود (عکس، ویدیو، فایل) را ارسال کنید:\n\n"
        f"⚠️ رسانه شما بررسی {approval_text} در کانال منتشر خواهد شد."
    )

async def handle_set_display_name_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set display name button"""
    if not update.effective_user:
        return
        
    user = get_or_create_user(update.effective_user.id)
    if user.get('display_name_set'):
        await update.message.reply_text(MESSAGES['name_already_set'])
        return
    
    user_states[update.effective_user.id] = 'waiting_for_name'
    await update.message.reply_text(
        "✏️ لطفاً نام نمایشی جدید خود را وارد کنید:\n\n"
        "⚠️ توجه: نام نمایشی فقط یک بار قابل تغییر است و باید یکتا باشد."
    )

async def handle_help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help button"""
    rate_limit = get_rate_limit_minutes()
    help_msg = MESSAGES['help'].format(rate_limit)
    await update.message.reply_text(help_msg)

async def handle_channel_link_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle channel link button"""
    if CHANNEL_USERNAME:
        keyboard = get_channel_link_keyboard(CHANNEL_USERNAME)
        await update.message.reply_text("🔗 لینک کانال:", reply_markup=keyboard)
    else:
        await update.message.reply_text("❌ لینک کانال تنظیم نشده است.")

async def handle_restart_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle restart button"""
    if not update.effective_user:
        return
        
    # Clear user state
    if update.effective_user.id in user_states:
        del user_states[update.effective_user.id]
    
    # Show main menu
    keyboard = get_main_menu()
    await update.message.reply_text(
        "🔄 ربات مجدداً راه‌اندازی شد!\n\n" + MESSAGES['welcome'],
        reply_markup=keyboard
    )

async def handle_admin_management_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin management button"""
    keyboard = get_admin_management_menu()
    await update.message.reply_text(
        "👥 مدیریت ادمین‌ها:\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )

async def handle_profanity_management_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profanity management button"""
    keyboard = get_profanity_menu()
    await update.message.reply_text(
        "🚫 مدیریت کلمات نامناسب:\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )

async def handle_settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings button"""
    keyboard = get_settings_menu()
    await update.message.reply_text(
        "⚙️ تنظیمات سیستم:\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )

async def handle_stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stats button"""
    # Get system statistics
    admins_count = len(get_all_admins())
    profanity_count = len(get_profanity_words())
    rate_limit = get_rate_limit_minutes()
    start_hour, end_hour = get_activity_hours()
    require_approval = get_setting('require_approval') == 'true'
    
    stats_text = f"""📊 آمار و وضعیت سیستم:

👥 تعداد ادمین‌ها: {admins_count}
🚫 تعداد کلمات نامناسب: {profanity_count}
⏰ محدودیت زمانی: {rate_limit} دقیقه
🕐 ساعات فعالیت: {start_hour}:00 - {end_hour}:00
📋 تأیید رسانه: {'فعال' if require_approval else 'غیرفعال'}

🤖 ربات فعال و آماده دریافت پیام‌هاست."""
    
    await update.message.reply_text(stats_text)

async def handle_media_approval_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle media approval button"""
    await update.message.reply_text(
        "📋 برای تأیید رسانه‌ها:\n\n"
        "• پس از ارسال رسانه توسط کاربران، پیام تأیید برای شما ارسال می‌شود\n"
        "• از دکمه‌های ✅ تأیید یا ❌ رد استفاده کنید\n"
        "• در صورت رد، دلیل به کاربر اطلاع داده می‌شود"
    )

async def handle_back_to_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to user menu"""
    keyboard = get_main_menu()
    await update.message.reply_text("🔙 بازگشت به منوی اصلی:", reply_markup=keyboard)

async def handle_add_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add admin button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_admin_id'
    await update.message.reply_text(
        "➕ افزودن ادمین جدید:\n\n"
        "لطفاً ID کاربری ادمین جدید را ارسال کنید:\n"
        "مثال: 123456789"
    )

async def handle_remove_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove admin button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_remove_admin_id'
    await update.message.reply_text(
        "➖ حذف ادمین:\n\n"
        "لطفاً ID کاربری ادمینی که می‌خواهید حذف کنید را ارسال کنید:\n"
        "مثال: 123456789"
    )

async def handle_list_admins_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle list admins button"""
    admins = get_all_admins()
    if not admins:
        await update.message.reply_text("👥 هیچ ادمینی یافت نشد.")
        return
    
    admins_text = "👥 لیست ادمین‌ها:\n\n"
    for i, admin_id in enumerate(admins, 1):
        admins_text += f"{i}. {admin_id}\n"
    
    await update.message.reply_text(admins_text)

async def handle_add_profanity_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add profanity button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_profanity_word'
    await update.message.reply_text(
        "➕ افزودن کلمه نامناسب:\n\n"
        "لطفاً کلمه نامناسب جدید را ارسال کنید:"
    )

async def handle_remove_profanity_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove profanity button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_remove_profanity'
    await update.message.reply_text(
        "➖ حذف کلمه نامناسب:\n\n"
        "لطفاً کلمه‌ای که می‌خواهید حذف کنید را ارسال کنید:"
    )

async def handle_list_profanity_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle list profanity button"""
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

async def handle_set_rate_limit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set rate limit button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_rate_limit'
    current_limit = get_rate_limit_minutes()
    await update.message.reply_text(
        f"⏰ تنظیم محدودیت زمانی:\n\n"
        f"محدودیت فعلی: {current_limit} دقیقه\n\n"
        f"لطفاً تعداد دقیقه جدید را وارد کنید:"
    )

async def handle_set_activity_hours_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set activity hours button"""
    if not update.effective_user:
        return
        
    user_states[update.effective_user.id] = 'waiting_for_activity_hours'
    start_hour, end_hour = get_activity_hours()
    await update.message.reply_text(
        f"🕐 تنظیم ساعات فعالیت:\n\n"
        f"ساعات فعلی: {start_hour}:00 - {end_hour}:00\n\n"
        f"لطفاً ساعت شروع و پایان را وارد کنید:\n"
        f"مثال: 8 22"
    )

async def handle_toggle_approval_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle toggle approval button"""
    current_setting = get_setting('require_approval')
    new_setting = 'false' if current_setting == 'true' else 'true'
    
    if set_setting('require_approval', new_setting):
        if new_setting == 'true':
            await update.message.reply_text(MESSAGES['approval_enabled'])
        else:
            await update.message.reply_text(MESSAGES['approval_disabled'])
    else:
        await update.message.reply_text("❌ خطا در تغییر تنظیمات.")

async def handle_view_settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view settings button"""
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

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button - context sensitive"""
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    # Clear any active state
    if user_id in user_states:
        del user_states[user_id]
    
    # Determine which menu to show based on admin status
    if is_admin(user_id):
        keyboard = get_admin_menu()
        await update.message.reply_text("🔙 بازگشت به منوی ادمین:", reply_markup=keyboard)
    else:
        keyboard = get_main_menu()
        await update.message.reply_text("🔙 بازگشت به منوی اصلی:", reply_markup=keyboard)

async def handle_user_state_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input when user is in a specific state"""
    if not update.effective_user or not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_states:
        return False
    
    state = user_states[user_id]
    
    if state == 'waiting_for_name':
        await handle_display_name_input(update, context, text)
    elif state == 'waiting_for_admin_id':
        await handle_admin_id_input(update, context, text)
    elif state == 'waiting_for_remove_admin_id':
        await handle_remove_admin_id_input(update, context, text)
    elif state == 'waiting_for_profanity_word':
        await handle_profanity_word_input(update, context, text)
    elif state == 'waiting_for_remove_profanity':
        await handle_remove_profanity_input(update, context, text)
    elif state == 'waiting_for_rate_limit':
        await handle_rate_limit_input(update, context, text)
    elif state == 'waiting_for_activity_hours':
        await handle_activity_hours_input(update, context, text)
    
    return True

async def handle_display_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle display name input"""
    if not update.effective_user or not update.message:
        return
        
    from bot.utils import is_valid_display_name
    from bot.database import set_user_display_name
    
    if not is_valid_display_name(text):
        await update.message.reply_text(MESSAGES['name_invalid'])
        return
    
    if set_user_display_name(update.effective_user.id, text):
        await update.message.reply_text(MESSAGES['name_set'].format(text))
        del user_states[update.effective_user.id]
    else:
        await update.message.reply_text(MESSAGES['name_taken'])

async def handle_admin_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle admin ID input"""
    if not update.effective_user or not update.message:
        return
        
    try:
        admin_id = int(text)
        if add_admin(admin_id, update.effective_user.id):
            await update.message.reply_text(MESSAGES['admin_added'])
        else:
            await update.message.reply_text("❌ خطا در افزودن ادمین.")
        del user_states[update.effective_user.id]
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")

async def handle_remove_admin_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle remove admin ID input"""
    if not update.effective_user or not update.message:
        return
        
    try:
        admin_id = int(text)
        if remove_admin(admin_id):
            await update.message.reply_text(MESSAGES['admin_removed'])
        else:
            await update.message.reply_text(MESSAGES['admin_not_found'])
        del user_states[update.effective_user.id]
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")

async def handle_profanity_word_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle profanity word input"""
    if not update.effective_user or not update.message:
        return
        
    if add_profanity_word(text.lower(), update.effective_user.id):
        await update.message.reply_text(MESSAGES['profanity_added'])
    else:
        await update.message.reply_text("❌ خطا در افزودن کلمه.")
    del user_states[update.effective_user.id]

async def handle_remove_profanity_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle remove profanity input"""
    if not update.effective_user or not update.message:
        return
        
    if remove_profanity_word(text.lower()):
        await update.message.reply_text(MESSAGES['profanity_removed'])
    else:
        await update.message.reply_text(MESSAGES['profanity_not_found'])
    del user_states[update.effective_user.id]

async def handle_rate_limit_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle rate limit input"""
    if not update.effective_user or not update.message:
        return
        
    try:
        minutes = int(text)
        if minutes < 0:
            await update.message.reply_text("❌ تعداد دقیقه باید مثبت باشد.")
            return
        
        if set_setting('rate_limit_minutes', str(minutes)):
            await update.message.reply_text(MESSAGES['rate_limit_set'].format(minutes))
        else:
            await update.message.reply_text("❌ خطا در تنظیم محدودیت زمانی.")
        del user_states[update.effective_user.id]
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید.")

async def handle_activity_hours_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle activity hours input"""
    if not update.effective_user or not update.message:
        return
        
    try:
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ لطفاً دو عدد وارد کنید. مثال: 8 22")
            return
        
        start_hour = int(parts[0])
        end_hour = int(parts[1])
        
        if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
            await update.message.reply_text("❌ ساعت باید بین 0 تا 23 باشد.")
            return
        
        if set_setting('activity_start_hour', str(start_hour)) and set_setting('activity_end_hour', str(end_hour)):
            await update.message.reply_text(MESSAGES['activity_hours_set'].format(start_hour, end_hour))
        else:
            await update.message.reply_text("❌ خطا در تنظیم ساعات فعالیت.")
        del user_states[update.effective_user.id]
    except ValueError:
        await update.message.reply_text("❌ لطفاً دو عدد معتبر وارد کنید.")