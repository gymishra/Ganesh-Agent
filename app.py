#!/usr/bin/env python3
from flask import Flask, render_template_string, request, session, redirect, jsonify
import boto3
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
S3_BUCKET = "sap-qbiz-kbnew"
QUIP_API_TOKEN = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
s3_client = boto3.client('s3')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return redirect('/dashboard')

@app.route('/login')
def login():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Document Uploader - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #007bff; color: white; border: none; cursor: pointer; }
        .sso-link { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Quip Document Uploader</h1>
        <form method="POST" action="/auth">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login" class="btn">
        </form>
        <div class="sso-link">
            <p>Or use AWS Identity Center:</p>
            <a href="https://d-9767435275.awsapps.com/start" target="_blank">🔐 AWS SSO Login</a>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        session['user'] = username
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
    except:
        pass
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Document Uploader - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form { background: white; padding: 30px; border-radius: 8px; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #28a745; color: white; border: none; cursor: pointer; padding: 12px 24px; }
        .btn:disabled { background: #6c757d; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; background: #e9ecef; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Quip Document Uploader</h1>
            <div style="float: right;">Welcome, {{ user }}! <a href="/logout">Logout</a></div>
            <div style="clear: both;"></div>
        </div>
        
        <div class="form">
            <h2>Upload Quip Document to S3</h2>
            <div id="message"></div>
            
            <form id="uploadForm">
                <label>Quip Document URL:</label>
                <input type="url" id="quip_url" placeholder="https://quip-amazon.com/documentId/Document-Title" required>
                
                <label>S3 Directory:</label>
                <select id="directory" required>
                    <option value="">Select directory...</option>
                    {% for dir in directories %}
                    <option value="{{ dir }}">{{ dir }}</option>
                    {% endfor %}
                </select>
                
                <button type="submit" class="btn" id="uploadBtn">📤 Download & Upload to S3</button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
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
                    result.innerHTML = '<strong>S3 Location:</strong> ' + data.s3_location;
                    result.style.display = 'block';
                    document.getElementById('uploadForm').reset();
                } else {
                    message.innerHTML = '<div class="error">❌ ' + data.error + '</div>';
                }
            })
            .catch(error => {
                btn.disabled = false;
                btn.textContent = '📤 Download & Upload to S3';
                message.innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
            });
        });
    </script>
</body>
</html>
    ''', user=session['user'], directories=directories)

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
        return jsonify({'error': 'Invalid Quip URL'}), 400
    
    # Download from Quip
    headers = {'Authorization': f'Bearer {QUIP_API_TOKEN}'}
    url = f'https://platform.quip-amazon.com/1/threads/{doc_id}'
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to download from Quip'}), 500
        
        data = response.json()
        title = data.get('thread', {}).get('title', 'Untitled')
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
    </style>
</head>
<body>
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
            'message': f'Document "{title}" uploaded successfully!',
            's3_location': f's3://{S3_BUCKET}/{s3_key}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("🚀 Starting Quip Document Uploader")
    print("📍 Access at: http://localhost:5000")
    print("🔐 Identity Center: https://d-9767435275.awsapps.com/start")
    print("📦 S3 Bucket: sap-qbiz-kbnew")
    app.run(debug=True, host='0.0.0.0', port=5000)
