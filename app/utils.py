"""
Utility functions for file handling, ZIP operations, and text processing
"""
import os
import shutil
import zipfile
import tempfile
import logging
from typing import Tuple, List, Dict, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_zip(zip_path: str, extract_to: str) -> None:
    """
    Extract ZIP file to specified directory.
    
    Args:
        zip_path: Path to ZIP file
        extract_to: Directory to extract to
        
    Raises:
        FileNotFoundError: If ZIP file doesn't exist
        zipfile.BadZipFile: If ZIP file is corrupted
        Exception: For other extraction errors
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")
    
    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check for potential security issues
            for member in zip_ref.infolist():
                # Prevent directory traversal attacks
                if os.path.isabs(member.filename) or ".." in member.filename:
                    logger.warning(f"Skipping potentially unsafe file: {member.filename}")
                    continue
                    
                # Extract the file
                zip_ref.extract(member, extract_to)
        
        logger.info(f"Successfully extracted ZIP file to: {extract_to}")
        
    except zipfile.BadZipFile:
        raise zipfile.BadZipFile(f"Invalid or corrupted ZIP file: {zip_path}")
    except Exception as e:
        raise Exception(f"Error extracting ZIP file: {str(e)}")

def create_zip(folder_path: str, output_path: str) -> None:
    """
    Create ZIP file from folder contents.
    
    Args:
        folder_path: Directory to compress
        output_path: Path for output ZIP file
        
    Raises:
        FileNotFoundError: If folder doesn't exist
        Exception: For other compression errors
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    try:
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path for ZIP archive
                    arc_name = os.path.relpath(file_path, folder_path)
                    zip_ref.write(file_path, arc_name)
        
        logger.info(f"Successfully created ZIP file: {output_path}")
        
    except Exception as e:
        raise Exception(f"Error creating ZIP file: {str(e)}")

def read_text(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read text file with proper encoding handling.
    
    Args:
        file_path: Path to text file
        encoding: File encoding (default: utf-8)
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For other reading errors
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Try multiple encodings if UTF-8 fails
    encodings = [encoding, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as file:
                content = file.read()
                logger.debug(f"Successfully read file {file_path} with encoding {enc}")
                return content
        except UnicodeDecodeError:
            if enc == encodings[-1]:  # Last encoding attempt
                logger.error(f"Failed to read file {file_path} with all encodings")
                raise Exception(f"Unable to decode file with any supported encoding: {file_path}")
            continue
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")

def write_text(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    Write text to file with proper encoding.
    
    Args:
        file_path: Path to output file
        content: Text content to write
        encoding: File encoding (default: utf-8)
        
    Raises:
        Exception: For writing errors
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(content)
        
        logger.debug(f"Successfully wrote file: {file_path}")
        
    except Exception as e:
        raise Exception(f"Error writing file {file_path}: {str(e)}")

def get_file_info(file_path: str) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {"exists": False}
    
    try:
        stat_info = os.stat(file_path)
        
        return {
            "exists": True,
            "size": stat_info.st_size,
            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
            "modified": stat_info.st_mtime,
            "is_file": os.path.isfile(file_path),
            "is_dir": os.path.isdir(file_path),
            "extension": os.path.splitext(file_path)[1].lower(),
            "basename": os.path.basename(file_path)
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {"exists": True, "error": str(e)}

def clean_filename(filename: str) -> str:
    """
    Clean filename to remove invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for filesystem
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    cleaned = filename
    
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip(' .')
    
    # Ensure filename isn't empty
    if not cleaned:
        cleaned = "unnamed_file"
    
    return cleaned

def ensure_directory(directory: str) -> None:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path to create
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        raise

def copy_file(source: str, destination: str) -> bool:
    """
    Copy file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        ensure_directory(os.path.dirname(destination))
        
        shutil.copy2(source, destination)
        logger.debug(f"Copied file: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying file {source} to {destination}: {e}")
        return False

def move_file(source: str, destination: str) -> bool:
    """
    Move file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        ensure_directory(os.path.dirname(destination))
        
        shutil.move(source, destination)
        logger.debug(f"Moved file: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error moving file {source} to {destination}: {e}")
        return False

def delete_file(file_path: str) -> bool:
    """
    Delete file if it exists.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
            return True
        else:
            logger.debug(f"File doesn't exist, nothing to delete: {file_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

def get_text_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get all text files in directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of text file paths
    """
    text_extensions = {'.txt', '.text', '.md', '.markdown', '.rst'}
    text_files = []
    
    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if Path(file).suffix.lower() in text_extensions:
                        text_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and Path(file).suffix.lower() in text_extensions:
                    text_files.append(file_path)
        
        # Sort files for consistent ordering
        text_files.sort()
        logger.debug(f"Found {len(text_files)} text files in {directory}")
        
    except Exception as e:
        logger.error(f"Error getting text files from {directory}: {e}")
    
    return text_files

def create_temp_directory() -> str:
    """
    Create a temporary directory.
    
    Returns:
        Path to temporary directory
    """
    try:
        temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Error creating temporary directory: {e}")
        raise

def cleanup_temp_directory(temp_dir: str) -> bool:
    """
    Clean up temporary directory.
    
    Args:
        temp_dir: Path to temporary directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up temporary directory {temp_dir}: {e}")
        return False

def validate_file_path(file_path: str, must_exist: bool = True) -> Tuple[bool, str]:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path is empty"
    
    if must_exist and not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"
    
    # Check for directory traversal
    if ".." in file_path or file_path.startswith("/"):
        return False, "Invalid file path (security concern)"
    
    return True, ""

def get_directory_size(directory: str) -> int:
    """
    Get total size of directory in bytes.
    
    Args:
        directory: Directory path
        
    Returns:
        Size in bytes
    """
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"Error calculating directory size for {directory}: {e}")
    
    return total_size