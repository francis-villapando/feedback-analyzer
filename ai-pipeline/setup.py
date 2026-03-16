"""
Setup script for AI Pipeline package.
"""

from setuptools import setup, find_packages

setup(
    name="ai-pipeline",
    version="1.0.0",
    description="AI Pipeline for Feedback Analyzer",
    author="System Architect",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "spacy>=3.6.0",
        "nltk>=3.8.0",
        "pyspellchecker>=0.7.0",
        "bertopic>=0.15.0",
        "sentence-transformers>=2.2.0",
        "umap-learn>=0.5.3",
        "hdbscan>=0.8.29",
        "accelerate>=0.20.0",
        "supabase>=2.0.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0",
        "scikit-learn>=1.3.0",
        "joblib>=1.3.0",
        "ipython>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
)
