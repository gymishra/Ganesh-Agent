#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

import boto3
import json
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from datetime import datetime
import time
import logging
import traceback

class CloudWatchLogger:
    """Custom CloudWatch logger for deployment monitoring"""
    
    def __init__(self, log_group_name, log_stream_name, region='us-east-1'):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.region = region
        self.cloudwatch_logs = boto3.client('logs', region_name=region)
        self.cloudwatch_metrics = boto3.client('cloudwatch', region_name=region)
        self.sequence_token = None
        
        # Create log group and stream
        self._setup_logging()
        
        # Setup console logging too
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
    
    def send_metric(self, metric_name, value, unit='Count', phase=None):
        """Send custom metric to CloudWatch"""
        try:
            dimensions = [
                {'Name': 'DeploymentPhase', 'Value': phase or 'Unknown'},
                {'Name': 'LogStream', 'Value': self.log_stream_name}
            ]
            
            self.cloudwatch_metrics.put_metric_data(
                Namespace='SageMaker/ODataDeployment',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Dimensions': dimensions,
                        'Timestamp': datetime.now()
                    }
                ]
            )
            self.log('INFO', f"📊 Metric sent: {metric_name} = {value} {unit}", phase)
        except Exception as e:
            self.log('WARNING', f"Failed to send metric {metric_name}: {str(e)}", phase)

