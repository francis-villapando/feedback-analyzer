"""
Lemmatizer Module

Provides lemmatization functionality to reduce words to their base/dictionary form.
Uses spaCy for lemmatization (more accurate than NLTK's WordNet lemmatizer).
"""

from typing import List, Optional
import spacy


def load_lemmatizer(model: str = "en_core_web_sm") -> spacy.language.Language:
    """
    Load a spaCy model for lemmatization.
    
    Args:
        model: SpaCy model name
        
    Returns:
        Loaded spaCy model
    """
    try:
        nlp = spacy.load(model)
        return nlp
    except OSError:
        import subprocess
        print(f"Downloading spaCy model: {model}")
        try:
            subprocess.run(
                ["python", "-m", "spacy", "download", model],
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
            nlp = spacy.load(model)
            return nlp
        except (subprocess.TimeoutExpired, Exception) as e:
            raise RuntimeError(f"Failed to download spaCy model '{model}': {e}")


# Global lemmatizer instance (lazy loaded)
_lemmatizer = None


def get_lemmatizer() -> spacy.language.Language:
    """
    Get the global lemmatizer instance.
    
    Returns:
        spaCy language model
    """
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = load_lemmatizer()
    return _lemmatizer


def lemmatize_word(word: str) -> str:
    """
    Lemmatize a single word.
    
    Args:
        word: Input word
        
    Returns:
        Lemmatized form of the word
    """
    if not word:
        return ""
    
    nlp = get_lemmatizer()
    doc = nlp(word)
    
    # Return the lemma of the first token
    return doc[0].lemma_


def lemmatize_text(text: str) -> str:
    """
    Lemmatize all words in a text.
    
    Args:
        text: Input text string
        
    Returns:
        Lemmatized text string
    """
    if not text:
        return ""
    
    nlp = get_lemmatizer()
    doc = nlp(text)
    
    # Get lemmas for all tokens
    lemmas = [token.lemma_ for token in doc]
    
    return " ".join(lemmas)


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """
    Lemmatize a list of tokens.
    
    Args:
        tokens: List of tokens
        
    Returns:
        List of lemmatized tokens
    """
    if not tokens:
        return []
    
    # Join tokens, lemmatize, then split
    text = " ".join(tokens)
    lemmatized_text = lemmatize_text(text)
    
    return lemmatized_text.split()


def lemmatize_with_pos(text: str) -> List[tuple]:
    """
    Lemmatize text and return POS tags alongside.
    
    Useful for more advanced processing.
    
    Args:
        text: Input text string
        
    Returns:
        List of (lemma, POS_tag) tuples
    """
    if not text:
        return []
    
    nlp = get_lemmatizer()
    doc = nlp(text)
    
    return [(token.lemma_, token.pos_) for token in doc]


# NLTK fallback lemmatizer (for comparison or fallback)
def nltk_lemmatize(word: str) -> str:
    """
    Lemmatize using NLTK's WordNet lemmatizer (fallback).
    
    Note: This is less accurate than spaCy but works without spaCy models.
    
    Args:
        word: Input word
        
    Returns:
        Lemmatized form
    """
    from nltk.stem import WordNetLemmatizer
    
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(word)


# Test function
if __name__ == "__main__":
    test_cases = [
        "running",
        "children",
        "better",
        "was",
        "studying",
        "universities",
        "ran",
        "gone",
        "geese",
    ]
    
    print("=" * 60)
    print("Lemmatizer Test Results")
    print("=" * 60)
    
    # Test with spaCy
    print("\nUsing spaCy lemmatizer:")
    for word in test_cases:
        lemma = lemmatize_word(word)
        print(f"  {word} -> {lemma}")
    
    # Test with sentences
    sentences = [
        "The children were running to the school.",
        "I have gone to the store.",
    ]
    
    print("\nSentence lemmatization:")
    for sentence in sentences:
        lemma = lemmatize_text(sentence)
        print(f"  '{sentence}' -> '{lemma}'")
    
    # Show POS tags
    print("\nWith POS tags:")
    result = lemmatize_with_pos("The children were running to the school.")
    print(f"  {result}")
