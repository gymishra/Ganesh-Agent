#!/usr/bin/env python3
"""
AWS Identity Center OAuth App Setup
Application created: arn:aws:sso::642286905124:application/ssoins-82593444a1047377/apl-f9557cd4e57df351
"""

print("✅ Application created in Identity Center!")
print("📍 Application ARN: arn:aws:sso::642286905124:application/ssoins-82593444a1047377/apl-f9557cd4e57df351")
print()
print("🔧 Manual setup required in AWS Console:")
print("1. Go to: https://ap-southeast-2.console.aws.amazon.com/singlesignon/identity/home")
print("2. Navigate: Applications > Customer managed applications")
print("3. Find: 'Quip-Document-Uploader'")
print("4. Click 'Edit application'")
print("5. Set Application type: OAuth 2.0")
print("6. Add Redirect URI: http://localhost:5000/sso-callback")
print("7. Copy the Client ID")
print()
print("🔄 Update your Flask app with the Client ID:")

# Generate the updated Flask app configuration
config_update = '''
# Update this in final_app_sso_fixed.py:
SSO_CONFIG = {
    'start_url': 'https://d-9767435275.awsapps.com/start',
    'client_id': 'YOUR_CLIENT_ID_FROM_CONSOLE',  # Replace with actual Client ID
    'redirect_uri': 'http://localhost:5000/sso-callback'
}
'''

print(config_update)
print("🚀 Then restart your Flask app for real SSO integration!")
