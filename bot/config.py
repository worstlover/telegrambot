"""
Configuration settings for the bot
"""

import os

# Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # Channel where messages will be posted
CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "")  # Without @

# Database Configuration
DATABASE_PATH = "bot_database.db"

# Default Settings
DEFAULT_RATE_LIMIT_MINUTES = 5
DEFAULT_ACTIVITY_START_HOUR = 0  # 24-hour format
DEFAULT_ACTIVITY_END_HOUR = 23
DEFAULT_REQUIRE_APPROVAL = True

# Default Profanity Words (Persian and English)
DEFAULT_PROFANITY_WORDS = [
    # Persian profanity words
    "کس", "کیر", "کون", "جنده", "فاحشه", "گاییدم", "کسکش", "کونی",
    "مادرجنده", "پدرسگ", "بیناموس", "حرومزاده", "کصخل", "گوز",
    # English profanity words
    "fuck", "shit", "damn", "bitch", "bastard", "asshole", "crap",
    "fucking", "motherfucker", "cocksucker", "dickhead", "prick"
]

# Bot Messages
MESSAGES = {
    "welcome": """🤖 به ربات کانال ناشناس خوش آمدید!

📝 برای ارسال پیام متنی، کافیست پیام خود را ارسال کنید.
📷 برای ارسال رسانه (عکس، ویدیو، فایل)، آن را ارسال کنید تا بررسی شود.
✏️ برای تنظیم نام نمایشی: /setname
❓ برای راهنما: /help

⚠️ تمام پیام‌ها ناشناس هستند و هویت شما محفوظ می‌ماند.""",
    
    "help": """📋 راهنمای استفاده:

🔸 /start - شروع مجدد ربات
🔸 /setname [نام] - تنظیم نام نمایشی (فقط یک بار قابل تغییر)
🔸 /help - نمایش این راهنما

📝 ارسال پیام متنی:
• پیام خود را تایپ کنید و ارسال کنید
• اگر حاوی کلمات نامناسب نباشد، مستقیماً در کانال منتشر می‌شود

📷 ارسال رسانه:
• عکس، ویدیو یا فایل خود را ارسال کنید
• پس از بررسی مدیر، در صورت تأیید در کانال منتشر می‌شود

⚠️ توجه:
• هر کاربر هر {} دقیقه یک بار می‌تواند پیام ارسال کند
• تمام پیام‌ها کاملاً ناشناس هستند
• نام نمایشی شما فقط یک بار قابل تغییر است""",
    
    "name_set": "✅ نام نمایشی شما با موفقیت تنظیم شد: {}",
    "name_already_set": "⚠️ شما قبلاً نام نمایشی خود را تنظیم کرده‌اید و نمی‌توانید تغییر دهید.",
    "name_taken": "❌ این نام قبلاً انتخاب شده است. لطفاً نام دیگری انتخاب کنید.",
    "name_invalid": "❌ نام نمایشی نامعتبر است. لطفاً نام معتبری انتخاب کنید.",
    
    "message_sent": "✅ پیام شما در کانال منتشر شد!\n🔗 مشاهده: @{}",
    "message_filtered": "❌ پیام شما حاوی کلمات نامناسب است و ارسال نشد.",
    "media_sent_for_review": "📋 رسانه شما برای بررسی ارسال شد. نتیجه به زودی اطلاع داده می‌شود.",
    "media_approved": "✅ رسانه شما تأیید و در کانال منتشر شد!\n🔗 مشاهده: @{}",
    "media_rejected": "❌ رسانه شما رد شد.\n📝 دلیل: {}",
    
    "rate_limited": "⏰ شما اخیراً پیام ارسال کرده‌اید. لطفاً {} دقیقه صبر کنید.",
    "channel_inactive": "😴 کانال در حال حاضر غیرفعال است. ساعات فعالیت: {}:00 تا {}:00",
    
    "admin_panel": """🔧 پنل مدیریت:

/addadmin [user_id] - افزودن مدیر
/removeadmin [user_id] - حذف مدیر
/addprofanity [کلمه] - افزودن کلمه نامناسب
/removeprofanity [کلمه] - حذف کلمه نامناسب
/toggleapproval - تغییر وضعیت تأیید رسانه
/setratelimit [دقیقه] - تنظیم محدودیت زمانی
/setactivityhours [ساعت_شروع] [ساعت_پایان] - تنظیم ساعات فعالیت
/settings - نمایش تنظیمات
/listadmins - لیست مدیران
/listprofanity - لیست کلمات نامناسب""",
    
    "not_admin": "❌ شما مجوز دسترسی به این بخش را ندارید.",
    "admin_added": "✅ مدیر جدید اضافه شد.",
    "admin_removed": "✅ مدیر حذف شد.",
    "admin_not_found": "❌ مدیر یافت نشد.",
    "profanity_added": "✅ کلمه نامناسب اضافه شد.",
    "profanity_removed": "✅ کلمه نامناسب حذف شد.",
    "profanity_not_found": "❌ کلمه یافت نشد.",
    "approval_enabled": "✅ تأیید رسانه فعال شد.",
    "approval_disabled": "✅ تأیید رسانه غیرفعال شد.",
    "rate_limit_set": "✅ محدودیت زمانی به {} دقیقه تنظیم شد.",
    "activity_hours_set": "✅ ساعات فعالیت به {}:00 - {}:00 تنظیم شد.",
    "invalid_command": "❌ فرمت دستور نامعتبر است.",
}

# Channel footer message
CHANNEL_FOOTER = f"\n\n📢 @{CHANNEL_USERNAME}"
