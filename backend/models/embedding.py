"""
Embedding model for storing vector embeddings for RAG.
"""

from config.database import get_db_cursor
import json


class Embedding:
    """Model for managing vector embeddings for RAG system."""
    
    @staticmethod
    def create(project_id, content, embedding_vector, metadata=None):
        """
        Create an embedding record.
        
        Args:
            project_id: UUID of the project
            content: Text content that was embedded
            embedding_vector: Vector embedding (list of floats)
            metadata: Optional metadata dict
            
        Returns:
            dict: Created embedding object
        """
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Convert list to pgvector format
        vector_str = '[' + ','.join(map(str, embedding_vector)) + ']'
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO document_chunks (project_id, content, embedding, chunk_index, section_type, section_title, token_count, char_count)
                VALUES (%s, %s, %s::vector, %s, %s, %s, %s, %s)
                RETURNING id, project_id, content, chunk_index, section_type, section_title, created_at
            """, (
                project_id, 
                content, 
                vector_str,
                metadata.get('chunk_index', 0) if metadata else 0,
                metadata.get('section_type', '') if metadata else '',
                metadata.get('section_title', '') if metadata else '',
                metadata.get('token_count', len(content.split())) if metadata else len(content.split()),
                len(content)
            ))
            
            embedding = cursor.fetchone()
            result = dict(embedding)
            return result
    
    @staticmethod
    def find_similar(project_id, query_vector, limit=5):
        """
        Find most similar embeddings using cosine similarity.
        
        Args:
            project_id: UUID of the project
            query_vector: Query embedding vector
            limit: Number of results to return
            
        Returns:
            list: List of similar embeddings with similarity scores
        """
        # Convert query vector to pgvector format
        vector_str = '[' + ','.join(map(str, query_vector)) + ']'
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id,
                    project_id,
                    content,
                    section_type,
                    section_title,
                    chunk_index,
                    1 - (embedding <=> %s::vector) as similarity
                FROM document_chunks
                WHERE project_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (vector_str, project_id, vector_str, limit))
            
            results = cursor.fetchall()
            embeddings = [dict(row) for row in results]
            
            return embeddings
    
    @staticmethod
    def delete_by_project_id(project_id):
        """Delete all embeddings for a project."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM document_chunks WHERE project_id = %s", (project_id,))
            return cursor.rowcount
    
    @staticmethod
    def count_by_project_id(project_id):
        """Get count of embeddings for a project."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM document_chunks
                WHERE project_id = %s
            """, (project_id,))
            
            result = cursor.fetchone()
            return result['count'] if result else 0

