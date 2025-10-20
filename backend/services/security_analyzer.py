"""
Security analyzer service using Claude AI to detect vulnerabilities.
"""

from services.claude_service import ClaudeService
import json


class SecurityAnalyzer:
    """Service for analyzing code security."""
    
    def __init__(self):
        """Initialize with Claude service."""
        self.claude_service = ClaudeService()
    
    def analyze_file(self, filename, content):
        """
        Analyze a single file for security vulnerabilities.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            list: List of finding dicts
        """
        try:
            # Get analysis from Claude
            response = self.claude_service.find_security_vulnerabilities(content, filename)
            
            # Parse JSON response
            findings = self._parse_findings(response)
            
            # Add filename to each finding
            for finding in findings:
                finding['file_path'] = filename
            
            return findings
        
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            return []
    
    def analyze_project(self, code_files, max_files=None):
        """
        Analyze ALL files for security issues.
        
        Args:
            code_files: Dict of {file_path: content}
            max_files: Maximum files to analyze (None = analyze all files)
            
        Returns:
            list: Combined list of all findings
        """
        all_findings = []
        
        # Prioritize certain file types (backend, auth, database)
        priority_extensions = ['.py', '.js', '.ts', '.php', '.java', '.go']
        priority_names = ['auth', 'login', 'password', 'database', 'db', 'sql', 'api']
        
        # Sort files by priority (high-priority files analyzed first)
        sorted_files = sorted(
            code_files.items(),
            key=lambda x: (
                any(ext in x[0].lower() for ext in priority_extensions),
                any(name in x[0].lower() for name in priority_names)
            ),
            reverse=True
        )
        
        # Apply limit if specified, otherwise analyze all files
        files_to_analyze = sorted_files[:max_files] if max_files else sorted_files
        
        print(f"[Security] Analyzing {len(files_to_analyze)} files for vulnerabilities...")
        
        # Analyze files
        for idx, (file_path, content) in enumerate(files_to_analyze, 1):
            # Skip very large files (truncate to 10000 chars)
            if len(content) > 10000:
                content = content[:10000]
            
            print(f"[Security] ({idx}/{len(files_to_analyze)}) Analyzing {file_path}...")
            findings = self.analyze_file(file_path, content)
            all_findings.extend(findings)
        
        print(f"[Security] ✅ Found {len(all_findings)} security issues across {len(files_to_analyze)} files")
        return all_findings
    
    def _parse_findings(self, claude_response):
        """
        Parse Claude's JSON response into finding objects.
        
        Args:
            claude_response: JSON string from Claude
            
        Returns:
            list: List of finding dicts
        """
        try:
            # Try to extract JSON from response
            response = claude_response.strip()
            
            # Remove markdown code blocks
            if '```json' in response.lower():
                # Find the json code block
                start_marker = response.lower().find('```json')
                start = response.find('\n', start_marker) + 1
                end = response.find('```', start)
                if end == -1:
                    end = len(response)
                response = response[start:end].strip()
            elif '```' in response:
                # Find any code block
                start = response.find('```') + 3
                # Skip language identifier if present
                newline_pos = response.find('\n', start)
                if newline_pos != -1 and newline_pos - start < 20:
                    start = newline_pos + 1
                end = response.find('```', start)
                if end == -1:
                    end = len(response)
                response = response[start:end].strip()
            
            # Try to find JSON array
            if '[' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                response = response[start:end]
            
            # Clean up any remaining non-JSON text
            response = response.strip()
            
            # Parse JSON
            findings = json.loads(response)
            
            if not isinstance(findings, list):
                print(f"Warning: Expected list, got {type(findings)}")
                return []
            
            # Validate and normalize findings
            validated = []
            for finding in findings:
                if self._validate_finding(finding):
                    validated.append(finding)
            
            print(f"Successfully parsed {len(validated)} security findings")
            return validated
        
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response (first 500 chars): {claude_response[:500]}")
            print(f"Attempted to parse: {response[:500] if 'response' in locals() else 'N/A'}")
            return []
        except Exception as e:
            print(f"Error parsing findings: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def _validate_finding(self, finding):
        """
        Validate that finding has required fields.
        
        Args:
            finding: Finding dict
            
        Returns:
            bool: True if valid
        """
        required = ['severity', 'title', 'description', 'recommendation', 'category']
        
        for field in required:
            if field not in finding:
                return False
        
        # Validate severity
        valid_severities = ['critical', 'high', 'medium', 'low', 'info']
        if finding['severity'] not in valid_severities:
            finding['severity'] = 'info'
        
        return True
    
    def calculate_security_score(self, findings):
        """
        Calculate security score based on findings.
        
        Args:
            findings: List of security findings
            
        Returns:
            int: Score from 0-100 (100 is best)
        """
        if not findings:
            return 100
        
        # Deduct points based on severity
        score = 100
        severity_penalties = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2,
            'info': 1,
        }
        
        for finding in findings:
            penalty = severity_penalties.get(finding.get('severity', 'info'), 1)
            score -= penalty
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))

