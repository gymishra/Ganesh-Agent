#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
import requests
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError
from urllib.parse import urlencode
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
IDENTITY_CENTER_START_URL = "https://d-9767435275.awsapps.com/start"
S3_BUCKET = "sap-qbiz-kbnew"
QUIP_API_TOKEN = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="

# Initialize AWS clients
try:
    s3_client = boto3.client('s3')
    print("✅ AWS S3 client initialized")
except Exception as e:
    print(f"❌ Error initializing S3 client: {e}")
    s3_client = None

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/login')
def login():
    return render_template('login.html', sso_url=IDENTITY_CENTER_START_URL)

@app.route('/auth', methods=['POST'])
def authenticate():
    # Simplified auth - in production, integrate with AWS Identity Center OIDC
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Mock authentication - replace with actual Identity Center integration
    if username and password:
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get S3 directories
    try:
        directories = get_s3_directories()
        return render_template('dashboard.html', 
                             user=session['user'], 
                             directories=directories)
    except Exception as e:
        flash(f'Error loading directories: {str(e)}')
        return render_template('dashboard.html', user=session['user'], directories=[])

@app.route('/upload_quip', methods=['POST'])
def upload_quip():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    quip_url = request.form.get('quip_url')
    directory = request.form.get('directory')
    
    if not quip_url or not directory:
        return jsonify({'error': 'Missing URL or directory'}), 400
    
    try:
        # Extract document ID from Quip URL
        doc_id = extract_document_id(quip_url)
        if not doc_id:
            return jsonify({'error': 'Invalid Quip URL'}), 400
        
        # Download from Quip API
        content = download_quip_document(doc_id)
        if not content:
            return jsonify({'error': 'Failed to download document'}), 500
        
        # Upload to S3
        s3_key = f"{directory}/{doc_id}.html"
        upload_to_s3(content, s3_key)
        
        return jsonify({
            'success': True, 
            'message': f'Document uploaded to {s3_key}',
            's3_location': f's3://{S3_BUCKET}/{s3_key}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def get_s3_directories():
    """Get list of directories in S3 bucket"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Delimiter='/'
        )
        
        directories = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                directories.append(prefix['Prefix'].rstrip('/'))
        
        return directories
    except Exception as e:
        print(f"Error getting directories: {e}")
        return []

def extract_document_id(quip_url):
    """Extract document ID from Quip URL"""
    try:
        # Handle URLs like: https://quip-amazon.com/keRQAkKnY2D0/Document-Title
        if 'quip-amazon.com' in quip_url:
            parts = quip_url.split('/')
            for part in parts:
                if len(part) > 8 and part.isalnum():
                    return part
        return None
    except:
        return None

def download_quip_document(doc_id):
    """Download document from Quip API"""
    headers = {
        'Authorization': f'Bearer {QUIP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://platform.quip-amazon.com/1/threads/{doc_id}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            title = data.get('thread', {}).get('title', 'Untitled')
            html_content = data.get('html', '')
            
            # Create clean HTML
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
            return html
        return None
    except Exception as e:
        print(f"Error downloading document: {e}")
        return None

def upload_to_s3(content, s3_key):
    """Upload content to S3"""
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=content.encode('utf-8'),
        ContentType='text/html'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
