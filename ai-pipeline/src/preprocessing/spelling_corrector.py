"""
Spelling Corrector Module

Provides spelling correction for codeswitched Filipino-English text.
Uses pyspellchecker with a protected dictionary of Tagalog words.

Pipeline:
1. Custom corrections (known misspellings)
2. Protected Tagalog words (loaded into spell checker)
3. English spell correction
"""

from typing import List, Set
from spellchecker import SpellChecker


# Custom corrections for common misspellings in codeswitched text
# (abbreviations and spelling variations)
CUSTOM_CORRECTIONS = {
    # Tagalog abbreviations (common in text messages)
    "q": "ko",
    "aq": "ako",
    "kc": "kasi",
    "kci": "kasi",
    "bk8": "bakit",
    "bka": "baka",
    "bkt": "bakit",
    "bkit": "bakit",
    "hnd": "hindi",
    "hndi": "hindi",
    "di": "hindi",
    "nd": "hindi",
    "dn": "din",
    "dpat": "dapat",
    "prn": "pa rin",
    "prng": "parang",
    "lng": "lang",
    "ung": "yung",
    "syang": "siyang",
    "sya": "siya",
    "puwede": "pwede",
    "pwed": "pwede",
    "pls": "please",
    "plz": "please",
    "sge": "sige",
    "cge": "sige",
    # Common English misspellings
    "teh": "the",
    "recieve": "receive",
    "wierd": "weird",
    "occured": "occurred",
    "seperate": "separate",
    "definite": "definitely",
    "accomodate": "accommodate",
    "occurence": "occurrence",
    "untill": "until",
    "begining": "beginning",
    "beleive": "believe",
    "concious": "conscious",
    "embarass": "embarrass",
    "enviroment": "environment",
    "goverment": "government",
    "independant": "independent",
    "neccessary": "necessary",
    "occassion": "occasion",
    "priviledge": "privilege",
    "recomend": "recommend",
    "refered": "referred",
    "tommorow": "tomorrow",
    # Numbers in words
    "onee": "one",
    "twoo": "two",
    "tree": "three",
    "fore": "four",
    "fiv": "five",
    "sixx": "six",
    "sevn": "seven",
    "ate": "eight",
    "nien": "nine",
    "tenn": "ten",
}


# Protected Tagalog/Filipino words
# These are loaded into the spell checker dictionary to prevent corruption
PROTECTED_TAGALOG_WORDS = {
    # Pronouns
    "ako", "ka", "mo", "ko", "siya", "kayo", "tayo", "kami", "nila", "sila",
    "namin", "natin", "nila", "kay", "nina", "sina", "ni", "si",
    # Demonstratives
    "ito", "iyon", "iyun", "yan", "yun", "dito", "doon", "diyan", "dun",
    "nito", "niyan", "niyon", "niyan", "iyon",
    # Particles
    "po", "opo", "ba", "nga", "na", "pa", "din", "rin", "naman",
    # Adverbs
    "lang", "lng", "muna", "pala", "sana", "talaga", "mas", "dapat", "hindi",
    "kasi", "dahil", "pero", "subalit", "at", "o", "pati", "saka",
    # Prepositions
    "sa", "sa", "ng", "nang", "kay", "kina", "ni", "nina",
    # Others
    "mabilis", "yung", "ung", "ang", "mga", "si", "naka", "mag", "um", "in",
    "maging", "laban", "tungkol", "para", "ay", "kasi",
}


def create_spell_checker(distance: int = 2) -> SpellChecker:
    """
    Create a spell checker instance with protected Tagalog words.

    Args:
        distance: Maximum edit distance to consider (default: 2)

    Returns:
        SpellChecker instance
    """
    checker = SpellChecker(language="en", distance=distance)
    # Load protected Tagalog words into dictionary
    checker.word_frequency.load_words(PROTECTED_TAGALOG_WORDS)
    return checker


# Global spell checker instance
_spell_checker = None


def get_spell_checker() -> SpellChecker:
    """Get the global spell checker instance."""
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = create_spell_checker()
    return _spell_checker


def add_to_dictionary(words: Set[str]) -> None:
    """
    Add words to the spell checker's dictionary.

    Useful for adding proper nouns, technical terms, or
    common words in your specific domain.

    Args:
        words: Set of words to add
    """
    checker = get_spell_checker()
    checker.word_frequency.load_words(words)


def correct_word(word: str) -> str:
    """
    Correct a single word.

    Pipeline:
    1. Custom corrections (known misspellings)
    2. Protected words (in spell checker dictionary)
    3. English spell correction

    Args:
        word: Word to correct

    Returns:
        Corrected word
    """
    if not word:
        return ""

    word_lower = word.lower()

    # Step 1: Check custom corrections
    if word_lower in CUSTOM_CORRECTIONS:
        correction = CUSTOM_CORRECTIONS[word_lower]
        if word.isupper():
            return correction.upper()
        elif word[0].isupper() if word else False:
            return correction.capitalize()
        return correction

    checker = get_spell_checker()

    # Step 2: If word is in dictionary (including protected Tagalog), return as-is
    if word_lower in checker:
        return word

    # Step 3: Try English spell correction
    correction = checker.correction(word_lower)

    if correction is None or correction == word_lower:
        return word

    # Preserve original case pattern
    if word.isupper():
        return correction.upper()
    elif word[0].isupper() if word else False:
        return correction.capitalize()

    return correction


def correct_text(text: str) -> str:
    """
    Correct spelling in a full text.

    Args:
        text: Input text string

    Returns:
        Corrected text string
    """
    if not text:
        return ""

    words = text.split()
    corrected_words = [correct_word(word) for word in words]

    return " ".join(corrected_words)


def correct_tokens(tokens: List[str]) -> List[str]:
    """
    Correct spelling in a list of tokens.

    Args:
        tokens: List of tokens

    Returns:
        List of corrected tokens
    """
    return [correct_word(token) for token in tokens]


def get_suggestions(word: str, n: int = 5) -> List[str]:
    """
    Get spelling suggestions for a word.

    Args:
        word: Word to get suggestions for
        n: Number of suggestions to return

    Returns:
        List of suggested corrections
    """
    suggestions = []
    word_lower = word.lower()

    # Add custom correction if available
    if word_lower in CUSTOM_CORRECTIONS:
        suggestions.append(CUSTOM_CORRECTIONS[word_lower])

    # Check if it's in dictionary
    checker = get_spell_checker()
    if word_lower in checker:
        return suggestions[:n]

    # Get spell checker candidates
    candidates = checker.candidates(word_lower)
    if candidates:
        suggestions.extend(candidates)

    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)

    return unique_suggestions[:n]


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Spelling Corrector Test Results")
    print("=" * 60)

    test_words = [
        # Tagalog abbreviations
        "kc", "bkit", "lng", "hndi", "sya",
        # Tagalog words (should be protected)
        "kasi", "naman", "yung", "po", "mas", "talaga",
        # English misspellings
        "teh", "recieve", "wierd",
        # Correct words
        "hello", "world", "thanks",
    ]

    for word in test_words:
        corrected = correct_word(word)
        status = "=" if corrected == word else "✓"
        print(f"  {word} -> {corrected} {status}")

    print("\n" + "=" * 60)
    print("Text Correction Test")
    print("=" * 60)

    test_texts = [
        "hindi ko mantindihan yung example",
        "kc mabilis pa lng sya",
        "teh recieve is wierd",
    ]

    for text in test_texts:
        corrected = correct_text(text)
        print(f"  '{text}'")
        print(f"  -> '{corrected}'")
        print()
