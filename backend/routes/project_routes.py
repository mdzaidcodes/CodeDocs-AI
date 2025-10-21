"""
Project routes for managing code documentation projects.
Includes upload, GitHub, documentation, security, improvements, and chat.
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import json
import io
from threading import Thread
from datetime import datetime

from utils.decorators import require_auth, handle_errors
from utils.validators import validate_project_name, validate_github_url, validate_file_extension
from models.project import Project
from models.documentation import Documentation
from models.security_finding import SecurityFinding
from models.code_improvement import CodeImprovement
from models.user_quota import UserQuota
from services.s3_service import S3Service
from services.github_service import GitHubService
from services.code_analyzer import CodeAnalyzer
from services.documentation_generator import DocumentationGenerator
from services.security_analyzer import SecurityAnalyzer
from services.code_quality_analyzer import CodeQualityAnalyzer
from services.rag_service import RAGService
from services.export_service import ExportService
from services.color_analyzer import ColorAnalyzer

# Create blueprint
project_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


def process_project_async(project_id, files_dict):
    """
    Background task to process project asynchronously.
    
    Args:
        project_id: UUID of the project
        files_dict: Dict of {file_path: content}
    """
    try:
        # Initialize S3 service for uploads
        s3_service = S3Service()
        
        # Step 1: Analyze code structure (10%)
        Project.update_status(project_id, 'processing', 10, 'Analyzing code structure...')
        analysis = CodeAnalyzer.analyze_files(files_dict)
        
        # Update project with analysis results
        Project.update(
            project_id,
            primary_language=analysis.get('primary_language'),
            total_files=analysis.get('file_count'),
            total_lines=analysis.get('total_lines', 0),
            technologies=json.dumps(analysis.get('technologies', [])),
            file_structure=json.dumps(analysis.get('file_structure', {}))
        )
        
        # Step 1.5: Analyze color palette (20%)
        Project.update_status(project_id, 'processing', 20, 'Analyzing color palette...')
        try:
            color_analyzer = ColorAnalyzer()
            project_data = Project.find_by_id(project_id)
            color_palette = color_analyzer.analyze_colors(files_dict, project_data.get('name', 'Project'))
            
            # Store color palette in project
            Project.update(
                project_id,
                color_palette=json.dumps(color_palette)
            )
            print(f"✅ Color palette analyzed: {len(color_palette.get('colors', []))} colors found")
        except Exception as e:
            print(f"⚠️ Color analysis failed: {e}")
            # Don't fail the entire process if color analysis fails
        
        # Step 2: Generate documentation (40%)
        Project.update_status(project_id, 'processing', 40, 'Generating documentation...')
        doc_gen = DocumentationGenerator()
        project = Project.find_by_id(project_id)
        doc_result = doc_gen.generate(project['name'], files_dict)
        
        # Store documentation in database
        # Calculate generation time (handle datetime object from database)
        created_at = project.get('created_at')
        if created_at:
            try:
                # Remove timezone info if present for calculation
                if hasattr(created_at, 'tzinfo') and created_at.tzinfo:
                    created_at = created_at.replace(tzinfo=None)
                generation_time = int((datetime.now() - created_at).total_seconds())
            except:
                generation_time = None
        else:
            generation_time = None
        
        word_count = len(doc_result['content'].split()) if doc_result.get('content') else 0
        
        Documentation.create(
            project_id=project_id,
            markdown_content=doc_result['content'],
            sections=doc_result.get('sections', []),
            word_count=word_count,
            generation_time_seconds=generation_time
        )
        
        # Upload documentation to S3
        project_data = Project.find_by_id(project_id)
        if project_data and project_data.get('s3_doc_path'):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.md') as temp_file:
                temp_file.write(doc_result['content'])
                temp_doc_path = temp_file.name
            
            s3_service.upload_file(temp_doc_path, project_data['s3_doc_path'])
            os.unlink(temp_doc_path)
        
        # ===== DOCUMENTATION IS READY - MARK AS COMPLETED =====
        # User can view documentation NOW while security/quality/embeddings run in background
        Project.update_status(project_id, 'completed', 100, 'Documentation ready')
        print(f"✅ Documentation completed for project {project_id} - User can view now!")
        
        # ===== BACKGROUND TASKS (Don't block user) =====
        # Step 3: Security Analysis (in background - analyzes ALL files)
        print(f"Starting background security analysis for project {project_id}...")
        try:
            sec_analyzer = SecurityAnalyzer()
            sec_findings = sec_analyzer.analyze_project(files_dict)  # Analyzes ALL files
            
            # Store security findings
            for finding in sec_findings:
                SecurityFinding.create(
                    project_id=project_id,
                    severity=finding['severity'],
                    title=finding['title'],
                    description=finding['description'],
                    file_path=finding['file_path'],
                    line_number=finding.get('line_number'),
                    recommendation=finding['recommendation'],
                    category=finding['category'],
                    code_snippet=finding.get('code_snippet'),
                    cwe_id=finding.get('cwe_id'),
                    cvss_score=finding.get('cvss_score'),
                    references=json.dumps(finding.get('references', []))
                )
            
            # Calculate security score
            security_score = sec_analyzer.calculate_security_score(sec_findings)
            vulnerabilities_count = len([f for f in sec_findings if f['severity'] in ['critical', 'high']])
            Project.update(
                project_id,
                security_score=security_score,
                vulnerabilities_count=vulnerabilities_count
            )
            
            # Upload security analysis to S3
            project_data = Project.find_by_id(project_id)
            if project_data and project_data.get('s3_analysis_path'):
                security_analysis_path = f"{project_data['s3_analysis_path']}security_findings.json"
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.json') as temp_file:
                    json.dump({
                        'findings': sec_findings,
                        'security_score': security_score,
                        'vulnerabilities_count': vulnerabilities_count,
                        'analyzed_at': str(datetime.now())
                    }, temp_file, indent=2)
                    temp_sec_path = temp_file.name
                
                s3_service.upload_file(temp_sec_path, security_analysis_path)
                os.unlink(temp_sec_path)
            
            print(f"✅ Security analysis completed for project {project_id}")
        except Exception as sec_error:
            print(f"⚠️ Security analysis failed for {project_id}: {sec_error}")
        
        # Step 4: Code Quality Analysis (in background - analyzes ALL files)
        print(f"Starting background code quality analysis for project {project_id}...")
        try:
            quality_analyzer = CodeQualityAnalyzer()
            improvements = quality_analyzer.analyze_project(files_dict)  # Analyzes ALL files
            
            # Store improvements
            for improvement in improvements:
                CodeImprovement.create(
                    project_id=project_id,
                    category=improvement.get('category', 'general'),
                    title=improvement['title'],
                    description=improvement['description'],
                    file_path=improvement['file_path'],
                    line_number=improvement.get('line_number'),
                    suggestion=improvement['suggestion'],
                    impact_level=improvement.get('impact_level', 'medium'),
                    code_snippet=improvement.get('code_snippet'),
                    improved_code=improvement.get('improved_code'),
                    estimated_effort=improvement.get('estimated_effort')
                )
            
            # Upload code quality analysis to S3
            project_data = Project.find_by_id(project_id)
            if project_data and project_data.get('s3_analysis_path'):
                quality_analysis_path = f"{project_data['s3_analysis_path']}code_improvements.json"
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.json') as temp_file:
                    json.dump({
                        'improvements': improvements,
                        'total_improvements': len(improvements),
                        'analyzed_at': str(datetime.now())
                    }, temp_file, indent=2)
                    temp_qual_path = temp_file.name
                
                s3_service.upload_file(temp_qual_path, quality_analysis_path)
                os.unlink(temp_qual_path)
            
            print(f"✅ Code quality analysis completed for project {project_id}")
        except Exception as qual_error:
            print(f"⚠️ Code quality analysis failed for {project_id}: {qual_error}")
        
        # Step 5: Create embeddings for RAG (in background)
        print(f"Starting background embedding creation for project {project_id}...")
        try:
            rag_service = RAGService()
            rag_service.reindex_project(project_id, files_dict, doc_result['sections'])
            print(f"✅ Embeddings completed for project {project_id}")
            Project.update_status(project_id, 'completed', 100, 'All analysis complete - Chat ready!')
        except Exception as embed_error:
            print(f"⚠️ Embedding creation failed for {project_id}: {embed_error}")
            # Don't fail the whole project if embeddings fail - docs are still viewable
            Project.update_status(project_id, 'completed', 100, 'Documentation ready (chat unavailable)')
        
        print(f"Project {project_id} fully processed")
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing project {project_id}: {e}")
        print(f"Full traceback:\n{error_details}")
        Project.update_status(project_id, 'failed', 0, f'Processing failed: {str(e)}')


@project_bp.route('', methods=['GET'])
@require_auth
@handle_errors
def get_projects(user_id):
    """
    Get all projects for authenticated user.
    
    GET /api/projects
    Returns: {success, data: {projects: [...]}}
    """
    projects = Project.find_by_user_id(user_id)
    
    return jsonify({
        'success': True,
        'data': {
            'projects': projects
        }
    }), 200


@project_bp.route('/<project_id>', methods=['GET'])
@require_auth
@handle_errors
def get_project(user_id, project_id):
    """
    Get specific project details.
    
    GET /api/projects/:id
    Returns: {success, data: {...project}}
    """
    project = Project.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    return jsonify({
        'success': True,
        'data': project
    }), 200


@project_bp.route('/upload', methods=['POST'])
@require_auth
@handle_errors
def upload_project(user_id):
    """
    Upload code files to create a project.
    Supports entire folder uploads with nested structure.
    
    POST /api/projects/upload
    Form Data: project_name, files[], file_paths[] (relative paths for each file)
    Returns: {success, data: {project_id, status}}
    """
    # Validate project name
    project_name = request.form.get('project_name')
    is_valid, error = validate_project_name(project_name)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # Get uploaded files
    files = request.files.getlist('files')
    if not files:
        return jsonify({
            'success': False,
            'error': 'No files uploaded'
        }), 400
    
    # Get file paths (relative paths preserving folder structure)
    file_paths = request.form.getlist('file_paths')
    
    # If file_paths not provided, use filenames
    if not file_paths or len(file_paths) != len(files):
        file_paths = [file.filename for file in files]
    
    # Check daily project creation quota (always active)
    has_quota, remaining, reset_time = UserQuota.check_quota_available(user_id)
    
    if not has_quota:
        return jsonify({
            'success': False,
            'error': 'Daily quota exceeded',
            'error_code': 'QUOTA_EXCEEDED',
            'message': "You've reached your limit of 3 projects for today. Your quota will reset tomorrow. Thank you for your patience!",
            'quota_info': {
                'max_projects_per_day': 3,
                'projects_created_today': 3,
                'remaining_quota': 0,
                'quota_reset_at': reset_time.isoformat(),
                'timezone': 'GMT+4'
            }
        }), 429  # 429 Too Many Requests
    
    # Create project with proper S3 paths
    project = Project.create(
        user_id=user_id,
        name=project_name,
        source_type='upload'
    )
    
    # Increment quota counter (always active)
    UserQuota.increment_quota(user_id)
    
    project_id = project['id']
    
    # Generate S3 paths after project creation (need project_id)
    s3_code_path = f"users/{user_id}/projects/{project_id}/code/"
    s3_doc_path = f"users/{user_id}/projects/{project_id}/documentation/generated_doc.md"
    s3_analysis_path = f"users/{user_id}/projects/{project_id}/analysis/"
    
    # Update project with S3 paths
    Project.update(
        project_id,
        s3_code_path=s3_code_path,
        s3_doc_path=s3_doc_path,
        s3_analysis_path=s3_analysis_path
    )
    
    # Upload files to S3 and collect content
    s3_service = S3Service()
    files_dict = {}
    
    for i, file in enumerate(files):
        if file.filename and validate_file_extension(file.filename):
            # Get relative path for this file (preserves folder structure)
            relative_path = file_paths[i] if i < len(file_paths) else file.filename
            
            # Make S3 compatible (replace backslashes, remove leading slashes)
            s3_compatible_path = relative_path.replace('\\', '/').lstrip('/')
            
            # If the path starts with a folder name, keep it
            # Otherwise, just use the filename
            if '/' in s3_compatible_path:
                # Has folder structure - preserve it
                file_key = s3_compatible_path
            else:
                # Just a filename - use it as is
                file_key = s3_compatible_path
            
            s3_key = f"{s3_code_path}{file_key}"
            
            print(f"[DEBUG] Uploading: {relative_path} → S3: {s3_key}")
            
            # Read file content
            content = file.read().decode('utf-8', errors='ignore')
            files_dict[file_key] = content
            
            # Upload to S3
            file.seek(0)
            s3_service.upload_file(file, s3_key)
    
    if not files_dict:
        return jsonify({
            'success': False,
            'error': 'No valid code files found'
        }), 400
    
    print(f"[DEBUG] Uploaded {len(files_dict)} files with folder structure preserved")
    
    # Start background processing
    thread = Thread(target=process_project_async, args=(project_id, files_dict))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'data': {
            'project_id': project_id,
            'status': 'processing'
        },
        'message': 'Files uploaded successfully. Processing started.'
    }), 201


@project_bp.route('/github', methods=['POST'])
@require_auth
@handle_errors
def connect_github(user_id):
    """
    Connect GitHub repository to create a project.
    
    POST /api/projects/github
    Body: {project_name, github_url, github_branch, github_pat?}
    Returns: {success, data: {project_id, status}}
    """
    data = request.get_json()
    
    # Validate project name
    project_name = data.get('project_name')
    is_valid, error = validate_project_name(project_name)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # Validate GitHub URL
    github_url = data.get('github_url')
    if not validate_github_url(github_url):
        return jsonify({
            'success': False,
            'error': 'Invalid GitHub URL'
        }), 400
    
    github_branch = data.get('github_branch', 'main')
    github_pat = data.get('github_pat')
    
    # Check daily project creation quota (always active)
    has_quota, remaining, reset_time = UserQuota.check_quota_available(user_id)
    
    if not has_quota:
        return jsonify({
            'success': False,
            'error': 'Daily quota exceeded',
            'error_code': 'QUOTA_EXCEEDED',
            'message': "You've reached your limit of 3 projects for today. Your quota will reset tomorrow. Thank you for your patience!",
            'quota_info': {
                'max_projects_per_day': 3,
                'projects_created_today': 3,
                'remaining_quota': 0,
                'quota_reset_at': reset_time.isoformat(),
                'timezone': 'GMT+4'
            }
        }), 429  # 429 Too Many Requests
    
    # Create project first
    project = Project.create(
        user_id=user_id,
        name=project_name,
        source_type='github_public' if not github_pat else 'github_private',
        github_url=github_url,
        github_branch=github_branch
    )
    
    # Increment quota counter (always active)
    UserQuota.increment_quota(user_id)
    
    project_id = project['id']
    
    # Generate S3 paths after project creation (need project_id)
    s3_code_path = f"users/{user_id}/projects/{project_id}/code/"
    s3_doc_path = f"users/{user_id}/projects/{project_id}/documentation/generated_doc.md"
    s3_analysis_path = f"users/{user_id}/projects/{project_id}/analysis/"
    
    # Update project with S3 paths
    Project.update(
        project_id,
        s3_code_path=s3_code_path,
        s3_doc_path=s3_doc_path,
        s3_analysis_path=s3_analysis_path
    )
    
    try:
        # Clone repository
        github_service = GitHubService(access_token=github_pat)
        repo_path = github_service.clone_repository(github_url, github_branch)
        
        # Get file tree
        files_list = github_service.get_file_tree(repo_path)
        print(f"[DEBUG] Found {len(files_list)} files in repository")
        print(f"[DEBUG] Sample files: {files_list[:10]}")
        
        # Read files and upload to S3
        s3_service = S3Service()
        files_dict = {}
        valid_file_count = 0
        
        for file_path in files_list:
            if validate_file_extension(file_path):
                valid_file_count += 1
                content = github_service.read_file(repo_path, file_path)
                if content:
                    # Make file path S3 compatible (replace backslashes)
                    s3_compatible_path = file_path.replace('\\', '/')
                    files_dict[s3_compatible_path] = content
                    
                    # Upload to S3 with proper folder structure
                    s3_key = f"{s3_code_path}{s3_compatible_path}"
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    
                    s3_service.upload_file(temp_file_path, s3_key)
                    os.unlink(temp_file_path)
        
        print(f"[DEBUG] Valid files with allowed extensions: {valid_file_count}")
        print(f"[DEBUG] Successfully read and stored: {len(files_dict)} files")
        
        # Cleanup cloned repo
        github_service.cleanup_repo(repo_path)
        
        if not files_dict:
            return jsonify({
                'success': False,
                'error': f'No valid code files found in repository. Found {len(files_list)} total files, {valid_file_count} with valid extensions.'
            }), 400
        
        # Start background processing
        thread = Thread(target=process_project_async, args=(project_id, files_dict))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'status': 'processing'
            },
            'message': 'Repository connected. Processing started.'
        }), 201
    
    except Exception as e:
        # Update project status to failed
        Project.update_status(project_id, 'failed', 0, str(e))
        raise


@project_bp.route('/<project_id>/status', methods=['GET'])
@require_auth
@handle_errors
def get_project_status(user_id, project_id):
    """
    Get project processing status for polling.
    
    GET /api/projects/:id/status
    Returns: {success, data: {status, progress, current_step}}
    """
    project = Project.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    return jsonify({
        'success': True,
        'data': {
            'status': project['status'],
            'progress': project.get('progress_percentage', 0),
            'progress_percentage': project.get('progress_percentage', 0),
            'progress_stage': project.get('progress_stage', ''),
            'current_step': project.get('progress_stage', ''),  # For backwards compatibility
            'message': f"Processing is {project.get('progress_percentage', 0)}% complete"
        }
    }), 200


@project_bp.route('/<project_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_project(user_id, project_id):
    """
    Delete a project and all its data.
    
    DELETE /api/projects/:id
    Returns: {success, message}
    """
    project = Project.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    # Delete from S3
    s3_service = S3Service()
    s3_service.delete_folder(f"projects/{project_id}/")
    
    # Delete from database (cascades to related data)
    Project.delete(project_id)
    
    return jsonify({
        'success': True,
        'message': 'Project deleted successfully'
    }), 200


@project_bp.route('/<project_id>/documentation', methods=['GET'])
@require_auth
@handle_errors
def get_documentation(user_id, project_id):
    """
    Get project documentation.
    
    GET /api/projects/:id/documentation
    Returns: {success, data: {id, content, sections, ...}}
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    documentation = Documentation.find_by_project_id(project_id)
    
    if not documentation:
        return jsonify({
            'success': False,
            'error': 'Documentation not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': documentation
    }), 200


