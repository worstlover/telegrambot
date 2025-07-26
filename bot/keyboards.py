"""
Keyboard layouts for the bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# Main menu for regular users
def get_main_menu():
    """Get main menu keyboard for users"""
    keyboard = [
        [KeyboardButton("📝 ارسال پیام"), KeyboardButton("📷 ارسال رسانه")],
        [KeyboardButton("✏️ تنظیم نام نمایشی"), KeyboardButton("❓ راهنما")],
        [KeyboardButton("🔗 لینک کانال"), KeyboardButton("🔄 شروع مجدد")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Admin menu
def get_admin_menu():
    """Get admin menu keyboard"""
    keyboard = [
        [KeyboardButton("👥 مدیریت ادمین‌ها"), KeyboardButton("🚫 مدیریت کلمات نامناسب")],
        [KeyboardButton("⚙️ تنظیمات سیستم"), KeyboardButton("📊 آمار و گزارش")],
        [KeyboardButton("📋 تأیید رسانه‌ها"), KeyboardButton("🔙 بازگشت به منوی کاربر")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Admin management submenu
def get_admin_management_menu():
    """Get admin management submenu"""
    keyboard = [
        [KeyboardButton("➕ افزودن ادمین"), KeyboardButton("➖ حذف ادمین")],
        [KeyboardButton("📋 لیست ادمین‌ها"), KeyboardButton("🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Profanity management submenu
def get_profanity_menu():
    """Get profanity management submenu"""
    keyboard = [
        [KeyboardButton("➕ افزودن کلمه"), KeyboardButton("➖ حذف کلمه")],
        [KeyboardButton("📋 لیست کلمات"), KeyboardButton("🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Settings submenu
def get_settings_menu():
    """Get settings submenu"""
    keyboard = [
        [KeyboardButton("⏰ تنظیم محدودیت زمانی"), KeyboardButton("🕐 تنظیم ساعات فعالیت")],
        [KeyboardButton("📋 تغییر وضعیت تأیید"), KeyboardButton("📊 مشاهده تنظیمات")],
        [KeyboardButton("🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Inline keyboards for media approval
def get_media_approval_keyboard(media_id: int):
    """Get inline keyboard for media approval"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f"approve_{media_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{media_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Inline keyboard for channel link
def get_channel_link_keyboard(channel_username: str):
    """Get inline keyboard for channel link"""
    keyboard = [
        [InlineKeyboardButton("🔗 مشاهده کانال", url=f"https://t.me/{channel_username}")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Confirmation keyboards
def get_confirmation_keyboard(action: str, item_id: str = ""):
    """Get confirmation keyboard for actions"""
    keyboard = [
        [
            InlineKeyboardButton("✅ بله", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton("❌ خیر", callback_data=f"cancel_{action}_{item_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Language selection keyboard (for future use)
def get_language_keyboard():
    """Get language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Back button
def get_back_button():
    """Get simple back button"""
    keyboard = [[KeyboardButton("🔙 بازگشت")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Remove keyboard
def remove_keyboard():
    """Remove keyboard"""
    from telegram import ReplyKeyboardRemove
    return ReplyKeyboardRemove()