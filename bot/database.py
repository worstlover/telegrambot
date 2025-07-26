"""
Database operations for the bot
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from bot.config import DATABASE_PATH, DEFAULT_PROFANITY_WORDS, DEFAULT_RATE_LIMIT_MINUTES

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    try:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                display_name TEXT UNIQUE,
                display_name_set BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP
            )
        ''')
        
        # Admins table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Profanity words table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profanity_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pending media table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pending_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                file_type TEXT NOT NULL,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Message logs table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize default settings
        default_settings = [
            ('require_approval', 'true'),
            ('rate_limit_minutes', str(DEFAULT_RATE_LIMIT_MINUTES)),
            ('activity_start_hour', '0'),
            ('activity_end_hour', '23')
        ]
        
        for key, value in default_settings:
            conn.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
        
        # Initialize default profanity words
        for word in DEFAULT_PROFANITY_WORDS:
            conn.execute('''
                INSERT OR IGNORE INTO profanity_words (word) VALUES (?)
            ''', (word,))
        
        # Add a default admin if none exists (using a placeholder ID)
        # In production, the first admin should be added manually
        admin_count = conn.execute('SELECT COUNT(*) as count FROM admins').fetchone()
        if admin_count and admin_count['count'] == 0:
            # Add a placeholder admin that needs to be replaced
            conn.execute('''
                INSERT INTO admins (telegram_id, added_by) VALUES (?, ?)
            ''', (123456789, 0))  # This should be replaced with real admin ID
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_or_create_user(telegram_id: int) -> dict:
    """Get existing user or create new one"""
    conn = get_db_connection()
    try:
        # Try to get existing user
        user = conn.execute('''
            SELECT * FROM users WHERE telegram_id = ?
        ''', (telegram_id,)).fetchone()
        
        if user:
            return dict(user)
        
        # Create new user with auto-generated display name
        cursor = conn.execute('''
            SELECT COUNT(*) as count FROM users
        ''')
        result = cursor.fetchone()
        user_count = result['count'] if result else 0
        display_name = f"کاربر{user_count + 1}"
        
        # Ensure uniqueness
        while True:
            existing = conn.execute('''
                SELECT id FROM users WHERE display_name = ?
            ''', (display_name,)).fetchone()
            
            if not existing:
                break
            user_count += 1
            display_name = f"کاربر{user_count + 1}"
        
        conn.execute('''
            INSERT INTO users (telegram_id, display_name) VALUES (?, ?)
        ''', (telegram_id, display_name))
        conn.commit()
        
        # Return the new user
        user = conn.execute('''
            SELECT * FROM users WHERE telegram_id = ?
        ''', (telegram_id,)).fetchone()
        
        if user:
            return dict(user)
        else:
            return {}
        
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        conn.rollback()
        return {}
    finally:
        conn.close()

def set_user_display_name(telegram_id: int, display_name: str) -> bool:
    """Set user display name (only once)"""
    conn = get_db_connection()
    try:
        # Check if user already set name
        user = conn.execute('''
            SELECT display_name_set FROM users WHERE telegram_id = ?
        ''', (telegram_id,)).fetchone()
        
        if not user:
            return False
        
        if user['display_name_set']:
            return False
        
        # Check if name is already taken
        existing = conn.execute('''
            SELECT id FROM users WHERE display_name = ? AND telegram_id != ?
        ''', (display_name, telegram_id)).fetchone()
        
        if existing:
            return False
        
        # Update name and mark as set
        conn.execute('''
            UPDATE users SET display_name = ?, display_name_set = TRUE 
            WHERE telegram_id = ?
        ''', (display_name, telegram_id))
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error setting display name: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_last_message_time(telegram_id: int):
    """Update user's last message time"""
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE users SET last_message_at = CURRENT_TIMESTAMP 
            WHERE telegram_id = ?
        ''', (telegram_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating last message time: {e}")
        conn.rollback()
    finally:
        conn.close()

def can_user_send_message(telegram_id: int) -> bool:
    """Check if user can send message based on rate limiting"""
    conn = get_db_connection()
    try:
        # Get rate limit setting
        rate_limit = conn.execute('''
            SELECT value FROM settings WHERE key = 'rate_limit_minutes'
        ''').fetchone()
        
        if not rate_limit:
            return True
        
        rate_limit_minutes = int(rate_limit['value'])
        
        # Get user's last message time
        user = conn.execute('''
            SELECT last_message_at FROM users WHERE telegram_id = ?
        ''', (telegram_id,)).fetchone()
        
        if not user or not user['last_message_at']:
            return True
        
        last_message = datetime.fromisoformat(user['last_message_at'])
        time_diff = datetime.now() - last_message
        
        return time_diff.total_seconds() >= (rate_limit_minutes * 60)
        
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return True
    finally:
        conn.close()

def is_channel_active() -> bool:
    """Check if channel is currently active based on activity hours"""
    conn = get_db_connection()
    try:
        start_hour = conn.execute('''
            SELECT value FROM settings WHERE key = 'activity_start_hour'
        ''').fetchone()
        
        end_hour = conn.execute('''
            SELECT value FROM settings WHERE key = 'activity_end_hour'
        ''').fetchone()
        
        if not start_hour or not end_hour:
            return True
        
        current_hour = datetime.now().hour
        start = int(start_hour['value'])
        end = int(end_hour['value'])
        
        if start <= end:
            return start <= current_hour <= end
        else:  # Overnight period
            return current_hour >= start or current_hour <= end
            
    except Exception as e:
        logger.error(f"Error checking channel activity: {e}")
        return True
    finally:
        conn.close()

def is_admin(telegram_id: int) -> bool:
    """Check if user is admin"""
    conn = get_db_connection()
    try:
        admin = conn.execute('''
            SELECT id FROM admins WHERE telegram_id = ?
        ''', (telegram_id,)).fetchone()
        return admin is not None
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False
    finally:
        conn.close()

def add_admin(telegram_id: int, added_by: int) -> bool:
    """Add new admin"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT OR IGNORE INTO admins (telegram_id, added_by) VALUES (?, ?)
        ''', (telegram_id, added_by))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def remove_admin(telegram_id: int) -> bool:
    """Remove admin"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            DELETE FROM admins WHERE telegram_id = ?
        ''', (telegram_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_profanity_words() -> List[str]:
    """Get all profanity words"""
    conn = get_db_connection()
    try:
        words = conn.execute('''
            SELECT word FROM profanity_words ORDER BY word
        ''').fetchall()
        return [word['word'] for word in words]
    except Exception as e:
        logger.error(f"Error getting profanity words: {e}")
        return []
    finally:
        conn.close()

def add_profanity_word(word: str, added_by: int) -> bool:
    """Add profanity word"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT OR IGNORE INTO profanity_words (word, added_by) VALUES (?, ?)
        ''', (word.lower(), added_by))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding profanity word: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def remove_profanity_word(word: str) -> bool:
    """Remove profanity word"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            DELETE FROM profanity_words WHERE word = ?
        ''', (word.lower(),))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing profanity word: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_setting(key: str) -> str:
    """Get setting value"""
    conn = get_db_connection()
    try:
        setting = conn.execute('''
            SELECT value FROM settings WHERE key = ?
        ''', (key,)).fetchone()
        return setting['value'] if setting else ""
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        return ""
    finally:
        conn.close()