@project_bp.route('/<project_id>/documentation', methods=['PUT'])
@require_auth
@handle_errors
def update_documentation(user_id, project_id):
    """
    Update project documentation in both database and S3.
    
    PUT /api/projects/:id/documentation
    Body: {content}
    Returns: {success, message}
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    # Update documentation in database
    Documentation.update(project_id, content)
    
    # Also upload to S3
    try:
        project = Project.find_by_id(project_id)
        if project and project.get('s3_doc_path'):
            s3_service = S3Service()
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.md') as temp_file:
                temp_file.write(content)
                temp_doc_path = temp_file.name
            
            s3_service.upload_file(temp_doc_path, project['s3_doc_path'])
            os.unlink(temp_doc_path)
            
            print(f"✅ Documentation updated in S3 for project {project_id}")
    except Exception as e:
        print(f"⚠️ Failed to update S3 documentation: {e}")
        # Don't fail the request if S3 upload fails - database is the source of truth
    
    return jsonify({
        'success': True,
        'message': 'Documentation updated successfully'
    }), 200


@project_bp.route('/<project_id>/documentation/export', methods=['GET'])
@require_auth
@handle_errors
def export_documentation(user_id, project_id):
    """
    Export project documentation in various formats.
    
    GET /api/projects/:id/documentation/export?format=md|docx|pdf
    Query params:
        - format: Export format (md, docx, pdf). Default: md
    Returns: File download with appropriate headers
    
    Export process:
    1. Verify project ownership and fetch documentation
    2. Get project details (name) for file naming
    3. Call ExportService to generate file in requested format
    4. Return file with proper content-type and download headers
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    # Get export format from query params
    export_format = request.args.get('format', 'md').lower()
    
    # Validate format
    if export_format not in ['md', 'docx', 'pdf']:
        return jsonify({
            'success': False,
            'error': 'Invalid format. Supported formats: md, docx, pdf'
        }), 400
    
    # Get project details
    project = Project.find_by_id(project_id)
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found'
        }), 404
    
    # Get documentation content
    doc = Documentation.find_by_project_id(project_id)
    if not doc:
        return jsonify({
            'success': False,
            'error': 'Documentation not found'
        }), 404
    
    documentation_content = doc.get('markdown_content', '')
    project_name = project.get('name', 'Project')
    
    # Initialize export service
    export_service = ExportService()
    
    try:
        # Generate export based on format
        if export_format == 'md':
            # Export as Markdown
            file_content, filename = export_service.export_markdown(
                project_name, 
                documentation_content
            )
            mimetype = 'text/markdown'
            
        elif export_format == 'docx':
            # Export as DOCX (Microsoft Word)
            file_content, filename = export_service.export_docx(
                project_name, 
                documentation_content
            )
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
        elif export_format == 'pdf':
            # Export as PDF
            file_content, filename = export_service.export_pdf(
                project_name, 
                documentation_content
            )
            mimetype = 'application/pdf'
        
        # Create file-like object for sending
        file_obj = io.BytesIO(file_content)
        file_obj.seek(0)
        
        # Send file with appropriate headers
        return send_file(
            file_obj,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Failed to export documentation: {str(e)}'
        }), 500


