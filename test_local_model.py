#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/gyanmis')

from odata_model_training import ODataServiceClassifier
import json

def test_local_model():
    """
    Test the OData classifier locally before deploying to SageMaker
    """
    print("Testing OData Service Classifier Locally")
    print("=" * 50)
    
    # Load sample metadata
    with open('/home/gyanmis/odata_metadata_template.json', 'r') as f:
        metadata = json.load(f)
    
    # Remove instructions section
    if 'INSTRUCTIONS' in metadata:
        del metadata['INSTRUCTIONS']
    
    # Initialize classifier
    classifier = ODataServiceClassifier()
    
    # Prepare training data
    print("\\n1. Preparing training data...")
    training_data = classifier.prepare_training_data(metadata)
    print(f"Generated {len(training_data)} training samples")
    
    # Show sample training data
    print("\\nSample training data:")
    print(training_data.head(10))
    
    # Train the model
    print("\\n2. Training the model...")
    try:
        classifier.train(training_data)
        print("Model trained successfully!")
    except Exception as e:
        print(f"Training failed: {str(e)}")
        return False
    
    # Test predictions
    print("\\n3. Testing predictions...")
    test_questions = [
        "What is the credit limit for customer ABC123?",
        "Show me recent sales orders",
        "Find customer contact information", 
        "Track order status for order 12345",
        "Get customer payment terms",
        "Check product inventory levels",
        "List all products in stock",
        "Update customer address",
        "Get sales order details",
        "Find customer by company name"
    ]
    
    print("\\nPrediction Results:")
    print("-" * 30)
    
    for question in test_questions:
        try:
            predictions = classifier.predict_service(question, top_k=2)
            print(f"\\nQ: {question}")
            for i, pred in enumerate(predictions, 1):
                print(f"  {i}. {pred['service']} (confidence: {pred['confidence']:.3f})")
        except Exception as e:
            print(f"Error predicting for '{question}': {str(e)}")
    
    # Save model for later use
    print("\\n4. Saving model...")
    try:
        classifier.save_model('/home/gyanmis/odata_classifier_local.pkl')
        print("Model saved successfully!")
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False
    
    return True

def validate_metadata_structure(metadata_file):
    """
    Validate the structure of OData metadata
    """
    print("\\nValidating metadata structure...")
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {str(e)}")
        return False
    
    required_fields = ['endpoint', 'oauth2_config', 'purpose', 'entities', 'use_cases']
    
    for service_name, service_info in metadata.items():
        if service_name == 'INSTRUCTIONS':
            continue
            
        print(f"\\nValidating service: {service_name}")
        
        # Check required fields
        missing_fields = []
        for field in required_fields:
            if field not in service_info:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ❌ Missing fields: {missing_fields}")
        else:
            print(f"  ✅ All required fields present")
        
        # Check entities structure
        entities = service_info.get('entities', {})
        if not entities:
            print(f"  ❌ No entities defined")
        else:
            print(f"  ✅ {len(entities)} entities defined")
            
            for entity_name, entity_info in entities.items():
                if 'description' not in entity_info:
                    print(f"    ❌ Entity {entity_name} missing description")
                if 'fields' not in entity_info or not entity_info['fields']:
                    print(f"    ❌ Entity {entity_name} has no fields")
                else:
                    print(f"    ✅ Entity {entity_name} has {len(entity_info['fields'])} fields")
    
    return True

if __name__ == "__main__":
    print("OData Model Local Testing Suite")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        '/home/gyanmis/odata_model_training.py',
        '/home/gyanmis/odata_metadata_template.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        sys.exit(1)
    
    # Validate metadata structure
    validate_metadata_structure('/home/gyanmis/odata_metadata_template.json')
    
    # Test local model
    success = test_local_model()
    
    if success:
        print("\\n" + "=" * 60)
        print("✅ LOCAL TESTING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\\nNext steps:")
        print("1. Customize odata_metadata_template.json with your actual services")
        print("2. Run: python deploy_odata_training.py")
        print("3. This will train and deploy your model to SageMaker")
    else:
        print("\\n" + "=" * 60)
        print("❌ LOCAL TESTING FAILED")
        print("=" * 60)
        print("Please fix the errors above before proceeding.")
