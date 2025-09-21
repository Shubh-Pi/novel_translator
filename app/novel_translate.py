"""
Novel translation module for batch processing ZIP files
"""
import os
import tempfile
import shutil
import logging
from pathlib import Path
from typing import List, Tuple
from .chapter_translate import translate_and_save_chapter
from .utils import extract_zip, create_zip, read_text
from .glossary import Glossary
from .detect_lang import detect_language

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global glossary for maintaining consistency across novel chapters
novel_glossary = Glossary()

def get_chapter_files(directory: str) -> List[Tuple[str, str]]:
    """
    Get all text files from directory, sorted by filename.
    
    Args:
        directory: Directory containing chapter files
        
    Returns:
        List of tuples (filename, full_path) sorted by filename
    """
    chapter_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.txt', '.text')):
                full_path = os.path.join(root, file)
                chapter_files.append((file, full_path))
    
    # Sort by filename to maintain chapter order
    chapter_files.sort(key=lambda x: x[0])
    
    logger.info(f"Found {len(chapter_files)} chapter files")
    return chapter_files

def analyze_novel_languages(chapter_files: List[Tuple[str, str]]) -> str:
    """
    Analyze the languages present in the novel by sampling chapters.
    
    Args:
        chapter_files: List of (filename, path) tuples
        
    Returns:
        Most common source language detected
    """
    language_counts = {}
    sample_size = min(3, len(chapter_files))  # Sample first 3 chapters
    
    for i in range(sample_size):
        filename, file_path = chapter_files[i]
        try:
            text_sample = read_text(file_path)[:1000]  # First 1000 chars
            detected_lang = detect_language(text_sample)
            language_counts[detected_lang] = language_counts.get(detected_lang, 0) + 1
        except Exception as e:
            logger.warning(f"Error analyzing language for {filename}: {e}")
    
    # Return most common language
    if language_counts:
        most_common_lang = max(language_counts, key=language_counts.get)
        logger.info(f"Detected novel language: {most_common_lang}")
        return most_common_lang
    else:
        logger.warning("Could not detect novel language, defaulting to 'en'")
        return 'en'

