#!/usr/bin/env python3

import sys
sys.path.append('/home/gyanmis')

print("🚀 Starting OData Model Deployment with Monitoring")
print("=" * 60)

try:
    print("📦 Loading dependencies...")
    import boto3
    import json
    import sagemaker
    from sagemaker.sklearn.estimator import SKLearn
    from datetime import datetime
    import time
    print("✅ Dependencies loaded successfully")
    
    print("\n📋 Loading optimized metadata...")
    with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
        optimized_metadata = json.load(f)
    
    # Remove metadata section
    if '_metadata' in optimized_metadata:
        del optimized_metadata['_metadata']
    
    print(f"✅ Loaded metadata for {len(optimized_metadata)} services")
    
    print("\n🔧 Initializing deployment configuration...")
    
    # Configuration
    region = 'us-east-1'
    role_arn = 'arn:aws:iam::953841955037:role/SageMakerODataRole'
    sagemaker_session = sagemaker.Session()
    bucket = sagemaker_session.default_bucket()
    
    print(f"✅ Configuration:")
    print(f"   - Region: {region}")
    print(f"   - Role: {role_arn}")
    print(f"   - Bucket: {bucket}")
    
    print("\n1️⃣ Uploading metadata to S3...")
    s3_key = 'odata-training-data/odata_metadata.json'
    s3_uri = f's3://{bucket}/{s3_key}'
    
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=json.dumps(optimized_metadata, indent=2),
        ContentType='application/json'
    )
    print(f"✅ Training data uploaded: {s3_uri}")
    
    print("\n2️⃣ Creating SageMaker training job...")
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    job_name = f'odata-classifier-monitored-{timestamp}'
    
    print(f"   Job name: {job_name}")
    
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
    print("✅ SKLearn estimator created")
    
    print("\n3️⃣ Starting training job...")
    
    # Start training job without waiting
    sklearn_estimator.fit(
        {'training': s3_uri},
        job_name=job_name,
        wait=False
    )
    print(f"✅ Training job '{job_name}' submitted!")
    
    print("\n4️⃣ Monitoring training job with timeout...")
    print("   Maximum wait time: 20 minutes")
    
    # Monitor training job with timeout
    sagemaker_client = boto3.client('sagemaker', region_name=region)
    max_wait_time = 1200  # 20 minutes
    start_time = time.time()
    check_interval = 30  # Check every 30 seconds
    
    while True:
        elapsed_time = time.time() - start_time
        
        if elapsed_time > max_wait_time:
            print(f"⏰ Timeout reached ({max_wait_time/60} minutes)")
            print("   Training job is still running but we'll proceed to check status")
            break
        
        try:
            # Get training job status
            response = sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            
            status = response['TrainingJobStatus']
            print(f"   Status: {status} (elapsed: {elapsed_time/60:.1f} min)")
            
            if status == 'Completed':
                print("✅ Training completed successfully!")
                break
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown error')
                print(f"❌ Training failed: {failure_reason}")
                raise Exception(f"Training job failed: {failure_reason}")
            elif status == 'Stopped':
                print("⏹️ Training job was stopped")
                raise Exception("Training job was stopped")
            
            # Wait before next check
            time.sleep(check_interval)
            
        except Exception as e:
            if "does not exist" in str(e):
                print(f"⚠️ Training job not found yet, waiting...")
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
            print(f"⚠️ Training job status: {final_status}")
            print("   You can monitor progress in the SageMaker console")
            print(f"   Job name: {job_name}")
            
            # Don't proceed to deployment if training isn't complete
            print("\n📊 Deployment Summary:")
            print(f"   Training Job: {job_name}")
            print(f"   Status: {final_status}")
            print(f"   Training Data: {s3_uri}")
            print("\n💡 Next Steps:")
            print("1. Wait for training to complete")
            print("2. Check SageMaker console for detailed logs")
            print("3. Run deployment again once training is complete")
            
        else:
            print("\n5️⃣ Training completed! Proceeding to deployment...")
            
            # Deploy the model
            timestamp_deploy = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            endpoint_name = f'odata-classifier-endpoint-{timestamp_deploy}'
            
            print(f"   Deploying to endpoint: {endpoint_name}")
            
            predictor = sklearn_estimator.deploy(
                initial_instance_count=1,
                instance_type='ml.t2.medium',
                endpoint_name=endpoint_name
            )
            print(f"✅ Model deployed to endpoint: {endpoint_name}")
            
            print("\n📊 Deployment Summary:")
            print(f"   Endpoint: {endpoint_name}")
            print(f"   Training Job: {job_name}")
            print(f"   Training Data: {s3_uri}")
            
    except Exception as e:
        print(f"⚠️ Could not get final training status: {str(e)}")
        print("   Check SageMaker console for job status")
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT SCRIPT COMPLETED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Deployment failed: {str(e)}")
    import traceback
    print("\n🔍 Full error details:")
    traceback.print_exc()
