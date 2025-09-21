"""
Emotion preservation module using ONNX models
"""
import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_emotion_model():
    """
    Load the emotion quantized ONNX model.
    
    Returns:
        Loaded ONNX model session or None if model not found
    """
    try:
        import onnxruntime as ort
        
        models_dir = "models"
        model_path = os.path.join(models_dir, "emotion_quantized.onnx")
        
        if not os.path.exists(model_path):
            logger.warning(f"Emotion ONNX model not found at {model_path}. Emotion preservation disabled.")
            return None
        
        session = ort.InferenceSession(model_path)
        logger.info(f"Loaded emotion model: {model_path}")
        return session
        
    except ImportError:
        logger.warning("ONNXRuntime not available. Emotion preservation disabled.")
        return None
    except Exception as e:
        logger.error(f"Error loading emotion ONNX model: {e}")
        return None

# Global model instance
_emotion_model = None

def get_emotion_model():
    """Get or load the emotion model."""
    global _emotion_model
    if _emotion_model is None:
        _emotion_model = load_emotion_model()
    return _emotion_model

def analyze_emotion(text: str) -> Dict[str, float]:
    """
    Analyze emotion in the given text.
    
    Args:
        text: Text to analyze for emotions
        
    Returns:
        Dictionary with emotion scores
    """
    if not text or not text.strip():
        return {"neutral": 1.0}
    
    model = get_emotion_model()
    
    if model is None:
        # Fallback emotion analysis using simple heuristics
        return analyze_emotion_fallback(text)
    
    try:
        # Prepare input for ONNX model
        # Note: This is a simplified example - actual implementation depends on your specific model
        inputs = {'text': [text]}
        
        # Run inference
        outputs = model.run(None, inputs)
        
        # Process outputs (assuming the model returns emotion probabilities)
        if outputs and len(outputs) > 0:
            emotion_scores = outputs[0][0]  # Assuming first output, first batch
            
            # Map to emotion labels (adjust based on your model)
            emotion_labels = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]
            emotions = {}
            
            for i, score in enumerate(emotion_scores):
                if i < len(emotion_labels):
                    emotions[emotion_labels[i]] = float(score)
            
            return emotions
        else:
            return {"neutral": 1.0}
            
    except Exception as e:
        logger.error(f"Error during emotion analysis: {e}")
        return analyze_emotion_fallback(text)

def analyze_emotion_fallback(text: str) -> Dict[str, float]:
    """
    Fallback emotion analysis using simple keyword matching.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with emotion scores
    """
    text_lower = text.lower()
    
    # Define emotion keywords
    emotion_keywords = {
        "joy": ["happy", "joyful", "excited", "delighted", "cheerful", "glad", "pleased", "content", "blissful", "elated", "laugh", "smile", "wonderful", "amazing", "fantastic"],
        "sadness": ["sad", "depressed", "melancholy", "sorrowful", "gloomy", "dejected", "downhearted", "mournful", "cry", "weep", "tears", "grief", "lonely", "despair"],
        "anger": ["angry", "furious", "enraged", "livid", "irate", "mad", "irritated", "annoyed", "frustrated", "hostile", "rage", "wrath", "hate", "damn", "hell"],
        "fear": ["afraid", "scared", "frightened", "terrified", "anxious", "worried", "nervous", "panic", "dread", "horror", "alarmed", "apprehensive", "uneasy"],
        "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned", "bewildered", "startled", "unexpected", "sudden", "wow", "incredible", "unbelievable"],
        "disgust": ["disgusted", "revolted", "repulsed", "nauseated", "sickened", "appalled", "horrified", "gross", "yuck", "eww", "horrible", "awful"],
        "neutral": ["said", "went", "came", "looked", "walked", "moved", "turned", "opened", "closed", "took", "gave", "found", "saw", "heard"]
    }
    
    emotion_scores = {}
    total_matches = 0
    
    # Count keyword matches for each emotion
    for emotion, keywords in emotion_keywords.items():
        count = 0
        for keyword in keywords:
            count += text_lower.count(keyword)
        emotion_scores[emotion] = count
        total_matches += count
    
    # Normalize scores
    if total_matches > 0:
        for emotion in emotion_scores:
            emotion_scores[emotion] = emotion_scores[emotion] / total_matches
    else:
        # No emotional keywords found, assume neutral
        emotion_scores = {"neutral": 1.0}
    
    # Ensure we have at least some score for the dominant emotion
    if max(emotion_scores.values()) == 0:
        emotion_scores["neutral"] = 1.0
    
    logger.debug(f"Emotion analysis result: {emotion_scores}")
    return emotion_scores

