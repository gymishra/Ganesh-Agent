#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

from deploy_odata_training import ODataModelDeployment
import json

def deploy_optimized_model():
    """
    Deploy the final optimized OData model using Bedrock-enhanced metadata
    """
    print("🚀 Deploying Final Optimized OData Model")
    print("=" * 60)
    
    # Load the optimized metadata
    with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
        optimized_metadata = json.load(f)
    
    # Remove metadata section
    if '_metadata' in optimized_metadata:
        del optimized_metadata['_metadata']
    
    print("📋 Deploying with services:")
    for service_name in optimized_metadata.keys():
        print(f"  • {service_name}")
    
    # Initialize deployment
    deployment = ODataModelDeployment()
    
    try:
        # Step 1: Upload optimized training data
        print("\\n1. Uploading optimized metadata to S3...")
        training_data_uri = deployment.upload_training_data(optimized_metadata)
        
        # Step 2: Start training job
        print("\\n2. Starting SageMaker training job with optimized data...")
        estimator, job_name = deployment.create_training_job(training_data_uri)
        
        print(f"✅ Training job '{job_name}' started successfully!")
        print("📊 Training with Bedrock-enhanced, optimized metadata")
        print("⏱️  Training will take 5-10 minutes...")
        
        # Wait for training to complete
        print("\\n3. Waiting for training to complete...")
        estimator.latest_training_job.wait()
        
        # Step 3: Deploy model
        print("\\n4. Deploying optimized model to endpoint...")
        predictor, endpoint_name = deployment.deploy_model(estimator)
        
        # Step 4: Test endpoint with domain-specific questions
        print("\\n5. Testing optimized endpoint...")
        test_optimized_endpoint(predictor)
        
        # Step 5: Create Lambda integration
        print("\\n6. Creating Lambda integration...")
        lambda_code = deployment.create_lambda_integration(endpoint_name)
        
        print("\\n" + "=" * 60)
        print("🎉 OPTIMIZED MODEL DEPLOYMENT COMPLETED!")
        print("=" * 60)
        print(f"📍 SageMaker Endpoint: {endpoint_name}")
        print(f"📁 Training Data: {training_data_uri}")
        print(f"💻 Lambda Code: /home/gyanmis/odata_lambda.py")
        
        print("\\n✅ Key Features:")
        print("• Bedrock-enhanced metadata descriptions")
        print("• Clear service domain differentiation")
        print("• Business-focused field descriptions")
        print("• Comprehensive use case coverage")
        print("• OAuth2 integration ready")
        
        print("\\n🔧 Next Steps:")
        print("1. Update endpoints with your actual SAP system URLs")
        print("2. Configure OAuth2 credentials in AWS Secrets Manager")
        print("3. Create Lambda function using generated code")
        print("4. Set up API Gateway for external access")
        print("5. Test with your real user questions")
        
        return endpoint_name
        
    except Exception as e:
        print(f"\\n❌ Deployment failed: {str(e)}")
        print("Please check the error and try again.")
        return None

def test_optimized_endpoint(predictor):
    """
    Test the optimized endpoint with domain-specific questions
    """
    test_questions = [
        # Customer Master Service questions
        "What is the credit limit for customer ABC123?",
        "Find customer contact information",
        "Get customer address for shipping",
        "Check customer payment terms",
        
        # Sales Order Management Service questions
        "Track my order status",
        "Get order delivery date",
        "Show order line items",
        "Find orders by customer",
        
        # Product Inventory Service questions
        "Check product availability",
        "Get current stock levels",
        "Find product pricing",
        "Check inventory status"
    ]
    
    print("\\n🧪 Testing Optimized Model:")
    print("-" * 50)
    
    for question in test_questions:
        try:
            response = predictor.predict({'question': question})
            print(f"\\n❓ {question}")
            
            for i, pred in enumerate(response[:2], 1):
                service = pred['service']
                confidence = pred['confidence']
                
                # Determine confidence level
                if confidence > 0.7:
                    emoji = "🎯"
                elif confidence > 0.5:
                    emoji = "📊"
                else:
                    emoji = "❓"
                
                print(f"  {i}. {emoji} {service}")
                print(f"     Confidence: {confidence:.3f}")
                
        except Exception as e:
            print(f"❌ Error testing '{question}': {str(e)}")

def create_usage_guide():
    """
    Create a usage guide for the deployed model
    """
    usage_guide = """
# OData AI Classifier Usage Guide

## 🎯 Model Overview
Your OData AI Classifier has been trained on Bedrock-enhanced metadata and deployed to AWS SageMaker.

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
    EndpointName='your-endpoint-name',
    ContentType='application/json',
    Body=json.dumps({'question': 'What is the credit limit for customer ABC?'})
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

## 🔍 Improving Accuracy
1. Add more specific business terminology to metadata
2. Include more use cases and synonyms
3. Test with real user questions and refine descriptions
4. Consider fine-tuning with actual usage data

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
"""
    
    with open('/home/gyanmis/USAGE_GUIDE.md', 'w') as f:
        f.write(usage_guide)
    
    print("📖 Usage guide created: /home/gyanmis/USAGE_GUIDE.md")

if __name__ == "__main__":
    print("🤖 Final OData Model Deployment")
    print("=" * 60)
    print("This will deploy your Bedrock-enhanced OData classifier to AWS SageMaker")
    print()
    
    confirm = input("Ready to deploy? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        endpoint_name = deploy_optimized_model()
        
        if endpoint_name:
            create_usage_guide()
            print(f"\\n🎉 Deployment successful! Endpoint: {endpoint_name}")
        else:
            print("\\n❌ Deployment failed. Please check the logs above.")
    else:
        print("Deployment cancelled.")
