#!/usr/bin/env python3
import requests
import json
import subprocess

def download_q_developer_abap():
    """Download Q Developer ABAP document"""
    
    # Extract document ID from URL: https://quip-amazon.com/keRQAkKnY2D0/Q-Developer-for-ABAP-Customer-and-Partner-Opportunities-and-Roadmap-and-Requests
    document_id = "keRQAkKnY2D0"
    api_token = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://platform.quip-amazon.com/1/threads/{document_id}'
    
    try:
        print(f"📡 Downloading Q Developer ABAP document...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('thread', {}).get('title', 'Q Developer ABAP')
            html_content = data.get('html', '')
            
            print(f"✅ Success! Title: {title}")
            
            # Create clean HTML
            html_file = "q_developer_abap_roadmap.html"
            html_content_clean = f'''<!DOCTYPE html>
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
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content_clean)
            
            print(f"✅ HTML saved: {html_file}")
            
            # Upload to S3
            print("📤 Uploading to S3...")
            result = subprocess.run([
                "aws", "s3", "cp", html_file, 
                "s3://quip-documents-for-q-business/"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Successfully uploaded to S3!")
                print(f"🔗 S3 location: s3://quip-documents-for-q-business/{html_file}")
            else:
                print(f"❌ Upload failed: {result.stderr}")
                
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    download_q_developer_abap()
