#!/usr/bin/env python3
import requests
import boto3
import json
from datetime import datetime

def fetch_quip_document(api_token, document_id):
    """Fetch Quip document content using API token"""
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Quip API endpoint for getting document
    url = f'https://platform.quip.com/1/threads/{document_id}'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching document: {e}")
        return None

def upload_to_s3(content, bucket_name, key):
    """Upload content to S3"""
    s3 = boto3.client('s3')
    
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            ContentType='application/json'
        )
        print(f"Uploaded to s3://{bucket_name}/{key}")
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False

def main():
    # Configuration
    API_TOKEN = "YOUR_QUIP_API_TOKEN"  # Replace with your actual token
    DOCUMENT_ID = "8UhjA0uQupLl"  # From the URL
    BUCKET_NAME = "quip-documents-for-q-business"
    
    # Fetch document
    print("Fetching Quip document...")
    doc_data = fetch_quip_document(API_TOKEN, DOCUMENT_ID)
    
    if doc_data:
        # Convert to JSON string
        content = json.dumps(doc_data, indent=2)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quip_sap_community_{timestamp}.json"
        
        # Upload to S3
        if upload_to_s3(content, BUCKET_NAME, filename):
            print(f"Successfully uploaded Quip document to S3")
            print(f"Configure S3 connector in Q Business with bucket: {BUCKET_NAME}")
        else:
            print("Failed to upload to S3")
    else:
        print("Failed to fetch document")

if __name__ == "__main__":
    main()
