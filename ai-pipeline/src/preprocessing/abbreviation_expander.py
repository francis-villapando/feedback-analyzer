"""
Abbreviation Expander Module

Expands common abbreviations, especially Tagalog-English codeswitching:
- Common English abbreviations (pls, thx, bc, etc.)
- Taglish abbreviations
- Internet slang
"""

import re
from typing import Optional


ABBREVIATIONS = {
    # Common English
    "pls": "please",
    "plz": "please",
    "plss": "please",
    "plsss": "please",
    "thx": "thanks",
    "thnx": "thanks",
    "ty": "thank you",
    "tnx": "thanks",
    "tysm": "thank you so much",
    "np": "no problem",
    "no prob": "no problem",
    "sry": "sorry",
    "srry": "sorry",
    "srsly": "seriously",
    "bc": "because",
    "bcoz": "because",
    "bcos": "because",
    "cuz": "because",
    "coz": "because",
    "cos": "because",
    "w/": "with",
    "w/o": "without",
    "wtd": "what to do",
    "idk": "i don't know",
    "btw": "by the way",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "tbh": "to be honest",
    "ngl": "not going to lie",
    "fr": "for real",
    "frfr": "for real for real",
    "asap": "as soon as possible",
    "rn": "right now",
    "omg": "oh my god",
    "omfg": "oh my god",
    "wtf": "what the heck",
    "wth": "what the heck",
    "jk": "just kidding",
    "lol": "laughing out loud",
    "lmao": "laughing my butt off",
    "smh": "shaking my head",
    "fyi": "for your information",
    "bt": "but",
    # Tagalog-English (Taglish)
    "po": "po",
    "opo": "opo",
    "sige": "sige",
    "cge": "sige",
    "prev": "previous",
    "nxt": "next",
    "sna": "sana",
    "pg": "page",
    "pge": "page",
    "prc": "po read comments",
    "prl": "po like",
    "pcm": "please comment",
    "lng": "lang",
    "kasi": "kasi",
    "nmn": "naman",
    "y": "why",
    "n": "and",
    "d": "the",
    "r": "are",
    "u": "you",
    "ur": "your",
    "yall": "you all",
    "msg": "message",
    "pic": "picture",
    "pics": "pictures",
    "info": "information",
    # More variations
    "deets": "details",
    "dm": "direct message",
    "pm": "private message",
    "fb": "facebook",
    "ig": "instagram",
    "yt": "youtube",
    "gonna": "going to",
    "gotta": "got to",
    "wanna": "want to",
}


def expand_abbreviation(word: str) -> str:
    """
    Expand a single word if it's an abbreviation.

    Preserves original case for identity mappings (e.g., PO stays PO).
    Applies case transfer for actual expansions (e.g., TBH -> to be honest).

    Args:
        word: Single word to check

    Returns:
        Expanded word or original if not found
    """
    lower_word = word.lower()
    expansion = ABBREVIATIONS.get(lower_word)
    if expansion is None:
        return word
    # Identity mapping (e.g., "po" -> "po") — preserve original case
    if expansion == lower_word:
        return word
    # Real expansion — return the expansion as-is
    return expansion


def expand_abbreviations(text: str) -> str:
    """
    Expand all abbreviations in text.

    Preserves original case for words not in the dictionary.

    Args:
        text: Input text string

    Returns:
        Text with abbreviations expanded
    """
    if not text:
        return ""

    # Special handling for w/ and w/o as they contain / which breaks \b
    text = re.sub(r"\bw/o\b", "without", text, flags=re.IGNORECASE)
    text = re.sub(r"\bw/\b", "with", text, flags=re.IGNORECASE)

    def replace_word(match):
        word = match.group(0)
        expanded = expand_abbreviation(word)
        return expanded

    # Change + to * to allow single-character abbreviations like 'u', 'r', 'n'
    pattern = r"\b[a-zA-Z][a-zA-Z0-9]*\b"
    result = re.sub(pattern, replace_word, text)

    return result


def expand_abbreviations_preserve_case(text: str) -> str:
    """
    Expand abbreviations while preserving original case where possible.

    For known abbreviations, try to preserve the original capitalization pattern.

    Args:
        text: Input text string

    Returns:
        Text with abbreviations expanded
    """
    if not text:
        return ""

    words = text.split()
    expanded_words = []

    for word in words:
        lower_word = word.lower()
        if lower_word in ABBREVIATIONS:
            replacement = ABBREVIATIONS[lower_word]
            if word.isupper():
                expanded_words.append(replacement.upper())
            elif word[0].isupper():
                expanded_words.append(replacement.capitalize())
            else:
                expanded_words.append(replacement)
        else:
            expanded_words.append(word)

    return " ".join(expanded_words)


def add_abbreviation(abbrev: str, expansion: str) -> None:
    """
    Add a custom abbreviation to the dictionary.

    Args:
        abbrev: Abbreviation (e.g., "btw")
        expansion: Full word or phrase (e.g., "by the way")
    """
    ABBREVIATIONS[abbrev.lower()] = expansion


def remove_abbreviation(abbrev: str) -> Optional[str]:
    """
    Remove an abbreviation from the dictionary.

    Args:
        abbrev: Abbreviation to remove

    Returns:
        The removed expansion or None if not found
    """
    return ABBREVIATIONS.pop(abbrev.lower(), None)


def get_abbreviation(abbrev: str) -> Optional[str]:
    """
    Get the expansion for an abbreviation.

    Args:
        abbrev: Abbreviation to look up

    Returns:
        Expansion or None if not found
    """
    return ABBREVIATIONS.get(abbrev.lower())


if __name__ == "__main__":
    test_cases = [
        "pls help me",
        "thx for the info",
        "bc i dont understand",
        "w/ regards to this",
        "w/o you",
        "tbh i dont know",
        "ngl this is hard",
        "u r so good n smart",
        "asap please",
        "imo this is correct",
    ]

    print("=" * 60)
    print("Abbreviation Expander Test Results")
    print("=" * 60)

    for text in test_cases:
        expanded = expand_abbreviations(text)
        print(f"Input:  '{text}'")
        print(f"Output: '{expanded}'")
        print("-" * 60)
