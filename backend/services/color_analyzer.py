"""
Color Analyzer Service

Extracts and analyzes colors from code files to generate a color palette.
Identifies colors from:
- CSS files (hex, rgb, rgba, hsl)
- Tailwind CSS classes (bg-, text-, border- colors)
- Theme configuration files
- JavaScript/TypeScript color constants

Uses Claude AI to categorize and describe color usage.
"""

import re
from collections import Counter
from services.claude_service import ClaudeService


class ColorAnalyzer:
    """Analyzes code files to extract and categorize color palette."""
    
    def __init__(self):
        """Initialize color analyzer with Claude service."""
        self.claude_service = ClaudeService()
        
        # Common Tailwind color mappings (name -> hex)
        self.tailwind_colors = {
            # Slate
            'slate-50': '#f8fafc', 'slate-100': '#f1f5f9', 'slate-200': '#e2e8f0',
            'slate-300': '#cbd5e1', 'slate-400': '#94a3b8', 'slate-500': '#64748b',
            'slate-600': '#475569', 'slate-700': '#334155', 'slate-800': '#1e293b',
            'slate-900': '#0f172a', 'slate-950': '#020617',
            # Gray
            'gray-50': '#f9fafb', 'gray-100': '#f3f4f6', 'gray-200': '#e5e7eb',
            'gray-300': '#d1d5db', 'gray-400': '#9ca3af', 'gray-500': '#6b7280',
            'gray-600': '#4b5563', 'gray-700': '#374151', 'gray-800': '#1f2937',
            'gray-900': '#111827', 'gray-950': '#030712',
            # Blue
            'blue-50': '#eff6ff', 'blue-100': '#dbeafe', 'blue-200': '#bfdbfe',
            'blue-300': '#93c5fd', 'blue-400': '#60a5fa', 'blue-500': '#3b82f6',
            'blue-600': '#2563eb', 'blue-700': '#1d4ed8', 'blue-800': '#1e40af',
            'blue-900': '#1e3a8a', 'blue-950': '#172554',
            # Red
            'red-50': '#fef2f2', 'red-100': '#fee2e2', 'red-200': '#fecaca',
            'red-300': '#fca5a5', 'red-400': '#f87171', 'red-500': '#ef4444',
            'red-600': '#dc2626', 'red-700': '#b91c1c', 'red-800': '#991b1b',
            'red-900': '#7f1d1d', 'red-950': '#450a0a',
            # Green
            'green-50': '#f0fdf4', 'green-100': '#dcfce7', 'green-200': '#bbf7d0',
            'green-300': '#86efac', 'green-400': '#4ade80', 'green-500': '#22c55e',
            'green-600': '#16a34a', 'green-700': '#15803d', 'green-800': '#166534',
            'green-900': '#14532d', 'green-950': '#052e16',
            # Yellow
            'yellow-50': '#fefce8', 'yellow-100': '#fef9c3', 'yellow-200': '#fef08a',
            'yellow-300': '#fde047', 'yellow-400': '#facc15', 'yellow-500': '#eab308',
            'yellow-600': '#ca8a04', 'yellow-700': '#a16207', 'yellow-800': '#854d0e',
            'yellow-900': '#713f12', 'yellow-950': '#422006',
            # Purple
            'purple-50': '#faf5ff', 'purple-100': '#f3e8ff', 'purple-200': '#e9d5ff',
            'purple-300': '#d8b4fe', 'purple-400': '#c084fc', 'purple-500': '#a855f7',
            'purple-600': '#9333ea', 'purple-700': '#7e22ce', 'purple-800': '#6b21a8',
            'purple-900': '#581c87', 'purple-950': '#3b0764',
            # Orange
            'orange-50': '#fff7ed', 'orange-100': '#ffedd5', 'orange-200': '#fed7aa',
            'orange-300': '#fdba74', 'orange-400': '#fb923c', 'orange-500': '#f97316',
            'orange-600': '#ea580c', 'orange-700': '#c2410c', 'orange-800': '#9a3412',
            'orange-900': '#7c2d12', 'orange-950': '#431407',
            # White/Black
            'white': '#ffffff', 'black': '#000000',
        }
    
    def analyze_colors(self, code_files, project_name):
        """
        Analyze code files to extract and categorize color palette.
        
        Process:
        1. Extract all color values from files
        2. Count frequency of each color
        3. Normalize and deduplicate colors
        4. Get top 5 most used colors
        5. Use Claude to categorize and describe colors
        
        Args:
            code_files: Dictionary of {filename: content}
            project_name: Name of the project
            
        Returns:
            dict: Color palette with top 5 colors and metadata
        """
        try:
            # Step 1: Extract all colors from code files
            all_colors = []
            
            for filename, content in code_files.items():
                # Only analyze relevant files
                if self._is_color_relevant_file(filename):
                    colors = self._extract_colors_from_content(content, filename)
                    all_colors.extend(colors)
            
            if not all_colors:
                return self._get_default_palette()
            
            # Step 2: Count color frequency
            color_counter = Counter(all_colors)
            
            # Step 3: Get top 5 colors
            top_colors = color_counter.most_common(5)
            
            # Step 4: Format colors with metadata
            colors_for_analysis = []
            for color_hex, frequency in top_colors:
                colors_for_analysis.append({
                    'hex': color_hex,
                    'frequency': frequency
                })
            
            # Step 5: Use Claude to categorize and describe colors
            color_descriptions = self._get_color_descriptions(
                colors_for_analysis,
                project_name
            )
            
            # Step 6: Build final palette
            palette = {
                'colors': color_descriptions,
                'total_colors_found': len(color_counter),
                'scheme_type': self._determine_scheme_type(color_descriptions)
            }
            
            return palette
            
        except Exception as e:
            print(f"Color analysis error: {e}")
            return self._get_default_palette()
    
    def _is_color_relevant_file(self, filename):
        """
        Check if file is relevant for color extraction.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if file should be analyzed
        """
        color_file_extensions = [
            '.css', '.scss', '.sass', '.less',  # Stylesheets
            '.tsx', '.jsx', '.ts', '.js',       # React/JS files with Tailwind
            '.vue', '.svelte',                  # Other frameworks
            '.html', '.htm',                    # HTML files
            'tailwind.config', 'theme',         # Config files
        ]
        
        filename_lower = filename.lower()
        
        return any(
            filename_lower.endswith(ext) or ext in filename_lower
            for ext in color_file_extensions
        )
    
    def _extract_colors_from_content(self, content, filename):
        """
        Extract color values from file content.
        
        Extraction methods:
        1. Hex colors (#RRGGBB, #RGB)
        2. RGB/RGBA colors (rgb(), rgba())
        3. HSL/HSLA colors (hsl(), hsla())
        4. Tailwind classes (bg-blue-500, text-red-600, etc.)
        
        Args:
            content: File content string
            filename: Name of the file
            
        Returns:
            list: List of hex color codes
        """
        colors = []
        
        # Extract hex colors (#RRGGBB or #RGB)
        hex_colors = re.findall(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])', content)
        for hex_color in hex_colors:
            # Convert 3-digit hex to 6-digit
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            colors.append(f'#{hex_color.upper()}')
        
        # Extract RGB/RGBA colors
        rgb_colors = re.findall(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', content)
        for r, g, b in rgb_colors:
            hex_color = f'#{int(r):02X}{int(g):02X}{int(b):02X}'
            colors.append(hex_color)
        
        # Extract Tailwind color classes
        tailwind_patterns = [
            r'bg-(\w+-\d+)',      # bg-blue-500
            r'text-(\w+-\d+)',    # text-red-600
            r'border-(\w+-\d+)',  # border-gray-300
            r'from-(\w+-\d+)',    # from-purple-500 (gradients)
            r'to-(\w+-\d+)',      # to-blue-500
            r'via-(\w+-\d+)',     # via-pink-500
        ]
        
        for pattern in tailwind_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match in self.tailwind_colors:
                    colors.append(self.tailwind_colors[match].upper())
        
        return colors
    
    def _get_color_descriptions(self, colors_data, project_name):
        """
        Use Claude to categorize and describe colors.
        
        Args:
            colors_data: List of {hex, frequency} dicts
            project_name: Project name for context
            
        Returns:
            list: List of color objects with descriptions
        """
        # Build prompt for Claude
        colors_list = "\n".join([
            f"- {c['hex']} (used {c['frequency']} times)"
            for c in colors_data
        ])
        
        prompt = f"""Analyze these colors from the "{project_name}" application and provide categorization and usage descriptions.

Colors found:
{colors_list}

For each color, provide:
1. A descriptive name (e.g., "Primary Blue", "Background Dark", "Accent Red")
2. Category (primary, secondary, accent, background, text, border, success, error, warning, info)
3. A brief description of likely usage (1 sentence)

Return as JSON array with this exact structure:
[
  {{
    "hex": "#3B82F6",
    "name": "Primary Blue",
    "category": "primary",
    "description": "Main brand color used for buttons, links, and key UI elements"
  }},
  ...
]

Respond with ONLY the JSON array, no other text."""

        try:
            response = self.claude_service.generate_completion(prompt, max_tokens=1000)
            
            # Parse JSON response
            import json
            
            # Extract JSON from response
            response = response.strip()
            if '```json' in response.lower():
                start = response.lower().find('```json') + 7
                end = response.find('```', start)
                response = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                response = response[start:end].strip()
            
            # Find JSON array
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                response = response[start:end]
            
            color_descriptions = json.loads(response)
            
            # Add frequency and calculate RGB
            for i, color_desc in enumerate(color_descriptions):
                if i < len(colors_data):
                    color_desc['frequency'] = colors_data[i]['frequency']
                    color_desc['rgb'] = self._hex_to_rgb(color_desc['hex'])
            
            return color_descriptions
            
        except Exception as e:
            print(f"Claude color description error: {e}")
            # Fallback to simple descriptions
            return self._get_simple_descriptions(colors_data)
    
    def _get_simple_descriptions(self, colors_data):
        """
        Generate simple color descriptions without Claude.
        
        Args:
            colors_data: List of {hex, frequency} dicts
            
        Returns:
            list: List of color objects with basic descriptions
        """
        descriptions = []
        categories = ['primary', 'secondary', 'accent', 'background', 'text']
        
        for i, color in enumerate(colors_data):
            hex_code = color['hex']
            rgb = self._hex_to_rgb(hex_code)
            
            # Determine color name from RGB
            name = self._get_color_name_from_rgb(rgb)
            
            descriptions.append({
                'hex': hex_code,
                'name': f"{name} {i+1}",
                'category': categories[i] if i < len(categories) else 'other',
                'description': f"Used {color['frequency']} times throughout the application",
                'frequency': color['frequency'],
                'rgb': rgb
            })
        
        return descriptions
    
    def _hex_to_rgb(self, hex_color):
        """
        Convert hex color to RGB.
        
        Args:
            hex_color: Hex color string (#RRGGBB)
            
        Returns:
            dict: {r, g, b} values
        """
        hex_color = hex_color.lstrip('#')
        return {
            'r': int(hex_color[0:2], 16),
            'g': int(hex_color[2:4], 16),
            'b': int(hex_color[4:6], 16)
        }
    
    def _get_color_name_from_rgb(self, rgb):
        """
        Get a simple color name from RGB values.
        
        Args:
            rgb: {r, g, b} dict
            
        Returns:
            str: Color name
        """
        r, g, b = rgb['r'], rgb['g'], rgb['b']
        
        # Simple heuristics for common colors
        if r > 200 and g > 200 and b > 200:
            return "Light"
        elif r < 50 and g < 50 and b < 50:
            return "Dark"
        elif r > g and r > b:
            return "Red"
        elif g > r and g > b:
            return "Green"
        elif b > r and b > g:
            return "Blue"
        elif r > 150 and g > 150:
            return "Yellow"
        elif r > 150 and b > 150:
            return "Purple"
        elif g > 150 and b > 150:
            return "Cyan"
        else:
            return "Gray"
    
    def _determine_scheme_type(self, colors):
        """
        Determine if color scheme is dark or light.
        
        Args:
            colors: List of color objects
            
        Returns:
            str: 'dark', 'light', or 'mixed'
        """
        if not colors:
            return 'mixed'
        
        dark_count = 0
        light_count = 0
        
        for color in colors:
            rgb = color.get('rgb', {})
            r, g, b = rgb.get('r', 128), rgb.get('g', 128), rgb.get('b', 128)
            
            # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            if luminance < 0.5:
                dark_count += 1
            else:
                light_count += 1
        
        if dark_count > light_count * 1.5:
            return 'dark'
        elif light_count > dark_count * 1.5:
            return 'light'
        else:
            return 'mixed'
    
    def _get_default_palette(self):
        """
        Return default palette when no colors found.
        
        Returns:
            dict: Default color palette
        """
        return {
            'colors': [
                {
                    'hex': '#3B82F6',
                    'name': 'Primary Blue',
                    'category': 'primary',
                    'description': 'Default primary color',
                    'frequency': 1,
                    'rgb': {'r': 59, 'g': 130, 'b': 246}
                }
            ],
            'total_colors_found': 0,
            'scheme_type': 'mixed'
        }

