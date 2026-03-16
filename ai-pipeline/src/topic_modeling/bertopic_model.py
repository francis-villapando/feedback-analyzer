"""
BERTopic Model Module

This module provides topic modeling using BERTopic for identifying
themes in pedagogical feedback (unsupervised learning).

BERTopic uses:
- Sentence transformers for embeddings
- UMAP for dimensionality reduction
- HDBSCAN for clustering
- c-TF-IDF for topic representation

Note: This is for Phase 1 (Zero-Shot Development). Topics will be
automatically discovered from the data.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Import configuration
try:
    from config.settings import BERTOPIC_CONFIG
except ImportError:
    BERTOPIC_CONFIG = {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "nr_topics": "auto",
        "min_topic_size": 5,
        "verbose": True,
    }

# Topic modeling result dataclass
@dataclass
class TopicResult:
    """Result from topic modeling."""
    topic_id: int
    topic_words: List[str]
    topic_label: str
    document_count: int


@dataclass
class DocumentTopicResult:
    """Result for a single document."""
    text: str
    topic_id: int
    topic_label: str
    topic_probability: float


# Global BERTopic model instance
_bertopic_model = None
_embedding_model = None


def load_embedding_model():
    """
    Load the sentence transformer embedding model.
    
    Returns:
        SentenceTransformer model
    """
    global _embedding_model
    
    if _embedding_model is not None:
        return _embedding_model
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = BERTOPIC_CONFIG.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name}...")
        
        _embedding_model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully!")
        return _embedding_model
        
    except ImportError as e:
        raise ImportError(
            "sentence-transformers library not installed. "
            "Run: pip install sentence-transformers"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to load embedding model: {e}"
        ) from e


def create_bertopic_model():
    """
    Create and configure a BERTopic model.
    
    Returns:
        Configured BERTopic model
    """
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        
        # Get configuration
        embedding_model_name = BERTOPIC_CONFIG.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        nr_topics = BERTOPIC_CONFIG.get("nr_topics", "auto")
        min_topic_size = BERTOPIC_CONFIG.get("min_topic_size", 5)
        verbose = BERTOPIC_CONFIG.get("verbose", True)
        
        print("Configuring BERTopic model...")
        
        # Load embedding model
        embedding_model = SentenceTransformer(embedding_model_name)
        
        # Create BERTopic with configuration
        # Using default parameters that work well for short texts
        topic_model = BERTopic(
            embedding_model=embedding_model,
            nr_topics=nr_topics,
            min_topic_size=min_topic_size,
            verbose=verbose,
            # UMAP parameters (dimensionality reduction)
            umap_model=None,  # Will use defaults
            # HDBSCAN parameters (clustering)
            hdbscan_model=None,  # Will use defaults
            # c-TF-IDF parameters
            vectorizer_model=None,  # Will use defaults
            # Representation parameters
            representation_model=None,  # Will use defaults
        )
        
        print("BERTopic model configured successfully!")
        return topic_model
        
    except ImportError as e:
        raise ImportError(
            "bertopic library not installed. "
            "Run: pip install bertopic"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to create BERTopic model: {e}"
        ) from e


def load_model():
    """
    Load the BERTopic model (lazy loading).
    
    Returns:
        BERTopic model
    """
    global _bertopic_model
    
    if _bertopic_model is not None:
        return _bertopic_model
    
    _bertopic_model = create_bertopic_model()
    return _bertopic_model


def fit_topics(texts: List[str], docs: Optional[List[str]] = None) -> Tuple:
    """
    Fit BERTopic model on texts and discover topics.
    
    Args:
        texts: List of input texts
        docs: Optional preprocessed documents (if different from texts)
        
    Returns:
        Tuple of (topics, probabilities)
    """
    topic_model = load_model()
    
    if not texts:
        return [], []
    
    # Use docs if provided, otherwise use texts
    documents = docs if docs is not None else texts
    
    print(f"Fitting BERTopic on {len(texts)} documents...")
    
    topics, probs = topic_model.fit_transform(documents)
    
    print(f"Discovered {len(set(topics)) - (1 if -1 in topics else 0)} topics")
    
    return topics, probs


def get_topic_info():
    """
    Get information about discovered topics.
    
    Returns:
        DataFrame with topic information
    """
    topic_model = load_model()
    return topic_model.get_topic_info()


def get_topic(topic_id: int) -> List[Tuple[str, float]]:
    """
    Get words for a specific topic.
    
    Args:
        topic_id: Topic ID
        
    Returns:
        List of (word, weight) tuples
    """
    topic_model = load_model()
    return topic_model.get_topic(topic_id)


def get_document_topic(text: str) -> DocumentTopicResult:
    """
    Get topic for a single document.
    
    Args:
        text: Input text
        
    Returns:
        DocumentTopicResult
    """
    topic_model = load_model()
    
    topics, probs = topic_model.transform([text])
    
    topic_id = topics[0]
    prob = probs[0] if probs else 0.0
    
    # Get topic label
    if topic_id == -1:
        topic_label = "outlier"
    else:
        topic_words = topic_model.get_topic(topic_id)
        if topic_words:
            topic_label = ", ".join([word for word, _ in topic_words[:3]])
        else:
            topic_label = f"topic_{topic_id}"
    
    return DocumentTopicResult(
        text=text,
        topic_id=topic_id,
        topic_label=topic_label,
        topic_probability=prob
    )


def assign_topics(texts: List[str]) -> List[DocumentTopicResult]:
    """
    Assign topics to a batch of texts.
    
    Args:
        texts: List of input texts
        
    Returns:
        List of DocumentTopicResult
    """
    if not texts:
        return []
    
    topic_model = load_model()
    
    topics, probs = topic_model.transform(texts)
    
    results = []
    for i, text in enumerate(texts):
        topic_id = topics[i]
        prob = probs[i] if probs is not None and len(probs) > i else 0.0
        
        # Get topic label
        if topic_id == -1:
            topic_label = "outlier"
        else:
            topic_words = topic_model.get_topic(topic_id)
            if topic_words:
                topic_label = ", ".join([word for word, _ in topic_words[:3]])
            else:
                topic_label = f"topic_{topic_id}"
        
        results.append(DocumentTopicResult(
            text=text,
            topic_id=topic_id,
            topic_label=topic_label,
            topic_probability=prob
        ))
    
    return results


def filter_by_topic(
    texts: List[str],
    topic_ids: Optional[List[int]] = None,
    min_probability: float = 0.5
) -> Tuple[List[str], List[DocumentTopicResult]]:
    """
    Filter texts by specific topics.
    
    Args:
        texts: List of input texts
        topic_ids: List of topic IDs to keep (None = keep all non-outlier)
        min_probability: Minimum topic probability
        
    Returns:
        Tuple of (filtered_texts, all_results)
    """
    results = assign_topics(texts)
    
    filtered = []
    for result in results:
        if topic_ids is not None:
            # Keep only specified topics
            if result.topic_id in topic_ids and result.topic_probability >= min_probability:
                filtered.append(result.text)
        else:
            # Keep all non-outliers
            if result.topic_id != -1 and result.topic_probability >= min_probability:
                filtered.append(result.text)
    
    return filtered, results


def get_topic_statistics(results: List[DocumentTopicResult]) -> Dict:
    """
    Get statistics from topic assignment results.
    
    Args:
        results: List of DocumentTopicResult
        
    Returns:
        Dictionary with statistics
    """
    total = len(results)
    if total == 0:
        return {"total": 0}
    
    # Count documents per topic
    topic_counts = {}
    outlier_count = 0
    total_probability = 0.0
    
    for result in results:
        if result.topic_id == -1:
            outlier_count += 1
        else:
            topic_counts[result.topic_id] = topic_counts.get(result.topic_id, 0) + 1
        total_probability += result.topic_probability
    
    # Get unique topics
    unique_topics = len(topic_counts)
    
    return {
        "total": total,
        "unique_topics": unique_topics,
        "outliers": outlier_count,
        "outlier_percentage": (outlier_count / total) * 100 if total > 0 else 0,
        "topic_counts": topic_counts,
        "average_probability": total_probability / total if total > 0 else 0,
    }


def visualize_topics(save_path: Optional[str] = None):
    """
    Visualize discovered topics.
    
    Args:
        save_path: Optional path to save the visualization
        
    Returns:
        matplotlib figure
    """
    topic_model = load_model()
    
    # Create visualization
    fig = topic_model.visualize_topics()
    
    if save_path:
        fig.write_html(save_path)
        print(f"Visualization saved to {save_path}")
    
    return fig


def visualize_hierarchy(save_path: Optional[str] = None):
    """
    Visualize topic hierarchy.
    
    Args:
        save_path: Optional path to save the visualization
        
    Returns:
        matplotlib figure
    """
    topic_model = load_model()
    
    fig = topic_model.visualize_hierarchy()
    
    if save_path:
        fig.write_html(save_path)
        print(f"Hierarchy visualization saved to {save_path}")
    
    return fig


# Test function
if __name__ == "__main__":
    # Sample pedagogical feedback messages
    sample_messages = [
        # Topic: Understanding
        "I don't understand this concept",
        "Can you explain more clearly?",
        "I'm confused about the formula",
        "This is hard to understand",
        "Need more explanation please",
        
        # Topic: Examples
        "Can you give more examples?",
        "Need another example",
        "Like what you did before",
        "Example would help",
        "More examples please",
        
        # Topic: Pace
        "Too fast please slow down",
        "The pace is too quick",
        "Can you go slower?",
        "Please wait a bit",
        "Slow down please",
        
        # Topic: Gratitude
        "Thank you for the lesson",
        "Salamat po sa lesson",
        "Maraming salamat",
        "Thanks for explaining",
        "Appreciate the help",
        
        # Topic: Questions
        "I have a question",
        "May question po ako",
        "What about this?",
        "Question about the topic",
        "Ask something please",
    ]
    
    print("=" * 70)
    print("BERTopic Model Test")
    print("=" * 70)
    print(f"Testing with {len(sample_messages)} sample messages")
    print()
    
    # Fit topics
    topics, probs = fit_topics(sample_messages)
    
    # Get topic info
    print()
    print("Topic Information:")
    topic_info = get_topic_info()
    print(topic_info)
    
    # Assign topics to documents
    print()
    print("Document Topics:")
    results = assign_topics(sample_messages)
    
    for result in results:
        print(f"Text: {result.text[:50]}...")
        print(f"  Topic: {result.topic_id} ({result.topic_label})")
        print(f"  Probability: {result.topic_probability:.3f}")
    
    # Get statistics
    print()
    stats = get_topic_statistics(results)
    print("Statistics:")
    print(f"  Total documents: {stats['total']}")
    print(f"  Unique topics: {stats['unique_topics']}")
    print(f"  Outliers: {stats['outliers']} ({stats['outlier_percentage']:.1f}%)")
    print(f"  Average probability: {stats['average_probability']:.3f}")
    
    print()
    print("BERTopic test completed!")
