"""
RAG (Retrieval-Augmented Generation) service for intelligent code queries.
Combines vector similarity search with Claude AI.
"""

from services.embedding_service import EmbeddingService
from services.claude_service import ClaudeService
from models.embedding import Embedding


class RAGService:
    """Service for RAG-powered question answering."""
    
    def __init__(self):
        """Initialize RAG service with embedding and Claude services."""
        self.embedding_service = EmbeddingService()
        self.claude_service = ClaudeService()
    
    def answer_question(self, project_id, question):
        """
        Answer a question about a project using RAG.
        
        Process:
        1. Create embedding for the question
        2. Find similar content from project embeddings
        3. Use retrieved content as context for Claude
        4. Generate answer with Claude
        
        Args:
            project_id: UUID of the project
            question: User's question
            
        Returns:
            dict: {message: answer, sources: list of source files}
        """
        try:
            # Step 1: Create embedding for question
            question_embedding = self.embedding_service.create_embedding(question)
            
            # Step 2: Find similar content (top 5 most relevant)
            similar_embeddings = Embedding.find_similar(
                project_id,
                question_embedding,
                limit=5
            )
            
            if not similar_embeddings:
                return {
                    'message': "I don't have enough context about this project to answer your question. Please make sure the project has been processed and documentation has been generated.",
                    'sources': []
                }
            
            # Step 3: Build context from retrieved content
            context_parts = []
            sources = []
            
            for emb in similar_embeddings:
                context_parts.append(f"--- Content (similarity: {emb['similarity']:.2f}) ---\n{emb['content']}\n")
                
                # Extract source from section info
                if emb.get('section_title'):
                    sources.append(f"Documentation: {emb['section_title']}")
                elif emb.get('section_type'):
                    sources.append(f"Documentation: {emb['section_type']}")
            
            context = "\n".join(context_parts)
            
            # Step 4: Generate answer with Claude
            answer = self.claude_service.answer_question(question, context)
            
            # Remove duplicates from sources
            sources = list(set(sources))
            
            return {
                'message': answer,
                'sources': sources
            }
        
        except Exception as e:
            print(f"RAG error: {e}")
            return {
                'message': "Sorry, I encountered an error while processing your question. Please try again.",
                'sources': []
            }
    
    def index_code_files(self, project_id, code_files):
        """
        Create embeddings for code files and store them.
        
        Args:
            project_id: UUID of the project
            code_files: Dict of {filename: content}
            
        Returns:
            int: Number of embeddings created
        """
        count = 0
        chunk_index = 0  # Track unique index for each file
        
        for filename, content in code_files.items():
            try:
                # Skip if content is too short or empty
                if not content or len(content) < 50:
                    continue
                
                # Create embedding for file
                result = self.embedding_service.embed_code_file(filename, content)
                
                # Add unique chunk_index to metadata
                metadata = result.get('metadata', {})
                metadata['chunk_index'] = chunk_index
                chunk_index += 1
                
                # Store embedding
                Embedding.create(
                    project_id=project_id,
                    content=result['text'],
                    embedding_vector=result['embedding'],
                    metadata=metadata
                )
                
                count += 1
            
            except Exception as e:
                print(f"Error indexing file {filename}: {e}")
                continue
        
        return count
    
    def index_documentation(self, project_id, sections):
        """
        Create embeddings for documentation sections.
        
        Args:
            project_id: UUID of the project
            sections: List of section objects OR Dict of {section_name: content} (backwards compatible)
            
        Returns:
            int: Number of embeddings created
        """
        count = 0
        chunk_index = 1000  # Start from 1000 to avoid conflicts with code files
        
        # Handle both list (new format) and dict (old format)
        if isinstance(sections, list):
            # New format: list of section objects
            for section in sections:
                try:
                    section_name = section.get('title', 'Unknown Section')
                    content = section.get('content', '')
                    
                    # Skip if content is too short or empty
                    if not content or len(content) < 50:
                        continue
                    
                    # Create embedding for section
                    result = self.embedding_service.embed_documentation(section_name, content)
                    
                    # Add unique chunk_index and section metadata
                    metadata = result.get('metadata', {})
                    metadata['chunk_index'] = chunk_index
                    metadata['section_type'] = section.get('type', '')
                    metadata['section_title'] = section_name
                    chunk_index += 1
                    
                    # Store embedding
                    Embedding.create(
                        project_id=project_id,
                        content=result['text'],
                        embedding_vector=result['embedding'],
                        metadata=metadata
                    )
                    
                    count += 1
                
                except Exception as e:
                    print(f"Error indexing section {section_name}: {e}")
                    continue
        else:
            # Old format: dict of section_name: content
            for section_name, content in sections.items():
                try:
                    # Skip if content is too short or empty
                    if not content or len(content) < 50:
                        continue
                    
                    # Create embedding for section
                    result = self.embedding_service.embed_documentation(section_name, content)
                    
                    # Add unique chunk_index to metadata
                    metadata = result.get('metadata', {})
                    metadata['chunk_index'] = chunk_index
                    chunk_index += 1
                    
                    # Store embedding
                    Embedding.create(
                        project_id=project_id,
                        content=result['text'],
                        embedding_vector=result['embedding'],
                        metadata=metadata
                    )
                    
                    count += 1
                
                except Exception as e:
                    print(f"Error indexing section {section_name}: {e}")
                    continue
        
        return count
    
    def reindex_project(self, project_id, code_files, documentation_sections):
        """
        Reindex entire project (delete old embeddings and create new ones).
        
        Args:
            project_id: UUID of the project
            code_files: Dict of {filename: content}
            documentation_sections: Dict of {section_name: content}
            
        Returns:
            int: Total number of embeddings created
        """
        # Delete existing embeddings
        Embedding.delete_by_project_id(project_id)
        
        # Index code files
        code_count = self.index_code_files(project_id, code_files)
        
        # Index documentation
        doc_count = self.index_documentation(project_id, documentation_sections)
        
        total = code_count + doc_count
        print(f"Reindexed project {project_id}: {total} embeddings created")
        
        return total

