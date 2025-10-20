# ⚡ Quick Production Setup - AWS Secrets Manager

## 🎯 TL;DR

Get your backend running in production with AWS Secrets Manager in 5 minutes.

---

## Step 1: Upload Secrets (Local Machine)

```bash
cd backend
python setup_aws_secret.py --env-file .env
```

✅ Done! Your secrets are now in AWS Secrets Manager.

---

## Step 2: Configure Production Server

### SSH into your production server:

```bash
ssh user@your-server-ip
```

### Configure AWS CLI (one-time setup):

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter region: us-east-1
# Enter format: json
```

### Test it works:

```bash
aws secretsmanager get-secret-value --secret-id codedocs-ai --region us-east-1
```

✅ If you see JSON output with your secrets, you're good!

---

## Step 3: Deploy Backend

```bash
# Clone repo
cd /var/www
git clone https://github.com/yourusername/CodeDocs-AI.git
cd CodeDocs-AI/backend

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create startup script
nano start-production.sh
```

**Paste this:**

```bash
#!/bin/bash
export ENVIRONMENT=production
export AWS_REGION=us-east-1
export SECRET_NAME=codedocs-ai
cd /var/www/CodeDocs-AI/backend
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 600 app:app
```

**Make it executable and run:**

```bash
chmod +x start-production.sh
./start-production.sh
```

---

## ✅ Verify It Works

**Check logs - you should see:**

```
🔐 Production mode: Loading configuration from AWS Secrets Manager...
✅ Loaded: DATABASE_URL
✅ Loaded: AWS_ACCESS_KEY_ID
✅ Loaded: AWS_SECRET_ACCESS_KEY
... (all your secrets)
✅ Successfully loaded 15 secrets from AWS Secrets Manager
✅ Database connection successful
Flask is running on http://0.0.0.0:5000
```

**Test API:**

```bash
curl http://localhost:5000/api/health
```

---

## 🎉 Done!

Your backend is now running with secrets from AWS Secrets Manager!

---

## 🔄 To Update Secrets

```bash
# Local machine:
python setup_aws_secret.py --env-file .env

# Production server:
# Restart backend (it will reload secrets)
```

---

## 🐛 Troubleshooting

**"Secret not found"**
```bash
# Check secret exists
aws secretsmanager list-secrets
```

**"Access denied"**
```bash
# Check AWS credentials
aws sts get-caller-identity

# If empty, run aws configure again
```

**Backend falls back to .env**
```bash
# Make sure ENVIRONMENT=production is set
echo $ENVIRONMENT

# If empty:
export ENVIRONMENT=production
```

---

## 📚 Need More Details?

See `PRODUCTION_DEPLOYMENT.md` for:
- Systemd service setup
- IAM permissions
- Security best practices
- Detailed troubleshooting

---

**That's it! Your production backend is secure! 🔐**

