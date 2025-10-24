#!/usr/bin/env python3
import requests
import json
import sys

def download_quip_amazon_api(api_token, document_id, output_file="quip_amazon_content.json"):
    """Download from Quip Amazon using dev token"""
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Quip Amazon API endpoint
    url = f'https://quip-amazon.com/api/1/threads/{document_id}'
    
    try:
        print(f"📡 Fetching from Quip Amazon API...")
        print(f"🔗 URL: {url}")
        print(f"🔑 Token: {api_token[:20]}...")
        
        response = requests.get(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Save JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Extract content
            html_content = data.get('html', '')
            title = data.get('thread', {}).get('title', 'Amazon Q Business SAP Community')
            
            # Save HTML
            html_file = output_file.replace('.json', '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>''')
            
            print(f"✅ JSON saved: {output_file}")
            print(f"✅ HTML saved: {html_file}")
            print(f"📋 Title: {title}")
            
            return html_file
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    document_id = "8UhjA0uQupLl"
    api_token = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
    
    html_file = download_quip_amazon_api(api_token, document_id)
    
    if html_file:
        print(f"\n🎉 Success! Ready to upload to S3")
        upload = input("Upload HTML to S3? (y/n): ").strip().lower()
        if upload == 'y':
            import subprocess
            result = subprocess.run(["aws", "s3", "cp", html_file, "s3://quip-documents-for-q-business/"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Uploaded to S3!")
            else:
                print(f"❌ Upload failed: {result.stderr}")
    else:
        print("❌ Failed to download content")
