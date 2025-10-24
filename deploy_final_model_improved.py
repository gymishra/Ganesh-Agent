#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

print("🚀 Starting Final OData Model Deployment")
print("=" * 60)

try:
    print("📦 Loading dependencies...")
    from deploy_odata_training import ODataModelDeployment
    import json
    print("✅ Dependencies loaded successfully")
    
    print("\n📋 Loading optimized metadata...")
    with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
        optimized_metadata = json.load(f)
    
    # Remove metadata section
    if '_metadata' in optimized_metadata:
        del optimized_metadata['_metadata']
    
    print(f"✅ Loaded metadata for {len(optimized_metadata)} services:")
    for service_name in optimized_metadata.keys():
        print(f"  • {service_name}")
    
    print("\n🔧 Initializing deployment...")
    deployment = ODataModelDeployment()
    print(f"✅ Deployment initialized")
    print(f"   - Region: {deployment.region}")
    print(f"   - Bucket: {deployment.bucket}")
    print(f"   - Role: {deployment.role}")
    
    print("\n1️⃣ Uploading optimized metadata to S3...")
    training_data_uri = deployment.upload_training_data(optimized_metadata)
    print(f"✅ Training data uploaded: {training_data_uri}")
    
    print("\n2️⃣ Starting SageMaker training job...")
    estimator, job_name = deployment.create_training_job(training_data_uri)
    print(f"✅ Training job '{job_name}' started successfully!")
    print("📊 Training with Bedrock-enhanced, optimized metadata")
    print("⏱️  Training will take 5-10 minutes...")
    
    print("\n3️⃣ Waiting for training to complete...")
    print("   (This may take several minutes - please be patient)")
    estimator.latest_training_job.wait()
    print("✅ Training completed successfully!")
    
    print("\n4️⃣ Deploying model to endpoint...")
    predictor, endpoint_name = deployment.deploy_model(estimator)
    print(f"✅ Model deployed to endpoint: {endpoint_name}")
    
    print("\n5️⃣ Testing the deployed endpoint...")
    test_questions = [
        "What is the credit limit for customer ABC123?",
        "Track my order status",
        "Check product availability"
    ]
    
    print("🧪 Running test predictions:")
    for question in test_questions:
        try:
            response = predictor.predict({'question': question})
            print(f"❓ {question}")
            if response and len(response) > 0:
                service = response[0]['service']
                confidence = response[0]['confidence']
                print(f"   ✅ {service} (confidence: {confidence:.3f})")
            else:
                print("   ⚠️  No prediction returned")
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")
    
    print("\n6️⃣ Creating Lambda integration code...")
    lambda_code = deployment.create_lambda_integration(endpoint_name)
    print("✅ Lambda integration code created: /home/gyanmis/odata_lambda.py")
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📍 SageMaker Endpoint: {endpoint_name}")
    print(f"📁 Training Data: {training_data_uri}")
    print(f"💻 Lambda Code: /home/gyanmis/odata_lambda.py")
    
    print("\n✅ Key Features:")
    print("• Bedrock-enhanced metadata descriptions")
    print("• Clear service domain differentiation")
    print("• Business-focused field descriptions")
    print("• Comprehensive use case coverage")
    print("• OAuth2 integration ready")
    
    print("\n🔧 Next Steps:")
    print("1. Update endpoints with your actual SAP system URLs")
    print("2. Configure OAuth2 credentials in AWS Secrets Manager")
    print("3. Create Lambda function using generated code")
    print("4. Set up API Gateway for external access")
    print("5. Test with your real user questions")
    
    # Create usage guide
    usage_guide = f"""
# OData AI Classifier Usage Guide

## 🎯 Model Overview
Your OData AI Classifier has been successfully deployed to AWS SageMaker.

**Endpoint Name:** {endpoint_name}
**Training Data:** {training_data_uri}
**Region:** {deployment.region}

## 📋 Supported Services
1. **CustomerMasterService** - Customer data, contacts, credit, addresses
2. **SalesOrderManagementService** - Orders, delivery, tracking, fulfillment  
3. **ProductInventoryService** - Products, stock, pricing, availability

## 🔧 Integration Options

### Option 1: Direct SageMaker Endpoint
```python
import boto3
import json

runtime = boto3.client('runtime.sagemaker')
response = runtime.invoke_endpoint(
    EndpointName='{endpoint_name}',
    ContentType='application/json',
    Body=json.dumps({{'question': 'What is the credit limit for customer ABC?'}})
)
```

### Option 2: Lambda Function
Use the generated Lambda code in `/home/gyanmis/odata_lambda.py`

### Option 3: API Gateway
Create REST API that calls the Lambda function

## 📊 Expected Performance
- **High Confidence (>70%)**: Clear, domain-specific questions
- **Medium Confidence (50-70%)**: Somewhat ambiguous questions  
- **Low Confidence (<50%)**: Very generic or unclear questions

## 🔐 OAuth2 Setup
1. Store credentials in AWS Secrets Manager
2. Update Lambda function to retrieve secrets
3. Implement token refresh logic
4. Handle authentication errors gracefully

## 📈 Monitoring
- Monitor endpoint performance in CloudWatch
- Track prediction confidence scores
- Log user questions for continuous improvement
- Set up alerts for low confidence predictions

## 🎯 Testing Commands
```bash
# Test the endpoint directly
aws sagemaker-runtime invoke-endpoint \\
    --endpoint-name {endpoint_name} \\
    --content-type application/json \\
    --body '{{"question": "Check my order status"}}' \\
    response.json

# View the response
cat response.json
```

## 🔄 Model Updates
To retrain the model with new data:
1. Update the metadata in `/home/gyanmis/odata_metadata_optimized.json`
2. Run the deployment script again
3. The new model will replace the existing endpoint

## 🆘 Troubleshooting
- Check CloudWatch logs for detailed error messages
- Verify IAM permissions for SageMaker and Lambda
- Ensure OAuth2 credentials are properly configured
- Monitor endpoint health in SageMaker console
"""
    
    with open('/home/gyanmis/DEPLOYMENT_SUCCESS_GUIDE.md', 'w') as f:
        f.write(usage_guide)
    
    print(f"\n📖 Complete usage guide created: /home/gyanmis/DEPLOYMENT_SUCCESS_GUIDE.md")
    print("\n🎊 Your OData AI Classifier is ready to use!")
    
except Exception as e:
    print(f"\n❌ Deployment failed: {str(e)}")
    import traceback
    print("\n🔍 Full error details:")
    traceback.print_exc()
    print("\n💡 Troubleshooting tips:")
    print("1. Check your AWS credentials and permissions")
    print("2. Verify SageMaker service limits in your region")
    print("3. Ensure the S3 bucket is accessible")
    print("4. Check CloudWatch logs for detailed error messages")
