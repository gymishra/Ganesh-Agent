#!/usr/bin/env python3

import argparse
import joblib
import json
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import boto3

def model_fn(model_dir):
    """
    Load model for SageMaker inference
    """
    model_path = os.path.join(model_dir, 'odata_classifier.pkl')
    model_data = joblib.load(model_path)
    return model_data

def input_fn(request_body, content_type='application/json'):
    """
    Parse input data for inference
    """
    if content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data['question']
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    """
    Make predictions using the loaded model
    """
    vectorizer = model['vectorizer']
    classifier = model['classifier']
    
    # Transform input
    question_vec = vectorizer.transform([input_data])
    
    # Get predictions with probabilities
    probabilities = classifier.predict_proba(question_vec)[0]
    classes = classifier.classes_
    
    # Get top 3 predictions
    top_indices = probabilities.argsort()[-3:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'service': classes[idx],
            'confidence': float(probabilities[idx])
        })
    
    return results

def output_fn(prediction, accept='application/json'):
    """
    Format prediction output
    """
    if accept == 'application/json':
        return json.dumps(prediction), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")

def prepare_training_data(metadata_file):
    """
    Prepare training data from OData metadata
    """
    with open(metadata_file, 'r') as f:
        odata_metadata = json.load(f)
    
    training_samples = []
    
    for service_name, service_info in odata_metadata.items():
        purpose = service_info.get('purpose', '')
        entities = service_info.get('entities', {})
        use_cases = service_info.get('use_cases', [])
        
        # Add purpose-based samples
        training_samples.append({
            'text': purpose,
            'service': service_name,
            'weight': 1.0
        })
        
        # Add use case samples
        for use_case in use_cases:
            training_samples.append({
                'text': f"{use_case} {purpose}",
                'service': service_name,
                'weight': 0.9
            })
        
        # Add entity-based samples
        for entity_name, entity_info in entities.items():
            entity_desc = entity_info.get('description', '')
            
            training_samples.append({
                'text': f"{entity_desc} {purpose}",
                'service': service_name,
                'weight': 0.8
            })
            
            # Add field-based samples
            fields = entity_info.get('fields', {})
            for field_name, field_desc in fields.items():
                training_samples.append({
                    'text': f"{field_desc} {field_name} {entity_desc}",
                    'service': service_name,
                    'weight': 0.6
                })
                
                # Add field name variations
                training_samples.append({
                    'text': f"get {field_name} from {entity_name}",
                    'service': service_name,
                    'weight': 0.7
                })
    
    return pd.DataFrame(training_samples)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    
    # Hyperparameters
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_features', type=int, default=1000)
    parser.add_argument('--test_size', type=float, default=0.2)
    
    args = parser.parse_args()
    
    print("Starting OData service classifier training...")
    
    # Load training data
    metadata_file = os.path.join(args.train, 'odata_metadata.json')
    
    if not os.path.exists(metadata_file):
        print(f"Creating sample metadata file at {metadata_file}")
        # Create sample metadata if not provided
        sample_metadata = {
            "CustomerService": {
                "purpose": "Manages customer master data including demographics, contact information, credit limits, and business relationships",
                "entities": {
                    "Customer": {
                        "description": "Core customer entity containing business partner information and financial details",
                        "fields": {
                            "CustomerID": "Unique identifier for customer records in the system",
                            "CompanyName": "Legal business name of the customer organization",
                            "CreditLimit": "Maximum credit amount approved for customer transactions",
                            "ContactEmail": "Primary email address for customer communication"
                        }
                    }
                },
                "use_cases": ["customer lookup", "credit checks", "contact management"]
            },
            "SalesOrderService": {
                "purpose": "Handles sales order processing, order tracking, line items, and order fulfillment status",
                "entities": {
                    "SalesOrder": {
                        "description": "Sales order header information with customer and order details",
                        "fields": {
                            "OrderID": "Unique sales order identifier",
                            "OrderDate": "Date when the sales order was created",
                            "OrderStatus": "Current status of the sales order processing",
                            "TotalAmount": "Total monetary value of the sales order"
                        }
                    }
                },
                "use_cases": ["order tracking", "sales data", "order history"]
            }
        }
        
        os.makedirs(args.train, exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(sample_metadata, f, indent=2)
    
    # Prepare training data
    print("Preparing training data from OData metadata...")
    training_df = prepare_training_data(metadata_file)
    print(f"Generated {len(training_df)} training samples")
    
    # Initialize vectorizer and classifier
    vectorizer = TfidfVectorizer(
        max_features=args.max_features,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1
    )
    
    classifier = RandomForestClassifier(
        n_estimators=args.n_estimators,
        random_state=42,
        class_weight='balanced'
    )
    
    # Prepare features and labels
    X = training_df['text']
    y = training_df['service']
    sample_weights = training_df['weight']
    
    print(f"Training on {len(X)} samples with {len(y.unique())} services")
    print(f"Services: {list(y.unique())}")
    
    # Split data
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y, sample_weights, test_size=args.test_size, random_state=42, stratify=y
    )
    
    # Vectorize text
    print("Vectorizing text data...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train classifier
    print("Training classifier...")
    classifier.fit(X_train_vec, y_train, sample_weight=w_train)
    
    # Evaluate
    print("Evaluating model...")
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    print("Saving model...")
    model_data = {
        'classifier': classifier,
        'vectorizer': vectorizer
    }
    
    model_path = os.path.join(args.model_dir, 'odata_classifier.pkl')
    joblib.dump(model_data, model_path)
    
    print(f"Model saved to {model_path}")
    print("Training completed successfully!")
