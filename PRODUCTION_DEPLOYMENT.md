# 🚀 Production Deployment Guide - AWS Secrets Manager

This guide explains how to deploy the CodeDocs AI backend to production using AWS Secrets Manager for secure configuration management.

---

## 📋 Prerequisites

- [x] Production server (AWS EC2, VPS, etc.)
- [x] AWS CLI configured on your **local machine** and **production server**
- [x] IAM permissions for AWS Secrets Manager
- [x] Backend `.env` file with all required variables

---

## 🔐 Step 1: Upload Secrets to AWS Secrets Manager

### Option A: Using the Setup Script (Recommended)

**On your local machine:**

```bash
cd backend

# Dry run to see what will be uploaded (doesn't actually upload)
python setup_aws_secret.py --env-file .env --dry-run

# Actually upload to AWS Secrets Manager
python setup_aws_secret.py --env-file .env --secret-name codedocs-ai --region us-east-1
```

**Expected output:**
```
📁 Loading environment variables from: .env

🔑 Found 15 environment variables:
   - DATABASE_URL: postgresql...
   - AWS_ACCESS_KEY_ID: AKIA...
   - AWS_SECRET_ACCESS_KEY: aBcDe...
   ... (masked values)

🚀 Uploading to AWS Secrets Manager...
   Secret Name: codedocs-ai
   Region: us-east-1

✅ Created secret: codedocs-ai
   ARN: arn:aws:secretsmanager:us-east-1:123456789:secret:codedocs-ai-AbCdEf

✅ Success! Your secrets are now stored in AWS Secrets Manager
```

### Option B: Manual Upload via AWS Console

1. Go to AWS Secrets Manager console
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Add key-value pairs for each environment variable:
   - `DATABASE_URL`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_BUCKET_NAME`
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - `JWT_SECRET_KEY`
   - `FRONTEND_URL`
   - (all other variables from your `.env`)
5. Name it `codedocs-ai`
6. Click "Store"

### Option C: AWS CLI

```bash
# Create a JSON file with your secrets (DO NOT commit this file!)
cat > secrets.json << 'EOF'
{
  "DATABASE_URL": "postgresql://user:pass@host:5432/db",
  "AWS_ACCESS_KEY_ID": "AKIA...",
  "AWS_SECRET_ACCESS_KEY": "...",
  "AWS_BUCKET_NAME": "your-bucket",
  "ANTHROPIC_API_KEY": "sk-ant-...",
  "OPENAI_API_KEY": "sk-...",
  "JWT_SECRET_KEY": "your-secret-key",
  "FRONTEND_URL": "https://yourdomain.com"
}
EOF

# Upload to Secrets Manager
aws secretsmanager create-secret \
    --name codedocs-ai \
    --description "CodeDocs AI production environment variables" \
    --secret-string file://secrets.json \
    --region us-east-1

# Clean up the file
rm secrets.json
```

---

## 🖥️ Step 2: Configure Production Server

### 2.1: Install AWS CLI (if not already installed)

```bash
# On your production server
sudo apt update
sudo apt install awscli -y

# Verify installation
aws --version
```

### 2.2: Configure AWS CLI Credentials

```bash
# Configure AWS CLI with your access key and secret key
aws configure
```

**Enter your AWS credentials:**
```
AWS Access Key ID [None]: AKIA...
AWS Secret Access Key [None]: ...
Default region name [None]: us-east-1
Default output format [None]: json
```

### 2.3: Test Access to Secrets Manager

```bash
# Test that you can retrieve the secret
aws secretsmanager get-secret-value \
    --secret-id codedocs-ai \
    --region us-east-1
```

**Expected output:**
```json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:123456789:secret:codedocs-ai-AbCdEf",
    "Name": "codedocs-ai",
    "VersionId": "...",
    "SecretString": "{\"DATABASE_URL\":\"...\",\"AWS_ACCESS_KEY_ID\":\"...\", ...}",
    "CreatedDate": "2025-01-20T12:00:00.000000+00:00"
}
```

✅ If you see this, you're good to go!

❌ If you get permission errors, check your IAM policy (see Step 3)

---

## 🔑 Step 3: IAM Permissions

Ensure your AWS user/role has these permissions:

### Minimum IAM Policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:codedocs-ai-*"
        }
    ]
}
```

### To attach this policy:

1. Go to IAM Console
2. Find your user/role
3. Click "Add permissions" → "Create inline policy"
4. Paste the JSON above (replace `YOUR_ACCOUNT_ID`)
5. Name it `CodeDocsSecretsAccess`
6. Create policy

---

## 📦 Step 4: Deploy Backend

### 4.1: Clone Repository

```bash
# On production server
cd /var/www  # or your preferred directory
git clone https://github.com/yourusername/CodeDocs-AI.git
cd CodeDocs-AI/backend
```

### 4.2: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.3: Set Production Environment Variables

**Create a production startup script:**

```bash
nano /var/www/CodeDocs-AI/backend/start-production.sh
```

**Add this content:**

```bash
#!/bin/bash

# Set environment to production (this triggers AWS Secrets Manager loading)
export ENVIRONMENT=production

# AWS configuration
export AWS_REGION=us-east-1
export SECRET_NAME=codedocs-ai

# Start the Flask application
cd /var/www/CodeDocs-AI/backend
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 600 app:app
```

