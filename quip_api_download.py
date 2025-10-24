#!/usr/bin/env python3
import requests
import json
import sys

def download_quip_with_api(api_token, document_id, output_file="quip_api_content.json"):
    """Download Quip document using API token"""
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Quip API endpoint
    url = f'https://platform.quip.com/1/threads/{document_id}'
    
    try:
        print(f"📡 Fetching document: {document_id}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Save raw JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Extract and save readable content
        html_content = data.get('html', '')
        title = data.get('thread', {}).get('title', 'Untitled')
        
        readable_file = output_file.replace('.json', '.html')
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write(f'<html><head><title>{title}</title></head><body>')
            f.write(html_content)
            f.write('</body></html>')
        
        print(f"✅ JSON saved: {output_file}")
        print(f"✅ HTML saved: {readable_file}")
        print(f"📋 Title: {title}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Extract document ID from URL
    document_id = "8UhjA0uQupLl"  # From your URL
    
    api_token = sys.argv[1] if len(sys.argv) > 1 else input("Enter your Quip API token: ")
    
    success = download_quip_with_api(api_token, document_id, "quip_sap_community_api.json")
    
    if success:
        upload = input("\nUpload HTML to S3? (y/n): ").strip().lower()
        if upload == 'y':
            import subprocess
            subprocess.run(["aws", "s3", "cp", "quip_sap_community_api.html", "s3://quip-documents-for-q-business/"])
            print("✅ Uploaded to S3!")
