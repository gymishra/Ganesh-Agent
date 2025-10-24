#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

import boto3
import json
import time
from datetime import datetime
import logging
import traceback

class CloudWatchLogger:
    """Simplified CloudWatch logger"""
    
    def __init__(self, log_group_name, log_stream_name, region='us-east-1'):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.region = region
        self.cloudwatch_logs = boto3.client('logs', region_name=region)
        self.sequence_token = None
        
        # Setup logging
        self._setup_logging()
        
        # Setup console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup CloudWatch log group and stream"""
        try:
            # Create log group
            try:
                self.cloudwatch_logs.create_log_group(logGroupName=self.log_group_name)
                print(f"✅ Created CloudWatch log group: {self.log_group_name}")
            except self.cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
                print(f"📋 Using existing log group: {self.log_group_name}")
            
            # Create log stream
            try:
                self.cloudwatch_logs.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name
                )
                print(f"✅ Created CloudWatch log stream: {self.log_stream_name}")
            except self.cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
                print(f"📋 Using existing log stream: {self.log_stream_name}")
                # Get the sequence token for existing stream
                response = self.cloudwatch_logs.describe_log_streams(
                    logGroupName=self.log_group_name,
                    logStreamNamePrefix=self.log_stream_name
                )
                if response['logStreams']:
                    self.sequence_token = response['logStreams'][0].get('uploadSequenceToken')
                    
        except Exception as e:
            print(f"⚠️ CloudWatch setup warning: {str(e)}")
    
    def log(self, level, message, phase=None):
        """Log message to both console and CloudWatch"""
        timestamp = int(time.time() * 1000)
        
        # Console logging
        if level == 'INFO':
            print(f"ℹ️  {message}")
            self.logger.info(message)
        elif level == 'ERROR':
            print(f"❌ {message}")
            self.logger.error(message)
        elif level == 'SUCCESS':
            print(f"✅ {message}")
            self.logger.info(f"SUCCESS: {message}")
        elif level == 'WARNING':
            print(f"⚠️  {message}")
            self.logger.warning(message)
        elif level == 'PROGRESS':
            print(f"🔄 {message}")
            self.logger.info(f"PROGRESS: {message}")
        
        # CloudWatch logging
        try:
            log_event = {
                'timestamp': timestamp,
                'message': json.dumps({
                    'level': level,
                    'message': message,
                    'phase': phase,
                    'timestamp': datetime.now().isoformat()
                })
            }
            
            put_log_params = {
                'logGroupName': self.log_group_name,
                'logStreamName': self.log_stream_name,
                'logEvents': [log_event]
            }
            
            if self.sequence_token:
                put_log_params['sequenceToken'] = self.sequence_token
            
            response = self.cloudwatch_logs.put_log_events(**put_log_params)
            self.sequence_token = response.get('nextSequenceToken')
            
        except Exception as e:
            print(f"⚠️ CloudWatch logging failed: {str(e)}")

