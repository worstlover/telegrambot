# ربات تلگرام مدیریت کانال ناشناس

ربات جامع برای مدیریت کانال‌های تلگرام با قابلیت ارسال پیام‌های ناشناس، سیستم تایید مدیر، فیلتر کلمات نامناسب و کنترل‌های مدیریتی پیشرفته.

## ویژگی‌های اصلی

### برای کاربران عادی:
- 📝 ارسال پیام‌های متنی ناشناس به کانال
- 📷 ارسال رسانه (عکس، ویدیو، فایل) با سیستم تایید مدیر
- ✏️ تنظیم نام نمایشی یکتا (فقط یک بار قابل تغییر)
- 🔗 دسترسی آسان به لینک کانال
- ⏰ محدودیت زمانی بین ارسال پیام‌ها (پیش‌فرض: 5 دقیقه)

### برای مدیران:
- 👥 مدیریت ادمین‌ها (افزودن/حذف/لیست)
- 🚫 مدیریت کلمات فیلتر (افزودن/حذف/مشاهده)
- ⚙️ تنظیمات سیستم (محدودیت زمانی، ساعات فعالیت)
- 📋 تایید/رد رسانه‌های ارسالی
- 📊 مشاهده آمار و گزارش‌ها

### ویژگی‌های فنی:
- 🛡️ فیلتر هوشمند کلمات نامناسب (فارسی و انگلیسی)
- 🕐 کنترل ساعات فعالیت کانال
- 💾 ذخیره‌سازی در SQLite
- 🔒 حفظ کامل ناشناس بودن کاربران
- 📱 رابط کاربری با کیبورد تعاملی

## راه‌اندازی

### پیش‌نیازها
1. Python 3.11+
2. کتابخانه `python-telegram-bot`
3. ربات تلگرام از BotFather
4. کانال تلگرام

### مراحل نصب

1. **ایجاد ربات در تلگرام:**
   - به @BotFather پیام دهید
   - دستور `/newbot` را اجرا کنید
   - نام و username ربات را تعیین کنید
   - توکن دریافتی را ذخیره کنید

2. **ایجاد کانال:**
   - کانال جدیدی بسازید
   - ربات را به عنوان ادمین به کانال اضافه کنید
   - ID کانال را بدست آورید

3. **تنظیم متغیرهای محیطی:**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHANNEL_ID=@your_channel_username_or_-100channel_id
   TELEGRAM_CHANNEL_USERNAME=your_channel_username
   ```

4. **اجرای ربات:**
   ```bash
   python main.py
   ```

## راهنمای استفاده

### برای کاربران

1. **شروع استفاده:**
   - ربات را `/start` کنید
   - منوی اصلی نمایش داده می‌شود

2. **ارسال پیام متنی:**
   - دکمه "📝 ارسال پیام" را بزنید
   - پیام متنی خود را ارسال کنید
   - در صورت عدم وجود کلمات نامناسب، در کانال منتشر می‌شود

3. **ارسال رسانه:**
   - دکمه "📷 ارسال رسانه" را بزنید
   - فایل خود را ارسال کنید
   - پس از تایید مدیر در کانال منتشر می‌شود

4. **تنظیم نام نمایشی:**
   - دکمه "✏️ تنظیم نام نمایشی" را بزنید
   - نام مورد نظر را وارد کنید (فقط یک بار قابل تغییر)

### برای مدیران

1. **دسترسی به پنل مدیریت:**
   - پس از `/start`، منوی مدیریت نمایش داده می‌شود
   - یا از دکمه "🔙 بازگشت به منوی کاربر" استفاده کنید

2. **مدیریت ادمین‌ها:**
   - "👥 مدیریت ادمین‌ها" → انتخاب عملیات مورد نظر
   - برای افزودن: ID تلگرام کاربر جدید را وارد کنید

3. **تایید رسانه‌ها:**
   - پیام‌های تایید به صورت خودکار ارسال می‌شود
   - از دکمه‌های ✅ تایید یا ❌ رد استفاده کنید

4. **تنظیمات سیستم:**
   - محدودیت زمانی بین پیام‌ها
   - ساعات فعالیت کانال (مثلاً 8:00 تا 22:00)
   - فعال/غیرفعال کردن سیستم تایید رسانه

## ساختار پروژه

```
├── main.py                 # نقطه ورود اصلی
├── bot/
│   ├── __init__.py
│   ├── config.py          # تنظیمات و پیام‌ها
│   ├── database.py        # عملیات پایگاه داده
│   ├── handlers.py        # هندلرهای اصلی پیام
│   ├── admin_handlers.py  # هندلرهای مدیریتی
│   ├── menu_handlers.py   # هندلرهای منو و کیبورد
│   ├── keyboards.py       # کیبوردهای تعاملی
│   ├── filters.py         # فیلتر کلمات نامناسب
│   └── utils.py          # توابع کمکی
└── bot_database.db        # پایگاه داده SQLite
```

## پایگاه داده

ربات دارای 6 جدول اصلی است:

- **users**: اطلاعات کاربران و نام‌های نمایشی
- **admins**: لیست مدیران سیستم
- **profanity_words**: کلمات فیلتر شده
- **settings**: تنظیمات سیستم
- **pending_media**: رسانه‌های در انتظار تایید
- **message_logs**: لاگ تمام پیام‌ها

## امنیت و حریم خصوصی

- ✅ ID تلگرام کاربران هیچ‌گاه ذخیره نمی‌شود
- ✅ تمام پیام‌ها کاملاً ناشناس منتشر می‌شوند
- ✅ فیلتر هوشمند کلمات نامناسب
- ✅ سیستم محدودیت زمانی برای جلوگیری از spam
- ✅ کنترل ساعات فعالیت

## دستورات مدیریتی (اختیاری)

علاوه بر منوی تعاملی، دستورات زیر نیز قابل استفاده است:

```
/admin - نمایش پنل مدیریت
/addadmin [user_id] - افزودن مدیر
/removeadmin [user_id] - حذف مدیر
/addprofanity [word] - افزودن کلمه فیلتر
/removeprofanity [word] - حذف کلمه فیلتر
/toggleapproval - تغییر وضعیت تایید
/setratelimit [minutes] - تنظیم محدودیت زمانی
/setactivityhours [start] [end] - تنظیم ساعات فعالیت
/settings - نمایش تنظیمات
```

## عیب‌یابی

### مشکلات رایج:

1. **ربات پاسخ نمی‌دهد:**
   - بررسی کنید توکن ربات صحیح باشد
   - اطمینان حاصل کنید ربات در کانال ادمین است

2. **پیام‌ها در کانال منتشر نمی‌شود:**
   - ID کانال را بررسی کنید
   - مجوزهای ربات در کانال را چک کنید

3. **فیلتر کلمات کار نمی‌کند:**
   - لیست کلمات فیلتر را بررسی کنید: `/listprofanity`
   - کلمات جدید اضافه کنید: `/addprofanity`

## مشارکت

برای گزارش باگ یا پیشنهاد ویژگی جدید، issue جدیدی ایجاد کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.