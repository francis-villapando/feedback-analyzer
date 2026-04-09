"""
URL Remover Module

Provides functions to remove URLs from text:
- HTTP/HTTPS URLs
- www. URLs
- Preserves non-URL text
"""

import re


URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")


def remove_urls(text: str) -> str:
    """
    Remove all URLs from text.

    Removes:
    - http:// URLs
    - https:// URLs
    - www. URLs

    Args:
        text: Input text string

    Returns:
        Text with URLs removed
    """
    if not text:
        return ""

    return URL_PATTERN.sub("", text)


def remove_urls_preserve_whitespace(text: str) -> str:
    """
    Remove URLs from text while preserving word spacing.

    Args:
        text: Input text string

    Returns:
        Text with URLs removed, extra whitespace cleaned
    """
    if not text:
        return ""

    result = URL_PATTERN.sub("", text)
    result = re.sub(r"\s+", " ", result)
    return result.strip()


def has_urls(text: str) -> bool:
    """
    Check if text contains URLs.

    Args:
        text: Input text string

    Returns:
        True if URLs found, False otherwise
    """
    if not text:
        return False

    return bool(URL_PATTERN.search(text))


def extract_urls(text: str) -> list:
    """
    Extract all URLs from text.

    Args:
        text: Input text string

    Returns:
        List of URLs found
    """
    if not text:
        return []

    return URL_PATTERN.findall(text)


if __name__ == "__main__":
    test_cases = [
        "Check out https://example.com for more info",
        "Visit www.github.com for code",
        "Hello world, no URLs here",
        "Multiple URLs: http://foo.com and https://bar.com",
        "No URLs in this text",
        "  https://test.com  ",
    ]

    print("=" * 60)
    print("URL Remover Test Results")
    print("=" * 60)

    for text in test_cases:
        cleaned = remove_urls_preserve_whitespace(text)
        has_url = has_urls(text)
        urls = extract_urls(text)
        print(f"Input:     '{text}'")
        print(f"Output:    '{cleaned}'")
        print(f"Has URLs:  {has_url}")
        if urls:
            print(f"Found:     {urls}")
        print("-" * 60)