**Make it executable:**

```bash
chmod +x /var/www/CodeDocs-AI/backend/start-production.sh
```

### 4.4: Create Systemd Service (Recommended)

```bash
sudo nano /etc/systemd/system/codedocs-backend.service
```

**Add this content:**

```ini
[Unit]
Description=CodeDocs AI Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/CodeDocs-AI/backend
Environment="ENVIRONMENT=production"
Environment="AWS_REGION=us-east-1"
Environment="SECRET_NAME=codedocs-ai"
Environment="PATH=/var/www/CodeDocs-AI/backend/venv/bin"
ExecStart=/var/www/CodeDocs-AI/backend/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 600 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable codedocs-backend
sudo systemctl start codedocs-backend
```

**Check status:**

```bash
sudo systemctl status codedocs-backend
```

**View logs:**

```bash
sudo journalctl -u codedocs-backend -f
```

---

## ✅ Step 5: Verify Deployment

### 5.1: Check Backend Logs

```bash
# View systemd logs
sudo journalctl -u codedocs-backend -n 50

# Or if using the startup script directly
tail -f /var/log/codedocs-backend.log
```

**You should see:**
```
🔐 Production mode: Loading configuration from AWS Secrets Manager...
🔐 Loading secrets from AWS Secrets Manager: 'codedocs-ai'...
✅ Loaded: DATABASE_URL
✅ Loaded: AWS_ACCESS_KEY_ID
✅ Loaded: AWS_SECRET_ACCESS_KEY
✅ Loaded: AWS_BUCKET_NAME
✅ Loaded: ANTHROPIC_API_KEY
✅ Loaded: OPENAI_API_KEY
✅ Loaded: JWT_SECRET_KEY
✅ Loaded: FRONTEND_URL
✅ Successfully loaded 15 secrets from AWS Secrets Manager
✅ Database connection successful
✅ S3 connection verified
Flask is running on http://0.0.0.0:5000
```

### 5.2: Test API Endpoint

```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
    "status": "healthy",
    "environment": "production",
    "secrets_source": "aws_secrets_manager"
}
```

---

## 🔄 Updating Secrets

### To update a secret value:

```bash
# Get current secret
aws secretsmanager get-secret-value \
    --secret-id codedocs-ai \
    --region us-east-1 \
    --query SecretString \
    --output text > current-secret.json

# Edit the JSON file
nano current-secret.json

# Update the secret
aws secretsmanager update-secret \
    --secret-id codedocs-ai \
    --secret-string file://current-secret.json \
    --region us-east-1

# Restart the backend to load new values
sudo systemctl restart codedocs-backend
```

**Or use the setup script again:**

```bash
# On your local machine, update .env then run:
python setup_aws_secret.py --env-file .env

# Then on production server:
sudo systemctl restart codedocs-backend
```

---

## 🐛 Troubleshooting

### Problem: "Secret not found"

**Solution:**
```bash
# Check secret exists
aws secretsmanager list-secrets --region us-east-1

# Check secret name matches
aws secretsmanager describe-secret --secret-id codedocs-ai --region us-east-1
```

### Problem: "Access Denied"

**Solution:**
- Check IAM permissions (Step 3)
- Verify AWS credentials are configured: `aws sts get-caller-identity`
- Check secret resource ARN in IAM policy

### Problem: "Backend falls back to .env"

**Solution:**
```bash
# Ensure ENVIRONMENT=production is set
echo $ENVIRONMENT

# If not set, add to systemd service or startup script
export ENVIRONMENT=production
```

### Problem: "Module not found: boto3"

**Solution:**
```bash
# Make sure boto3 is installed in your virtual environment
source venv/bin/activate
pip install boto3
```

### Problem: Backend loads wrong secrets

**Solution:**
```bash
# Check what the backend is loading
sudo journalctl -u codedocs-backend | grep "Loaded:"

# Verify secret contents
aws secretsmanager get-secret-value --secret-id codedocs-ai --region us-east-1
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files or `secrets.json` to Git**
2. **Rotate secrets regularly:**
   ```bash
   aws secretsmanager rotate-secret --secret-id codedocs-ai
   ```
3. **Use IAM roles instead of access keys when possible:**
   - Attach an IAM role to your EC2 instance
   - Remove `aws configure` credentials
   - Backend will automatically use instance role

4. **Enable CloudWatch Logs for Secrets Manager:**
   - Monitor who accesses secrets and when

5. **Use different secrets for staging/production:**
   - `codedocs-ai-staging`
   - `codedocs-ai-production`

---

## 🎉 Done!

Your backend is now running in production with secrets securely managed by AWS Secrets Manager!

**Key Points:**
- ✅ No `.env` file needed on production server
- ✅ Secrets stored securely in AWS
- ✅ Easy to rotate and update secrets
- ✅ Audit trail via AWS CloudTrail
- ✅ Falls back to `.env` in development

**Next Steps:**
1. Set up Nginx reverse proxy
2. Configure SSL certificate
3. Set up automated backups
4. Configure monitoring and alerts

