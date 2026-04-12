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
    "tokenize": True,
    "spell_check": True,
}
# NOTE: Old local-model configurations (BERT, BERTopic, RoBERTa) have been
# deprecated in favor of an external MCP-backed model server. Keep these
# entries removed to avoid accidental usage of local models.

# MCP (Model Context Protocol) Configuration - points to the external model
# server (e.g., a Hugging Face Spaces or other MCP server) that exposes
# classification, ABSA, and strategy endpoints.
MCP_CONFIG = {
    "server_url": os.getenv("MCP_SERVER_URL", ""),
    "api_key": os.getenv("MCP_API_KEY", ""),
    "timeout_seconds": int(os.getenv("MCP_TIMEOUT_SECONDS", "10")),
}

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Pipeline Configuration
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "16"))
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "128"))
