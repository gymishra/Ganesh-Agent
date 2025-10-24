#!/usr/bin/env python3
import requests
import json

def download_quip_final(api_token, document_id):
    """Final working Quip Amazon API download"""
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Correct endpoint found
    url = f'https://platform.quip-amazon.com/1/threads/{document_id}'
    
    try:
        print(f"📡 Downloading from: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            title = data.get('thread', {}).get('title', 'Untitled')
            html_content = data.get('html', '')
            
            print(f"✅ Success! Title: {title}")
            
            # Save complete JSON
            with open("quip_complete.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Create clean HTML
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
            
            with open("quip_sap_community_final.html", 'w', encoding='utf-8') as f:
                f.write(html_content_clean)
            
            print("✅ Files saved:")
            print("   📄 quip_complete.json (raw data)")
            print("   🌐 quip_sap_community_final.html (readable)")
            
            return "quip_sap_community_final.html"
            
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    document_id = "8UhjA0uQupLl"
    api_token = "WVRYOU1BSjF0YVo=|1789367060|Qs7njUqA9i+dLhU8Tl0gFr2HOrw28ZYKECYWc6AX6xc="
    
    html_file = download_quip_final(api_token, document_id)
    
    if html_file:
        print(f"\n🎉 Ready to upload to S3!")
        
        # Auto-upload to S3
        import subprocess
        print("📤 Uploading to S3...")
        result = subprocess.run([
            "aws", "s3", "cp", html_file, 
            "s3://quip-documents-for-q-business/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully uploaded to S3!")
            print("🔗 S3 location: s3://quip-documents-for-q-business/quip_sap_community_final.html")
            print("\n📋 Next steps:")
            print("1. Configure Amazon Q Business S3 data source")
            print("2. Point to bucket: quip-documents-for-q-business")
            print("3. Start sync to index the content")
        else:
            print(f"❌ Upload failed: {result.stderr}")

if __name__ == "__main__":
    main()
