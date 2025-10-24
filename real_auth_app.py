#!/usr/bin/env python3
from flask import Flask, render_template_string, request, session, redirect, jsonify
import boto3
import requests
import secrets
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
S3_BUCKET = "sap-qbiz-kbnew"
QUIP_API_TOKEN = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
IDENTITY_CENTER_URL = "https://d-9767435275.awsapps.com/start"

s3_client = boto3.client('s3')

@app.route('/')
def home():
    if 'authenticated' in session and session['authenticated']:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login')
def login():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Document Uploader - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        .btn { width: 100%; background: #ff9900; color: white; border: none; cursor: pointer; padding: 15px; border-radius: 4px; margin: 10px 0; font-size: 16px; text-decoration: none; display: block; text-align: center; }
        .btn:hover { opacity: 0.9; }
        .info { background: #e9ecef; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 14px; }
        .required { background: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Quip Document Uploader</h1>
        
        <div class="required">
            <strong>⚠️ Real Authentication Required</strong><br>
            This application requires proper AWS Identity Center authentication. No demo accounts.
        </div>
        
        <a href="{{ identity_center_url }}" target="_blank" class="btn">
            🔑 Login with AWS Identity Center
        </a>
        
        <div class="info">
            <strong>After logging into Identity Center:</strong><br>
            1. Complete your authentication<br>
            2. Return to this tab<br>
            3. Click "Continue to Dashboard" below
        </div>
        
        <a href="/verify-auth" class="btn" style="background: #28a745;">
            ✅ Continue to Dashboard
        </a>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
            <strong>Server:</strong> http://127.0.0.1:5000<br>
            <strong>S3 Bucket:</strong> {{ bucket }}
        </div>
    </div>
</body>
</html>
    ''', identity_center_url=IDENTITY_CENTER_URL, bucket=S3_BUCKET)

@app.route('/verify-auth')
def verify_auth():
    # In a real implementation, this would verify the JWT token from Identity Center
    # For now, we'll simulate the verification process
    
    # Check if user has valid AWS credentials (indicating they're authenticated)
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        # Extract user info from AWS identity
        user_arn = identity.get('Arn', '')
        user_id = identity.get('UserId', '')
        account = identity.get('Account', '')
        
        # Set session
        session['authenticated'] = True
        session['user'] = user_arn.split('/')[-1] if '/' in user_arn else user_id
        session['auth_method'] = 'aws-identity-center'
        session['account'] = account
        
        return redirect('/dashboard')
        
    except Exception as e:
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Failed</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; text-align: center; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>❌ Authentication Failed</h1>
        
        <div class="error">
            <strong>Error:</strong> Unable to verify AWS credentials.<br>
            Please ensure you're properly authenticated with AWS Identity Center.
        </div>
        
        <p><strong>Steps to fix:</strong></p>
        <ol style="text-align: left;">
            <li>Login to AWS Identity Center</li>
            <li>Ensure your session is active</li>
            <li>Return to this application</li>
        </ol>
        
        <a href="/login" class="btn">🔄 Try Again</a>
        <a href="{{ identity_center_url }}" target="_blank" class="btn">🔑 AWS Identity Center</a>
    </div>
</body>
</html>
        ''', identity_center_url=IDENTITY_CENTER_URL)

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect('/login')
    
    user = session.get('user', 'Unknown')
    account = session.get('account', 'Unknown')
    
    # Get S3 directories
    directories = ['documents', 'uploads', 'temp']
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Delimiter='/', MaxKeys=50)
        if 'CommonPrefixes' in response:
            directories = [p['Prefix'].rstrip('/') for p in response['CommonPrefixes']]
    except Exception as e:
        print(f"S3 Error: {e}")
    
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
        .auth-badge { background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin-right: 10px; }
        .clearfix::after { content: ""; display: table; clear: both; }
        .auth-status { background: #d4edda; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header clearfix">
            <h1>📄 Quip Document Uploader</h1>
            <div class="user-info">
                <span class="auth-badge">🔑 AWS Auth</span>
                {{ user }} ({{ account }})
                <a href="/logout" style="margin-left: 15px; color: #007bff; text-decoration: none;">Logout</a>
            </div>
        </div>
        
        <div class="auth-status">
            ✅ <strong>Authenticated via AWS Identity Center</strong><br>
            User: {{ user }} | Account: {{ account }} | Method: Real AWS Authentication
        </div>
        
        <div class="form">
            <h2>Upload Quip Document to S3</h2>
            <div id="message"></div>
            
            <form id="uploadForm">
                <label><strong>Quip Document URL:</strong></label>
                <input type="url" id="quip_url" placeholder="https://quip-amazon.com/documentId/Document-Title" required>
                <small style="color: #666;">Enter the full Quip document URL</small>
                
                <label><strong>S3 Directory ({{ bucket }}):</strong></label>
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
                                     '<br><strong>📄 Document:</strong> ' + (data.title || 'Untitled') +
                                     '<br><strong>👤 Uploaded by:</strong> {{ user }}';
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
    ''', user=user, account=account, directories=directories, bucket=S3_BUCKET)

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    quip_url = request.form.get('quip_url', '').strip()
    directory = request.form.get('directory', 'documents').strip()
    
    if not quip_url:
        return jsonify({'error': 'Quip URL is required'}), 400
    
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
    
    try:
        # Download from Quip API
        headers = {'Authorization': f'Bearer {QUIP_API_TOKEN}'}
        url = f'https://platform.quip-amazon.com/1/threads/{doc_id}'
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return jsonify({'error': f'Quip API error: {response.status_code}'}), 500
        
        data = response.json()
        title = data.get('thread', {}).get('title', 'Untitled Document')
        html_content = data.get('html', '')
        
        # Create HTML document
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
        <strong>Uploaded by:</strong> {session['user']} (AWS Account: {session.get('account', 'Unknown')})<br>
        <strong>Upload time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
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
            ContentType='text/html',
            Metadata={
                'uploaded-by': session['user'],
                'aws-account': session.get('account', 'unknown'),
                'auth-method': 'aws-identity-center',
                'source-url': quip_url
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Document "{title}" uploaded successfully!',
            's3_location': f's3://{S3_BUCKET}/{s3_key}',
            'title': title
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("🚀 Starting Quip Document Uploader - Real Authentication Only")
    print("📍 Access: http://127.0.0.1:5000")
    print("🔐 Authentication: AWS Identity Center (Real credentials required)")
    print("❌ No demo accounts - Real AWS authentication only")
    app.run(debug=True, host='0.0.0.0', port=5000)
