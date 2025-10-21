"""
Claude API service for AI-powered code analysis and documentation generation.
"""

from anthropic import Anthropic
from config.settings import Config


class ClaudeService:
    """Service for interacting with Claude AI API."""
    
    def __init__(self):
        """Initialize Claude client with API key."""
        # Initialize Anthropic client with only API key
        self.client = Anthropic(
            api_key=Config.CLAUDE_API_KEY,
            timeout=1800.0,  # 30 minute timeout
            max_retries=3
        )
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
        
        prompt = f"""Generate concise technical documentation for '{project_name}'.

Code Files:{code_context}

# {project_name} Documentation

## Purpose and Objectives
What does this project do? What problems does it solve? (2-3 sentences)

## Setup and Installation

### Prerequisites and Dependencies
List required tools and libraries (with versions if available).

### Installation Instructions
Step-by-step installation commands.

### Configuration Steps
Environment variables and configuration files needed.

### Environment Setup
Development environment setup.

## Architecture Documentation

### System Architecture and Tech Stack
Technologies, frameworks, and languages used.

### Component Relationships
How components interact and project structure.

### Simple Data Flow
How data flows through the system.

### Database Schemas or Data Models
Database tables and data structures.

## Code Documentation

### API Reference and Endpoints
API endpoints with methods, paths, and descriptions.

### Function/Method Documentation
Key functions and their purpose.

### Code Comments and Inline Documentation
Important code patterns and logic.

### Usage Examples and Code Samples
Practical usage examples.

## User Guides

### Feature Documentation
Key features and how they work.

### FAQs
Common questions and answers.

## Development Documentation

### Coding Standards and Conventions
Coding style and practices.

### Development Workflow
Development and contribution process.

### Testing Procedures
How to run and write tests.

### Deployment Processes
Deployment steps and platforms.

## Maintenance Information

### Version History and Changelog
Version info and recent changes.

### Known Issues and Limitations
Known bugs and limitations.

### Performance Considerations
Performance optimization and bottlenecks.

### Security Considerations
Security measures and best practices.

## Reference Materials

### Glossary of Terms
Technical terms and acronyms.

### External Dependencies
Third-party libraries and services.

---

**Keep it concise! Each section should be 2-5 sentences max. If info isn't in code, write "Not specified in codebase".**"""
        
        system_message = "You are a technical writer. Generate CONCISE documentation by analyzing code. Be brief and direct."
        
        return self.generate_completion(prompt, max_tokens=6000)
    
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

