"""
Noise Cleaner Module

Provides functions to clean noise from text:
- Remove URLs
- Remove hashtags
- Remove HTML tags
- Remove specific emojis
- Remove mentions (@username)
"""

import re


URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HASHTAG_PATTERN = re.compile(r"#\w+")
MENTION_PATTERN = re.compile(r"@\w+")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

EMOJI_PATTERN = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map symbols
    "\U0001f900-\U0001f9ff"  # supplemental symbols & pictographs (🤣, 🤔, etc.)
    "\U0001fa00-\U0001fa6f"  # chess symbols, extended-A
    "\U0001fa70-\U0001faff"  # symbols & pictographs extended-A
    "\U0001f1e0-\U0001f1ff"  # flags
    "\U00002702-\U000027b0"
    "\U000024c2-\U0001f251"
    "\U00002600-\U000026ff"  # misc symbols (☀, ⚡, etc.)
    "\U0000fe00-\U0000fe0f"  # variation selectors
    "\U0000200d"             # zero width joiner
    "]+",
    flags=re.UNICODE,
)

REPEATING_CHARS_PATTERN = re.compile(r"(.)\1{2,}")


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    if not text:
        return ""
    return URL_PATTERN.sub("", text)


def remove_hashtags(text: str) -> str:
    """Remove hashtags from text."""
    if not text:
        return ""
    return HASHTAG_PATTERN.sub("", text)


def remove_mentions(text: str) -> str:
    """Remove @mentions from text."""
    if not text:
        return ""
    return MENTION_PATTERN.sub("", text)


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    return HTML_TAG_PATTERN.sub("", text)


def remove_emojis(text: str) -> str:
    """Remove emojis from text."""
    if not text:
        return ""
    return EMOJI_PATTERN.sub("", text)


def remove_repeating_chars(text: str) -> str:
    """Reduce repeating characters to max 2 (e.g., 'hellooo' -> 'helloo')."""
    if not text:
        return ""
    return REPEATING_CHARS_PATTERN.sub(r"\1\1", text)


def clean_noise(
    text: str,
    remove_urls_flag: bool = True,
    remove_hashtags_flag: bool = True,
    remove_mentions_flag: bool = True,
    remove_html_tags_flag: bool = True,
    remove_emojis_flag: bool = True,
    normalize_elongation_flag: bool = True,
) -> str:
    """
    Full noise cleaning pipeline.

    Pipeline:
    1. Remove URLs (if enabled)
    2. Remove hashtags (if enabled)
    3. Remove mentions (if enabled)
    4. Remove HTML tags (if enabled)
    5. Remove emojis (if enabled)
    6. Normalize elongated words (if enabled)

    Args:
        text: Input text string
        remove_urls_flag: Whether to remove URLs
        remove_hashtags_flag: Whether to remove hashtags
        remove_mentions_flag: Whether to remove @mentions
        remove_html_tags_flag: Whether to remove HTML tags
        remove_emojis_flag: Whether to remove emojis
        normalize_elongation_flag: Whether to normalize elongated words

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    if remove_urls_flag:
        text = remove_urls(text)

    if remove_hashtags_flag:
        text = remove_hashtags(text)

    if remove_mentions_flag:
        text = remove_mentions(text)

    if remove_html_tags_flag:
        text = remove_html_tags(text)

    if remove_emojis_flag:
        text = remove_emojis(text)

    if normalize_elongation_flag:
        text = remove_repeating_chars(text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":
    test_cases = [
        "Check out https://example.com for more info",
        "Great #learning experience @teacher",
        "<p>HTML content</p>",
        "Hello 👋😊 how are you???",
        "Hellooooo waayyyy tooooo longgg",
        "Mixed: https://url.com #tag @mention <html>😀</html>",
    ]

    print("=" * 60)
    print("Noise Cleaner Test Results")
    print("=" * 60)

    for text in test_cases:
        cleaned = clean_noise(text)
        print(f"Input:  '{text}'")
        print(f"Output: '{cleaned}'")
        print("-" * 60)