def set_setting(key: str, value: str) -> bool:
    """Set setting value"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error setting value: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_pending_media(user_telegram_id: int, message_id: int, file_id: str, 
                     file_type: str, caption: str = None) -> int:
    """Add pending media for approval"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            INSERT INTO pending_media (user_telegram_id, message_id, file_id, file_type, caption)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_telegram_id, message_id, file_id, file_type, caption))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error adding pending media: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_pending_media(media_id: int) -> dict:
    """Get pending media by ID"""
    conn = get_db_connection()
    try:
        media = conn.execute('''
            SELECT * FROM pending_media WHERE id = ?
        ''', (media_id,)).fetchone()
        return dict(media) if media else None
    except Exception as e:
        logger.error(f"Error getting pending media: {e}")
        return None
    finally:
        conn.close()

def remove_pending_media(media_id: int) -> bool:
    """Remove pending media"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            DELETE FROM pending_media WHERE id = ?
        ''', (media_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing pending media: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def log_message(user_telegram_id: int, message_type: str, status: str, reason: str = None):
    """Log message activity"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO message_logs (user_telegram_id, message_type, status, reason)
            VALUES (?, ?, ?, ?)
        ''', (user_telegram_id, message_type, status, reason))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging message: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_all_admins() -> List[int]:
    """Get all admin telegram IDs"""
    conn = get_db_connection()
    try:
        admins = conn.execute('''
            SELECT telegram_id FROM admins ORDER BY created_at
        ''').fetchall()
        return [admin['telegram_id'] for admin in admins]
    except Exception as e:
        logger.error(f"Error getting admins: {e}")
        return []
    finally:
        conn.close()
