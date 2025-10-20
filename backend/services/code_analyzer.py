"""
Code analyzer service for analyzing codebase structure and content.
"""

import os
from utils.helpers import detect_language
from utils.validators import validate_file_extension


class CodeAnalyzer:
    """Service for analyzing code structure and content."""
    
    @staticmethod
    def analyze_files(file_paths_and_content):
        """
        Analyze files to extract metadata and statistics.
        
        Args:
            file_paths_and_content: Dict of {file_path: content}
            
        Returns:
            dict: Analysis results with statistics
        """
        analysis = {
            'file_count': len(file_paths_and_content),
            'total_lines': 0,
            'languages': {},
            'file_types': {},
            'avg_file_size': 0,
            'largest_file': None,
            'primary_language': None,
        }
        
        total_size = 0
        largest_size = 0
        
        for file_path, content in file_paths_and_content.items():
            # Count lines
            lines = content.count('\n') + 1
            analysis['total_lines'] += lines
            
            # Track file size
            size = len(content)
            total_size += size
            
            if size > largest_size:
                largest_size = size
                analysis['largest_file'] = file_path
            
            # Track file extension
            ext = os.path.splitext(file_path)[1].lower()
            analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
        
        # Calculate average file size
        if analysis['file_count'] > 0:
            analysis['avg_file_size'] = total_size // analysis['file_count']
        
        # Detect primary language
        file_paths = list(file_paths_and_content.keys())
        analysis['primary_language'] = detect_language(file_paths)
        
        return analysis
    
    @staticmethod
    def filter_code_files(files_dict):
        """
        Filter to keep only valid code files.
        
        Args:
            files_dict: Dict of {file_path: content}
            
        Returns:
            dict: Filtered dict with only code files
        """
        filtered = {}
        
        for file_path, content in files_dict.items():
            # Check if extension is allowed
            if validate_file_extension(file_path):
                # Skip empty files
                if content and len(content.strip()) > 0:
                    filtered[file_path] = content
        
        return filtered
    
    @staticmethod
    def get_file_summaries(files_dict, max_files=20):
        """
        Get summaries of files for overview.
        
        Args:
            files_dict: Dict of {file_path: content}
            max_files: Maximum number of files to summarize
            
        Returns:
            list: List of file summary dicts
        """
        summaries = []
        
        for file_path, content in list(files_dict.items())[:max_files]:
            lines = content.count('\n') + 1
            size = len(content)
            ext = os.path.splitext(file_path)[1].lower()
            
            summaries.append({
                'path': file_path,
                'lines': lines,
                'size': size,
                'extension': ext,
            })
        
        return summaries
    
    @staticmethod
    def identify_important_files(files_dict):
        """
        Identify key files like README, config files, entry points.
        
        Args:
            files_dict: Dict of {file_path: content}
            
        Returns:
            dict: Categorized important files
        """
        important = {
            'readme': [],
            'config': [],
            'entry_points': [],
            'tests': [],
        }
        
        for file_path in files_dict.keys():
            filename = os.path.basename(file_path).lower()
            
            # README files
            if 'readme' in filename:
                important['readme'].append(file_path)
            
            # Config files
            config_names = ['package.json', 'requirements.txt', 'setup.py', 'cargo.toml',
                          'pom.xml', 'build.gradle', 'composer.json', 'go.mod']
            if filename in config_names or filename.endswith('.config.js'):
                important['config'].append(file_path)
            
            # Entry points
            entry_names = ['main.py', 'index.js', 'app.py', 'main.go', 'main.rs',
                         'index.ts', 'server.js', 'app.js']
            if filename in entry_names:
                important['entry_points'].append(file_path)
            
            # Test files
            if 'test' in filename or filename.startswith('test_') or filename.endswith('_test.py'):
                important['tests'].append(file_path)
        
        return important

