"""
Project model for managing code documentation projects.
"""

from config.database import get_db_cursor


class Project:
    """Project model with CRUD operations."""
    
    @staticmethod
    def create(user_id, name, source_type, **kwargs):
        """
        Create a new project.
        
        Args:
            user_id: UUID of the project owner
            name: Project name
            source_type: 'upload' or 'github'
            **kwargs: Optional fields (description, github_url, github_branch)
            
        Returns:
            dict: Created project object
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO projects (
                    user_id, name, description, source_type,
                    github_url, github_branch, s3_code_path, status,
                    progress_percentage, progress_stage
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                user_id,
                name,
                kwargs.get('description'),
                source_type,
                kwargs.get('github_url'),
                kwargs.get('github_branch', 'main'),
                kwargs.get('s3_code_path', ''),  # Will be set after project creation
                'pending',
                0,
                'Initializing...'
            ))
            
            project = cursor.fetchone()
            return dict(project)
    
    @staticmethod
    def find_by_id(project_id):
        """Get project by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()
            return dict(project) if project else None
    
    @staticmethod
    def find_by_user_id(user_id):
        """Get all projects for a user."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM projects
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            projects = cursor.fetchall()
            return [dict(p) for p in projects]
    
    @staticmethod
    def update(project_id, **kwargs):
        """
        Update project fields.
        
        Args:
            project_id: UUID of the project
            **kwargs: Fields to update
            
        Returns:
            dict: Updated project object
        """
        # Build dynamic UPDATE query
        fields = []
        values = []
        
        allowed_fields = [
            'primary_language', 'total_files', 'total_lines', 'security_score',
            'code_quality_score', 'status', 'progress_percentage', 'progress_stage',
            'description', 'vulnerabilities_count', 'technologies', 'file_structure',
            's3_code_path', 's3_doc_path', 's3_analysis_path', 'error_message', 'processed_at',
            'color_palette'
        ]
        
        for field in allowed_fields:
            if field in kwargs:
                fields.append(f"{field} = %s")
                values.append(kwargs[field])
        
        if not fields:
            return Project.find_by_id(project_id)
        
        values.append(project_id)
        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = %s RETURNING *"
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)
            project = cursor.fetchone()
            return dict(project) if project else None
    
    @staticmethod
    def update_status(project_id, status, progress_percentage=None, progress_stage=None):
        """
        Update project processing status.
        
        Args:
            project_id: UUID of the project
            status: New status ('pending', 'processing', 'completed', 'failed')
            progress_percentage: Progress percentage (0-100)
            progress_stage: Description of current processing step
        """
        fields = ['status = %s', 'updated_at = NOW()']
        values = [status]
        
        if progress_percentage is not None:
            fields.append('progress_percentage = %s')
            values.append(progress_percentage)
        
        if progress_stage is not None:
            # Truncate to fit database column (max 200 chars)
            truncated_stage = progress_stage[:200] if len(progress_stage) > 200 else progress_stage
            fields.append('progress_stage = %s')
            values.append(truncated_stage)
        
        # Set processed_at when completed
        if status == 'completed':
            fields.append('processed_at = NOW()')
        
        values.append(project_id)
        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = %s"
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)
    
    @staticmethod
    def delete(project_id):
        """Delete a project and all related data (cascade)."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def check_ownership(project_id, user_id):
        """
        Check if a project belongs to a user.
        
        Returns:
            bool: True if user owns the project
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM projects
                WHERE id = %s AND user_id = %s
            """, (project_id, user_id))
            
            result = cursor.fetchone()
            return result['count'] > 0

