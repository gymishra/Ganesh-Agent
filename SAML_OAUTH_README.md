# SAML OAuth 2.0 SAP Integration

This project implements seamless SAP OData calls using OAuth 2.0 SAML Bearer grant type by extracting user email from AWS Identity Center and using self-signed certificates for SAML assertion signing.

## 🎯 What This Does

- Extracts user email from AWS Identity Center based on user ID
- Creates signed SAML assertions using self-signed certificates
- Exchanges SAML assertions for OAuth 2.0 access tokens
- Creates SAP sales orders using the obtained access tokens
- Provides both Lambda function and local testing capabilities

## 📁 Project Structure

```
/home/gyanmis/
├── saml_sales_order_lambda_recreated.py  # Main Lambda function
├── deploy_saml_lambda.py                  # AWS deployment script
├── test_saml_oauth_local.py              # Local testing script
├── setup_saml_oauth.sh                   # Setup and dependency script
├── SAML_OAUTH_README.md                  # This documentation
└── sagar/                                # Reference files
    ├── saml-private.key                  # Private key for SAML signing
    ├── saml-cert.pem                     # Certificate for SAP STRUST
    ├── test_saml_oauth_fixed.py          # Reference implementation
    └── metadata.xml                      # SAML metadata
```

## 🚀 Quick Start

### 1. Setup Dependencies

```bash
cd /home/gyanmis
./setup_saml_oauth.sh
```

### 2. Test Locally

```bash
python3 test_saml_oauth_local.py
```

### 3. Deploy to AWS

```bash
python3 deploy_saml_lambda.py
```

## 🔧 Configuration

### SAP System Configuration

- **SAP System URL**: `https://vhcals4hci.awspoc.club`
- **OAuth Client ID**: `AW07241704C`
- **OAuth Client Secret**: `Welcome1234$`
- **OData Service**: `ZAPI_SALES_ORDER_SRV_0001`
- **Sales Order Endpoint**: `/sap/opu/odata/SAP/ZORDER_SRV/sordSet`

### AWS Identity Center Configuration

- **Identity Store ID**: `d-9067c76e54`
- **User Lookup**: Based on UserName attribute
- **Email Extraction**: From user's primary email

### SAML Configuration

- **Issuer**: `cognito-identity-provider`
- **Audience**: OAuth Client ID
- **NameID Format**: Email address format
- **Subject Confirmation**: Bearer method
- **Signing Algorithm**: RSA-SHA256

## 📋 Prerequisites

### SAP System Setup

1. **OAuth Client Configuration** (Transaction: SOAUTH2)
   ```
   Client ID: AW07241704C
   Grant Types: Client Credentials, SAML Bearer Assertion
   Scope: ZAPI_SALES_ORDER_SRV_0001
   ```

2. **SAML Certificate Upload** (Transaction: STRUST)
   - Upload `saml-cert.pem` to SAP Trust Manager
   - Configure as trusted certificate for SAML assertions

3. **User Management**
   - Ensure user exists in SAP system
   - User should have access to sales order creation

### AWS Setup

1. **Identity Center Configuration**
   - Users configured with email addresses
   - Identity Store accessible via API

2. **Lambda Execution Role**
   - Basic Lambda execution permissions
   - Identity Store read access
   - CloudWatch logging permissions

## 🔍 How It Works

### 1. User Email Extraction

```python
def get_user_email_from_identity_center(user_id):
    response = identity_store.list_users(
        IdentityStoreId=IDENTITY_STORE_ID,
        Filters=[{
            'AttributePath': 'UserName',
            'AttributeValue': user_id
        }]
    )
    # Extract email from response
```

### 2. SAML Assertion Creation

```python
def create_saml_assertion(user_email):
    assertion_xml = f"""<Assertion ID="{assertion_id}" ...>
        <Issuer>cognito-identity-provider</Issuer>
        <Subject>
            <NameID>{user_email}</NameID>
            <SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <SubjectConfirmationData Recipient="{SAP_TOKEN_URL}"/>
            </SubjectConfirmation>
        </Subject>
        ...
    </Assertion>"""
```

### 3. OAuth Token Exchange

```python
def exchange_saml_for_token(signed_assertion):
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:saml2-bearer",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "assertion": signed_assertion
    }
    # POST to SAP OAuth endpoint
```

