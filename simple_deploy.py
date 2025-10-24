#!/usr/bin/env python3

import boto3
import json
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from datetime import datetime
import time

def deploy_odata_classifier():
    """
    Simplified deployment of OData classifier
    """
    print("🚀 Deploying OData AI Classifier to AWS")
    print("=" * 50)
    
    # Initialize AWS clients
    session = sagemaker.Session()
    role_arn = sagemaker.get_execution_role()
    bucket = session.default_bucket()
    
    print(f"📋 Using S3 bucket: {bucket}")
    print(f"🔐 Using IAM role: {role_arn}")
    
    # Load optimized metadata
    with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
        metadata = json.load(f)
    
    if '_metadata' in metadata:
        del metadata['_metadata']
    
    print(f"📊 Deploying {len(metadata)} services:")
    for service_name in metadata.keys():
        print(f"  • {service_name}")
    
    try:
        # Step 1: Upload training data to S3
        print("\n1️⃣ Uploading training data to S3...")
        s3_key = 'odata-training-data/odata_metadata.json'
        s3_uri = f's3://{bucket}/{s3_key}'
        
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json.dumps(metadata, indent=2),
            ContentType='application/json'
        )
        print(f"✅ Training data uploaded to: {s3_uri}")
        
        # Step 2: Create SageMaker training job
        print("\n2️⃣ Creating SageMaker training job...")
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        job_name = f'odata-classifier-{timestamp}'
        
        sklearn_estimator = SKLearn(
            entry_point='train.py',
            source_dir='/home/gyanmis',
            role=role_arn,
            instance_type='ml.m5.large',
            instance_count=1,
            framework_version='1.0-1',
            py_version='py3',
            hyperparameters={
                'n_estimators': 150,
                'max_features': 1500,
                'test_size': 0.2
            },
            output_path=f's3://{bucket}/odata-model-output',
            sagemaker_session=session
        )
        
        # Start training (non-blocking)
        sklearn_estimator.fit(
            {'training': s3_uri},
            job_name=job_name,
            wait=False
        )
        
        print(f"✅ Training job started: {job_name}")
        print("⏱️  Training will take 5-10 minutes...")
        
        # Step 3: Create Lambda integration code
        print("\n3️⃣ Generating Lambda integration code...")
        lambda_code = f'''
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to invoke OData service classifier
    """
    try:
        # Extract question from event
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            question = body.get('question', '')
        else:
            question = event.get('question', '')
        
        if not question:
            return {{
                'statusCode': 400,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{'error': 'Question parameter is required'}})
            }}
        
        logger.info(f"Processing question: {{question}}")
        
        # TODO: Replace with your actual endpoint name after training completes
        endpoint_name = 'odata-classifier-endpoint-{timestamp}'
        
        # Invoke SageMaker endpoint
        runtime = boto3.client('runtime.sagemaker')
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({{'question': question}})
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        # Get top prediction
        top_prediction = result[0] if result else {{'service': 'unknown', 'confidence': 0.0}}
        
        # TODO: Add OAuth2 integration here
        # oauth2_token = get_oauth2_token(top_prediction['service'])
        # odata_response = call_odata_service(top_prediction['service'], question, oauth2_token)
        
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{
                'question': question,
                'predicted_service': top_prediction['service'],
                'confidence': top_prediction['confidence'],
                'all_predictions': result,
                'message': 'Add OAuth2 integration to call actual OData service'
            }})
        }}
        
    except Exception as e:
        logger.error(f"Error processing request: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': str(e)}})
        }}

def get_oauth2_token(service_name):
    """
    Get OAuth2 token for the specified service
    """
    # TODO: Implement OAuth2 token retrieval from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret_name = f"{{service_name.lower()}}-secret"
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        credentials = json.loads(response['SecretString'])
        
        # Make OAuth2 token request
        # Implementation depends on your SAP OAuth2 configuration
        
        return "your-oauth2-token"
    except Exception as e:
        logger.error(f"Failed to get OAuth2 token: {{str(e)}}")
        return None

def call_odata_service(service_name, question, token):
    """
    Call the actual OData service
    """
    # TODO: Implement actual OData service calls
    # This would map service_name to actual OData endpoints
    # and make authenticated requests
    
    service_endpoints = {{
        'CustomerMasterService': 'https://your-sap-system/odata/CustomerMasterService',
        'SalesOrderManagementService': 'https://your-sap-system/odata/SalesOrderManagementService',
        'ProductInventoryService': 'https://your-sap-system/odata/ProductInventoryService'
    }}
    
    endpoint = service_endpoints.get(service_name)
    if not endpoint:
        return {{'error': f'Unknown service: {{service_name}}'}}
    
    # Make authenticated OData request
    # Implementation depends on your specific OData queries
    
    return {{'message': f'Would call {{endpoint}} with token {{token}}'}}
'''
        
        with open('/home/gyanmis/odata_lambda_generated.py', 'w') as f:
            f.write(lambda_code)
        
        print("✅ Lambda code generated: /home/gyanmis/odata_lambda_generated.py")
        
        # Step 4: Create deployment summary
        print("\n4️⃣ Creating deployment summary...")
        summary = {
            'deployment_timestamp': datetime.now().isoformat(),
            'training_job_name': job_name,
            'training_data_s3_uri': s3_uri,
            'services_deployed': list(metadata.keys()),
            'next_steps': [
                'Monitor training job in SageMaker console',
                'Deploy model to endpoint after training completes',
                'Create Lambda function using generated code',
                'Configure OAuth2 credentials in Secrets Manager',
                'Set up API Gateway for external access'
            ]
        }
        
        with open('/home/gyanmis/deployment_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("✅ Deployment summary saved: /home/gyanmis/deployment_summary.json")
        
        # Success message
        print("\n" + "🎉" * 20)
        print("DEPLOYMENT INITIATED SUCCESSFULLY!")
        print("🎉" * 20)
        
        print(f"\n📊 Training Job: {job_name}")
        print(f"📁 Training Data: {s3_uri}")
        print(f"🔧 Lambda Code: /home/gyanmis/odata_lambda_generated.py")
        
        print("\n📋 What's Happening Now:")
        print("1. ⏳ SageMaker is training your model (5-10 minutes)")
        print("2. 🤖 Model learns to route questions to correct OData services")
        print("3. 📊 Training uses Bedrock-enhanced metadata for better accuracy")
        
        print("\n🔄 Next Steps (after training completes):")
        print("1. 🚀 Deploy model to SageMaker endpoint")
        print("2. 🔧 Create Lambda function with generated code")
        print("3. 🔐 Configure OAuth2 credentials in Secrets Manager")
        print("4. 🌐 Set up API Gateway for external access")
        print("5. 🧪 Test with real user questions")
        
        print(f"\n📈 Monitor Progress:")
        print(f"   AWS Console → SageMaker → Training Jobs → {job_name}")
        
        return job_name
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check AWS credentials and permissions")
        print("2. Verify SageMaker service limits")
        print("3. Check S3 bucket access")
        return None

if __name__ == "__main__":
    deploy_odata_classifier()
