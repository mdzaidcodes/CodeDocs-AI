"""
Code quality analyzer service using Claude AI for improvement suggestions.
"""

from services.claude_service import ClaudeService
import json


class CodeQualityAnalyzer:
    """Service for analyzing code quality and suggesting improvements."""
    
    def __init__(self):
        """Initialize with Claude service."""
        self.claude_service = ClaudeService()
    
    def analyze_file(self, filename, content):
        """
        Analyze a single file for quality improvements.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            list: List of improvement dicts
        """
        try:
            # Get analysis from Claude
            response = self.claude_service.suggest_code_improvements(content, filename)
            
            # Parse JSON response
            improvements = self._parse_improvements(response)
            
            # Add filename to each improvement
            for improvement in improvements:
                improvement['file_path'] = filename
            
            return improvements
        
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            return []
    
    def analyze_project(self, code_files, max_files=None):
        """
        Analyze ALL files for quality improvements.
        
        Args:
            code_files: Dict of {file_path: content}
            max_files: Maximum files to analyze (None = analyze all files)
            
        Returns:
            list: Combined list of all improvements
        """
        all_improvements = []
        
        # Apply limit if specified, otherwise analyze all files
        files_to_analyze = list(code_files.items())[:max_files] if max_files else list(code_files.items())
        
        print(f"[Quality] Analyzing {len(files_to_analyze)} files for code quality...")
        
        # Analyze files
        for idx, (file_path, content) in enumerate(files_to_analyze, 1):
            # Skip very large files (truncate to 10000 chars)
            if len(content) > 10000:
                content = content[:10000]
            
            print(f"[Quality] ({idx}/{len(files_to_analyze)}) Analyzing {file_path}...")
            improvements = self.analyze_file(file_path, content)
            all_improvements.extend(improvements)
        
        print(f"[Quality] ✅ Found {len(all_improvements)} improvement suggestions across {len(files_to_analyze)} files")
        return all_improvements
    
    def _parse_improvements(self, claude_response):
        """
        Parse Claude's JSON response into improvement objects.
        
        Args:
            claude_response: JSON string from Claude
            
        Returns:
            list: List of improvement dicts
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
            improvements = json.loads(response)
            
            if not isinstance(improvements, list):
                print(f"Warning: Expected list, got {type(improvements)}")
                return []
            
            # Validate and normalize improvements
            validated = []
            for improvement in improvements:
                if self._validate_improvement(improvement):
                    validated.append(improvement)
            
            print(f"Successfully parsed {len(validated)} improvements")
            return validated
        
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response (first 500 chars): {claude_response[:500]}")
            print(f"Attempted to parse: {response[:500] if 'response' in locals() else 'N/A'}")
            return []
        except Exception as e:
            print(f"Error parsing improvements: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def _validate_improvement(self, improvement):
        """
        Validate that improvement has required fields and normalize values.
        
        Args:
            improvement: Improvement dict
            
        Returns:
            bool: True if valid
        """
        required = ['category', 'title', 'description', 'suggestion', 'impact_level']
        
        for field in required:
            if field not in improvement:
                return False
        
        # Normalize category to lowercase with hyphens
        # This ensures consistency with frontend filter values
        # "Performance" -> "performance", "Best Practices" -> "best-practice"
        if 'category' in improvement:
            category = improvement['category'].lower().strip()
            # Replace spaces with hyphens
            category = category.replace(' ', '-')
            # Normalize common variations
            if 'best' in category and 'practice' in category:
                category = 'best-practice'
            elif 'performance' in category or 'perf' in category:
                category = 'performance'
            elif 'readability' in category or 'readable' in category or 'clarity' in category:
                category = 'readability'
            elif 'maintainability' in category or 'maintain' in category:
                category = 'maintainability'
            elif 'security' in category or 'secure' in category:
                category = 'security'
            elif 'error' in category and 'handling' in category:
                category = 'error-handling'
            improvement['category'] = category
        
        # Normalize impact_level to lowercase
        if 'impact_level' in improvement:
            improvement['impact_level'] = improvement['impact_level'].lower().strip()
        
        # Validate impact_level
        valid_impact_levels = ['high', 'medium', 'low']
        if improvement['impact_level'] not in valid_impact_levels:
            improvement['impact_level'] = 'medium'
        
        # Normalize estimated_effort to lowercase if present
        if 'estimated_effort' in improvement:
            improvement['estimated_effort'] = improvement['estimated_effort'].lower().strip()
            valid_efforts = ['high', 'medium', 'low']
            if improvement['estimated_effort'] not in valid_efforts:
                improvement['estimated_effort'] = 'medium'
        
        return True

