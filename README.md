# OData Service AI Classifier

This project creates an AI model that intelligently routes user questions to the appropriate OAuth2-enabled OData services based on enriched metadata descriptions.

## 🎯 What This Does

Instead of training on actual data, this system trains on **metadata and descriptions** of your OData services so an AI agent can:

- Understand user questions in natural language
- Route questions to the correct SAP OData service
- Handle OAuth2 authentication automatically
- Provide intelligent service selection based on business context

## 📁 Project Structure

```
/home/gyanmis/
├── odata_model_training.py      # Core classifier implementation
├── train.py                     # SageMaker training script
├── deploy_odata_training.py     # Full deployment pipeline
├── test_local_model.py          # Local testing script
├── odata_metadata_template.json # Template for your OData metadata
├── odata_lambda.py              # Generated Lambda integration code
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Test Locally First

```bash
cd /home/gyanmis
source odata_env/bin/activate
python test_local_model.py
```

This validates your setup and shows how the model performs with sample data.

### 2. Customize Your Metadata

Edit `odata_metadata_template.json` with your actual OData services:

```json
{
  "CustomerService": {
    "endpoint": "https://your-sap-system/odata/CustomerService",
    "oauth2_config": {
      "token_endpoint": "https://your-sap-system/oauth/token",
      "client_id": "your-client-id"
    },
    "purpose": "Detailed description of what this service does...",
    "entities": {
      "Customer": {
        "description": "What customer entity contains...",
        "fields": {
          "CustomerID": "What this field is used for...",
          "CompanyName": "Business purpose of this field..."
        }
      }
    },
    "use_cases": ["customer lookup", "credit checks", "contact management"]
  }
}
```

### 3. Deploy to AWS

```bash
python deploy_odata_training.py
```

This will:
- Upload your metadata to S3
- Train a SageMaker model
- Deploy to a SageMaker endpoint
- Generate Lambda integration code

## 🔧 Configuration Tips

### Writing Good Descriptions

**Purpose Field:**
- Describe business processes, not technical details
- Include all major use cases
- Use terms your users would understand

**Field Descriptions:**
- Explain business meaning, not just data type
- Include when/why the field is used
- Add context about business rules

**Use Cases:**
- List how users would ask for this data
- Include synonyms and alternative terms
- Think about real user questions

### Example Good vs Bad Descriptions

❌ **Bad:** "CustomerID - Primary key field"
✅ **Good:** "CustomerID - Unique identifier used to look up customer records, reference customers in orders, and link customer data across systems"

❌ **Bad:** "Purpose: Customer data management"
✅ **Good:** "Purpose: Manages comprehensive customer information including contact details, credit limits, payment terms, and business relationships for all customer interactions and sales processes"

## 🧪 Testing Your Model

### Local Testing
```bash
python test_local_model.py
```

### Test Questions to Try
- "What is the credit limit for customer ABC123?"
- "Show me recent sales orders"
- "Check product inventory levels"
- "Find customer contact information"
- "Track order status for order 12345"

### Improving Accuracy

If predictions aren't accurate:

1. **Add more descriptive text** to your metadata
2. **Include more use cases** that match how users ask questions
3. **Add synonyms** and alternative terms
4. **Be more specific** about business processes

## 🔐 OAuth2 Integration

The system handles OAuth2 authentication by:

1. Storing client credentials in AWS Secrets Manager
2. Using Lambda functions to obtain access tokens
3. Making authenticated calls to your OData endpoints

### Setting Up Secrets

```bash
aws secretsmanager create-secret \
  --name "customer-service-secret" \
  --description "OAuth2 credentials for Customer Service" \
  --secret-string '{"client_id":"your-id","client_secret":"your-secret"}'
```

## 📊 Architecture

```
User Question → Lambda Function → SageMaker Endpoint → Service Classification
                     ↓
OAuth2 Token → SAP OData Service → Response → User
```

## 🛠️ Advanced Usage

### Custom Training Parameters

Edit `deploy_odata_training.py` to adjust:

```python
hyperparameters={
    'n_estimators': 150,      # More trees = better accuracy
    'max_features': 1500,     # More features = more context
    'test_size': 0.2         # Validation split
}
```

### Adding New Services

1. Add service to `odata_metadata_template.json`
2. Run local test to validate
3. Redeploy with `python deploy_odata_training.py`

### Monitoring and Logging

- Check SageMaker console for training metrics
- Monitor Lambda logs for runtime issues
- Use CloudWatch for endpoint performance

## 🔍 Troubleshooting

### Common Issues

**Low Prediction Confidence:**
- Add more descriptive metadata
- Include more use cases and synonyms
- Test with more varied questions

**Wrong Service Selection:**
- Make service descriptions more distinct
- Add negative examples (what the service doesn't do)
- Increase training data variety

**OAuth2 Errors:**
- Verify credentials in Secrets Manager
- Check token endpoint URLs
- Validate client permissions

### Getting Help

1. Check the local test output for validation errors
2. Review SageMaker training logs for model issues
3. Test Lambda function independently
4. Validate OAuth2 credentials manually

## 📈 Next Steps

1. **Start Small:** Begin with 2-3 well-described services
2. **Test Thoroughly:** Use real user questions for validation
3. **Iterate:** Improve descriptions based on prediction results
4. **Scale Up:** Add more services once accuracy is good
5. **Monitor:** Track usage and accuracy in production

## 🎉 Success Metrics

Your model is working well when:
- Top prediction confidence > 0.7 for clear questions
- Correct service selected for 90%+ of test questions
- Users can ask questions naturally without learning syntax
- OAuth2 integration works seamlessly

---

**Ready to get started?** Run `python test_local_model.py` to validate your setup!
