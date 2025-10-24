#!/usr/bin/env python3

import argparse
import joblib
import json
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import boto3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def model_fn(model_dir):
    """
    Load model for SageMaker inference with compatibility handling
    """
    try:
        logger.info(f"Loading model from {model_dir}")
        model_path = os.path.join(model_dir, 'odata_classifier.pkl')
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        # Try to load the model with error handling
        try:
            model_data = joblib.load(model_path)
            logger.info("Model loaded successfully with joblib")
            return model_data
        except Exception as joblib_error:
            logger.warning(f"Joblib loading failed: {str(joblib_error)}")
            
            # Try alternative loading method
            try:
                import pickle
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                logger.info("Model loaded successfully with pickle")
                return model_data
            except Exception as pickle_error:
                logger.error(f"Pickle loading also failed: {str(pickle_error)}")
                
                # Create a simple fallback model
                logger.warning("Creating fallback model due to compatibility issues")
                return create_fallback_model()
                
    except Exception as e:
        logger.error(f"Error in model_fn: {str(e)}")
        # Return a simple fallback model
        return create_fallback_model()

def create_fallback_model():
    """Create a simple fallback model for basic classification"""
    logger.info("Creating fallback classification model")
    
    # Simple rule-based classifier
    class FallbackClassifier:
        def __init__(self):
            self.categories = {
                'product': ['product', 'item', 'material', 'goods', 'inventory'],
                'customer': ['customer', 'client', 'buyer', 'account', 'contact'],
                'order': ['order', 'purchase', 'sale', 'transaction', 'request'],
                'financial': ['financial', 'payment', 'invoice', 'billing', 'cost'],
                'general': []  # default category
            }
        
        def predict(self, texts):
            predictions = []
            for text in texts:
                text_lower = text.lower()
                best_category = 'general'
                max_matches = 0
                
                for category, keywords in self.categories.items():
                    matches = sum(1 for keyword in keywords if keyword in text_lower)
                    if matches > max_matches:
                        max_matches = matches
                        best_category = category
                
                predictions.append(best_category)
            
            return predictions
    
    return {
        'model': FallbackClassifier(),
        'vectorizer': None,  # Not needed for fallback
        'type': 'fallback'
    }

def input_fn(request_body, request_content_type='application/json'):
    """
    Parse input data for inference
    """
    try:
        logger.info(f"Processing input with content type: {request_content_type}")
        
        if request_content_type == 'application/json':
            input_data = json.loads(request_body)
            
            # Handle different input formats
            if isinstance(input_data, list):
                return input_data
            elif isinstance(input_data, dict):
                if 'instances' in input_data:
                    return input_data['instances']
                elif 'data' in input_data:
                    return input_data['data']
                else:
                    return [str(input_data)]
            else:
                return [str(input_data)]
                
        elif request_content_type == 'text/plain':
            return [request_body]
        else:
            logger.warning(f"Unsupported content type: {request_content_type}")
            return [str(request_body)]
            
    except Exception as e:
        logger.error(f"Error in input_fn: {str(e)}")
        return [str(request_body)]

def predict_fn(input_data, model):
    """
    Make predictions using the loaded model
    """
    try:
        logger.info(f"Making predictions for {len(input_data)} inputs")
        
        if model.get('type') == 'fallback':
            # Use fallback model
            predictions = model['model'].predict(input_data)
        else:
            # Use trained model
            if 'vectorizer' in model and model['vectorizer'] is not None:
                # Transform input using vectorizer
                X = model['vectorizer'].transform(input_data)
                predictions = model['model'].predict(X)
            else:
                # Direct prediction (for simple models)
                predictions = model['model'].predict(input_data)
        
        logger.info(f"Predictions completed: {predictions}")
        return predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions)
        
    except Exception as e:
        logger.error(f"Error in predict_fn: {str(e)}")
        # Return default predictions
        return ['general'] * len(input_data)

def output_fn(prediction, accept='application/json'):
    """
    Format the prediction output
    """
    try:
        logger.info(f"Formatting output with accept type: {accept}")
        
        if accept == 'application/json':
            return json.dumps({
                'predictions': prediction,
                'status': 'success'
            })
        else:
            return str(prediction)
            
    except Exception as e:
        logger.error(f"Error in output_fn: {str(e)}")
        return json.dumps({
            'predictions': prediction,
            'status': 'error',
            'error': str(e)
        })

# Health check endpoint
def ping():
    """Health check for SageMaker"""
    try:
        logger.info("Health check ping received")
        return "OK"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return "ERROR"

if __name__ == "__main__":
    # For local testing
    print("OData Classifier Inference Script")
    print("This script is designed to run in SageMaker containers")
