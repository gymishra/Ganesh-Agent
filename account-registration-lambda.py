import json
import boto3
import re

def lambda_handler(event, context):
    """
    Lambda function to automatically register workshop participant accounts
    """
    try:
        # Extract account ID from the request
        account_id = event.get('account_id') or event.get('AccountId')
        
        if not account_id:
            # Try to extract from caller identity
            sts = boto3.client('sts')
            caller_identity = sts.get_caller_identity()
            account_id = caller_identity['Account']
        
        # Validate account ID format
        if not re.match(r'^\d{12}$', account_id):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid account ID format'})
            }
        
        # Get current bucket policy
        s3 = boto3.client('s3')
        bucket_name = 'wrkshp-qbiz-data'
        
        try:
            response = s3.get_bucket_policy(Bucket=bucket_name)
            current_policy = json.loads(response['Policy'])
        except s3.exceptions.NoSuchBucketPolicy:
            # Create new policy if none exists
            current_policy = {
                "Version": "2012-10-17",
                "Statement": []
            }
        
        # Find the workshop accounts statement
        workshop_statement = None
        for statement in current_policy['Statement']:
            if statement.get('Sid') == 'AllowWorkshopAccounts':
                workshop_statement = statement
                break
        
        if not workshop_statement:
            # Create new statement
            workshop_statement = {
                "Sid": "AllowWorkshopAccounts",
                "Effect": "Allow",
                "Principal": {"AWS": []},
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket", 
                    "s3:GetBucketLocation"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }
            current_policy['Statement'].append(workshop_statement)
        
        # Add account if not already present
        account_arn = f"arn:aws:iam::{account_id}:root"
        if isinstance(workshop_statement['Principal']['AWS'], str):
            workshop_statement['Principal']['AWS'] = [workshop_statement['Principal']['AWS']]
        
        if account_arn not in workshop_statement['Principal']['AWS']:
            workshop_statement['Principal']['AWS'].append(account_arn)
            
            # Update bucket policy
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(current_policy)
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Account {account_id} registered successfully',
                    'account_id': account_id
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Account {account_id} already registered',
                    'account_id': account_id
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
