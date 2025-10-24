#!/usr/bin/env python3
from flask import Flask, render_template_string, request, session, redirect, jsonify, url_for
import boto3
import requests
import secrets
import json
from urllib.parse import urlencode
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
S3_BUCKET = "sap-qbiz-kbnew"
QUIP_API_TOKEN = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
INTERNAL_IP = "172.30.89.194"

# AWS Identity Center OIDC Configuration
# TODO: Replace these with actual values after registering the app
OIDC_CLIENT_ID = "REPLACE_WITH_ACTUAL_CLIENT_ID"
OIDC_CLIENT_SECRET = "REPLACE_WITH_ACTUAL_CLIENT_SECRET"
OIDC_AUTHORIZATION_ENDPOINT = "https://d-9767435275.awsapps.com/start/oauth2/authorize"
OIDC_TOKEN_ENDPOINT = "https://d-9767435275.awsapps.com/start/oauth2/token"
OIDC_USERINFO_ENDPOINT = "https://d-9767435275.awsapps.com/start/oauth2/userInfo"
OIDC_REDIRECT_URI = f"http://{INTERNAL_IP}:5000/callback"

s3_client = boto3.client('s3')

# Check if OIDC is configured
OIDC_CONFIGURED = not OIDC_CLIENT_ID.startswith("REPLACE_WITH")

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return redirect('/dashboard')

