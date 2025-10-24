#!/usr/bin/env python3

import boto3
import json
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.model import SKLearnModel
import time
from datetime import datetime

class ODataModelDeployment:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.sagemaker_session = sagemaker.Session()
        self.role = self.get_or_create_sagemaker_role()
        self.bucket = self.sagemaker_session.default_bucket()
        
    def get_or_create_sagemaker_role(self):
        """
        Get or create SageMaker execution role
        """
        iam = boto3.client('iam')
        role_name = 'SageMakerODataRole'
        
        try:
            role = iam.get_role(RoleName=role_name)
            return role['Role']['Arn']
        except iam.exceptions.NoSuchEntityException:
            print(f"Creating SageMaker role: {role_name}")
            
            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "sagemaker.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='SageMaker execution role for OData model training'
            )
            
            # Attach policies
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
            )
            
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
            )
            
            # Wait for role to be available
            time.sleep(10)
            
            return role['Role']['Arn']
    
    def upload_training_data(self, odata_metadata):
        """
        Upload OData metadata to S3 for training
        """
        s3_key = 'odata-training-data/odata_metadata.json'
        s3_uri = f's3://{self.bucket}/{s3_key}'
        
        # Upload metadata to S3
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=json.dumps(odata_metadata, indent=2),
            ContentType='application/json'
        )
        
        print(f"Training data uploaded to: {s3_uri}")
        return s3_uri
    
    def create_training_job(self, training_data_uri):
        """
        Create and start SageMaker training job
        """
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        job_name = f'odata-classifier-{timestamp}'
        
        # Create SKLearn estimator
        sklearn_estimator = SKLearn(
            entry_point='train.py',
            source_dir='/home/gyanmis',  # Directory containing train.py
            role=self.role,
            instance_type='ml.m5.large',
            instance_count=1,
            framework_version='1.0-1',
            py_version='py3',
            script_mode=True,
            hyperparameters={
                'n_estimators': 150,
                'max_features': 1500,
                'test_size': 0.2
            },
            output_path=f's3://{self.bucket}/odata-model-output',
            sagemaker_session=self.sagemaker_session
        )
        
        # Start training
        print(f"Starting training job: {job_name}")
        sklearn_estimator.fit(
            {'training': training_data_uri},
            job_name=job_name,
            wait=False
        )
        
        return sklearn_estimator, job_name
    
    def deploy_model(self, estimator, endpoint_name=None):
        """
        Deploy trained model to SageMaker endpoint
        """
        if endpoint_name is None:
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            endpoint_name = f'odata-classifier-endpoint-{timestamp}'
        
        print(f"Deploying model to endpoint: {endpoint_name}")
        
        predictor = estimator.deploy(
            initial_instance_count=1,
            instance_type='ml.t2.medium',
            endpoint_name=endpoint_name
        )
        
        return predictor, endpoint_name
    
    def test_endpoint(self, predictor):
        """
        Test the deployed endpoint with sample questions
        """
        test_questions = [
            "What is the credit limit for customer ABC123?",
            "Show me recent sales orders",
            "Find customer contact information",
            "Track order status for order 12345",
            "Get customer payment terms",
            "List all products in inventory",
            "Update customer address information"
        ]
        
        print("\nTesting deployed endpoint:")
        print("=" * 50)
        
        for question in test_questions:
            try:
                response = predictor.predict({'question': question})
                print(f"\nQuestion: {question}")
                print("Predictions:")
                for pred in response:
                    print(f"  - Service: {pred['service']}")
                    print(f"    Confidence: {pred['confidence']:.3f}")
            except Exception as e:
                print(f"Error testing question '{question}': {str(e)}")
    
    def create_lambda_integration(self, endpoint_name):
        """
        Create Lambda function to integrate with the SageMaker endpoint
        """
        lambda_code = f'''
import json
import boto3

def lambda_handler(event, context):
    """
    Lambda function to invoke OData service classifier
    """
    runtime = boto3.client('runtime.sagemaker')
    endpoint_name = '{endpoint_name}'
    
    try:
        # Extract question from event
        question = event.get('question', '')
        if not question:
            return {{
                'statusCode': 400,
                'body': json.dumps({{'error': 'Question parameter is required'}})
            }}
        
        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({{'question': question}})
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'question': question,
                'predictions': result
            }})
        }}
        
    except Exception as e:
        return {{
            'statusCode': 500,
            'body': json.dumps({{'error': str(e)}})
        }}
'''
        
        # Save Lambda code to file
        with open('/home/gyanmis/odata_lambda.py', 'w') as f:
            f.write(lambda_code)
        
        print(f"Lambda integration code saved to: /home/gyanmis/odata_lambda.py")
        print(f"Endpoint name: {endpoint_name}")
        
        return lambda_code

