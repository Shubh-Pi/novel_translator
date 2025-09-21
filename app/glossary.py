"""
Glossary management for maintaining translation consistency across chapters
"""
import logging
from typing import Dict, Optional, List
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Glossary:
    """
    Maintains a glossary of translations to ensure consistency across chapters.
    """
    
    def __init__(self):
        """Initialize empty glossary."""
        self._terms: Dict[str, str] = {}
        self._usage_count: Dict[str, int] = {}
        self._context: Dict[str, List[str]] = {}  # Store context for each term
    
    def add_term(self, original: str, translated: str, context: Optional[str] = None) -> None:
        """
        Add a term and its translation to the glossary.
        
        Args:
            original: Original term
            translated: Translated term
            context: Optional context where the term appears
        """
        if not original or not original.strip():
            return
        
        original = original.strip()
        translated = translated.strip() if translated else ""
        
        # Update or add the term
        if original in self._terms and translated and self._terms[original] != translated:
            logger.info(f"Updating translation for '{original}': '{self._terms[original]}' -> '{translated}'")
        
        self._terms[original] = translated
        
        # Update usage count
        self._usage_count[original] = self._usage_count.get(original, 0) + 1
        
        # Add context if provided
        if context:
            if original not in self._context:
                self._context[original] = []
            if context not in self._context[original]:
                self._context[original].append(context)
                # Limit context history
                if len(self._context[original]) > 5:
                    self._context[original] = self._context[original][-5:]
        
        logger.debug(f"Added term to glossary: '{original}' -> '{translated}'")
    
    def get_translation(self, original: str) -> Optional[str]:
        """
        Get the translation for a term from the glossary.
        
        Args:
            original: Original term to look up
            
        Returns:
            Translated term if found, None otherwise
        """
        if not original or not original.strip():
            return None
        
        original = original.strip()
        translation = self._terms.get(original)
        
        if translation and translation.strip():
            logger.debug(f"Found glossary translation: '{original}' -> '{translation}'")
            return translation
        
        return None
    
    def has_term(self, original: str) -> bool:
        """
        Check if a term exists in the glossary.
        
        Args:
            original: Term to check
            
        Returns:
            True if term exists, False otherwise
        """
        return original.strip() in self._terms if original else False
    
    def remove_term(self, original: str) -> bool:
        """
        Remove a term from the glossary.
        
        Args:
            original: Term to remove
            
        Returns:
            True if term was removed, False if not found
        """
        if not original or not original.strip():
            return False
        
        original = original.strip()
        
        if original in self._terms:
            del self._terms[original]
            self._usage_count.pop(original, None)
            self._context.pop(original, None)
            logger.info(f"Removed term from glossary: '{original}'")
            return True
        
        return False
    
    def get_usage_count(self, original: str) -> int:
        """
        Get usage count for a term.
        
        Args:
            original: Term to check
            
        Returns:
            Number of times the term has been used
        """
        return self._usage_count.get(original.strip() if original else "", 0)
    
    def get_context(self, original: str) -> List[str]:
        """
        Get context examples for a term.
        
        Args:
            original: Term to get context for
            
        Returns:
            List of context strings
        """
        return self._context.get(original.strip() if original else "", [])
    
    def get_all_terms(self) -> Dict[str, str]:
        """
        Get all terms and their translations.
        
        Returns:
            Dictionary of original -> translated terms
        """
        return self._terms.copy()
    
    def get_frequent_terms(self, min_usage: int = 2) -> Dict[str, str]:
        """
        Get frequently used terms.
        
        Args:
            min_usage: Minimum usage count to include
            
        Returns:
            Dictionary of frequently used terms and translations
        """
        frequent_terms = {}
        for original, translated in self._terms.items():
            if self._usage_count.get(original, 0) >= min_usage:
                frequent_terms[original] = translated
        
        return frequent_terms
    
    def merge_glossary(self, other_glossary: 'Glossary', prefer_existing: bool = True) -> None:
        """
        Merge another glossary into this one.
        
        Args:
            other_glossary: Glossary to merge from
            prefer_existing: If True, keep existing translations in case of conflicts
        """
        if not isinstance(other_glossary, Glossary):
            raise TypeError("Can only merge with another Glossary instance")
        
        for original, translated in other_glossary.get_all_terms().items():
            if original in self._terms:
                if not prefer_existing or not self._terms[original]:
                    # Update with new translation
                    self.add_term(original, translated)
                # Always update usage count
                self._usage_count[original] = (self._usage_count.get(original, 0) + 
                                             other_glossary.get_usage_count(original))
            else:
                # Add new term
                self.add_term(original, translated)
                self._usage_count[original] = other_glossary.get_usage_count(original)
        
        logger.info(f"Merged glossary with {len(other_glossary.get_all_terms())} terms")
    
    def clear(self) -> None:
        """Clear all terms from the glossary."""
        term_count = len(self._terms)
        self._terms.clear()
        self._usage_count.clear()
        self._context.clear()
        logger.info(f"Cleared glossary ({term_count} terms removed)")
    
    def size(self) -> int:
        """Get number of terms in glossary."""
        return len(self._terms)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save glossary to a JSON file.
        
        Args:
            file_path: Path to save the glossary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            glossary_data = {
                'terms': self._terms,
                'usage_count': self._usage_count,
                'context': self._context
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(glossary_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved glossary to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving glossary to {file_path}: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load glossary from a JSON file.
        
        Args:
            file_path: Path to load the glossary from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Glossary file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                glossary_data = json.load(f)
            
            self._terms = glossary_data.get('terms', {})
            self._usage_count = glossary_data.get('usage_count', {})
            self._context = glossary_data.get('context', {})
            
            logger.info(f"Loaded glossary from {file_path} ({len(self._terms)} terms)")
            return True
        
        except Exception as e:
            logger.error(f"Error loading glossary from {file_path}: {e}")
            return False
    
    def find_similar_terms(self, term: str, max_results: int = 5) -> List[str]:
        """
        Find terms similar to the given term.
        
        Args:
            term: Term to find similarities for
            max_results: Maximum number of similar terms to return
            
        Returns:
            List of similar terms
        """
        if not term or not term.strip():
            return []
        
        term = term.strip().lower()
        similar_terms = []
        
        for original in self._terms.keys():
            original_lower = original.lower()
            
            # Exact match (case-insensitive)
            if original_lower == term:
                continue
            
            # Contains match
            if term in original_lower or original_lower in term:
                similar_terms.append(original)
            
            # Simple edit distance approximation
            elif len(set(term) & set(original_lower)) >= min(len(term), len(original_lower)) * 0.7:
                similar_terms.append(original)
        
        # Sort by usage count (more frequent terms first)
        similar_terms.sort(key=lambda x: self._usage_count.get(x, 0), reverse=True)
        
        return similar_terms[:max_results]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the glossary.
        
        Returns:
            Dictionary with glossary statistics
        """
        if not self._terms:
            return {
                'total_terms': 0,
                'avg_usage': 0,
                'most_used_term': None,
                'terms_with_context': 0
            }
        
        total_terms = len(self._terms)
        total_usage = sum(self._usage_count.values())
        avg_usage = total_usage / total_terms if total_terms > 0 else 0
        
        most_used_term = max(self._usage_count.keys(), key=lambda k: self._usage_count[k]) if self._usage_count else None
        terms_with_context = len([t for t in self._context.keys() if self._context[t]])
        
        return {
            'total_terms': total_terms,
            'total_usage': total_usage,
            'avg_usage': round(avg_usage, 2),
            'most_used_term': most_used_term,
            'most_used_count': self._usage_count.get(most_used_term, 0) if most_used_term else 0,
            'terms_with_context': terms_with_context
        }
    
    def __len__(self) -> int:
        """Return number of terms in glossary."""
        return len(self._terms)
    
    def __str__(self) -> str:
        """String representation of glossary."""
        stats = self.get_statistics()
        return f"Glossary({stats['total_terms']} terms, avg_usage: {stats['avg_usage']})"
    
    def __repr__(self) -> str:
        """Detailed representation of glossary."""
        return f"Glossary(terms={len(self._terms)}, usage_entries={len(self._usage_count)}, context_entries={len(self._context)})"