def build_novel_glossary(chapter_files: List[Tuple[str, str]], source_lang: str) -> None:
    """
    Build a glossary of common terms across the novel for consistency.
    
    Args:
        chapter_files: List of chapter files to analyze
        source_lang: Source language of the novel
    """
    logger.info("Building novel glossary for consistency...")
    
    # For demonstration, we'll identify common proper nouns and terms
    common_terms = {}
    
    # Sample every few chapters to build glossary
    sample_indices = range(0, len(chapter_files), max(1, len(chapter_files) // 5))
    
    for i in sample_indices:
        filename, file_path = chapter_files[i]
        try:
            text = read_text(file_path)
            
            # Simple extraction of capitalized words (likely proper nouns)
            words = text.split()
            for word in words:
                if word.istitle() and len(word) > 2 and word.isalpha():
                    common_terms[word] = common_terms.get(word, 0) + 1
                    
        except Exception as e:
            logger.warning(f"Error processing {filename} for glossary: {e}")
    
    # Add most common terms to glossary (they'll be translated consistently)
    threshold = 2  # Appear at least twice
    for term, count in common_terms.items():
        if count >= threshold:
            # Initially, we don't have translations, they'll be added during translation
            novel_glossary.add_term(term, "")  # Placeholder
    
    logger.info(f"Built glossary with {len(common_terms)} potential terms")

def translate_novel(zip_path: str, target_lang: str) -> str:
    """
    Translate an entire novel from a ZIP file.
    
    Args:
        zip_path: Path to ZIP file containing novel chapters
        target_lang: Target language code
        
    Returns:
        Path to the translated novel ZIP file
        
    Raises:
        Exception: If translation fails
    """
    logger.info(f"Starting novel translation: {zip_path} -> {target_lang}")
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, "extracted")
        output_dir = os.path.join(temp_dir, "translated")
        
        os.makedirs(extract_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract the ZIP file
            extract_zip(zip_path, extract_dir)
            logger.info(f"Extracted novel to: {extract_dir}")
            
            # Get all chapter files
            chapter_files = get_chapter_files(extract_dir)
            
            if not chapter_files:
                raise Exception("No text files found in the ZIP archive")
            
            # Analyze novel languages
            source_lang = analyze_novel_languages(chapter_files)
            
            # Skip translation if source and target are the same
            if source_lang == target_lang:
                logger.info("Source and target languages are the same. Creating copy.")
                shutil.copytree(extract_dir, output_dir, dirs_exist_ok=True)
            else:
                # Build glossary for consistency
                build_novel_glossary(chapter_files, source_lang)
                
                # Translate each chapter
                failed_chapters = []
                for i, (filename, file_path) in enumerate(chapter_files):
                    logger.info(f"Translating chapter {i+1}/{len(chapter_files)}: {filename}")
                    
                    # Determine output path (preserve directory structure)
                    relative_path = os.path.relpath(file_path, extract_dir)
                    output_path = os.path.join(output_dir, relative_path)
                    
                    # Create output directory if needed
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Translate the chapter
                    success = translate_and_save_chapter(file_path, output_path, target_lang)
                    
                    if not success:
                        failed_chapters.append(filename)
                        # Copy original file as fallback
                        shutil.copy2(file_path, output_path)
                        logger.warning(f"Translation failed for {filename}, using original")
                
                if failed_chapters:
                    logger.warning(f"Failed to translate {len(failed_chapters)} chapters: {failed_chapters}")
            
            # Create output ZIP file
            output_zip_path = os.path.join(temp_dir, "translated_novel.zip")
            create_zip(output_dir, output_zip_path)
            
            # Move to permanent location
            permanent_zip_path = os.path.join(tempfile.gettempdir(), "translated_novel.zip")
            shutil.move(output_zip_path, permanent_zip_path)
            
            logger.info(f"Novel translation completed: {permanent_zip_path}")
            return permanent_zip_path
            
        except Exception as e:
            logger.error(f"Error during novel translation: {e}")
            raise Exception(f"Novel translation failed: {str(e)}")

def get_translation_progress(current_chapter: int, total_chapters: int) -> dict:
    """
    Get current translation progress information.
    
    Args:
        current_chapter: Current chapter being processed
        total_chapters: Total number of chapters
        
    Returns:
        Dictionary with progress information
    """
    progress_percent = (current_chapter / total_chapters) * 100 if total_chapters > 0 else 0
    
    return {
        "current_chapter": current_chapter,
        "total_chapters": total_chapters,
        "progress_percent": round(progress_percent, 2),
        "status": f"Processing chapter {current_chapter} of {total_chapters}"
    }

def validate_novel_structure(zip_path: str) -> Tuple[bool, str]:
    """
    Validate that the ZIP file contains a proper novel structure.
    
    Args:
        zip_path: Path to ZIP file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = os.path.join(temp_dir, "validate")
            extract_zip(zip_path, extract_dir)
            
            chapter_files = get_chapter_files(extract_dir)
            
            if not chapter_files:
                return False, "No text files found in ZIP archive"
            
            # Check if files are too small (likely empty)
            empty_files = []
            for filename, file_path in chapter_files:
                try:
                    text = read_text(file_path)
                    if len(text.strip()) < 10:  # Very small files
                        empty_files.append(filename)
                except:
                    empty_files.append(filename)
            
            if len(empty_files) == len(chapter_files):
                return False, "All files appear to be empty or unreadable"
            
            if empty_files:
                logger.warning(f"Found {len(empty_files)} empty/small files: {empty_files}")
            
            return True, f"Valid novel structure with {len(chapter_files)} chapters"
            
    except Exception as e:
        return False, f"Error validating ZIP structure: {str(e)}"