### 4. Sales Order Creation

```python
def create_sales_order(access_token, customer, material, quantity):
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {"Customer": customer, "Material": material, "Quantity": quantity}
    # POST to SAP OData endpoint
```

## 🧪 Testing

### Local Testing

Test the complete flow locally:

```bash
python3 test_saml_oauth_local.py
```

Expected output:
```
=== SAML OAuth 2.0 SAP Integration Test ===
1. Testing Client Credentials OAuth...
✓ Client credentials OAuth successful!

2. Testing SAML Bearer OAuth...
✓ SAML Bearer OAuth successful!

3. Testing Sales Order with SAML Token...
✓ Sales order created successfully!
  Result: Sales order created
  Sales Order: 12345
```

### Lambda Testing

After deployment, test via API Gateway:

```bash
curl "https://api-id.execute-api.region.amazonaws.com/prod/sales-order?user_id=gyanmis&Customer=1000&Material=M001&Quantity=10"
```

Expected response:
```json
{
  "success": true,
  "user_email": "gyanmis@amazon.com",
  "sales_order": {
    "Result": "Sales order created",
    "Salesord": "12345",
    "Status": "Success"
  },
  "method": "SAML Bearer OAuth 2.0"
}
```

## 🔐 Security Considerations

### Certificate Management

- Private key is embedded in Lambda function code
- Consider using AWS Secrets Manager for production
- Rotate certificates regularly

### Token Security

- OAuth tokens are short-lived (typically 1 hour)
- Tokens are not stored, only used for immediate requests
- SAML assertions include time-based validity

### Network Security

- All communications use HTTPS
- SAP system should be accessible only from authorized networks
- Consider VPC endpoints for Lambda functions

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid SAML assertion"**
   - Check certificate is uploaded to SAP STRUST
   - Verify SAML assertion format and timing
   - Ensure audience matches OAuth client ID

2. **"User not found in Identity Center"**
   - Verify user exists with correct UserName
   - Check Identity Store ID is correct
   - Ensure Lambda has Identity Store permissions

3. **"OAuth client not found"**
   - Verify OAuth client configuration in SAP
   - Check client ID and secret are correct
   - Ensure SAML Bearer grant type is enabled

4. **"Sales order creation failed"**
   - Verify user has SAP authorizations
   - Check OData service is active
   - Validate customer/material data

### Debug Steps

1. **Test Client Credentials First**
   ```bash
   # This validates basic OAuth setup
   python3 test_saml_oauth_local.py
   ```

2. **Check SAP Logs**
   - Transaction: SM21 (System Log)
   - Look for OAuth and SAML related errors

3. **Verify Certificate**
   - Transaction: STRUST
   - Ensure certificate is valid and trusted

4. **Test SAML Assertion**
   - Use SAP OAuth test tools
   - Validate assertion format manually

## 📈 Performance Considerations

### Lambda Optimization

- Use Lambda layers for dependencies
- Implement connection pooling for high volume
- Consider provisioned concurrency for consistent performance

### Caching

- Cache OAuth tokens (with proper expiration)
- Cache Identity Center user lookups
- Use CloudFront for API Gateway endpoints

## 🔄 Deployment Pipeline

### Manual Deployment

```bash
# 1. Setup dependencies
./setup_saml_oauth.sh

# 2. Test locally
python3 test_saml_oauth_local.py

# 3. Deploy to AWS
python3 deploy_saml_lambda.py
```

### Automated Deployment

Consider using AWS CDK or CloudFormation for production deployments:

- Infrastructure as Code
- Environment-specific configurations
- Automated testing and rollback capabilities

## 📚 References

- [OAuth 2.0 SAML Bearer Assertion](https://tools.ietf.org/html/rfc7522)
- [SAP OAuth 2.0 Configuration](https://help.sap.com/docs/SAP_NETWEAVER_AS_ABAP_752/68bf513362174d54b58cddec28794093/7e658b3e4cea4a79b035d0f1d2798c1f.html)
- [AWS Identity Center API](https://docs.aws.amazon.com/singlesignon/latest/IdentityStoreAPIReference/welcome.html)
- [SAML 2.0 Specification](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review SAP system logs and configurations
3. Validate AWS Identity Center setup
4. Test individual components separately

---

**Ready to get started?** Run `./setup_saml_oauth.sh` to begin!
