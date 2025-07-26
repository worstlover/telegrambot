"""
Profanity filtering functionality
"""

import re
import logging
from typing import List
from bot.database import get_profanity_words

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """Normalize text for filtering (remove extra chars, normalize spacing)"""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Common character substitutions used to bypass filters
    substitutions = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't',
        '@': 'a', '$': 's', '!': 'i', '+': 't', '×': 'x',
        # Persian number substitutions
        '۰': 'o', '۱': 'i', '۳': 'e', '۴': 'a', '۵': 's', '۷': 't'
    }
    
    normalized = text.lower()
    for old, new in substitutions.items():
        normalized = normalized.replace(old, new)
    
    return normalized

def contains_profanity(text: str) -> bool:
    """Check if text contains profanity"""
    if not text:
        return False
    
    try:
        # Get profanity words from database
        profanity_words = get_profanity_words()
        
        if not profanity_words:
            return False
        
        # Normalize the input text
        normalized_text = normalize_text(text)
        
        # Check for each profanity word
        for word in profanity_words:
            normalized_word = normalize_text(word)
            
            # Check for exact word match (with word boundaries)
            if re.search(r'\b' + re.escape(normalized_word) + r'\b', normalized_text):
                logger.info(f"Profanity detected: {word}")
                return True
            
            # Check for word with common separators or without spaces
            pattern = re.escape(normalized_word).replace(r'\ ', r'[\s\-_\.]*')
            if re.search(pattern, normalized_text):
                logger.info(f"Profanity detected (with separators): {word}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking profanity: {e}")
        # In case of error, be conservative and don't filter
        return False

def get_clean_text(text: str) -> str:
    """Get cleaned version of text (for future enhancement)"""
    # For now, just return original text
    # This could be enhanced to auto-censor words instead of blocking
    return text
