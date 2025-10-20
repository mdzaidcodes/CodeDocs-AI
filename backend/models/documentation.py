"""
Documentation model for storing generated documentation.
"""

from config.database import get_db_cursor
import json


class Documentation:
    """Documentation model for managing project documentation."""
    
    @staticmethod
    def create(project_id, markdown_content, sections=None, word_count=None, generation_time_seconds=None):
        """
        Create documentation for a project.
        
        Args:
            project_id: UUID of the project
            markdown_content: Full markdown content
            sections: List of documentation sections
            word_count: Word count of documentation
            generation_time_seconds: Time taken to generate
            
        Returns:
            dict: Created documentation object
        """
        sections_json = json.dumps(sections) if sections else '[]'
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO documentation (
                    project_id, markdown_content, sections,
                    word_count, generation_time_seconds
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (project_id, markdown_content, sections_json, word_count, generation_time_seconds))
            
            doc = cursor.fetchone()
            result = dict(doc)
            # Parse sections JSON
            if result.get('sections'):
                result['sections'] = json.loads(result['sections']) if isinstance(result['sections'], str) else result['sections']
            return result
    
    @staticmethod
    def find_by_project_id(project_id):
        """Get documentation for a project."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM documentation
                WHERE project_id = %s
                ORDER BY version DESC, created_at DESC
                LIMIT 1
            """, (project_id,))
            
            doc = cursor.fetchone()
            if not doc:
                return None
            
            result = dict(doc)
            # Parse sections JSON
            if result.get('sections'):
                result['sections'] = json.loads(result['sections']) if isinstance(result['sections'], str) else result['sections']
            # For backwards compatibility, map markdown_content to content
            if result.get('markdown_content'):
                result['content'] = result['markdown_content']
            return result
    
    @staticmethod
    def update(project_id, markdown_content, sections=None):
        """
        Update documentation content.
        
        Args:
            project_id: UUID of the project
            markdown_content: Updated markdown content
            sections: Updated sections list
            
        Returns:
            dict: Updated documentation object
        """
        # Check if documentation exists
        existing = Documentation.find_by_project_id(project_id)
        
        if existing:
            # Update existing and increment version
            sections_json = json.dumps(sections) if sections else '[]'
            new_version = existing.get('version', 1) + 1
            word_count = len(markdown_content.split()) if markdown_content else 0
            
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE documentation
                    SET markdown_content = %s, sections = %s, 
                        version = %s, word_count = %s, updated_at = NOW()
                    WHERE project_id = %s
                    RETURNING *
                """, (markdown_content, sections_json, new_version, word_count, project_id))
                
                doc = cursor.fetchone()
                result = dict(doc)
                if result.get('sections'):
                    result['sections'] = json.loads(result['sections']) if isinstance(result['sections'], str) else result['sections']
                if result.get('markdown_content'):
                    result['content'] = result['markdown_content']
                return result
        else:
            # Create new
            return Documentation.create(project_id, markdown_content, sections)
    
    @staticmethod
    def delete_by_project_id(project_id):
        """Delete documentation for a project."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM documentation WHERE project_id = %s", (project_id,))
            return cursor.rowcount > 0

