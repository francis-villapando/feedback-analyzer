"""
Vowel Normalizer Module

Provides functions to normalize elongated/vstretched words:
- Standardize repeated vowels (e.g., 'helloooo' -> 'hello')
- Handle common elongation patterns in informal text
"""

import re


VOWELS = set("aeiouAEIOU")

ELONGATION_PATTERN = re.compile(r"([a-zA-Z])\1{2,}")


def normalize_elongation(text: str, reduce_to: int = 1) -> str:
    """
    Normalize elongated words by reducing repeated characters.

    Examples:
    - "helloooo" -> "hello"
    - "sooooo" -> "so"
    - "waaaay" -> "way"

    Args:
        text: Input text string
        reduce_to: Maximum number of repeated characters (default: 1)

    Returns:
        Text with normalized elongation
    """
    if not text:
        return ""

    def reduce_repeats(match):
        char = match.group(1)
        return char * reduce_to

    return ELONGATION_PATTERN.sub(reduce_repeats, text)


def normalize_vowels(text: str) -> str:
    """
    Normalize vowels in text - reduce elongation.

    This handles informal text with stretched words like:
    - "hellooooo" -> "hello"
    - "sooooo" -> "so"

    Args:
        text: Input text string

    Returns:
        Text with normalized vowels
    """
    if not text:
        return ""

    text = normalize_elongation(text, reduce_to=1)

    return text


def normalize_text(
    text: str, normalize_elongation_flag: bool = True
) -> str:
    """
    Full vowel normalization pipeline.

    Pipeline:
    1. Normalize elongation (reduce repeated characters)

    Args:
        text: Input text string
        normalize_elongation_flag: Whether to normalize elongation

    Returns:
        Normalized text string
    """
    if not text:
        return ""

    if normalize_elongation_flag:
        text = normalize_elongation(text, reduce_to=1)

    return text


if __name__ == "__main__":
    test_cases = [
        "hellooooo",
        "soooooonnn",
        "waaaayyyy",
        "Mixed: helloooo goooo",
    ]

    print("=" * 60)
    print("Vowel Normalizer Test Results")
    print("=" * 60)

    for text in test_cases:
        normalized = normalize_text(text)
        print(f"Input:    '{text}'")
        print(f"Output:   '{normalized}'")
        print("-" * 60)