@project_bp.route('/<project_id>/security', methods=['GET'])
@require_auth
@handle_errors
def get_security_findings(user_id, project_id):
    """
    Get security findings for a project.
    
    GET /api/projects/:id/security
    Returns: {success, data: {findings: [...]}}
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    findings = SecurityFinding.find_by_project_id(project_id)
    
    return jsonify({
        'success': True,
        'data': {
            'findings': findings
        }
    }), 200


@project_bp.route('/<project_id>/improvements', methods=['GET'])
@require_auth
@handle_errors
def get_code_improvements(user_id, project_id):
    """
    Get code improvement suggestions for a project.
    
    GET /api/projects/:id/improvements
    Returns: {success, data: {improvements: [...]}}
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    improvements = CodeImprovement.find_by_project_id(project_id)
    
    return jsonify({
        'success': True,
        'data': {
            'improvements': improvements
        }
    }), 200


@project_bp.route('/<project_id>/chat', methods=['POST'])
@require_auth
@handle_errors
def chat_with_project(user_id, project_id):
    """
    Chat with RAG assistant about the project.
    
    POST /api/projects/:id/chat
    Body: {message}
    Returns: {success, data: {message, sources}}
    """
    # Check ownership
    if not Project.check_ownership(project_id, user_id):
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({
            'success': False,
            'error': 'Message is required'
        }), 400
    
    # Check daily message quota (always active)
    has_quota, remaining, reset_time = UserQuota.check_message_quota_available(user_id)
    
    if not has_quota:
        return jsonify({
            'success': False,
            'error': 'Message quota exceeded',
            'error_code': 'MESSAGE_QUOTA_EXCEEDED',
            'message': "You've reached your daily limit of 5 messages. Your quota will reset tomorrow. Thank you for your understanding!",
            'quota_info': {
                'max_messages_per_day': 5,
                'messages_sent_today': 5,
                'remaining_quota': 0,
                'quota_reset_at': reset_time.isoformat(),
                'timezone': 'GMT+4'
            }
        }), 429  # 429 Too Many Requests
    
    # Get answer from RAG service
    rag_service = RAGService()
    response = rag_service.answer_question(project_id, message)
    
    # Increment message quota counter (always active)
    UserQuota.increment_message_quota(user_id)
    
    return jsonify({
        'success': True,
        'data': response
    }), 200


@project_bp.route('/quota', methods=['GET'])
@require_auth
@handle_errors
def get_quota_status(user_id):
    """
    Get current user's project quota status.
    
    GET /api/projects/quota
    Returns: {success, data: {quota_info}}
    """
    from config.settings import Config
    
    # Get quota statistics (always active)
    quota_stats = UserQuota.get_quota_stats(user_id)
    
    return jsonify({
        'success': True,
        'data': {
            'environment': Config.FLASK_ENV,
            'quota_enabled': True,
            **quota_stats
        }
    }), 200


@project_bp.route('/chat/quota', methods=['GET'])
@require_auth
@handle_errors
def get_message_quota_status(user_id):
    """
    Get current user's message quota status.
    
    GET /api/projects/chat/quota
    Returns: {success, data: {quota_info}}
    """
    from config.settings import Config
    
    # Get message quota statistics (always active)
    quota_stats = UserQuota.get_message_quota_stats(user_id)
    
    return jsonify({
        'success': True,
        'data': {
            'environment': Config.FLASK_ENV,
            'quota_enabled': True,
            **quota_stats
        }
    }), 200

