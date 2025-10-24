#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

print("🔍 Testing deployment components...")

try:
    # Test 1: Import the deployment class
    print("1. Testing imports...")
    from deploy_odata_training import ODataModelDeployment
    print("✅ ODataModelDeployment imported successfully")
    
    # Test 2: Load metadata
    print("2. Testing metadata loading...")
    import json
    with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
        metadata = json.load(f)
    print(f"✅ Metadata loaded: {len(metadata)} services")
    
    # Test 3: Initialize deployment class
    print("3. Testing deployment initialization...")
    deployment = ODataModelDeployment()
    print("✅ Deployment class initialized")
    print(f"   - Region: {deployment.region}")
    print(f"   - Bucket: {deployment.bucket}")
    print(f"   - Role: {deployment.role}")
    
    # Test 4: Test S3 access
    print("4. Testing S3 access...")
    import boto3
    s3 = boto3.client('s3')
    s3.head_bucket(Bucket=deployment.bucket)
    print("✅ S3 bucket accessible")
    
    print("\n🎉 All tests passed! The deployment should work.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
