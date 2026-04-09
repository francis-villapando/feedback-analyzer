"""
XLM-RoBERTa Tokenizer Module

Provides tokenization for XLM-RoBERTa models using SentencePiece tokenizer:
- XLM-RoBERTa base (12 layers, 768 hidden, 250K vocab)
- Attention-ready encoding
- Configurable max length (default: 128)
"""

from typing import Optional, Union
import torch


MODEL_NAME = "xlm-roberta-base"
DEFAULT_MAX_LENGTH = 128


def get_tokenizer(model_name: str = MODEL_NAME, use_fast: bool = True):
    """
    Load XLM-RoBERTa tokenizer.

    Args:
        model_name: Hugging Face model name
        use_fast: Use fast tokenizer (recommended)

    Returns:
        XLM-RoBERTa tokenizer instance
    """
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(model_name)


class XLMRobertaPreprocessor:
    """
    XLM-RoBERTa tokenizer wrapper for preprocessing feedback text.

    Provides:
    - SentencePiece tokenization
    - Attention mask generation
    - Token-level decoding
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        max_length: int = DEFAULT_MAX_LENGTH,
        padding: str = "max_length",
        truncation: bool = True,
    ):
        """
        Initialize XLM-RoBERTa preprocessor.

        Args:
            model_name: Hugging Face model name
            max_length: Maximum sequence length
            padding: Padding strategy ("max_length" or "longest")
            truncation: Whether to truncate sequences
        """
        self.model_name = model_name
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
        self.tokenizer = get_tokenizer(model_name)

    def tokenize(self, text: str) -> list:
        """
        Tokenize text into tokens.

        Args:
            text: Input text string

        Returns:
            List of token strings
        """
        return self.tokenizer.tokenize(text)

    def encode(
        self, text: str, return_tensors: Optional[str] = None
    ) -> Union[dict, torch.Tensor]:
        """
        Encode text to token IDs with attention mask.

        Args:
            text: Input text string
            return_tensors: Return tensors ("pt" for PyTorch)

        Returns:
            Dictionary with input_ids and attention_mask,
            or tensors if return_tensors specified
        """
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding=self.padding,
            truncation=self.truncation,
            return_tensors=return_tensors,
        )
        return encoding

    def encode_plus(self, text: str, return_tensors: Optional[str] = None) -> dict:
        """
        Encode text with full encoding details.

        Returns dictionary with:
        - input_ids: Token IDs
        - attention_mask: Attention mask (1 for real tokens, 0 for padding)
        - token_type_ids: Token type IDs (empty for XLM-RoBERTa)
        - special_tokens_mask: Mask for special tokens

        Args:
            text: Input text string
            return_tensors: Return tensors ("pt" for PyTorch)

        Returns:
            Full encoding dictionary
        """
        encoding = self.tokenizer.encode_plus(
            text,
            max_length=self.max_length,
            padding=self.padding,
            truncation=self.truncation,
            return_tensors=return_tensors,
            return_special_tokens_mask=True,
            return_token_type_ids=True,
        )
        return encoding

    def tokenize_and_encode(self, text: str, return_dict: bool = True) -> dict:
        """
        Full tokenization and encoding pipeline.

        Returns:
            Dictionary with:
            - input_ids: Tensor of token IDs
            - attention_mask: Tensor of attention mask
            - tokens: List of token strings
            - token_count: Number of tokens
            - truncated: Whether text was truncated
        """
        tokens = self.tokenize(text)
        encoding = self.encode(text, return_tensors="pt")

        return {
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"],
            "tokens": tokens,
            "token_count": len(tokens),
            "truncated": encoding["input_ids"][0][-1] == self.tokenizer.pad_token_id
            if self.truncation
            else False,
        }

    def decode(self, token_ids: Union[list, torch.Tensor]) -> str:
        """
        Decode token IDs back to text.

        Args:
            token_ids: List or tensor of token IDs

        Returns:
            Decoded text string
        """
        if isinstance(token_ids, torch.Tensor):
            token_ids = token_ids.tolist()

        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def decode_batch(self, token_ids_list: list) -> list:
        """
        Decode a batch of token IDs to text.

        Args:
            token_ids_list: List of token ID lists

        Returns:
            List of decoded text strings
        """
        return self.tokenizer.batch_decode(token_ids_list, skip_special_tokens=True)

    def get_vocab_size(self) -> int:
        """
        Get vocabulary size.

        Returns:
            Vocabulary size (250002 for xlm-roberta-base)
        """
        return len(self.tokenizer)

    def get_special_tokens(self) -> dict:
        """
        Get special token information.

        Returns:
            Dictionary with special token IDs
        """
        return {
            "pad_token": self.tokenizer.pad_token,
            "pad_token_id": self.tokenizer.pad_token_id,
            "unk_token": self.tokenizer.unk_token,
            "unk_token_id": self.tokenizer.unk_token_id,
            "bos_token": self.tokenizer.bos_token,
            "bos_token_id": self.tokenizer.bos_token_id,
            "eos_token": self.tokenizer.eos_token,
            "eos_token_id": self.tokenizer.eos_token_id,
        }


def tokenize_and_encode(
    text: str, model_name: str = MODEL_NAME, max_length: int = DEFAULT_MAX_LENGTH
) -> dict:
    """
    Convenience function for tokenization and encoding.

    Args:
        text: Input text string
        model_name: Hugging Face model name
        max_length: Maximum sequence length

    Returns:
        Dictionary with encoding results
    """
    preprocessor = XLMRobertaPreprocessor(model_name, max_length)
    return preprocessor.tokenize_and_encode(text)


if __name__ == "__main__":
    test_texts = [
        "I don't understand this concept, can you explain it more slowly?",
        "The examples are really helpful, thank you!",
        "https://example.com this is a test",
        "pls explain bc i dont get it",
    ]

    preprocessor = XLMRobertaPreprocessor()

    print("=" * 60)
    print("XLM-RoBERTa Tokenizer Test Results")
    print(f"Vocab size: {preprocessor.get_vocab_size()}")
    print("=" * 60)

    for text in test_texts:
        result = preprocessor.tokenize_and_encode(text)
        print(f"Input:  '{text}'")
        print(f"Tokens: {result['tokens'][:10]}...")  # Show first 10
        print(f"Count:  {result['token_count']}")
        print(f"Truncated: {result['truncated']}")
        print("-" * 60)
