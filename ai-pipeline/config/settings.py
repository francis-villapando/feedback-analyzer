"""
Configuration settings for the AI Pipeline.

This file contains all configuration in ONE place for easy management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DATA_DIR = DATA_DIR / "output"
MODELS_DIR = BASE_DIR / "models"

# Preprocessing Configuration
PREPROCESSING_CONFIG = {
    "lowercase": True,
    "remove_punctuation": True,
    "tokenize": True,
    "remove_stopwords": False,  # KEEP for codeswitching (Tagalog-English)
    "lemmatize": True,
    "spell_check": True,
}

# BERT Classification Configuration
BERT_CONFIG = {
    "model_name": "bert-base-uncased",
    "max_length": 128,
    "batch_size": 16,
    "use_rule_based_first": True,  # Apply rules before BERT
}

# BERTopic Configuration
BERTOPIC_CONFIG = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "nr_topics": "auto",
    "min_topic_size": 5,
    "verbose": True,
}

# RoBERTa Problem Detection Configuration
ROBERTA_PROBLEM_CONFIG = {
    "model_name": "roberta-base",
    "max_length": 128,
    "problem_categories": [
        "misconception_about_concept",
        "difficulty_understanding_explanation",
        "need_more_examples",
        "pace_too_fast",
        "pace_too_slow",
        "need_practical_application",
        "unclear_instruction",
        "technical_difficulty",
    ],
}

# RoBERTa Strategy Mapping Configuration
ROBERTA_STRATEGY_CONFIG = {
    "model_name": "roberta-base",
    "strategy_mappings": {
        "misconception_about_concept": [
            "Provide a concrete real-world example that illustrates this concept",
            "Create a simple diagram showing how this concept works",
            "Address this misconception directly by explaining why it is incorrect",
            "Use an analogy that relates to everyday life"
        ],
        "difficulty_understanding_explanation": [
            "Break down this explanation into 3 smaller parts and explain each separately",
            "Rephrase this concept using simpler words and shorter sentences",
            "Use a step-by-step approach with visual aids",
            "Ask students what specific part they do not understand"
        ],
        "need_more_examples": [
            "Provide 3 additional worked examples with complete solutions",
            "Show examples from different contexts or applications",
            "Create a practice problem similar to the one just presented",
            "Share links to online resources with more examples"
        ],
        "pace_too_fast": [
            "Pause for 30 seconds and ask if anyone has questions",
            "Repeat the last explanation more slowly",
            "Allow students to take notes before continuing",
            "Check for understanding by asking a quick question"
        ],
        "pace_too_slow": [
            "Proceed to the next topic: [suggest next topic]",
            "Offer optional advanced material for faster learners",
            "Introduce a related side topic that builds on current knowledge",
            "Provide additional optional exercises for practice"
        ],
        "need_practical_application": [
            "Demonstrate how this concept is used in real-world situations",
            "Show a practical example from everyday life",
            "Connect this to a real problem students might encounter",
            "Include a hands-on activity or exercise"
        ],
        "unclear_instruction": [
            "Restate the instruction in a different way",
            "Write the instruction on the screen",
            "Provide a checklist of steps to follow",
            "Give a completed example as reference"
        ],
        "technical_difficulty": [
            "Provide a step-by-step tutorial for using the technical tool",
            "Share a video tutorial demonstrating the process",
            "Offer alternative ways to accomplish the same task",
            "Schedule a brief one-on-one session to help"
        ],
    },
}

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Pipeline Configuration
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "16"))
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "128"))