def main():
    # Initialize CloudWatch logging
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    log_group_name = '/aws/sagemaker/odata-deployment'
    log_stream_name = f'deployment-{timestamp}'
    
    cw_logger = CloudWatchLogger(log_group_name, log_stream_name)
    
    try:
        cw_logger.log('INFO', "🚀 Starting OData Model Deployment with CloudWatch Monitoring", 'INITIALIZATION')
        cw_logger.log('INFO', "=" * 60, 'INITIALIZATION')
        
        # Send deployment start metric
        cw_logger.send_metric('DeploymentStarted', 1, 'Count', 'INITIALIZATION')
        
        cw_logger.log('PROGRESS', "📦 Loading dependencies...", 'INITIALIZATION')
        
        # Load dependencies with progress tracking
        start_time = time.time()
        
        cw_logger.log('SUCCESS', "Dependencies loaded successfully", 'INITIALIZATION')
        
        cw_logger.log('PROGRESS', "📋 Loading optimized metadata...", 'DATA_PREPARATION')
        with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
            optimized_metadata = json.load(f)
        
        # Remove metadata section
        if '_metadata' in optimized_metadata:
            del optimized_metadata['_metadata']
        
        services_count = len(optimized_metadata)
        cw_logger.log('SUCCESS', f"Loaded metadata for {services_count} services", 'DATA_PREPARATION')
        cw_logger.send_metric('ServicesLoaded', services_count, 'Count', 'DATA_PREPARATION')
        
        cw_logger.log('PROGRESS', "🔧 Initializing deployment configuration...", 'CONFIGURATION')
        
        # Configuration
        region = 'us-east-1'
        role_arn = 'arn:aws:iam::953841955037:role/SageMakerODataRole'
        sagemaker_session = sagemaker.Session()
        bucket = sagemaker_session.default_bucket()
        
        cw_logger.log('INFO', f"Configuration - Region: {region}", 'CONFIGURATION')
        cw_logger.log('INFO', f"Configuration - Role: {role_arn}", 'CONFIGURATION')
        cw_logger.log('INFO', f"Configuration - Bucket: {bucket}", 'CONFIGURATION')
        
        cw_logger.log('PROGRESS', "1️⃣ Uploading metadata to S3...", 'S3_UPLOAD')
        s3_key = 'odata-training-data/odata_metadata.json'
        s3_uri = f's3://{bucket}/{s3_key}'
        
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json.dumps(optimized_metadata, indent=2),
            ContentType='application/json'
        )
        cw_logger.log('SUCCESS', f"Training data uploaded: {s3_uri}", 'S3_UPLOAD')
        cw_logger.send_metric('S3UploadCompleted', 1, 'Count', 'S3_UPLOAD')
        
        cw_logger.log('PROGRESS', "2️⃣ Creating SageMaker training job...", 'TRAINING_SETUP')
        job_name = f'odata-classifier-monitored-{timestamp}'
        
        cw_logger.log('INFO', f"Job name: {job_name}", 'TRAINING_SETUP')
        
        # Create SKLearn estimator
        sklearn_estimator = SKLearn(
            entry_point='train.py',
            source_dir='/home/gyanmis',
            role=role_arn,
            instance_type='ml.m5.large',
            instance_count=1,
            framework_version='1.2-1',
            py_version='py3',
            script_mode=True,
            hyperparameters={
                'n_estimators': 150,
                'max_features': 1500,
                'test_size': 0.2
            },
            output_path=f's3://{bucket}/odata-model-output',
            sagemaker_session=sagemaker_session
        )
        cw_logger.log('SUCCESS', "SKLearn estimator created", 'TRAINING_SETUP')
        
        cw_logger.log('PROGRESS', "3️⃣ Starting training job...", 'TRAINING_START')
        
        # Start training job without waiting
        sklearn_estimator.fit(
            {'training': s3_uri},
            job_name=job_name,
            wait=False
        )
        cw_logger.log('SUCCESS', f"Training job '{job_name}' submitted!", 'TRAINING_START')
        cw_logger.send_metric('TrainingJobStarted', 1, 'Count', 'TRAINING_START')
        
        cw_logger.log('PROGRESS', "4️⃣ Monitoring training job with timeout...", 'TRAINING_MONITOR')
        cw_logger.log('INFO', "Maximum wait time: 20 minutes", 'TRAINING_MONITOR')
        
        # Monitor training job with timeout
        sagemaker_client = boto3.client('sagemaker', region_name=region)
        max_wait_time = 1200  # 20 minutes
        training_start_time = time.time()
        check_interval = 30  # Check every 30 seconds
        
        while True:
            elapsed_time = time.time() - training_start_time
            
            if elapsed_time > max_wait_time:
                cw_logger.log('WARNING', f"Timeout reached ({max_wait_time/60} minutes)", 'TRAINING_MONITOR')
                cw_logger.log('INFO', "Training job is still running but we'll proceed to check status", 'TRAINING_MONITOR')
                cw_logger.send_metric('TrainingTimeout', 1, 'Count', 'TRAINING_MONITOR')
                break
            
            try:
                # Get training job status
                response = sagemaker_client.describe_training_job(
                    TrainingJobName=job_name
                )
                
                status = response['TrainingJobStatus']
                cw_logger.log('INFO', f"Status: {status} (elapsed: {elapsed_time/60:.1f} min)", 'TRAINING_MONITOR')
                
                # Send training progress metrics
                cw_logger.send_metric('TrainingElapsedMinutes', elapsed_time/60, 'None', 'TRAINING_MONITOR')
                
                if status == 'Completed':
                    cw_logger.log('SUCCESS', "Training completed successfully!", 'TRAINING_COMPLETE')
                    cw_logger.send_metric('TrainingCompleted', 1, 'Count', 'TRAINING_COMPLETE')
                    break
                elif status == 'Failed':
                    failure_reason = response.get('FailureReason', 'Unknown error')
                    cw_logger.log('ERROR', f"Training failed: {failure_reason}", 'TRAINING_FAILED')
                    cw_logger.send_metric('TrainingFailed', 1, 'Count', 'TRAINING_FAILED')
                    raise Exception(f"Training job failed: {failure_reason}")
                elif status == 'Stopped':
                    cw_logger.log('WARNING', "Training job was stopped", 'TRAINING_STOPPED')
                    cw_logger.send_metric('TrainingStopped', 1, 'Count', 'TRAINING_STOPPED')
                    raise Exception("Training job was stopped")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except Exception as e:
                if "does not exist" in str(e):
                    cw_logger.log('WARNING', "Training job not found yet, waiting...", 'TRAINING_MONITOR')
                    time.sleep(check_interval)
                    continue
                else:
                    raise e
        
        # Check final status
        try:
            final_response = sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            final_status = final_response['TrainingJobStatus']
            
            if final_status != 'Completed':
                cw_logger.log('WARNING', f"Training job status: {final_status}", 'TRAINING_INCOMPLETE')
                cw_logger.log('INFO', "You can monitor progress in the SageMaker console", 'TRAINING_INCOMPLETE')
                cw_logger.log('INFO', f"Job name: {job_name}", 'TRAINING_INCOMPLETE')
                
                # Don't proceed to deployment if training isn't complete
                cw_logger.log('INFO', "📊 Deployment Summary:", 'SUMMARY')
                cw_logger.log('INFO', f"Training Job: {job_name}", 'SUMMARY')
                cw_logger.log('INFO', f"Status: {final_status}", 'SUMMARY')
                cw_logger.log('INFO', f"Training Data: {s3_uri}", 'SUMMARY')
                cw_logger.log('INFO', "💡 Next Steps:", 'SUMMARY')
                cw_logger.log('INFO', "1. Wait for training to complete", 'SUMMARY')
                cw_logger.log('INFO', "2. Check SageMaker console for detailed logs", 'SUMMARY')
                cw_logger.log('INFO', "3. Run deployment again once training is complete", 'SUMMARY')
                
            else:
                cw_logger.log('PROGRESS', "5️⃣ Training completed! Proceeding to deployment...", 'DEPLOYMENT_START')
                
                # Deploy the model
                timestamp_deploy = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                endpoint_name = f'odata-classifier-endpoint-{timestamp_deploy}'
                
                cw_logger.log('INFO', f"Deploying to endpoint: {endpoint_name}", 'DEPLOYMENT_START')
                
                predictor = sklearn_estimator.deploy(
                    initial_instance_count=1,
                    instance_type='ml.t2.medium',
                    endpoint_name=endpoint_name
                )
                cw_logger.log('SUCCESS', f"Model deployed to endpoint: {endpoint_name}", 'DEPLOYMENT_COMPLETE')
                cw_logger.send_metric('DeploymentCompleted', 1, 'Count', 'DEPLOYMENT_COMPLETE')
                
                cw_logger.log('INFO', "📊 Deployment Summary:", 'SUMMARY')
                cw_logger.log('INFO', f"Endpoint: {endpoint_name}", 'SUMMARY')
                cw_logger.log('INFO', f"Training Job: {job_name}", 'SUMMARY')
                cw_logger.log('INFO', f"Training Data: {s3_uri}", 'SUMMARY')
                
        except Exception as e:
            cw_logger.log('WARNING', f"Could not get final training status: {str(e)}", 'STATUS_CHECK_FAILED')
            cw_logger.log('INFO', "Check SageMaker console for job status", 'STATUS_CHECK_FAILED')
        
        # Calculate total deployment time
        total_time = time.time() - start_time
        cw_logger.send_metric('TotalDeploymentTimeMinutes', total_time/60, 'None', 'SUMMARY')
        
        cw_logger.log('INFO', "=" * 60, 'COMPLETE')
        cw_logger.log('SUCCESS', "🎉 DEPLOYMENT SCRIPT COMPLETED!", 'COMPLETE')
        cw_logger.log('INFO', f"Total time: {total_time/60:.1f} minutes", 'COMPLETE')
        cw_logger.log('INFO', "=" * 60, 'COMPLETE')
        
        # Send final success metric
        cw_logger.send_metric('DeploymentSuccess', 1, 'Count', 'COMPLETE')
        
        # Log CloudWatch access information
        print(f"\n📊 CloudWatch Monitoring Information:")
        print(f"   Log Group: {log_group_name}")
        print(f"   Log Stream: {log_stream_name}")
        print(f"   Metrics Namespace: SageMaker/ODataDeployment")
        print(f"   Console URL: https://console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name.replace('/', '%2F')}")
        
    except Exception as e:
        cw_logger.log('ERROR', f"Deployment failed: {str(e)}", 'FAILED')
        cw_logger.log('ERROR', "Full error details:", 'FAILED')
        cw_logger.log('ERROR', traceback.format_exc(), 'FAILED')
        cw_logger.send_metric('DeploymentFailed', 1, 'Count', 'FAILED')
        raise

if __name__ == "__main__":
    main()
