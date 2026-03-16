"""
Spelling Corrector Module

Provides spelling correction functionality using pyspellchecker.
Also includes custom corrections for common errors in codeswitched text.
"""

from typing import List, Set, Optional
from spellchecker import SpellChecker


# Custom corrections for common errors in Tagalog-English codeswitching
# These are corrections that the general spellchecker might miss
CUSTOM_CORRECTIONS = {
    # Common Filipino/Tagalog words (often misspelled by English keyboards)
    'po': 'po',           # polite particle
    'opo': 'opo',         # yes (polite)
    'hindi': 'hindi',     # no/not
    'salamat': 'salamat', # thanks
    'puwede': 'pwede',    # can/allowed (variation)
    'pwede': 'pwede',    # can/allowed
    'magkano': 'magkano', # how much
    'ilan': 'ilan',       # how many
    'paano': 'paano',     # how
    'bakit': 'bakit',     # why
    'saan': 'saan',       # where
    'kailan': 'kailan',   # when
    'naman': 'naman',     # again/now
    
    # Common chat abbreviations
    'thx': 'thanks',
    'thnx': 'thanks',
    'tnx': 'thanks',
    'ty': 'thank you',
    'pls': 'please',
    'plz': 'please',
    'bc': 'because',
    'bcos': 'because',
    'bcoz': 'because',
    'wht': 'what',
    'wat': 'what',
    'hw': 'how',
    'hv': 'have',
    'dnt': "don't",
    'cnt': "can't",
    'wnt': "want",
    'gonna': 'going to',
    'gotta': 'got to',
    'wanna': 'want to',
    'kinda': 'kind of',
    'sorta': 'sort of',
    'outta': 'out of',
    'lemme': 'let me',
    'gimme': 'give me',
    'dunno': "don't know",
    'idk': "I don't know",
    'imo': 'in my opinion',
    'imho': 'in my humble opinion',
    
    # Common errors
    'teh': 'the',
    'recieve': 'receive',
    'wierd': 'weird',
    'occured': 'occurred',
    'seperate': 'separate',
    'definite': 'definitely',
    'accomodate': 'accommodate',
    'occurence': 'occurrence',
    'untill': 'until',
    'begining': 'beginning',
    'beleive': 'believe',
    'concious': 'conscious',
    'embarass': 'embarrass',
    'enviroment': 'environment',
    'goverment': 'government',
    'independant': 'independent',
    'neccessary': 'necessary',
    'occassion': 'occasion',
    'priviledge': 'privilege',
    'recomend': 'recommend',
    'refered': 'referred',
    'successful': 'successful',
    'tommorow': 'tomorrow',
    'tue': 'Tuesday',
    'wed': 'Wednesday',
    'thu': 'Thursday',
    'fri': 'Friday',
    'sat': 'Saturday',
    'sun': 'Sunday',
    'mon': 'Monday',
    
    # Numbers in words
    'onee': 'one',
    'twoo': 'two',
    'tree': 'three',
    'fore': 'four',
    'fiv': 'five',
    'sixx': 'six',
    'sevn': 'seven',
    'ate': 'eight',
    'nien': 'nine',
    'tenn': 'ten',
}


def create_spell_checker(
    language: str = 'en',
    distance: int = 2
) -> SpellChecker:
    """
    Create a spell checker instance.
    
    Args:
        language: Language code (default: 'en' for English)
        distance: Maximum edit distance to consider (default: 2)
        
    Returns:
        SpellChecker instance
    """
    checker = SpellChecker(language=language, distance=distance)
    return checker


# Global spell checker instance
_spell_checker = None


def get_spell_checker() -> SpellChecker:
    """
    Get the global spell checker instance.
    
    Returns:
        SpellChecker instance
    """
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
    
    First checks custom corrections, then falls back to 
    the general spell checker.
    
    Args:
        word: Word to correct
        
    Returns:
        Corrected word
    """
    if not word:
        return ""
    
    word_lower = word.lower()
    
    # First check custom corrections
    if word_lower in CUSTOM_CORRECTIONS:
        correction = CUSTOM_CORRECTIONS[word_lower]
        # Preserve original case pattern
        if word.isupper():
            return correction.upper()
        elif word[0].isupper() if word else False:
            return correction.capitalize()
        return correction
    
    # Then check spell checker
    checker = get_spell_checker()
    
    # If word is in dictionary, return as is
    if word_lower in checker:
        return word
    
    # Get the most likely correction
    correction = checker.correction(word_lower)
    
    if correction is None:
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
    
    Note: This is a simple implementation that just corrects
    each word. It doesn't handle all edge cases.
    
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
    checker = get_spell_checker()
    
    # First check custom corrections
    suggestions = []
    word_lower = word.lower()
    
    if word_lower in CUSTOM_CORRECTIONS:
        suggestions.append(CUSTOM_CORRECTIONS[word_lower])
    
    # Get suggestions from spell checker
    checker_suggestions = list(checker.suggest(word_lower))[:n]
    suggestions.extend(checker_suggestions)
    
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
    test_words = [
        # English errors
        "teh", "recieve", "wierd",
        # Chat abbreviations
        "thx", "pls", "idk", "gonna",
        # Tagalog words
        "po", "pwede", "salamat",
        # Correct words
        "hello", "world", "thanks",
    ]
    
    print("=" * 60)
    print("Spelling Corrector Test Results")
    print("=" * 60)
    
    for word in test_words:
        corrected = correct_word(word)
        suggestions = get_suggestions(word, 3)
        print(f"  {word} -> {corrected}")
        if suggestions and corrected != word:
            print(f"    Suggestions: {suggestions}")
    
    # Test full text correction
    print("\nText correction:")
    test_text = "thx 4 teh help wth teh proejct"
    corrected = correct_text(test_text)
    print(f"  '{test_text}' -> '{corrected}'")
