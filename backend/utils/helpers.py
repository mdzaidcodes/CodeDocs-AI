"""
Helper utility functions.
"""

import uuid
from datetime import datetime
import re


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


def format_datetime(dt):
    """
    Format datetime to ISO 8601 string.
    
    Args:
        dt: datetime object
        
    Returns:
        str: ISO formatted datetime string
    """
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


def parse_github_url(url):
    """
    Parse GitHub URL to extract owner and repo name.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        tuple: (owner, repo_name) or (None, None) if invalid
    """
    if not url:
        return None, None
    
    # Remove trailing slash and .git
    url = url.rstrip('/').rstrip('.git')
    
    # Match github.com URLs
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1), match.group(2)
    
    return None, None


def detect_language(files):
    """
    Detect primary programming language from file list.
    
    Args:
        files: List of file paths
        
    Returns:
        str: Primary language or 'Multiple'
    """
    extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    
    # Count file extensions
    counts = {}
    for file_path in files:
        ext = file_path[file_path.rfind('.'):].lower() if '.' in file_path else ''
        if ext in extensions:
            lang = extensions[ext]
            counts[lang] = counts.get(lang, 0) + 1
    
    if not counts:
        return 'Unknown'
    
    # Return most common language
    max_lang = max(counts, key=counts.get)
    
    # If multiple languages with similar counts, return 'Multiple'
    max_count = counts[max_lang]
    similar_langs = [l for l, c in counts.items() if c > max_count * 0.7 and l != max_lang]
    
    if similar_langs:
        return 'Multiple'
    
    return max_lang


def chunk_text(text, max_chunk_size=1000, overlap=100):
    """
    Split text into overlapping chunks for embedding.
    
    Args:
        text: Text to split
        max_chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters
        
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # If not the last chunk, try to break at sentence or word boundary
        if end < len(text):
            # Look for sentence boundary
            sentence_end = text.rfind('. ', start, end)
            if sentence_end > start + max_chunk_size // 2:
                end = sentence_end + 1
            else:
                # Look for word boundary
                space = text.rfind(' ', start, end)
                if space > start + max_chunk_size // 2:
                    end = space
        
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

