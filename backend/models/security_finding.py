"""
Security Finding model for storing vulnerability findings.
"""

from config.database import get_db_cursor


class SecurityFinding:
    """Model for managing security vulnerability findings."""
    
    @staticmethod
    def create(project_id, severity, title, description, file_path, 
               recommendation, category, line_number=None, code_snippet=None,
               cwe_id=None, cvss_score=None, references=None):
        """
        Create a security finding.
        
        Args:
            project_id: UUID of the project
            severity: 'critical', 'high', 'medium', 'low', 'info'
            title: Finding title
            description: Detailed description
            file_path: Path to affected file
            recommendation: Security recommendation
            category: Finding category
            line_number: Optional line number
            code_snippet: Optional vulnerable code snippet
            cwe_id: Optional CWE identifier
            cvss_score: Optional CVSS score
            references: Optional JSON array of reference links
            
        Returns:
            dict: Created finding object
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO security_findings (
                    project_id, severity, title, description, recommendation,
                    file_path, line_number, code_snippet, category,
                    cwe_id, cvss_score, "references"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                project_id, severity, title, description, recommendation,
                file_path, line_number, code_snippet, category,
                cwe_id, cvss_score, references
            ))
            
            finding = cursor.fetchone()
            return dict(finding)
    
    @staticmethod
    def find_by_project_id(project_id, severity=None):
        """
        Get all security findings for a project.
        
        Args:
            project_id: UUID of the project
            severity: Optional severity filter
            
        Returns:
            list: List of finding objects
        """
        with get_db_cursor() as cursor:
            if severity:
                cursor.execute("""
                    SELECT * FROM security_findings
                    WHERE project_id = %s AND severity = %s
                    ORDER BY 
                        CASE severity
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                            WHEN 'info' THEN 5
                        END,
                        created_at DESC
                """, (project_id, severity))
            else:
                cursor.execute("""
                    SELECT * FROM security_findings
                    WHERE project_id = %s
                    ORDER BY 
                        CASE severity
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                            WHEN 'info' THEN 5
                        END,
                        created_at DESC
                """, (project_id,))
            
            findings = cursor.fetchall()
            return [dict(f) for f in findings]
    
    @staticmethod
    def delete_by_project_id(project_id):
        """Delete all security findings for a project."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM security_findings WHERE project_id = %s", (project_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_severity_counts(project_id):
        """
        Get count of findings by severity.
        
        Returns:
            dict: Counts by severity level
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM security_findings
                WHERE project_id = %s
                GROUP BY severity
            """, (project_id,))
            
            results = cursor.fetchall()
            counts = {row['severity']: row['count'] for row in results}
            
            # Ensure all severities are present
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                if severity not in counts:
                    counts[severity] = 0
            
            return counts
    
    @staticmethod
    def update_status(finding_id, status, notes=None):
        """
        Update the status of a security finding.
        
        Args:
            finding_id: UUID of the finding
            status: New status ('open', 'acknowledged', 'fixed', 'false_positive', 'wont_fix')
            notes: Optional notes about the status change
        """
        fields = ['status = %s', 'updated_at = NOW()']
        values = [status]
        
        if notes:
            fields.append('notes = %s')
            values.append(notes)
        
        if status in ['fixed', 'false_positive']:
            fields.append('resolved_at = NOW()')
        
        values.append(finding_id)
        query = f"UPDATE security_findings SET {', '.join(fields)} WHERE id = %s"
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)

