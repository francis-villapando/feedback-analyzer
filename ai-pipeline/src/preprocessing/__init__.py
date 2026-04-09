"""
Preprocessing Module

Implemented techniques:
- Noise cleaning (URLs, hashtags, HTML tags, emojis)
- Vowel normalization (elongated words)
- Abbreviation expansion
- Spelling correction
- Tokenization (including subword)
- XLM-RoBERTa encoding with truncation (128 tokens)
"""

from typing import Optional

from .noise_cleaner import (
    clean_noise,
    remove_urls,
    remove_hashtags,
    remove_mentions,
    remove_html_tags,
    remove_emojis,
    remove_repeating_chars,
)

from .vowel_normalizer import (
    normalize_elongation,
    normalize_vowels,
    normalize_text,
)

from .abbreviation_expander import (
    expand_abbreviation,
    expand_abbreviations,
    expand_abbreviations_preserve_case,
    add_abbreviation,
    remove_abbreviation,
    get_abbreviation,
)

from .text_cleaner import (
    clean_text,
)

from .tokenizer import (
    nltk_tokenize,
    simple_tokenize,
    spacy_tokenize,
    tokenize,
    detokenize,
)

from .spelling_corrector import (
    create_spell_checker,
    get_spell_checker,
    add_to_dictionary,
    correct_word,
    correct_text,
    correct_tokens,
    get_suggestions,
)

from .xlm_roberta_tokenizer import (
    XLMRobertaPreprocessor,
    tokenize_and_encode,
    get_tokenizer,
)


MAX_TOKEN_LENGTH = 128


def preprocess(
    text: str,
    tokenize_flag: bool = True,
    spell_check: bool = True,
    expand_abbrevs: bool = True,
    normalize_elongation: bool = True,
    remove_hashtags: bool = True,
    remove_mentions: bool = True,
    remove_html: bool = True,
    remove_emojis: bool = True,
    use_xlm_roberta: bool = False,
) -> dict:
    """
    Full preprocessing pipeline for a single text.

    Pipeline:
    1. Noise cleaning (URLs, hashtags, HTML, emojis, mentions)
    2. Vowel normalization (elongated words)
    3. Abbreviation expansion
    4. Clean text (special chars, whitespace)
    5. Tokenization
    6. Spell correction
    7. XLM-RoBERTa encoding with truncation (128 tokens)

    Args:
        text: Input text string
        tokenize_flag: Whether to tokenize
        spell_check: Whether to check spelling
        expand_abbrevs: Whether to expand abbreviations
        normalize_elongation: Whether to normalize elongated words
        remove_hashtags: Whether to remove hashtags
        remove_mentions: Whether to remove @mentions
        remove_html: Whether to remove HTML tags
        remove_emojis: Whether to remove emojis
        use_xlm_roberta: Whether to return XLM-RoBERTa encoding

    Returns:
        Dictionary with:
        - original: Original input text
        - cleaned_text: Fully processed text
        - tokens: List of tokens
        - encoding: XLM-RoBERTa encoding (if use_xlm_roberta=True)
        - metadata: Processing information
    """
    result = {
        "original": text,
        "cleaned_text": "",
        "tokens": [],
        "encoding": None,
        "metadata": {
            "tokenize": tokenize_flag,
            "spell_check": spell_check,
            "expand_abbreviations": expand_abbrevs,
            "normalize_elongation": normalize_elongation,
            "remove_hashtags": remove_hashtags,
            "remove_mentions": remove_mentions,
            "remove_html": remove_html,
            "remove_emojis": remove_emojis,
            "max_tokens": MAX_TOKEN_LENGTH,
        },
    }

    if not text:
        return result

    # Step 1: Noise cleaning (URLs, hashtags, HTML, emojis, mentions)
    text = clean_noise(
        text,
        remove_urls_flag=True,
        remove_hashtags_flag=remove_hashtags,
        remove_mentions_flag=remove_mentions,
        remove_html_tags_flag=remove_html,
        remove_emojis_flag=remove_emojis,
        normalize_elongation_flag=False,  # Handle separately
    )

    # Step 2: Vowel normalization (elongated words)
    if normalize_elongation:
        from .vowel_normalizer import normalize_elongation as norm_elong

        text = norm_elong(text)

    # Step 3: Expand abbreviations
    if expand_abbrevs:
        text = expand_abbreviations(text)

    # Step 4: Clean text
    text = clean_text(
        text,
        remove_urls_flag=False,
    )

    result["cleaned_text"] = text  # Store cleaned text before tokenization

    # Step 5: Tokenization
    if tokenize_flag:
        tokens = tokenize(text)
    else:
        tokens = simple_tokenize(text)

    # Step 6: Spell correction
    if spell_check:
        tokens = correct_tokens(tokens)

    result["tokens"] = tokens

    # Step 7: XLM-RoBERTa encoding with truncation
    if use_xlm_roberta:
        preprocessor = XLMRobertaPreprocessor(max_length=MAX_TOKEN_LENGTH)
        result["encoding"] = preprocessor.tokenize_and_encode(result["cleaned_text"])

    return result


def preprocess_for_model(
    text: str,
    max_tokens: int = MAX_TOKEN_LENGTH,
) -> dict:
    """
    Preprocess text specifically for AI model input.

    Returns encoding ready for XLM-RoBERTa model.

    Args:
        text: Input text string
        max_tokens: Maximum token length (default: 128)

    Returns:
        Dictionary with:
        - original: Original input
        - cleaned_text: Preprocessed text
        - encoding: Dict with input_ids, attention_mask, tokens
    """
    preprocessed = preprocess(
        text,
        tokenize_flag=True,
        spell_check=True,
        expand_abbrevs=True,
        normalize_elongation=True,
        remove_hashtags=True,
        remove_mentions=True,
        remove_html=True,
        remove_emojis=True,
        use_xlm_roberta=False,
    )

    preprocessor = XLMRobertaPreprocessor(max_length=max_tokens)
    encoding = preprocessor.tokenize_and_encode(preprocessed["cleaned_text"])

    return {
        "original": text,
        "cleaned_text": preprocessed["cleaned_text"],
        "tokens": preprocessed["tokens"],
        "input_ids": encoding["input_ids"],
        "attention_mask": encoding["attention_mask"],
        "token_count": encoding["token_count"],
        "truncated": encoding["truncated"],
    }


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
__version__ = "2.0.0"