def main():
    """
    Main deployment function
    """
    print("Starting OData Model Training and Deployment Pipeline")
    print("=" * 60)
    
    # Initialize deployment
    deployment = ODataModelDeployment()
    
    # Sample OData metadata (replace with your actual metadata)
    sample_odata_metadata = {
        "CustomerService": {
            "endpoint": "https://sap-system/odata/CustomerService",
            "oauth2_config": {
                "token_endpoint": "https://sap-system/oauth/token",
                "client_id": "customer-service-client"
            },
            "purpose": "Manages customer master data including demographics, contact information, credit limits, and business relationships for all business partners",
            "entities": {
                "Customer": {
                    "description": "Core customer entity containing comprehensive business partner information and financial details",
                    "fields": {
                        "CustomerID": "Unique identifier for customer records in the system",
                        "CompanyName": "Legal business name of the customer organization",
                        "Industry": "Business sector classification and industry type",
                        "CreditLimit": "Maximum credit amount approved for customer transactions",
                        "ContactEmail": "Primary email address for customer communication",
                        "PaymentTerms": "Standard payment terms and conditions for the customer",
                        "CustomerType": "Classification of customer type (retail, wholesale, enterprise)",
                        "RegistrationDate": "Date when customer was first registered in the system"
                    }
                },
                "CustomerAddress": {
                    "description": "Customer address information including billing and shipping addresses",
                    "fields": {
                        "AddressID": "Unique identifier for address records",
                        "CustomerID": "Reference to the customer this address belongs to",
                        "AddressType": "Type of address (billing, shipping, mailing)",
                        "Street": "Street address line",
                        "City": "City name",
                        "PostalCode": "Postal or ZIP code",
                        "Country": "Country code"
                    }
                }
            },
            "use_cases": ["customer lookup", "credit checks", "contact management", "customer demographics", "address management"]
        },
        "SalesOrderService": {
            "endpoint": "https://sap-system/odata/SalesOrderService",
            "oauth2_config": {
                "token_endpoint": "https://sap-system/oauth/token",
                "client_id": "sales-service-client"
            },
            "purpose": "Handles comprehensive sales order processing, order tracking, line items, pricing, and order fulfillment status management",
            "entities": {
                "SalesOrder": {
                    "description": "Sales order header information with customer details, pricing, and order management data",
                    "fields": {
                        "OrderID": "Unique sales order identifier",
                        "CustomerID": "Reference to customer who placed the order",
                        "OrderDate": "Date when the sales order was created",
                        "OrderStatus": "Current status of the sales order processing",
                        "TotalAmount": "Total monetary value of the sales order including taxes",
                        "DeliveryDate": "Planned or actual delivery date for the order",
                        "SalesRep": "Sales representative responsible for this order",
                        "OrderType": "Type of sales order (standard, rush, bulk)"
                    }
                },
                "SalesOrderItem": {
                    "description": "Individual line items within a sales order with product and pricing details",
                    "fields": {
                        "ItemID": "Unique identifier for the order line item",
                        "OrderID": "Reference to the parent sales order",
                        "ProductID": "Reference to the product being ordered",
                        "Quantity": "Number of units ordered for this item",
                        "UnitPrice": "Price per unit for the product",
                        "LineTotal": "Total amount for this line item",
                        "DiscountPercent": "Discount percentage applied to this line item"
                    }
                }
            },
            "use_cases": ["order tracking", "sales data", "order history", "order fulfillment", "sales reporting", "order status updates"]
        },
        "ProductService": {
            "endpoint": "https://sap-system/odata/ProductService",
            "oauth2_config": {
                "token_endpoint": "https://sap-system/oauth/token",
                "client_id": "product-service-client"
            },
            "purpose": "Manages product catalog, inventory levels, pricing information, and product specifications",
            "entities": {
                "Product": {
                    "description": "Product master data with specifications, pricing, and inventory information",
                    "fields": {
                        "ProductID": "Unique product identifier",
                        "ProductName": "Display name of the product",
                        "Description": "Detailed product description",
                        "Category": "Product category classification",
                        "UnitPrice": "Standard selling price per unit",
                        "StockQuantity": "Current inventory level",
                        "ReorderLevel": "Minimum stock level before reordering",
                        "Supplier": "Primary supplier for this product"
                    }
                }
            },
            "use_cases": ["product lookup", "inventory management", "pricing information", "product catalog", "stock levels"]
        }
    }
    
    try:
        # Step 1: Upload training data
        print("\\n1. Uploading training data to S3...")
        training_data_uri = deployment.upload_training_data(sample_odata_metadata)
        
        # Step 2: Start training job
        print("\\n2. Starting SageMaker training job...")
        estimator, job_name = deployment.create_training_job(training_data_uri)
        
        print(f"Training job '{job_name}' started successfully!")
        print("You can monitor the training job in the SageMaker console.")
        
        # Wait for training to complete (optional)
        print("\\n3. Waiting for training to complete...")
        print("This may take 5-10 minutes...")
        
        # Wait for training job to complete
        estimator.latest_training_job.wait()
        
        # Step 3: Deploy model
        print("\\n4. Deploying model to endpoint...")
        predictor, endpoint_name = deployment.deploy_model(estimator)
        
        # Step 4: Test endpoint
        print("\\n5. Testing deployed endpoint...")
        deployment.test_endpoint(predictor)
        
        # Step 5: Create Lambda integration
        print("\\n6. Creating Lambda integration...")
        lambda_code = deployment.create_lambda_integration(endpoint_name)
        
        print("\\n" + "=" * 60)
        print("DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"SageMaker Endpoint: {endpoint_name}")
        print(f"S3 Training Data: {training_data_uri}")
        print(f"Lambda Code: /home/gyanmis/odata_lambda.py")
        print("\\nNext Steps:")
        print("1. Create a Lambda function using the generated code")
        print("2. Set up API Gateway to expose the Lambda function")
        print("3. Integrate with your OData OAuth2 authentication")
        print("4. Add your actual OData metadata to improve accuracy")
        
    except Exception as e:
        print(f"\\nDeployment failed: {str(e)}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()
