"""
Text Cleaner Module

Provides functions to clean and normalize text:
- Convert to lowercase
- Remove punctuation
- Remove extra whitespace
"""

import re
import string


def to_lowercase(text: str) -> str:
    """
    Convert text to lowercase.
    
    Args:
        text: Input text string
        
    Returns:
        Lowercase text string
    """
    return text.lower()


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from text.
    
    Note: We keep apostrophes for contractions (e.g., "don't", "can't")
    as they are important for understanding meaning in codeswitched text.
    
    Args:
        text: Input text string
        
    Returns:
        Text with punctuation removed
    """
    # Keep apostrophes for contractions
    punctuation = string.punctuation.replace("'", "")
    return text.translate(str.maketrans("", "", punctuation))


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    - Trim leading/trailing whitespace
    - Replace multiple spaces with single space
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text with normalized whitespace
    """
    # Trim leading/trailing whitespace
    text = text.strip()
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text


def remove_special_characters(text: str, keep_codeswitching: bool = True) -> str:
    """
    Remove special characters while optionally preserving 
    characters common in Tagalog-English codeswitching.
    
    Args:
        text: Input text string
        keep_codeswitching: If True, keep characters common in codeswitched text
        
    Returns:
        Text with special characters handled
    """
    if keep_codeswitching:
        # Keep alphanumeric, spaces, and common punctuation
        # This preserves Filipino/Tagalog characters like 'ñ'
        pattern = r'[^\w\s\'-]'
    else:
        # Only keep alphanumeric and spaces
        pattern = r'[^\w\s]'
    
    return re.sub(pattern, '', text)


def clean_text(text: str, lowercase: bool = True, remove_punct: bool = True) -> str:
    """
    Main function to clean text with all basic cleaning operations.
    
    Pipeline:
    1. Remove special characters (keep codeswitching characters)
    2. Convert to lowercase (if enabled)
    3. Remove punctuation (if enabled)
    4. Remove extra whitespace
    
    Args:
        text: Input text string
        lowercase: Whether to convert to lowercase
        remove_punct: Whether to remove punctuation
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Step 1: Remove special characters (keep codeswitching)
    text = remove_special_characters(text, keep_codeswitching=True)
    
    # Step 2: Lowercase (if enabled)
    if lowercase:
        text = to_lowercase(text)
    
    # Step 3: Remove punctuation (if enabled)
    if remove_punct:
        text = remove_punctuation(text)
    
    # Step 4: Remove extra whitespace
    text = remove_extra_whitespace(text)
    
    return text


# Test function
if __name__ == "__main__":
    # Test examples including codeswitched text
    test_cases = [
        "Hello World!",
        "Ma'am, pwede po ba yung ibang example?",
        "I don't understand the CONCEPT.",
        "THANK YOU PO! 😊",
        "   Multiple   spaces   here   ",
        "What's the answer??",
    ]
    
    print("=" * 60)
    print("Text Cleaner Test Results")
    print("=" * 60)
    
    for text in test_cases:
        cleaned = clean_text(text)
        print(f"Input:  '{text}'")
        print(f"Output: '{cleaned}'")
        print("-" * 60)
