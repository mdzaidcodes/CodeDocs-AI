"""
Claude API service for AI-powered code analysis and documentation generation.
"""

from anthropic import Anthropic
from config.settings import Config


class ClaudeService:
    """Service for interacting with Claude AI API."""
    
    def __init__(self):
        """Initialize Claude client with API key."""
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = Config.CLAUDE_MODEL
        self.max_tokens = Config.CLAUDE_MAX_TOKENS
    
    def generate_completion(self, prompt, system_message=None, max_tokens=None):
        """
        Generate a completion using Claude.
        
        Args:
            prompt: User prompt/message
            system_message: Optional system message for context
            max_tokens: Optional max tokens override
            
        Returns:
            str: Claude's response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Prepare API call parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "messages": messages
            }
            
            # Add system message if provided
            if system_message:
                params["system"] = system_message
            
            # Make API call
            response = self.client.messages.create(**params)
            
            # Extract text from response
            text = response.content[0].text
            return text
        
        except Exception as e:
            print(f"Claude API error: {e}")
            raise Exception(f"Failed to generate completion: {str(e)}")
    
    def analyze_code(self, code, filename, task_description):
        """
        Analyze code with Claude for a specific task.
        
        Args:
            code: Source code content
            filename: Name of the file
            task_description: What to analyze for
            
        Returns:
            str: Analysis result
        """
        prompt = f"""Analyze the following code from file '{filename}'.

Task: {task_description}

Code:
```
{code}
```

Please provide a detailed analysis."""
        
        system_message = "You are an expert code analyst and developer. Provide clear, accurate, and actionable analysis."
        
        return self.generate_completion(prompt, system_message)
    
    def generate_documentation(self, code_files, project_name):
        """
        Generate comprehensive documentation for code.
        
        Args:
            code_files: Dict of {filename: content}
            project_name: Name of the project
            
        Returns:
            str: Generated markdown documentation
        """
        # Prepare code context
        code_context = ""
        for filename, content in list(code_files.items())[:10]:  # Limit to first 10 files
            code_context += f"\n\n### File: {filename}\n```\n{content[:2000]}\n```"  # Limit content length
        
        prompt = f"""Generate comprehensive technical documentation for the project '{project_name}'.

Code Files:{code_context}

Create complete markdown documentation following this EXACT structure and format:

# {project_name} Documentation

## Purpose and Objectives
Write a comprehensive paragraph explaining what this project does, its main purpose, goals, and the problems it solves. Analyze the code structure and functionality to understand the project's objectives.

## Setup and Installation

### Prerequisites and Dependencies
List all required software, libraries, and tools needed before installation. Include versions if found in package files.

### Installation Instructions
Provide clear step-by-step instructions for installing the project. Include commands and setup steps.

### Configuration Steps
Explain how to configure the project after installation. Include environment variables, config files, and settings.

### Environment Setup
Detail the complete environment setup process including development tools, IDE setup, and system requirements.

## Architecture Documentation

### System Architecture and Tech Stack
Describe the overall system architecture. List all technologies, frameworks, languages, and tools used in the project.

### Component Relationships
Explain how different components, modules, and services interact with each other. Show the project structure.

### Simple Data Flow
Describe the data flow through the system. Explain how data moves between components and the request/response cycle.

### Database Schemas or Data Models
Document all database tables, collections, or data structures. Include field names, types, and relationships.

## Code Documentation

### API Reference and Endpoints
List all API endpoints with methods (GET, POST, etc.), paths, parameters, request/response examples, and descriptions.

### Function/Method Documentation
Document key functions and methods including their purpose, parameters, return values, and usage.

### Code Comments and Inline Documentation
Explain important code patterns, algorithms, and logic found in the codebase.

### Usage Examples and Code Samples
Provide practical code examples showing how to use the main features and functionality.

## User Guides

### Feature Documentation
List ALL key features of the project with clear descriptions of what each feature does and how it works.

### FAQs
Provide answers to frequently asked questions about using the project, common issues, and best practices.

## Development Documentation

### Coding Standards and Conventions
Document the coding style, naming conventions, file organization, and development practices used in the project.

