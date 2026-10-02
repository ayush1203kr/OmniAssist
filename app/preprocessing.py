"""Query preprocessing with NLTK and a safe stdlib fallback."""
import re

_FALLBACK_STOP_WORDS = {
    "a","an","and","are","as","at","be","but","by","can","do","for","from","has",
    "have","how","i","if","in","is","it","me","my","of","on","or","our","the",
    "their","this","to","was","we","what","when","where","which","who","will",
    "with","you","your",
}

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    _REQUIRED_DATA = {"punkt":"tokenizers/punkt","punkt_tab":"tokenizers/punkt_tab","stopwords":"corpora/stopwords"}
    for _package, _path in _REQUIRED_DATA.items():
        try:
            nltk.data.find(_path)
        except LookupError:
            nltk.download(_package, quiet=True)
    _STOP_WORDS = set(stopwords.words("english"))
    _TOKENIZER = word_tokenize
except Exception:
    _STOP_WORDS = _FALLBACK_STOP_WORDS
    _TOKENIZER = lambda text: re.findall(r"\b[\w]+\b", text)

def preprocess_query(query: str) -> dict:
    tokens = _TOKENIZER(query.lower())
    tokens = [token for token in tokens if token.isalnum()]
    keywords = [token for token in tokens if token not in _STOP_WORDS]
    return {
        "original_query": query,
        "cleaned_query": " ".join(keywords),
        "keywords": keywords,
    }
