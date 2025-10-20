"""
Documentation generator service using Claude AI.
"""

from services.claude_service import ClaudeService
from services.code_analyzer import CodeAnalyzer


class DocumentationGenerator:
    """Service for generating comprehensive documentation."""
    
    def __init__(self):
        """Initialize with Claude service."""
        self.claude_service = ClaudeService()
    
    def generate(self, project_name, code_files):
        """
        Generate comprehensive documentation for a project.
        
        Args:
            project_name: Name of the project
            code_files: Dict of {file_path: content}
            
        Returns:
            dict: {content: markdown string, sections: dict of sections}
        """
        # Analyze codebase
        analysis = CodeAnalyzer.analyze_files(code_files)
        important_files = CodeAnalyzer.identify_important_files(code_files)
        
        # Prepare code samples (prioritize important files)
        code_samples = {}
        
        # Add README if exists
        for readme_path in important_files.get('readme', []):
            if readme_path in code_files:
                code_samples[readme_path] = code_files[readme_path][:2000]
        
        # Add config files
        for config_path in important_files.get('config', [])[:3]:
            if config_path in code_files:
                code_samples[config_path] = code_files[config_path][:1000]
        
        # Add entry points
        for entry_path in important_files.get('entry_points', [])[:3]:
            if entry_path in code_files:
                code_samples[entry_path] = code_files[entry_path][:2000]
        
        # Add a few more representative files
        remaining = 10 - len(code_samples)
        for file_path, content in list(code_files.items())[:remaining]:
            if file_path not in code_samples:
                code_samples[file_path] = content[:1500]
        
        # Generate documentation with Claude
        documentation_md = self.claude_service.generate_documentation(
            code_samples,
            project_name
        )
        
        # Parse sections from generated documentation
        sections = self._parse_sections(documentation_md)
        
        # Add project statistics as a footer if analysis is available
        if analysis:
            stats_text = f"\n\n---\n\n**Project Statistics:**\n"
            stats_text += f"- Total Files: {analysis['file_count']}\n"
            stats_text += f"- Total Lines of Code: {analysis['total_lines']}\n"
            stats_text += f"- Primary Language: {analysis['primary_language']}\n"
            
            if analysis.get('technologies'):
                stats_text += f"- Technologies: {', '.join(analysis['technologies'][:5])}\n"
            
            # Append to markdown content if not already present
            if "Project Statistics" not in documentation_md:
                documentation_md += stats_text
        
        return {
            'content': documentation_md,
            'sections': sections
        }
    
    def _parse_sections(self, markdown_content):
        """
        Parse markdown into structured sections based on headers.
        
        Args:
            markdown_content: Full markdown string
            
        Returns:
            list: Array of section objects with type, title, content, order
        """
        sections = []
        current_section_title = None
        current_content = []
        section_order = 0
        
        # Define section type mappings
        section_type_map = {
            'purpose and objectives': 'purpose',
            'setup and installation': 'setup',
            'architecture documentation': 'architecture',
            'code documentation': 'code',
            'user guides': 'user_guide',
            'development documentation': 'development',
            'maintenance information': 'maintenance',
            'additional notes': 'notes',
            'reference materials': 'reference'
        }
        
        lines = markdown_content.split('\n')
        
        for line in lines:
            # Check for section headers (## Header)
            if line.startswith('## '):
                # Save previous section
                if current_section_title and current_content:
                    content_text = '\n'.join(current_content).strip()
                    if content_text:  # Only add non-empty sections
                        section_key = current_section_title.lower()
                        section_type = section_type_map.get(section_key, 'other')
                        
                        sections.append({
                            'type': section_type,
                            'title': current_section_title,
                            'content': content_text,
                            'order': section_order
                        })
                        section_order += 1
                
                # Start new section
                current_section_title = line[3:].strip()
                current_content = []
            else:
                if current_section_title:  # Only collect content if we have a section
                    current_content.append(line)
        
        # Save last section
        if current_section_title and current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text:
                section_key = current_section_title.lower()
                section_type = section_type_map.get(section_key, 'other')
                
                sections.append({
                    'type': section_type,
                    'title': current_section_title,
                    'content': content_text,
                    'order': section_order
                })
        
        return sections
    
    def update_section(self, current_content, section_name, new_section_content):
        """
        Update a specific section in the documentation.
        
        Args:
            current_content: Current full markdown content
            section_name: Name of section to update
            new_section_content: New content for the section
            
        Returns:
            str: Updated markdown content
        """
        sections = self._parse_sections(current_content)
        sections[section_name] = new_section_content
        
        # Rebuild markdown
        rebuilt = []
        for section_key, content in sections.items():
            # Format section name
            header = section_key.replace('_', ' ').title()
            rebuilt.append(f"## {header}\n\n{content}\n")
        
        return '\n'.join(rebuilt)

