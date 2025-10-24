import boto3
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

class ODataServiceClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def prepare_training_data(self, odata_metadata):
        """
        Prepare training data from enriched OData metadata
        """
        training_samples = []
        
        for service_name, service_info in odata_metadata.items():
            # Create training samples from service descriptions
            purpose = service_info.get('purpose', '')
            entities = service_info.get('entities', {})
            
            # Generate samples from purpose description
            training_samples.append({
                'text': purpose,
                'service': service_name,
                'confidence': 1.0
            })
            
            # Generate samples from entity descriptions
            for entity_name, entity_info in entities.items():
                entity_desc = entity_info.get('description', '')
                training_samples.append({
                    'text': f"{entity_desc} {purpose}",
                    'service': service_name,
                    'confidence': 0.8
                })
                
                # Generate samples from field descriptions
                fields = entity_info.get('fields', {})
                for field_name, field_desc in fields.items():
                    training_samples.append({
                        'text': f"{field_desc} {field_name} {entity_desc}",
                        'service': service_name,
                        'confidence': 0.6
                    })
        
        return pd.DataFrame(training_samples)
    
    def train(self, training_data):
        """
        Train the classification model
        """
        # Prepare features and labels
        X = training_data['text']
        y = training_data['service']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Vectorize text
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train classifier
        self.classifier.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_vec)
        print("Classification Report:")
        print(classification_report(y_test, y_pred))
        
        return self.classifier, self.vectorizer
    
    def predict_service(self, question, top_k=3):
        """
        Predict which OData service to use for a given question
        """
        question_vec = self.vectorizer.transform([question])
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(question_vec)[0]
        classes = self.classifier.classes_
        
        # Get top k predictions
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'service': classes[idx],
                'confidence': probabilities[idx]
            })
        
        return results
    
    def save_model(self, model_path):
        """
        Save the trained model
        """
        joblib.dump({
            'classifier': self.classifier,
            'vectorizer': self.vectorizer
        }, model_path)

# Example usage and SageMaker integration
def create_sagemaker_training_job():
    """
    Create a SageMaker training job for the OData classifier
    """
    sagemaker_session = sagemaker.Session()
    role = sagemaker.get_execution_role()
    
    # Define the SKLearn estimator
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        role=role,
        instance_type='ml.m5.large',
        framework_version='0.23-1',
        py_version='py3',
        script_mode=True,
        hyperparameters={
            'n_estimators': 100,
            'max_features': 1000
        }
    )
    
    # Start training job
    sklearn_estimator.fit({'training': 's3://your-bucket/odata-training-data/'})
    
    return sklearn_estimator

if __name__ == "__main__":
    # Example OData metadata structure
    sample_metadata = {
        "CustomerService": {
            "endpoint": "https://sap-system/odata/CustomerService",
            "oauth2_config": {
                "token_endpoint": "https://sap-system/oauth/token",
                "client_id": "customer-service-client"
            },
            "purpose": "Manages customer master data including demographics, contact information, credit limits, and business relationships",
            "entities": {
                "Customer": {
                    "description": "Core customer entity containing business partner information and financial details",
                    "fields": {
                        "CustomerID": "Unique identifier for customer records in the system",
                        "CompanyName": "Legal business name of the customer organization",
                        "Industry": "Business sector classification and industry type",
                        "CreditLimit": "Maximum credit amount approved for customer transactions",
                        "ContactEmail": "Primary email address for customer communication",
                        "PaymentTerms": "Standard payment terms and conditions for the customer"
                    }
                }
            },
            "use_cases": ["customer lookup", "credit checks", "contact management", "customer demographics"]
        },
        "SalesOrderService": {
            "endpoint": "https://sap-system/odata/SalesOrderService",
            "oauth2_config": {
                "token_endpoint": "https://sap-system/oauth/token",
                "client_id": "sales-service-client"
            },
            "purpose": "Handles sales order processing, order tracking, line items, and order fulfillment status",
            "entities": {
                "SalesOrder": {
                    "description": "Sales order header information with customer and order details",
                    "fields": {
                        "OrderID": "Unique sales order identifier",
                        "CustomerID": "Reference to customer who placed the order",
                        "OrderDate": "Date when the sales order was created",
                        "OrderStatus": "Current status of the sales order processing",
                        "TotalAmount": "Total monetary value of the sales order",
                        "DeliveryDate": "Planned or actual delivery date for the order"
                    }
                },
                "SalesOrderItem": {
                    "description": "Individual line items within a sales order",
                    "fields": {
                        "ItemID": "Unique identifier for the order line item",
                        "ProductID": "Reference to the product being ordered",
                        "Quantity": "Number of units ordered for this item",
                        "UnitPrice": "Price per unit for the product",
                        "LineTotal": "Total amount for this line item"
                    }
                }
            },
            "use_cases": ["order tracking", "sales data", "order history", "order fulfillment"]
        }
    }
    
    # Initialize and train the classifier
    classifier = ODataServiceClassifier()
    training_data = classifier.prepare_training_data(sample_metadata)
    
    print(f"Generated {len(training_data)} training samples")
    print("\nSample training data:")
    print(training_data.head())
    
    # Train the model
    classifier.train(training_data)
    
    # Test predictions
    test_questions = [
        "What is the credit limit for customer ABC123?",
        "Show me recent sales orders",
        "Find customer contact information",
        "Track order status for order 12345",
        "Get customer payment terms"
    ]
    
    print("\nTest Predictions:")
    for question in test_questions:
        predictions = classifier.predict_service(question)
        print(f"\nQuestion: {question}")
        for pred in predictions:
            print(f"  Service: {pred['service']}, Confidence: {pred['confidence']:.3f}")
    
    # Save the model
    classifier.save_model('/home/gyanmis/odata_classifier_model.pkl')
    print("\nModel saved successfully!")
