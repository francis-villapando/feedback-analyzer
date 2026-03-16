"""
Topic Modeling Module

This module provides topic modeling functionality using BERTopic:
- Automatic topic discovery from feedback
- Document-topic assignment
- Topic visualization

Main Functions:
- fit_topics(): Discover topics from texts
- assign_topics(): Assign topics to documents
- get_topic_info(): Get topic information
- visualize_topics(): Create topic visualization
"""

# BERTopic exports
from .bertopic_model import (
    TopicResult,
    DocumentTopicResult,
    load_embedding_model,
    load_model,
    fit_topics,
    get_topic_info,
    get_topic,
    get_document_topic,
    assign_topics,
    filter_by_topic,
    get_topic_statistics,
    visualize_topics,
    visualize_hierarchy,
)


__version__ = "1.0.0"