@app.route('/login')
def login():
    oidc_status = "✅ Configured" if OIDC_CONFIGURED else "❌ Needs Setup"
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Document Uploader - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; background: #007bff; color: white; border: none; cursor: pointer; padding: 12px; border-radius: 4px; margin: 5px 0; font-size: 16px; text-decoration: none; display: block; text-align: center; }
        .btn-sso { background: #ff9900; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .divider { text-align: center; margin: 20px 0; color: #666; }
        .demo-note { background: #d1ecf1; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 14px; color: #0c5460; }
        .setup-note { background: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 14px; color: #856404; }
        .access-info { background: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Quip Document Uploader</h1>
        
        <div class="access-info">
            <strong>✅ Server Running:</strong><br>
            • Local: http://127.0.0.1:5000<br>
            • Network: http://{{ internal_ip }}:5000<br>
            • OIDC Status: {{ oidc_status }}
        </div>
        
        {% if not oidc_configured %}
        <div class="setup-note">
            <strong>⚠️ OIDC Setup Required:</strong><br>
            To enable real AWS Identity Center login, register this app in Identity Center console.
            <a href="/setup-guide" target="_blank">View Setup Guide</a>
        </div>
        {% endif %}
        
        <div class="demo-note">
            <strong>Demo Mode:</strong> Use any username/password to login, or click AWS SSO for {{ "real" if oidc_configured else "simulated" }} Identity Center login.
        </div>
        
        <form method="POST" action="/auth">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="🔐 Login" class="btn">
        </form>
        
        <div class="divider">── OR ──</div>
        
        {% if oidc_configured %}
        <a href="/sso-login" class="btn btn-sso">
            🔑 Login with AWS Identity Center
        </a>
        {% else %}
        <a href="/sso-login" class="btn btn-sso">
            🔑 Demo AWS Identity Center Login
        </a>
        {% endif %}
        
        <div style="text-align: center; margin-top: 15px; font-size: 12px; color: #666;">
            <a href="/reset-password">Forgot Password?</a>
        </div>
    </div>
</body>
</html>
    ''', internal_ip=INTERNAL_IP, oidc_status=oidc_status, oidc_configured=OIDC_CONFIGURED)

@app.route('/setup-guide')
def setup_guide():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>AWS Identity Center Setup Guide</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }
        h1, h2 { color: #333; }
        .step { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 4px; border-left: 4px solid #007bff; }
        .code { background: #f1f1f1; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
        .highlight { background: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 AWS Identity Center Setup Guide</h1>
        
        <div class="highlight">
            <strong>Current Status:</strong> OIDC not configured - using demo mode
        </div>
        
        <div class="step">
            <h2>Step 1: Access Identity Center Console</h2>
            <p>1. Go to AWS Console → <strong>AWS IAM Identity Center</strong></p>
            <p>2. Or directly: <a href="https://console.aws.amazon.com/singlesignon/" target="_blank">https://console.aws.amazon.com/singlesignon/</a></p>
        </div>
        
        <div class="step">
            <h2>Step 2: Create Application</h2>
            <p>1. Click <strong>Applications</strong> in left menu</p>
            <p>2. Click <strong>Add application</strong></p>
            <p>3. Choose <strong>Add custom OIDC application</strong></p>
        </div>
        
        <div class="step">
            <h2>Step 3: Configure Application</h2>
            <p><strong>Application name:</strong> Quip Document Uploader</p>
            <p><strong>Description:</strong> Web application for uploading Quip documents to S3</p>
            <p><strong>Application type:</strong> Web application</p>
            
            <p><strong>Redirect URLs:</strong></p>
            <div class="code">
http://127.0.0.1:5000/callback<br>
http://{{ internal_ip }}:5000/callback
            </div>
            
            <p><strong>Sign-out URLs:</strong></p>
            <div class="code">
http://127.0.0.1:5000/logout<br>
http://{{ internal_ip }}:5000/logout
            </div>
        </div>
        
        <div class="step">
            <h2>Step 4: Get Credentials</h2>
            <p>After creating the application, copy these values:</p>
            <ul>
                <li><strong>Client ID</strong></li>
                <li><strong>Client Secret</strong></li>
            </ul>
        </div>
        
        <div class="step">
            <h2>Step 5: Assign Users</h2>
            <p>1. In the application, go to <strong>Assigned users</strong> tab</p>
            <p>2. Click <strong>Assign users</strong> or <strong>Assign groups</strong></p>
            <p>3. Select users who should access the Quip Uploader</p>
        </div>
        
        <div class="step">
            <h2>Step 6: Update Application</h2>
            <p>Replace the OIDC configuration in the Flask app with your actual values.</p>
        </div>
        
        <p><a href="/login">← Back to Login</a></p>
    </div>
</body>
</html>
    ''', internal_ip=INTERNAL_IP)

@app.route('/sso-login')
def sso_login():
    if OIDC_CONFIGURED:
        # Real OIDC flow
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        params = {
            'response_type': 'code',
            'client_id': OIDC_CLIENT_ID,
            'redirect_uri': OIDC_REDIRECT_URI,
            'scope': 'openid email profile',
            'state': state
        }
        
        auth_url = f"{OIDC_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
        return redirect(auth_url)
    else:
        # Demo mode - simulate successful SSO login
        session['user'] = 'AWS-SSO-User (Demo)'
        session['auth_method'] = 'sso-demo'
        return redirect('/dashboard')

@app.route('/callback')
def callback():
    if not OIDC_CONFIGURED:
        return redirect('/login?error=oidc_not_configured')
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or state != session.get('oauth_state'):
        return redirect('/login?error=invalid_callback')
    
    # Exchange code for token
    try:
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': OIDC_CLIENT_ID,
            'client_secret': OIDC_CLIENT_SECRET,
            'code': code,
            'redirect_uri': OIDC_REDIRECT_URI
        }
        
        token_response = requests.post(OIDC_TOKEN_ENDPOINT, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_response = requests.get(OIDC_USERINFO_ENDPOINT, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Store user session
        session['user'] = user_info.get('email', user_info.get('sub', 'SSO-User'))
        session['auth_method'] = 'sso'
        session['user_info'] = user_info
        
        return redirect('/dashboard')
        
    except Exception as e:
        return redirect(f'/login?error=token_exchange_failed&details={str(e)}')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        session['user'] = username
        session['auth_method'] = 'local'
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    # Get S3 directories
    directories = ['documents', 'uploads', 'temp']
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Delimiter='/', MaxKeys=50)
        if 'CommonPrefixes' in response:
            directories = [p['Prefix'].rstrip('/') for p in response['CommonPrefixes']]
    except Exception as e:
        print(f"S3 Error: {e}")
    
    auth_method = session.get('auth_method', 'local')
    if auth_method == 'sso':
        auth_badge = "🔑 AWS SSO"
    elif auth_method == 'sso-demo':
        auth_badge = "🔑 SSO Demo"
    else:
        auth_badge = "🔐 Local"
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Document Uploader - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .container { max-width: 800px; margin: 0 auto; }
        .form { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #28a745; color: white; border: none; cursor: pointer; padding: 12px 24px; border-radius: 4px; font-size: 16px; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; background: #e9ecef; display: none; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .user-info { float: right; }
        .auth-badge { background: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin-right: 10px; }
        .clearfix::after { content: ""; display: table; clear: both; }
        .server-info { background: #e9ecef; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header clearfix">
            <h1>📄 Quip Document Uploader</h1>
            <div class="user-info">
                <span class="auth-badge">{{ auth_badge }}</span>
                Welcome, {{ user }}! 
                <a href="/logout" style="margin-left: 15px; color: #007bff; text-decoration: none;">Logout</a>
            </div>
        </div>
        
        <div class="server-info">
            <strong>🌐 Access URLs:</strong> 
            http://127.0.0.1:5000 | http://{{ internal_ip }}:5000 | 
            <strong>📦 S3:</strong> {{ bucket }} |
            <strong>🔧 OIDC:</strong> {{ "Configured" if oidc_configured else "Demo Mode" }}
        </div>
        
        <div class="form">
            <h2>Upload Quip Document to S3</h2>
            <div id="message"></div>
            
            <form id="uploadForm">
                <label><strong>Quip Document URL:</strong></label>
                <input type="url" id="quip_url" placeholder="https://quip-amazon.com/documentId/Document-Title" required>
                <small style="color: #666;">Enter the full Quip document URL</small>
                
                <label><strong>S3 Directory:</strong></label>
                <select id="directory" required>
                    <option value="">Select directory...</option>
                    {% for dir in directories %}
                    <option value="{{ dir }}">📁 {{ dir }}</option>
                    {% endfor %}
                </select>
                
                <button type="submit" class="btn" id="uploadBtn">
                    📤 Download & Upload to S3
                </button>
            </form>
            
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const btn = document.getElementById('uploadBtn');
            const result = document.getElementById('result');
            const message = document.getElementById('message');
            
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            result.style.display = 'none';
            message.innerHTML = '';
            
            const formData = new FormData();
            formData.append('quip_url', document.getElementById('quip_url').value);
            formData.append('directory', document.getElementById('directory').value);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                btn.disabled = false;
                btn.textContent = '📤 Download & Upload to S3';
                
                if (data.success) {
                    message.innerHTML = '<div class="success">✅ ' + data.message + '</div>';
                    result.innerHTML = '<strong>📍 S3 Location:</strong> ' + data.s3_location + 
                                     '<br><strong>📄 Document:</strong> ' + (data.title || 'Untitled');
                    result.style.display = 'block';
                    document.getElementById('uploadForm').reset();
                } else {
                    message.innerHTML = '<div class="error">❌ ' + data.error + '</div>';
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.textContent = '📤 Download & Upload to S3';
                message.innerHTML = '<div class="error">❌ Network Error: ' + error.message + '</div>';
            });
        });
    </script>
</body>
</html>
    ''', user=session['user'], directories=directories, auth_badge=auth_badge, 
         bucket=S3_BUCKET, internal_ip=INTERNAL_IP, oidc_configured=OIDC_CONFIGURED)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    quip_url = request.form.get('quip_url')
    directory = request.form.get('directory', 'documents')
    
    if not quip_url:
        return jsonify({'error': 'Missing Quip URL'}), 400
    
    # Extract document ID
    doc_id = None
    if 'quip-amazon.com' in quip_url:
        parts = quip_url.split('/')
        for part in parts:
            if len(part) >= 8 and any(c.isalnum() for c in part):
                doc_id = part.split('?')[0]
                break
    
    if not doc_id:
        return jsonify({'error': 'Invalid Quip URL format'}), 400
    
    # Download from Quip
    headers = {'Authorization': f'Bearer {QUIP_API_TOKEN}'}
    url = f'https://platform.quip-amazon.com/1/threads/{doc_id}'
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return jsonify({'error': f'Quip API error: {response.status_code}'}), 500
        
        data = response.json()
        title = data.get('thread', {}).get('title', 'Untitled Document')
        html_content = data.get('html', '')
        
        # Create HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="metadata">
        <strong>Document:</strong> {title}<br>
        <strong>Source:</strong> {quip_url}<br>
        <strong>Uploaded by:</strong> {session['user']} ({session.get('auth_method', 'local')})<br>
        <strong>S3 Location:</strong> s3://{S3_BUCKET}/{directory}/{doc_id}.html
    </div>
    <h1>{title}</h1>
    {html_content}
</body>
</html>'''
        
        # Upload to S3
        s3_key = f"{directory}/{doc_id}.html"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=html.encode('utf-8'),
            ContentType='text/html'
        )
        
        return jsonify({
            'success': True,
            'message': f'Document uploaded successfully!',
            's3_location': f's3://{S3_BUCKET}/{s3_key}',
            'title': title
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/reset-password')
def reset_password():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; text-align: center; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Reset Password</h1>
        <p>Password reset is handled through AWS Identity Center.</p>
        <a href="https://d-9767435275.awsapps.com/start" target="_blank" class="btn">Reset via AWS Identity Center</a>
        <br><br>
        <a href="/login">← Back to Login</a>
    </div>
</body>
</html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("🚀 Starting Quip Document Uploader with Real OIDC Support")
    print(f"📍 Local Access: http://127.0.0.1:5000")
    print(f"🌐 Network Access: http://{INTERNAL_IP}:5000")
    print(f"📦 S3 Bucket: {S3_BUCKET}")
    print(f"🔧 OIDC Status: {'Configured' if OIDC_CONFIGURED else 'Demo Mode - Setup Required'}")
    if not OIDC_CONFIGURED:
        print("📋 Setup Guide: http://127.0.0.1:5000/setup-guide")
    app.run(debug=True, host='0.0.0.0', port=5000)
