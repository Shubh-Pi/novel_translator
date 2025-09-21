"""
Chapter translation module using ONNX models
"""
import os
import logging
from typing import Optional
from .detect_lang import detect_language
from .emotion import apply_emotion
from .utils import read_text, write_text
from .glossary import Glossary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global glossary instance for maintaining consistency
chapter_glossary = Glossary()

def load_translation_model(source_lang: str, target_lang: str):
    """
    Load the appropriate ONNX translation model based on source and target languages.
    
    Args:
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Loaded ONNX model session or None if model not found
    """
    try:
        import onnxruntime as ort
        
        models_dir = "models"
        
        # Determine which model to use
        if source_lang == "en":
            model_path = os.path.join(models_dir, "translation_en2mul_quantized.onnx")
        else:
            model_path = os.path.join(models_dir, "translation_mul2en_quantized.onnx")
        
        if not os.path.exists(model_path):
            logger.warning(f"ONNX model not found at {model_path}. Using mock translation.")
            return None
            
        session = ort.InferenceSession(model_path)
        logger.info(f"Loaded translation model: {model_path}")
        return session
        
    except ImportError:
        logger.warning("ONNXRuntime not available. Using mock translation.")
        return None
    except Exception as e:
        logger.error(f"Error loading ONNX model: {e}")
        return None

def split_text_into_chunks(text: str, max_chunk_size: int = 512) -> list:
    """
    Split text into manageable chunks for translation while preserving sentence boundaries.
    
    Args:
        text: Input text to split
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    # Simple sentence-based splitting
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def translate_text_chunk(text_chunk: str, model_session, source_lang: str, target_lang: str) -> str:
    """
    Translate a single text chunk using the ONNX model.
    
    Args:
        text_chunk: Text to translate
        model_session: Loaded ONNX model session
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text chunk
    """
    if model_session is None:
        # Mock translation for demonstration
        return f"[{target_lang.upper()}] {text_chunk}"
    
    try:
        # Prepare input for ONNX model
        # Note: This is a simplified example - actual implementation would depend on your specific ONNX model
        inputs = {
            'input_text': [text_chunk],
            'source_lang': [source_lang],
            'target_lang': [target_lang]
        }
        
        # Run inference
        outputs = model_session.run(None, inputs)
        translated_text = outputs[0][0] if outputs and len(outputs[0]) > 0 else text_chunk
        
        return translated_text
        
    except Exception as e:
        logger.error(f"Error during translation: {e}")
        return f"[{target_lang.upper()}] {text_chunk}"  # Fallback

def translate_chapter(file_path: str, target_lang: str) -> str:
    """
    Translate a single chapter file.
    
    Args:
        file_path: Path to the chapter text file
        target_lang: Target language code
        
    Returns:
        Full translated text
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: For other translation errors
    """
    logger.info(f"Starting chapter translation: {file_path} -> {target_lang}")
    
    # Read the chapter text
    try:
        original_text = read_text(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Chapter file not found: {file_path}")
    
    if not original_text.strip():
        logger.warning("Empty chapter file")
        return ""
    
    # Detect source language
    source_lang = detect_language(original_text)
    logger.info(f"Detected source language: {source_lang}")
    
    # Skip translation if source and target are the same
    if source_lang == target_lang:
        logger.info("Source and target languages are the same. Returning original text.")
        return original_text
    
    # Load appropriate translation model
    model_session = load_translation_model(source_lang, target_lang)
    
    # Split text into manageable chunks
    chunks = split_text_into_chunks(original_text)
    logger.info(f"Split text into {len(chunks)} chunks")
    
    # Translate each chunk
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Translating chunk {i+1}/{len(chunks)}")
        
        # Check glossary for known translations
        glossary_translation = chapter_glossary.get_translation(chunk)
        if glossary_translation:
            translated_chunk = glossary_translation
        else:
            translated_chunk = translate_text_chunk(chunk, model_session, source_lang, target_lang)
            # Add to glossary for consistency
            chapter_glossary.add_term(chunk, translated_chunk)
        
        # Apply emotion preservation
        try:
            translated_chunk = apply_emotion(translated_chunk)
        except Exception as e:
            logger.warning(f"Error applying emotion preservation: {e}")
        
        translated_chunks.append(translated_chunk)
    
    # Combine translated chunks
    full_translated_text = " ".join(translated_chunks)
    
    logger.info("Chapter translation completed successfully")
    return full_translated_text

def translate_and_save_chapter(input_path: str, output_path: str, target_lang: str) -> bool:
    """
    Translate a chapter and save to output file.
    
    Args:
        input_path: Path to input chapter file
        output_path: Path to save translated chapter
        target_lang: Target language code
        
    Returns:
        True if successful, False otherwise
    """
    try:
        translated_text = translate_chapter(input_path, target_lang)
        write_text(output_path, translated_text)
        logger.info(f"Saved translated chapter: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error translating and saving chapter: {e}")
        return False