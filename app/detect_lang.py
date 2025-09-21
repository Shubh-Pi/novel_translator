"""
Language detection module
"""
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """
    Detect the language of given text.
    
    Args:
        text: Text to analyze for language detection
        
    Returns:
        Language code (e.g., 'en', 'es', 'fr', etc.)
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for language detection")
        return 'en'  # Default to English
    
    # Clean text for better detection
    clean_text = text.strip()[:1000]  # Use first 1000 characters for detection
    
    try:
        from langdetect import detect, LangDetectException
        
        detected_lang = detect(clean_text)
        logger.info(f"Detected language: {detected_lang}")
        
        # Map some common language codes
        language_mapping = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
        }
        
        detected_lang = language_mapping.get(detected_lang, detected_lang)
        
        return detected_lang
        
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return fallback_language_detection(clean_text)
    
    except ImportError:
        logger.warning("langdetect library not available, using fallback detection")
        return fallback_language_detection(clean_text)
    
    except Exception as e:
        logger.error(f"Unexpected error during language detection: {e}")
        return fallback_language_detection(clean_text)

def fallback_language_detection(text: str) -> str:
    """
    Fallback language detection using simple heuristics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code based on simple pattern matching
    """
    if not text:
        return 'en'
    
    text_lower = text.lower()
    
    # Simple pattern-based detection
    patterns = {
        'es': ['el ', 'la ', 'de ', 'que ', 'y ', 'a ', 'en ', 'un ', 'es ', 'se ', 'no ', 'te ', 'lo ', 'le ', 'da ', 'su ', 'por ', 'son ', 'con ', 'para ', 'una ', 'son ', 'del ', 'al ', 'qué ', 'más'],
        'fr': ['le ', 'de ', 'et ', 'à ', 'un ', 'il ', 'être ', 'et ', 'en ', 'avoir ', 'que ', 'pour ', 'dans ', 'ce ', 'son ', 'une ', 'sur ', 'avec ', 'ne ', 'se ', 'pas ', 'tout ', 'plus ', 'par ', 'grand', 'où', 'ou', 'qui'],
        'de': ['der ', 'die ', 'und ', 'in ', 'den ', 'von ', 'zu ', 'das ', 'mit ', 'sich ', 'des ', 'auf ', 'für ', 'ist ', 'im ', 'dem ', 'nicht ', 'ein ', 'eine ', 'als ', 'auch ', 'es ', 'an ', 'werden', 'aus', 'er', 'hat', 'dass'],
        'it': ['il ', 'di ', 'che ', 'e ', 'la ', 'per ', 'un ', 'in ', 'con ', 'del ', 'da ', 'a ', 'al ', 'sono ', 'le ', 'si ', 'gli ', 'una', 'dei', 'nel', 'alla', 'come', 'più', 'anche', 'tutto', 'già'],
        'pt': ['de ', 'a ', 'o ', 'que ', 'e ', 'do ', 'da ', 'em ', 'um ', 'para ', 'é ', 'com ', 'não ', 'uma ', 'os ', 'no ', 'se ', 'na ', 'por ', 'mais', 'das', 'dos', 'como', 'mas', 'foi', 'ao', 'ele'],
        'ja': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や', 'れる', 'など', 'なっ', 'また', 'その', 'これ'],
        'ko': ['이', '의', '가', '을', '는', '에', '과', '로', '으로', '에서', '와', '한', '하', '되', '있', '들', '것', '수', '등', '같', '후', '전', '다시', '또', '통해', '위해', '대한', '따른'],
        'zh': ['的', '一', '是', '在', '不', '了', '有', '和', '人', '这', '中', '大', '为', '上', '个', '国', '我', '以', '要', '他', '时', '来', '用', '们', '生', '到', '作', '地', '于', '出', '就'],
        'ru': ['и ', 'в ', 'не ', 'на ', 'я ', 'быть ', 'он ', 'с ', 'что ', 'а ', 'по ', 'это ', 'она ', 'этот ', 'к ', 'но ', 'они ', 'мы ', 'как ', 'из ', 'у ', 'который ', 'то ', 'за ', 'свой ', 'что ', 'же']
    }
    
    scores = {}
    
    for lang, words in patterns.items():
        score = 0
        for word in words:
            score += text_lower.count(word)
        scores[lang] = score
    
    if scores:
        detected_lang = max(scores, key=scores.get)
        if scores[detected_lang] > 0:
            logger.info(f"Fallback detection result: {detected_lang} (score: {scores[detected_lang]})")
            return detected_lang
    
    # Character-based detection for non-Latin scripts
    if any(ord(char) >= 0x4E00 and ord(char) <= 0x9FFF for char in text):  # Chinese characters
        logger.info("Detected Chinese characters")
        return 'zh'
    
    if any(ord(char) >= 0x3040 and ord(char) <= 0x309F for char in text):  # Hiragana
        logger.info("Detected Japanese (Hiragana)")
        return 'ja'
    
    if any(ord(char) >= 0x30A0 and ord(char) <= 0x30FF for char in text):  # Katakana
        logger.info("Detected Japanese (Katakana)")
        return 'ja'
    
    if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7AF for char in text):  # Korean
        logger.info("Detected Korean characters")
        return 'ko'
    
    if any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in text):  # Cyrillic
        logger.info("Detected Cyrillic characters")
        return 'ru'
    
    # Default to English if no patterns match
    logger.info("No language patterns matched, defaulting to English")
    return 'en'

def get_language_name(lang_code: str) -> str:
    """
    Get the full language name from language code.
    
    Args:
        lang_code: Language code (e.g., 'en', 'es')
        
    Returns:
        Full language name
    """
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'pl': 'Polish',
        'tr': 'Turkish',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        'he': 'Hebrew',
        'fa': 'Persian',
        'ur': 'Urdu',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'si': 'Sinhala',
        'my': 'Myanmar',
        'km': 'Khmer',
        'lo': 'Lao',
        'ka': 'Georgian',
        'am': 'Amharic',
        'sw': 'Swahili',
        'zu': 'Zulu',
        'af': 'Afrikaans',
        'sq': 'Albanian',
        'az': 'Azerbaijani',
        'be': 'Belarusian',
        'bg': 'Bulgarian',
        'ca': 'Catalan',
        'hr': 'Croatian',
        'cs': 'Czech',
        'et': 'Estonian',
        'eu': 'Basque',
        'gl': 'Galician',
        'hu': 'Hungarian',
        'is': 'Icelandic',
        'ga': 'Irish',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'mk': 'Macedonian',
        'mt': 'Maltese',
        'ro': 'Romanian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'uk': 'Ukrainian',
        'cy': 'Welsh'
    }
    
    return language_names.get(lang_code, f'Unknown ({lang_code})')

def is_supported_language(lang_code: str) -> bool:
    """
    Check if a language is supported for translation.
    
    Args:
        lang_code: Language code to check
        
    Returns:
        True if language is supported, False otherwise
    """
    supported_languages = {
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh', 'ru'
    }
    
    return lang_code in supported_languages

def get_supported_languages() -> dict:
    """
    Get all supported languages.
    
    Returns:
        Dictionary mapping language codes to names
    """
    supported_codes = {'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh', 'ru'}
    
    return {code: get_language_name(code) for code in supported_codes}