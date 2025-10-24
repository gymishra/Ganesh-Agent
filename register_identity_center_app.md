# Register Quip Uploader in AWS Identity Center

## Step 1: Access Identity Center Console

1. Go to AWS Console → **AWS IAM Identity Center**
2. Or directly: https://console.aws.amazon.com/singlesignon/

## Step 2: Create Application

1. In Identity Center console, click **Applications** in left menu
2. Click **Add application**
3. Choose **Add custom SAML 2.0 application** OR **Add custom OIDC application**

## Step 3: Configure Application (OIDC Method - Recommended)

**Application Details:**
- **Application name:** `Quip Document Uploader`
- **Description:** `Web application for uploading Quip documents to S3`
- **Application type:** `Web application`

**Redirect URLs:**
- `http://127.0.0.1:5000/callback`
- `http://172.30.89.194:5000/callback`

**Sign-out URLs:**
- `http://127.0.0.1:5000/logout`
- `http://172.30.89.194:5000/logout`

## Step 4: Get Client Credentials

After creating the application, you'll get:
- **Client ID** (e.g., `abcd1234-5678-90ef-ghij-klmnopqrstuv`)
- **Client Secret** (e.g., `secret-key-here`)
- **Authorization Endpoint** (e.g., `https://d-9767435275.awsapps.com/start/oauth2/authorize`)
- **Token Endpoint** (e.g., `https://d-9767435275.awsapps.com/start/oauth2/token`)

## Step 5: Assign Users/Groups

1. In the application, go to **Assigned users** tab
2. Click **Assign users** or **Assign groups**
3. Select the users who should have access to the Quip Uploader

## Step 6: Update Application Configuration

Replace these values in the Flask app:

```python
OIDC_CLIENT_ID = "your-actual-client-id"
OIDC_CLIENT_SECRET = "your-actual-client-secret"
OIDC_AUTHORIZATION_ENDPOINT = "https://d-9767435275.awsapps.com/start/oauth2/authorize"
OIDC_TOKEN_ENDPOINT = "https://d-9767435275.awsapps.com/start/oauth2/token"
```

## Alternative: Quick Manual Registration

If you can't access Identity Center admin:

1. Ask your AWS administrator to register the application
2. Provide them these details:
   - **App Name:** Quip Document Uploader
   - **Redirect URIs:** http://127.0.0.1:5000/callback, http://172.30.89.194:5000/callback
   - **Type:** Web Application (OIDC)
   - **Scopes:** openid, email, profile

## Current Status

✅ **Web App Running:** http://127.0.0.1:5000
✅ **Demo SSO Working:** Simulated login
❌ **Real SSO:** Needs Identity Center app registration

Once registered, the app will appear in your Identity Center portal alongside Q Business!