def apply_emotion_markers(text: str, emotions: Dict[str, float]) -> str:
    """
    Apply emotion markers to text based on emotion analysis.
    
    Args:
        text: Original text
        emotions: Emotion scores dictionary
        
    Returns:
        Text with emotion markers applied
    """
    if not emotions:
        return text
    
    # Find dominant emotion
    dominant_emotion = max(emotions, key=emotions.get)
    emotion_intensity = emotions[dominant_emotion]
    
    # Only apply markers if emotion is significant
    if emotion_intensity < 0.3:
        return text
    
    # Simple emotion markers (in a real implementation, this would be more sophisticated)
    emotion_markers = {
        "joy": {"prefix": "", "suffix": "!", "emphasis": True},
        "sadness": {"prefix": "", "suffix": "...", "emphasis": False},
        "anger": {"prefix": "", "suffix": "!", "emphasis": True},
        "fear": {"prefix": "", "suffix": "...", "emphasis": False},
        "surprise": {"prefix": "", "suffix": "?!", "emphasis": True},
        "disgust": {"prefix": "", "suffix": ".", "emphasis": False},
        "neutral": {"prefix": "", "suffix": ".", "emphasis": False}
    }
    
    markers = emotion_markers.get(dominant_emotion, emotion_markers["neutral"])
    
    # Apply basic formatting (this is simplified - real implementation would be more nuanced)
    modified_text = text
    
    if markers["emphasis"] and emotion_intensity > 0.6:
        # Add emphasis to emotional words
        emotional_words = {
            "joy": ["wonderful", "amazing", "fantastic", "incredible", "brilliant"],
            "anger": ["terrible", "awful", "horrible", "disgusting", "outrageous"],
            "surprise": ["incredible", "unbelievable", "amazing", "shocking"]
        }
        
        if dominant_emotion in emotional_words:
            for word in emotional_words[dominant_emotion]:
                modified_text = modified_text.replace(word, word.upper())
    
    return modified_text

def apply_emotion(text: str) -> str:
    """
    Apply emotion preservation to translated text.
    
    Args:
        text: Translated text to enhance with emotion
        
    Returns:
        Text with emotion preservation applied
    """
    if not text or not text.strip():
        return text
    
    try:
        # Analyze emotions in the text
        emotions = analyze_emotion(text)
        
        # Apply emotion markers
        enhanced_text = apply_emotion_markers(text, emotions)
        
        logger.debug(f"Applied emotion preservation. Dominant emotion: {max(emotions, key=emotions.get) if emotions else 'none'}")
        
        return enhanced_text
        
    except Exception as e:
        logger.error(f"Error applying emotion preservation: {e}")
        return text  # Return original text if emotion processing fails

def get_emotion_summary(text: str) -> Dict[str, Any]:
    """
    Get a summary of emotions detected in the text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with emotion analysis summary
    """
    emotions = analyze_emotion(text)
    
    if not emotions:
        return {"dominant_emotion": "neutral", "confidence": 0.0, "emotions": {}}
    
    dominant_emotion = max(emotions, key=emotions.get)
    confidence = emotions[dominant_emotion]
    
    # Filter out very low scores
    significant_emotions = {k: v for k, v in emotions.items() if v > 0.1}
    
    return {
        "dominant_emotion": dominant_emotion,
        "confidence": round(confidence, 3),
        "emotions": {k: round(v, 3) for k, v in significant_emotions.items()},
        "total_emotions": len(significant_emotions)
    }

def preserve_emotional_context(original_text: str, translated_text: str) -> str:
    """
    Preserve emotional context from original text in the translation.
    
    Args:
        original_text: Original text with emotional context
        translated_text: Translated text
        
    Returns:
        Translation with preserved emotional context
    """
    try:
        # Analyze emotions in original text
        original_emotions = analyze_emotion(original_text)
        
        # Apply similar emotional markers to translation
        preserved_translation = apply_emotion_markers(translated_text, original_emotions)
        
        logger.debug("Preserved emotional context in translation")
        return preserved_translation
        
    except Exception as e:
        logger.error(f"Error preserving emotional context: {e}")
        return translated_text  # Return translation as-is if context preservation fails