"""NLTK preprocessing: lowercase, tokenize, remove stopwords and punctuation,
extract useful keywords.

This runs before the agent so the LLM sees a pruned, noise-free version of the
user query (and so the keywords can be shown in the API response).
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# The small NLTK resources we need are downloaded once and cached on disk.
_REQUIRED_DATA = {
    "punkt": "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",  # newer NLTK versions use punkt_tab
    "stopwords": "corpora/stopwords",
}
for _package, _path in _REQUIRED_DATA.items():
    try:
        nltk.data.find(_path)
    except LookupError:
        nltk.download(_package, quiet=True)

_STOP_WORDS = set(stopwords.words("english"))


def preprocess_query(query: str) -> dict:
    """Clean a raw user query and extract its useful keywords.

    Example:
        >>> preprocess_query("Can I get a refund if I cancel my order?")
        {"original_query": "Can I get a refund if I cancel my order?",
         "cleaned_query": "get refund cancel order",
         "keywords": ["get", "refund", "cancel", "order"]}
    """
    tokens = word_tokenize(query.lower())                   # 1. lowercase + tokenize
    tokens = [token for token in tokens if token.isalnum()]  # 2. drop punctuation
    keywords = [token for token in tokens if token not in _STOP_WORDS]  # 3. drop stopwords

    return {
        "original_query": query,
        "cleaned_query": " ".join(keywords),
        "keywords": keywords,
    }
