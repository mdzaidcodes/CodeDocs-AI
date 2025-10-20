"""
Code Improvement model for storing quality improvement suggestions.
"""

from config.database import get_db_cursor


class CodeImprovement:
    """Model for managing code quality improvement suggestions."""
    
    @staticmethod
    def create(project_id, category, title, description, file_path,
               suggestion, impact_level, line_number=None, code_snippet=None,
               improved_code=None, estimated_effort=None):
        """
        Create a code improvement suggestion.
        
        Args:
            project_id: UUID of the project
            category: Improvement category
            title: Improvement title
            description: Detailed description
            file_path: Path to affected file
            suggestion: Improvement suggestion
            impact_level: 'high', 'medium', 'low'
            line_number: Optional line number
            code_snippet: Optional code snippet
            improved_code: Optional improved code example
            estimated_effort: Optional effort estimate ('high', 'medium', 'low')
            
        Returns:
            dict: Created improvement object
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO code_improvements (
                    project_id, category, title, description, suggestion,
                    file_path, line_number, code_snippet, improved_code,
                    impact_level, estimated_effort
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                project_id, category, title, description, suggestion,
                file_path, line_number, code_snippet, improved_code,
                impact_level, estimated_effort
            ))
            
            improvement = cursor.fetchone()
            return dict(improvement)
    
    @staticmethod
    def find_by_project_id(project_id, category=None, impact_level=None, status=None):
        """
        Get all code improvements for a project.
        
        Args:
            project_id: UUID of the project
            category: Optional category filter
            impact_level: Optional impact level filter ('high', 'medium', 'low')
            status: Optional status filter ('pending', 'implemented', 'dismissed')
            
        Returns:
            list: List of improvement objects
        """
        query = "SELECT * FROM code_improvements WHERE project_id = %s"
        params = [project_id]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if impact_level:
            query += " AND impact_level = %s"
            params.append(impact_level)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += """ ORDER BY 
            CASE impact_level
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END,
            created_at DESC
        """
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            improvements = cursor.fetchall()
            return [dict(i) for i in improvements]
    
    @staticmethod
    def delete_by_project_id(project_id):
        """Delete all improvements for a project."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM code_improvements WHERE project_id = %s", (project_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_category_counts(project_id):
        """
        Get count of improvements by category.
        
        Returns:
            dict: Counts by improvement category
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM code_improvements
                WHERE project_id = %s
                GROUP BY category
            """, (project_id,))
            
            results = cursor.fetchall()
            counts = {row['category']: row['count'] for row in results}
            
            return counts
    
    @staticmethod
    def update_status(improvement_id, status, notes=None):
        """
        Update the status of an improvement.
        
        Args:
            improvement_id: UUID of the improvement
            status: New status ('pending', 'implemented', 'dismissed')
            notes: Optional notes
        """
        fields = ['status = %s', 'updated_at = NOW()']
        values = [status]
        
        if notes:
            fields.append('notes = %s')
            values.append(notes)
        
        values.append(improvement_id)
        query = f"UPDATE code_improvements SET {', '.join(fields)} WHERE id = %s"
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)

