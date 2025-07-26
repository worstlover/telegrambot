"""
Utility functions for the bot
"""

import logging
from datetime import datetime
from bot.database import get_setting

logger = logging.getLogger(__name__)

def get_rate_limit_minutes() -> int:
    """Get current rate limit in minutes"""
    try:
        rate_limit = get_setting('rate_limit_minutes')
        return int(rate_limit) if rate_limit else 5
    except Exception as e:
        logger.error(f"Error getting rate limit: {e}")
        return 5

def get_activity_hours() -> tuple:
    """Get activity start and end hours"""
    try:
        start_hour = get_setting('activity_start_hour')
        end_hour = get_setting('activity_end_hour')
        start = int(start_hour) if start_hour else 0
        end = int(end_hour) if end_hour else 23
        return start, end
    except Exception as e:
        logger.error(f"Error getting activity hours: {e}")
        return 0, 23

def requires_approval() -> bool:
    """Check if media requires approval"""
    try:
        require_approval = get_setting('require_approval')
        return require_approval == 'true' if require_approval else True
    except Exception as e:
        logger.error(f"Error checking approval requirement: {e}")
        return True

def format_time_remaining(minutes: int) -> str:
    """Format remaining time in a user-friendly way"""
    if minutes < 1:
        return "کمتر از یک دقیقه"
    elif minutes == 1:
        return "یک دقیقه"
    elif minutes < 60:
        return f"{minutes} دقیقه"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} ساعت"
        else:
            return f"{hours} ساعت و {remaining_minutes} دقیقه"

def is_valid_display_name(name: str) -> bool:
    """Validate display name"""
    if not name or len(name.strip()) == 0:
        return False
    
    # Check length (between 1 and 50 characters)
    if len(name.strip()) > 50:
        return False
    
    # Check for invalid characters (basic validation)
    # Allow Persian, English, numbers, and some symbols
    import re
    if not re.match(r'^[\u0600-\u06FF\u200C\u200Da-zA-Z0-9\s\-_\.]+$', name.strip()):
        return False
    
    return True

def sanitize_text(text: str) -> str:
    """Sanitize text for safe display"""
    if not text:
        return ""
    
    # Remove or escape potentially dangerous characters
    # This is a basic implementation
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    return sanitized.strip()

def get_file_type_name(file_type: str) -> str:
    """Get user-friendly file type name"""
    type_names = {
        'photo': 'عکس',
        'video': 'ویدیو',
        'audio': 'صوت',
        'voice': 'پیام صوتی',
        'document': 'فایل',
        'animation': 'انیمیشن'
    }
    return type_names.get(file_type, 'فایل')
