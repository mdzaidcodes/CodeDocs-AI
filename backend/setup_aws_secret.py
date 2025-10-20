"""
Script to create or update AWS Secrets Manager secret for production.
Run this script once to set up your production secrets.

Usage:
    python setup_aws_secret.py --env-file .env
"""

import json
import argparse
import boto3
from botocore.exceptions import ClientError


def load_env_file(env_file_path):
    """
    Load environment variables from .env file.
    
    Args:
        env_file_path: Path to .env file
        
    Returns:
        dict: Environment variables as key-value pairs
    """
    secrets = {}
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                secrets[key] = value
    
    return secrets


def create_or_update_secret(secret_name, secrets_dict, region_name='us-east-1'):
    """
    Create or update a secret in AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret
        secrets_dict: Dictionary of key-value pairs to store
        region_name: AWS region
    """
    client = boto3.client('secretsmanager', region_name=region_name)
    
    secret_string = json.dumps(secrets_dict)
    
    try:
        # Try to create the secret
        response = client.create_secret(
            Name=secret_name,
            SecretString=secret_string,
            Description='CodeDocs AI production environment variables'
        )
        print(f"✅ Created secret: {secret_name}")
        print(f"   ARN: {response['ARN']}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            # Secret already exists, update it instead
            response = client.update_secret(
                SecretId=secret_name,
                SecretString=secret_string
            )
            print(f"✅ Updated existing secret: {secret_name}")
            print(f"   ARN: {response['ARN']}")
        else:
            print(f"❌ Error: {e}")
            raise e


def main():
    parser = argparse.ArgumentParser(
        description='Create or update AWS Secrets Manager secret from .env file'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    parser.add_argument(
        '--secret-name',
        default='codedocs-ai',
        help='Name of the secret in AWS Secrets Manager (default: codedocs-ai)'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be uploaded without actually doing it'
    )
    
    args = parser.parse_args()
    
    print(f"📁 Loading environment variables from: {args.env_file}")
    secrets = load_env_file(args.env_file)
    
    print(f"\n🔑 Found {len(secrets)} environment variables:")
    for key in secrets.keys():
        # Mask sensitive values
        value = secrets[key]
        if len(value) > 20:
            masked_value = value[:10] + '...' + value[-5:]
        else:
            masked_value = value[:3] + '...' + value[-2:]
        print(f"   - {key}: {masked_value}")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN: Would upload to AWS Secrets Manager:")
        print(f"   Secret Name: {args.secret_name}")
        print(f"   Region: {args.region}")
        print("\n⚠️  Run without --dry-run to actually create/update the secret")
        return
    
    print(f"\n🚀 Uploading to AWS Secrets Manager...")
    print(f"   Secret Name: {args.secret_name}")
    print(f"   Region: {args.region}")
    
    try:
        create_or_update_secret(args.secret_name, secrets, args.region)
        
        print(f"\n✅ Success! Your secrets are now stored in AWS Secrets Manager")
        print(f"\n📝 On your production server, set these environment variables:")
        print(f"   export ENVIRONMENT=production")
        print(f"   export AWS_REGION={args.region}")
        print(f"   export SECRET_NAME={args.secret_name}")
        print(f"\n   Or add to your systemd service file / startup script")
        
    except Exception as e:
        print(f"\n❌ Failed to upload secrets: {e}")
        print(f"\n💡 Make sure you have:")
        print(f"   1. AWS CLI configured (run: aws configure)")
        print(f"   2. Proper IAM permissions for Secrets Manager")
        print(f"   3. Network access to AWS Secrets Manager")


if __name__ == '__main__':
    main()

