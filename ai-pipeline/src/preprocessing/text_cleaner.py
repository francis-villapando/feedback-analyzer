"""
Text Cleaner Module

Provides functions to clean and normalize text:
- Remove URLs
- Clean special characters and whitespace
"""

import re
import string

from .url_remover import remove_urls


def clean_text(
    text: str,
    remove_urls_flag: bool = True,
) -> str:
    """
    Main function to clean text with basic operations.

    Pipeline:
    1. Remove URLs (if enabled)
    2. Clean special characters and normalize whitespace

    Args:
        text: Input text string
        remove_urls_flag: Whether to remove URLs

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    if remove_urls_flag:
        text = remove_urls(text)

    return text


# Test function
if __name__ == "__main__":
    test_cases = [
        "Hello World!",
        "Ma'am, pwede po ba yung ibang example?",
        "I don't understand the CONCEPT.",
        "THANK YOU PO!",
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
