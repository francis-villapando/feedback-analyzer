"""
Preprocessing Module

This module provides text preprocessing functions for the AI Pipeline.

Main Functions:
- clean_text(): Clean and normalize text
- tokenize(): Split text into tokens
- lemmatize(): Reduce words to base forms
- correct_spelling(): Fix spelling errors
- preprocess(): Full preprocessing pipeline

Note: Stopwords are kept by default for codeswitching (Tagalog-English).
"""

# Text Cleaner exports
from .text_cleaner import (
    to_lowercase,
    remove_punctuation,
    remove_extra_whitespace,
    remove_special_characters,
    clean_text,
)

# Tokenizer exports
from .tokenizer import (
    nltk_tokenize,
    simple_tokenize,
    spacy_tokenize,
    tokenize,
    detokenize,
)

# Lemmatizer exports
from .lemmatizer import (
    load_lemmatizer,
    get_lemmatizer,
    lemmatize_word,
    lemmatize_text,
    lemmatize_tokens,
    lemmatize_with_pos,
    nltk_lemmatize,
)

# Spelling Corrector exports
from .spelling_corrector import (
    create_spell_checker,
    get_spell_checker,
    add_to_dictionary,
    correct_word,
    correct_text,
    correct_tokens,
    get_suggestions,
)


def preprocess(
    text: str,
    lowercase: bool = True,
    remove_punct: bool = True,
    tokenize_flag: bool = True,
    lemmatize_flag: bool = True,
    spell_check: bool = True
) -> dict:
    """
    Full preprocessing pipeline for a single text.
    
    Pipeline:
    1. Clean text (lowercase, remove punctuation, remove extra whitespace)
    2. Tokenize
    3. Lemmatize (if enabled)
    4. Spell check (if enabled)
    
    Note: Stopwords are always kept since BERT models benefit from them.
    
    Args:
        text: Input text string
        lowercase: Whether to convert to lowercase
        remove_punct: Whether to remove punctuation
        tokenize_flag: Whether to tokenize
        lemmatize_flag: Whether to lemmatize
        spell_check: Whether to check spelling
        
    Returns:
        Dictionary with:
        - cleaned_text: Fully processed text
        - tokens: List of tokens
        - original: Original input
        - metadata: Processing information
    """
    result = {
        "original": text,
        "cleaned_text": "",
        "tokens": [],
        "metadata": {
            "lowercase": lowercase,
            "remove_punct": remove_punct,
            "tokenize": tokenize_flag,
            "lemmatize": lemmatize_flag,
            "spell_check": spell_check,
        }
    }
    
    if not text:
        return result
    
    # Step 1: Clean text
    cleaned = clean_text(text, lowercase=lowercase, remove_punct=remove_punct)
    result["cleaned_text"] = cleaned
    
    # Step 2: Tokenize
    if tokenize_flag:
        tokens = tokenize(cleaned)
    else:
        # Use simple_tokenize for consistency when tokenization is disabled
        tokens = simple_tokenize(cleaned)
    
    # Step 3: Lemmatize
    if lemmatize_flag:
        tokens = lemmatize_tokens(tokens)
    
    # Step 4: Spell check
    if spell_check:
        tokens = correct_tokens(tokens)
    
    result["tokens"] = tokens
    result["cleaned_text"] = " ".join(tokens)
    
    return result


def preprocess_batch(texts: list, **kwargs) -> list:
    """
    Preprocess a batch of texts.
    
    Args:
        texts: List of input text strings
        **kwargs: Additional arguments passed to preprocess()
        
    Returns:
        List of preprocessing results
    """
    return [preprocess(text, **kwargs) for text in texts]


# Module version
__version__ = "1.0.0"