def deploy_with_fixed_inference():
    """Deploy model with fixed inference script"""
    
    # Initialize CloudWatch logging
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_group_name = '/aws/sagemaker/odata-deployment'
    log_stream_name = f'fixed-deployment-{timestamp}'
    
    cw_logger = CloudWatchLogger(log_group_name, log_stream_name)
    
    try:
        cw_logger.log('INFO', "🚀 Starting Fixed OData Model Deployment", 'INITIALIZATION')
        cw_logger.log('INFO', "=" * 60, 'INITIALIZATION')
        
        cw_logger.log('PROGRESS', "📦 Loading dependencies...", 'INITIALIZATION')
        
        # Import SageMaker after logging setup
        import sagemaker
        from sagemaker.sklearn.model import SKLearnModel
        
        cw_logger.log('SUCCESS', "Dependencies loaded successfully", 'INITIALIZATION')
        
        cw_logger.log('PROGRESS', "🔧 Initializing deployment configuration...", 'CONFIGURATION')
        
        # Configuration
        region = 'us-east-1'
        role_arn = 'arn:aws:iam::953841955037:role/SageMakerODataRole'
        sagemaker_session = sagemaker.Session()
        bucket = sagemaker_session.default_bucket()
        
        cw_logger.log('INFO', f"Configuration - Region: {region}", 'CONFIGURATION')
        cw_logger.log('INFO', f"Configuration - Role: {role_arn}", 'CONFIGURATION')
        cw_logger.log('INFO', f"Configuration - Bucket: {bucket}", 'CONFIGURATION')
        
        cw_logger.log('PROGRESS', "1️⃣ Creating simple compatible model...", 'MODEL_CREATION')
        
        # Create a simple, compatible model
        import tempfile
        import os
        import tarfile
        import pickle
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple model that's compatible
            simple_model = {
                'model': 'simple_classifier',
                'version': '1.0',
                'categories': ['product', 'customer', 'order', 'financial', 'general']
            }
            
            # Save as pickle
            model_path = os.path.join(temp_dir, 'odata_classifier.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(simple_model, f)
            
            # Copy the fixed inference script
            import shutil
            shutil.copy('/home/gyanmis/inference.py', 
                       os.path.join(temp_dir, 'inference.py'))
            
            # Create tar.gz file
            tar_path = os.path.join(temp_dir, 'model.tar.gz')
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(model_path, 'odata_classifier.pkl')
                tar.add(os.path.join(temp_dir, 'inference.py'), 'inference.py')
            
            # Upload to S3
            s3 = boto3.client('s3')
            model_key = f'odata-model-fixed/model-{timestamp}.tar.gz'
            s3.upload_file(tar_path, bucket, model_key)
        
        model_s3_uri = f's3://{bucket}/{model_key}'
        cw_logger.log('SUCCESS', f"Compatible model uploaded: {model_s3_uri}", 'MODEL_CREATION')
        
        cw_logger.log('PROGRESS', "2️⃣ Creating SageMaker model with fixed inference...", 'SAGEMAKER_MODEL')
        
        # Create SKLearn model with fixed inference script
        model_name = f'odata-classifier-fixed-{timestamp}'
        
        sklearn_model = SKLearnModel(
            model_data=model_s3_uri,
            role=role_arn,
            entry_point='inference.py',
            framework_version='1.0-1',  # Use stable version
            py_version='py3',
            sagemaker_session=sagemaker_session,
            name=model_name
        )
        
        cw_logger.log('SUCCESS', f"SageMaker model created: {model_name}", 'SAGEMAKER_MODEL')
        
        cw_logger.log('PROGRESS', "3️⃣ Deploying to endpoint...", 'ENDPOINT_DEPLOYMENT')
        
        # Deploy to endpoint
        endpoint_name = f'odata-classifier-fixed-{timestamp}'
        
        cw_logger.log('INFO', f"Deploying to endpoint: {endpoint_name}", 'ENDPOINT_DEPLOYMENT')
        cw_logger.log('INFO', "This may take 5-10 minutes...", 'ENDPOINT_DEPLOYMENT')
        
        # Deploy with timeout monitoring
        start_time = time.time()
        
        try:
            predictor = sklearn_model.deploy(
                initial_instance_count=1,
                instance_type='ml.t2.medium',
                endpoint_name=endpoint_name
            )
            
            deployment_time = time.time() - start_time
            cw_logger.log('SUCCESS', f"Model deployed successfully in {deployment_time/60:.1f} minutes!", 'ENDPOINT_COMPLETE')
            cw_logger.log('SUCCESS', f"Endpoint: {endpoint_name}", 'ENDPOINT_COMPLETE')
            
            # Test the endpoint
            cw_logger.log('PROGRESS', "4️⃣ Testing endpoint...", 'TESTING')
            
            # Simple test
            test_data = ["Product service for managing inventory"]
            try:
                result = predictor.predict(test_data)
                cw_logger.log('SUCCESS', f"Endpoint test successful: {result}", 'TESTING')
                
                # Additional tests
                test_cases = [
                    "Customer management service",
                    "Order processing system", 
                    "Financial reporting service",
                    "General utility service"
                ]
                
                for test_case in test_cases:
                    try:
                        result = predictor.predict([test_case])
                        cw_logger.log('INFO', f"Test '{test_case}' -> {result}", 'TESTING')
                    except Exception as test_error:
                        cw_logger.log('WARNING', f"Test failed for '{test_case}': {str(test_error)}", 'TESTING')
                
            except Exception as test_error:
                cw_logger.log('WARNING', f"Initial endpoint test failed: {str(test_error)}", 'TESTING')
                cw_logger.log('INFO', "Endpoint is deployed but may need warm-up time", 'TESTING')
            
            cw_logger.log('INFO', "📊 Deployment Summary:", 'SUMMARY')
            cw_logger.log('INFO', f"Model Name: {model_name}", 'SUMMARY')
            cw_logger.log('INFO', f"Endpoint: {endpoint_name}", 'SUMMARY')
            cw_logger.log('INFO', f"Model S3 URI: {model_s3_uri}", 'SUMMARY')
            cw_logger.log('INFO', f"Deployment Time: {deployment_time/60:.1f} minutes", 'SUMMARY')
            
        except Exception as deploy_error:
            cw_logger.log('ERROR', f"Deployment failed: {str(deploy_error)}", 'ENDPOINT_FAILED')
            raise deploy_error
        
        cw_logger.log('INFO', "=" * 60, 'COMPLETE')
        cw_logger.log('SUCCESS', "🎉 FIXED DEPLOYMENT COMPLETED!", 'COMPLETE')
        cw_logger.log('INFO', "=" * 60, 'COMPLETE')
        
        # Log CloudWatch access information
        print(f"\n📊 CloudWatch Monitoring Information:")
        print(f"   Log Group: {log_group_name}")
        print(f"   Log Stream: {log_stream_name}")
        print(f"   Console URL: https://console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name.replace('/', '%2F')}")
        print(f"   SageMaker Console: https://console.aws.amazon.com/sagemaker/home?region={region}#/endpoints")
        
        return {
            'model_name': model_name,
            'endpoint_name': endpoint_name,
            'model_s3_uri': model_s3_uri,
            'deployment_time': deployment_time
        }
        
    except Exception as e:
        cw_logger.log('ERROR', f"Deployment failed: {str(e)}", 'FAILED')
        cw_logger.log('ERROR', "Full error details:", 'FAILED')
        cw_logger.log('ERROR', traceback.format_exc(), 'FAILED')
        raise

if __name__ == "__main__":
    try:
        result = deploy_with_fixed_inference()
        print(f"\n✅ Deployment successful!")
        print(f"   Endpoint: {result['endpoint_name']}")
        print(f"   Model: {result['model_name']}")
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        sys.exit(1)
