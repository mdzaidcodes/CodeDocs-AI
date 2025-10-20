"""
AWS Secrets Manager utility for retrieving secrets in production.
"""

import json
import os
import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name="codedocs-ai", region_name="us-east-1"):
    """
    Retrieve secret from AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region_name: AWS region where secret is stored
        
    Returns:
        dict: Secret key-value pairs
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Handle specific error codes
        error_code = e.response['Error']['Code']
        if error_code == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key
            print(f"❌ Secrets Manager can't decrypt the secret using the provided KMS key")
            raise e
        elif error_code == 'InternalServiceErrorException':
            # An error occurred on the server side
            print(f"❌ Internal service error from AWS Secrets Manager")
            raise e
        elif error_code == 'InvalidParameterException':
            # Invalid parameter in request
            print(f"❌ Invalid parameter provided to AWS Secrets Manager")
            raise e
        elif error_code == 'InvalidRequestException':
            # Invalid request to AWS Secrets Manager
            print(f"❌ Invalid request to AWS Secrets Manager")
            raise e
        elif error_code == 'ResourceNotFoundException':
            # Secret not found
            print(f"❌ Secret '{secret_name}' not found in AWS Secrets Manager")
            raise e
        else:
            print(f"❌ Error retrieving secret: {e}")
            raise e
    else:
        # Decrypts secret using the associated KMS key
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            # Binary secret (not common for environment variables)
            import base64
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)


def load_secrets_to_env(secret_name="codedocs-ai", region_name="us-east-1"):
    """
    Load secrets from AWS Secrets Manager and set them as environment variables.
    
    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region_name: AWS region where secret is stored
    """
    try:
        print(f"🔐 Loading secrets from AWS Secrets Manager: '{secret_name}'...")
        secrets = get_secret(secret_name, region_name)
        
        # Set each secret as an environment variable
        for key, value in secrets.items():
            os.environ[key] = str(value)
            print(f"✅ Loaded: {key}")
        
        print(f"✅ Successfully loaded {len(secrets)} secrets from AWS Secrets Manager")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load secrets from AWS Secrets Manager: {e}")
        print("⚠️  Falling back to local .env file (if available)")
        return False


def is_production():
    """
    Check if running in production environment.
    
    Returns:
        bool: True if production, False otherwise
    """
    # Check for common production indicators
    env = os.environ.get('ENVIRONMENT', '').lower()
    flask_env = os.environ.get('FLASK_ENV', '').lower()
    
    return (
        env in ['production', 'prod'] or
        flask_env == 'production' or
        os.environ.get('AWS_EXECUTION_ENV') is not None or  # Running on AWS
        os.environ.get('USE_SECRETS_MANAGER', '').lower() == 'true'
    )

