"""
Tokenizer Module

Provides functions to tokenize text into words/tokens.
Supports both spaCy and NLTK tokenizers.
"""

import re
from typing import List, Optional
import nltk
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


def nltk_tokenize(text: str) -> List[str]:
    """
    Tokenize text using NLTK's word_tokenize.
    
    NLTK's tokenizer is good for English and handles contractions well.
    
    Args:
        text: Input text string
        
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    tokens = word_tokenize(text)
    return tokens


def simple_tokenize(text: str) -> List[str]:
    """
    Simple whitespace-based tokenization.
    
    This is a fallback method that splits on whitespace.
    
    Args:
        text: Input text string
        
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    return text.split()


def tokenize(text: str, method: str = "nltk") -> List[str]:
    """
    Main tokenization function.
    
    Args:
        text: Input text string
        method: Tokenization method ('nltk', 'simple', or 'spacy')
        
    Returns:
        List of tokens
        
    Raises:
        ValueError: If an invalid method is specified
    """
    if not text:
        return []
    
    if method == "nltk":
        return nltk_tokenize(text)
    elif method == "simple":
        return simple_tokenize(text)
    elif method == "spacy":
        return spacy_tokenize(text)
    else:
        raise ValueError(f"Unknown tokenization method: {method}. Use 'nltk', 'simple', or 'spacy'.")


def spacy_tokenize(text: str) -> List[str]:
    """
    Tokenize text using spaCy.
    
    spaCy provides more sophisticated tokenization and is good
    for languages with complex word structures.
    
    Note: Requires spaCy model to be loaded. Falls back to NLTK if unavailable.
    
    Args:
        text: Input text string
        
    Returns:
        List of tokens
    """
    try:
        import spacy
        # Try to load the English model
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Download the model if not found
            import subprocess
            try:
                subprocess.run(
                    ["python", "-m", "spacy", "download", "en_core_web_sm"],
                    capture_output=True,
                    timeout=300  # 5 minute timeout
                )
                nlp = spacy.load("en_core_web_sm")
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"Warning: spaCy model download failed ({e}), using NLTK fallback")
                return nltk_tokenize(text)
        
        doc = nlp(text)
        return [token.text for token in doc]
    except Exception as e:
        # Fallback to NLTK if spaCy fails
        print(f"Warning: spaCy tokenization failed ({e}), using NLTK fallback")
        return nltk_tokenize(text)


def detokenize(tokens: List[str]) -> str:
    """
    Convert tokens back to text (detokenization).
    
    Handles punctuation spacing and common contractions.
    
    Args:
        tokens: List of tokens
        
    Returns:
        Detokenized text string
    """
    if not tokens:
        return ""
    
    text = " ".join(tokens)
    
    # Remove space before common trailing punctuation
    text = re.sub(r"\s+([.,!?;:%\)\]\}])", r"\1", text)
    
    # Remove space after common opening punctuation
    text = re.sub(r"([\(\[\{])\s+", r"\1", text)
    
    # Handle common contractions
    contractions = {
        "do n't": "don't",
        "ca n't": "can't",
        "wo n't": "won't",
        "is n't": "isn't",
        "are n't": "aren't",
        "was n't": "wasn't",
        "were n't": "weren't",
        "have n't": "haven't",
        "has n't": "hasn't",
        "had n't": "hadn't",
        "should n't": "shouldn't",
        "could n't": "couldn't",
        "would n't": "wouldn't",
        "i 'm": "I'm",
        "you 're": "you're",
        "he 's": "he's",
        "she 's": "she's",
        "it 's": "it's",
        "we 're": "we're",
        "they 're": "they're",
        "i 'll": "I'll",
        "you 'll": "you'll",
        "he 'll": "he'll",
        "she 'll": "she'll",
        "it 'll": "it'll",
        "we 'll": "we'll",
        "they 'll": "they'll",
        "i 've": "I've",
        "you 've": "you've",
        "we 've": "we've",
        "they 've": "they've",
    }
    
    for contraction, expanded in contractions.items():
        text = text.replace(contraction, expanded)
    
    return text


# Test function
if __name__ == "__main__":
    test_cases = [
        "Hello World!",
        "I don't understand this.",
        "Ma'am, pwede po ba?",
        "What's the answer?",
    ]
    
    print("=" * 60)
    print("Tokenizer Test Results")
    print("=" * 60)
    
    for text in test_cases:
        tokens = tokenize(text, method="nltk")
        print(f"Input:  '{text}'")
        print(f"Tokens: {tokens}")
        print("-" * 60)
