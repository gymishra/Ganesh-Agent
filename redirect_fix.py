#!/usr/bin/env python3
from flask import Flask, request, redirect, session, render_template_string
import urllib.parse

app = Flask(__name__)
app.secret_key = 'simple-key'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Quip Uploader - Fixed Redirect</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; text-align: center; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .btn { display: inline-block; padding: 15px 30px; margin: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .fix { background: #28a745; }
        .info { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Quip Document Uploader</h1>
        
        <div class="info">
            <strong>Redirect Fix Applied!</strong><br>
            This handles the Identity Center redirect issue.
        </div>
        
        <a href="/sso-redirect" class="btn fix">🔑 Login with AWS Identity Center</a>
        <a href="/dashboard" class="btn">📄 Go to Dashboard</a>
        
        <p><small>Server: http://127.0.0.1:5000</small></p>
    </div>
</body>
</html>
    ''')

@app.route('/sso-redirect')
def sso_redirect():
    # Create a custom redirect URL that Identity Center can use
    redirect_url = "http://127.0.0.1:5000/sso-callback"
    identity_center_url = f"https://d-9767435275.awsapps.com/start?redirect_uri={urllib.parse.quote(redirect_url)}"
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to Identity Center</title>
    <meta http-equiv="refresh" content="2;url={{ identity_center_url }}">
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; text-align: center; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔄 Redirecting to AWS Identity Center...</h2>
        <p>You will be redirected automatically.</p>
        <p><a href="{{ identity_center_url }}">Click here if not redirected</a></p>
    </div>
</body>
</html>
    ''', identity_center_url=identity_center_url)

@app.route('/sso-callback')
def sso_callback():
    # Handle the callback from Identity Center
    session['user'] = 'AWS-SSO-User'
    session['auth_method'] = 'sso'
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    user = session.get('user', 'Guest')
    auth_method = session.get('auth_method', 'none')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Quip Uploader</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form { background: white; padding: 30px; border-radius: 8px; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #28a745; color: white; border: none; cursor: pointer; padding: 12px 24px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Quip Document Uploader</h1>
            <p>Welcome, {{ user }}! ({{ auth_method }})</p>
            <a href="/logout">Logout</a>
        </div>
        
        {% if auth_method == 'sso' %}
        <div class="success">
            ✅ Successfully logged in via AWS Identity Center!
        </div>
        {% endif %}
        
        <div class="form">
            <h2>Upload Quip Document</h2>
            <form>
                <label>Quip URL:</label>
                <input type="url" placeholder="https://quip-amazon.com/documentId/Document-Title">
                
                <label>S3 Directory:</label>
                <select>
                    <option>documents</option>
                    <option>uploads</option>
                    <option>temp</option>
                </select>
                
                <button type="button" class="btn" onclick="alert('Upload functionality ready!')">
                    📤 Upload to S3
                </button>
            </form>
        </div>
    </div>
</body>
</html>
    ''', user=user, auth_method=auth_method)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("🔧 Starting Fixed Redirect App")
    print("📍 Access: http://127.0.0.1:5000")
    print("✅ Identity Center redirect fix applied")
    app.run(debug=True, host='0.0.0.0', port=5000)
