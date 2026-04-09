"""
Text Cleaner Module

Provides functions to clean and normalize text:
- Remove URLs
- Convert to lowercase
"""

import re
import string

from .url_remover import remove_urls


def to_lowercase(text: str) -> str:
    """
    Convert text to lowercase.

    Args:
        text: Input text string

    Returns:
        Lowercase text string
    """
    return text.lower()


def clean_text(
    text: str,
    lowercase: bool = True,
    remove_urls_flag: bool = True,
) -> str:
    """
    Main function to clean text with basic operations.

    Pipeline:
    1. Remove URLs (if enabled)
    2. Convert to lowercase (if enabled)

    Args:
        text: Input text string
        lowercase: Whether to convert to lowercase
        remove_urls_flag: Whether to remove URLs

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    # Step 1: Remove URLs (if enabled)
    if remove_urls_flag:
        text = remove_urls(text)

    # Step 2: Lowercase (if enabled)
    if lowercase:
        text = to_lowercase(text)

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
