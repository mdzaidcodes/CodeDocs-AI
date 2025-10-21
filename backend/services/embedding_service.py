"""
Embedding service using OpenAI for creating vector embeddings.
"""

from openai import OpenAI
from config.settings import Config


class EmbeddingService:
    """Service for creating vector embeddings using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        # Initialize OpenAI client with only API key (no proxies)
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=60.0,  # 60 second timeout
            max_retries=2
        )
        self.model = Config.OPENAI_EMBEDDING_MODEL
    
    def create_embedding(self, text):
        """
        Create embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector (list of floats)
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Clean text
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided")
            
            # Truncate if too long (OpenAI has token limits)
            if len(text) > 8000:
                text = text[:8000]
            
            # Create embedding
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            # Extract embedding vector
            embedding = response.data[0].embedding
            return embedding
        
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    def create_embeddings_batch(self, texts):
        """
        Create embeddings for multiple texts in batch.
        
        Args:
            texts: List of text strings
            
        Returns:
            list: List of embedding vectors
        """
        try:
            # Clean and truncate texts
            clean_texts = []
            for text in texts:
                text = text.strip()
                if text:
                    if len(text) > 8000:
                        text = text[:8000]
                    clean_texts.append(text)
            
            if not clean_texts:
                return []
            
            # Create embeddings in batch
            response = self.client.embeddings.create(
                model=self.model,
                input=clean_texts
            )
            
            # Extract embedding vectors
            embeddings = [item.embedding for item in response.data]
            return embeddings
        
        except Exception as e:
            print(f"OpenAI batch embedding error: {e}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
    
    def embed_code_file(self, filename, content):
        """
        Create embedding for a code file with metadata.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            dict: {text: formatted text, embedding: vector, metadata: info}
        """
        # Format text for embedding
        formatted_text = f"File: {filename}\n\n{content}"
        
        # Create embedding
        embedding = self.create_embedding(formatted_text)
        
        # Prepare metadata
        metadata = {
            'filename': filename,
            'type': 'code_file'
        }
        
        return {
            'text': formatted_text,
            'embedding': embedding,
            'metadata': metadata
        }
    
    def embed_documentation(self, section_name, content):
        """
        Create embedding for a documentation section.
        
        Args:
            section_name: Name of the section
            content: Section content
            
        Returns:
            dict: {text: formatted text, embedding: vector, metadata: info}
        """
        # Format text for embedding
        formatted_text = f"Documentation - {section_name}\n\n{content}"
        
        # Create embedding
        embedding = self.create_embedding(formatted_text)
        
        # Prepare metadata
        metadata = {
            'section': section_name,
            'type': 'documentation'
        }
        
        return {
            'text': formatted_text,
            'embedding': embedding,
            'metadata': metadata
        }