### Development Workflow
Explain the development process including branching strategy, code review process, and contribution guidelines.

### Testing Procedures
Describe how to run tests, what testing frameworks are used, and how to write new tests.

### Deployment Processes
Explain how to deploy the project including build steps, deployment platforms, and CI/CD processes.

## Maintenance Information

### Version History and Changelog
Document version information, recent changes, and update history if available in the code.

### Known Issues and Limitations
List any known bugs, limitations, or areas needing improvement found in the codebase.

### Performance Considerations
Discuss performance aspects including optimization techniques, bottlenecks, and scalability considerations.

### Security Considerations
Document security measures, authentication/authorization, data protection, and security best practices implemented.

## Additional Notes
Include any other important information that doesn't fit in the above categories but is relevant to users or developers.

## Reference Materials

### Glossary of Terms
Define technical terms, acronyms, and domain-specific terminology used in the project.

### External Dependencies
List all third-party libraries, services, and APIs used with their purposes and documentation links.

### Contact Information for Support
Provide information about where to get help, report issues, or contact the development team.

---

**IMPORTANT FORMATTING RULES:**
1. Use ## for main sections (Purpose and Objectives, Setup and Installation, etc.)
2. Use ### for subsections (Prerequisites and Dependencies, Installation Instructions, etc.)
3. Use bullet points (-) for lists within subsections
4. Write in clear, professional technical writing style
5. Be comprehensive but concise
6. If information is not available in the code, write "Not specified in codebase" but still create the section
7. Include code examples in markdown code blocks with language syntax
8. Make it practical and useful for both users and developers"""
        
        system_message = "You are an expert technical documentation specialist. Generate thorough, professional documentation by analyzing code structure, imports, comments, and patterns. Be comprehensive and detailed."
        
        return self.generate_completion(prompt, max_tokens=8000)
    
    def find_security_vulnerabilities(self, code, filename):
        """
        Identify security vulnerabilities in code.
        
        Args:
            code: Source code content
            filename: Name of the file
            
        Returns:
            str: JSON-formatted security findings
        """
        prompt = f"""Analyze this code for security vulnerabilities from file '{filename}'.

Code:
```
{code}
```

Identify security issues and return them as a JSON array with this structure:
[
  {{
    "severity": "critical|high|medium|low|info",
    "title": "Brief title",
    "description": "Detailed description",
    "line_number": 42 (if applicable),
    "recommendation": "How to fix",
    "category": "injection|xss|auth|crypto|etc"
  }}
]

Only return the JSON array, no additional text."""
        
        system_message = "You are a security expert specializing in code vulnerability analysis. Focus on practical, exploitable issues."
        
        return self.generate_completion(prompt)
    
    def suggest_code_improvements(self, code, filename):
        """
        Suggest code quality improvements.
        
        Args:
            code: Source code content
            filename: Name of the file
            
        Returns:
            str: JSON-formatted improvement suggestions
        """
        prompt = f"""Analyze this code for quality improvements from file '{filename}'.

Code:
```
{code}
```

Suggest improvements and return them as a JSON array with this structure:
[
  {{
    "category": "Performance|Security|Maintainability|Readability|Best Practices|Error Handling|etc",
    "title": "Brief title",
    "description": "What could be improved",
    "file_path": "path/to/file.py",
    "line_number": 42 (if applicable),
    "code_snippet": "relevant code snippet" (optional),
    "suggestion": "Specific improvement suggestion",
    "improved_code": "improved code example" (optional),
    "impact_level": "high|medium|low",
    "estimated_effort": "high|medium|low"
  }}
]

Only return the JSON array, no additional text."""
        
        system_message = "You are a code quality expert. Provide actionable, practical improvement suggestions."
        
        return self.generate_completion(prompt)
    
    def answer_question(self, question, context):
        """
        Answer a question about code using provided context.
        
        Args:
            question: User's question
            context: Relevant code/documentation context
            
        Returns:
            str: Answer to the question
        """
        prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {question}

Please provide a clear, detailed answer based solely on the provided context."""
        
        system_message = "You are a helpful AI assistant that answers questions about code. Be accurate and concise."
        
        return self.generate_completion(prompt)

