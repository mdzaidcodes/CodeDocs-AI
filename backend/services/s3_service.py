"""
AWS S3 service for file upload and download operations.
"""

import boto3
from botocore.exceptions import ClientError
from config.settings import Config
import os


class S3Service:
    """Service for interacting with AWS S3."""
    
    def __init__(self):
        """Initialize S3 client with AWS credentials."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        self.bucket_name = Config.S3_BUCKET_NAME
    
    def upload_file(self, file_obj, s3_key):
        """
        Upload a file to S3.
        
        Args:
            file_obj: File object or file path
            s3_key: S3 object key (path in bucket)
            
        Returns:
            str: S3 URL of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Upload file
            if isinstance(file_obj, str):
                # File path provided
                self.s3_client.upload_file(file_obj, self.bucket_name, s3_key)
            else:
                # File object provided
                self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key)
            
            # Return S3 URL
            return f"s3://{self.bucket_name}/{s3_key}"
        
        except ClientError as e:
            print(f"S3 upload error: {e}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def download_file(self, s3_key, local_path):
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key
            local_path: Local path to save file
            
        Returns:
            str: Local file path
            
        Raises:
            Exception: If download fails
        """
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            
            return local_path
        
        except ClientError as e:
            print(f"S3 download error: {e}")
            raise Exception(f"Failed to download file from S3: {str(e)}")
    
    def get_file_content(self, s3_key):
        """
        Get file content from S3 as string.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            str: File content
            
        Raises:
            Exception: If read fails
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return content
        
        except ClientError as e:
            print(f"S3 read error: {e}")
            raise Exception(f"Failed to read file from S3: {str(e)}")
    
    def list_files(self, prefix):
        """
        List files in S3 with given prefix.
        
        Args:
            prefix: S3 key prefix
            
        Returns:
            list: List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        
        except ClientError as e:
            print(f"S3 list error: {e}")
            return []
    
    def delete_file(self, s3_key):
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            bool: True if successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
    
    def delete_folder(self, prefix):
        """
        Delete all files with given prefix (folder).
        
        Args:
            prefix: S3 key prefix
            
        Returns:
            int: Number of files deleted
        """
        try:
            # List all files with prefix
            files = self.list_files(prefix)
            
            if not files:
                return 0
            
            # Delete files
            objects = [{'Key': key} for key in files]
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects}
            )
            
            deleted = len(response.get('Deleted', []))
            return deleted
        
        except ClientError as e:
            print(f"S3 delete folder error: {e}")
            return 0
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generate a presigned URL for temporary file access.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        
        except ClientError as e:
            print(f"S3 presigned URL error: {e}")
            return None

