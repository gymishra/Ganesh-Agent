# SAP GUI Cross-Account Access Setup

## For New AWS Accounts

Copy and paste this script into a file called `setup-cross-account-access.sh` in your AWS account:

```bash
#!/bin/bash

# Setup script for new AWS accounts to access SAP GUI downloads
set -e

echo "🔧 Setting up cross-account access for SAP GUI downloads..."

# Variables
ROLE_NAME="WorkshopParticipantRole"
SOURCE_ACCOUNT="953841955037"

# Get current account ID
CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo "📋 Current AWS Account: ${CURRENT_ACCOUNT}"

# Create trust policy for the role
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${CURRENT_ACCOUNT}:root"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the role
echo "🔑 Creating WorkshopParticipantRole..."
aws iam create-role \
    --role-name ${ROLE_NAME} \
    --assume-role-policy-document file://trust-policy.json \
    --description "Role for accessing SAP GUI downloads from account ${SOURCE_ACCOUNT}" \
    --max-session-duration 3600 || echo "Role may already exist"

# Create policy for S3 access
cat > s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::sap-gui-download-gyanmis",
                "arn:aws:s3:::sap-gui-download-gyanmis/*"
            ]
        }
    ]
}
EOF

# Attach policy to role
echo "📎 Attaching S3 access policy..."
aws iam put-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-name S3AccessPolicy \
    --policy-document file://s3-policy.json

# Clean up temporary files
rm -f trust-policy.json s3-policy.json

echo "✅ Setup complete!"
echo ""
echo "🔗 To download SAP GUI files, use these commands:"
echo ""
echo "# 1. Assume the role"
echo "aws sts assume-role \\"
echo "  --role-arn arn:aws:iam::${CURRENT_ACCOUNT}:role/${ROLE_NAME} \\"
echo "  --role-session-name sap-gui-download"
echo ""
echo "# 2. Export the temporary credentials from step 1 output"
echo "export AWS_ACCESS_KEY_ID=<AccessKeyId>"
echo "export AWS_SECRET_ACCESS_KEY=<SecretAccessKey>"
echo "export AWS_SESSION_TOKEN=<SessionToken>"
echo ""
echo "# 3. Download the file"
echo "aws s3 cp s3://sap-gui-download-gyanmis/sap_gui.zip ./sap_gui.zip"
```

## Quick Setup Commands

1. **Create the script:**
```bash
cat > setup-cross-account-access.sh << 'EOF'
[paste the script content above]
EOF
```

2. **Make executable and run:**
```bash
chmod +x setup-cross-account-access.sh
./setup-cross-account-access.sh
```

## Where to Execute

- **Execute in**: The NEW AWS account that needs SAP GUI access
- **NOT in**: Account 953841955037 (source account)
- **Requires**: AWS CLI configured with admin permissions in the target account
