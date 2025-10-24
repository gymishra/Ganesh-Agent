import json

def lambda_handler(event, context):
    # SAP-compatible SAML IdP metadata XML with proper structure
    metadata_xml = """<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" 
                     xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
                     entityID="cognito-identity-provider">
    <md:IDPSSODescriptor WantAuthnRequestsSigned="false" 
                         protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:KeyDescriptor use="signing">
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuGbXWiK3dQTyCbX5xdE4yCuYp0yyTn1WBIr3CLrABFVEntku7M3LotAqLtT92HQKGjBQvHjYmqh2qd4lAH+E2XCLLt9hxtfqAiAKXWiLqpMmjNn1YvliJHyXLanLa1Y3FC+jt7ERRy6g0QQWhToCV5Aw5BLb5YkeDbSTPrrjMrAG5vDNpw7SfVp5tgnI2mI+3uo85zQKtdydBgLuTdiAhLwjh8Js4TNz9M6JOGjGGpjmhp2q8ztJbrJDQXiFBfaA4bnwNVSqtHr9YhOlArWjFbhWk/9Rr4OcBajKNcf0ff1gXAcxCpz1V4aCi4E1qRdoXBHAiYqhkj4Go3iuSrVkTwIDAQABo1AwTjAdBgNVHQ4EFgQUhKs61nNq+Dc3xPSO0hTdggsVzyEwHwYDVR0jBBgwFoAUhKs61nNq+Dc3xPSO0hTdggsVzyEwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAeRqM36FKMoVVA6ufN0SgDP9H7WQ8qSXy1Z8GU4FcSKnHgjHAHMiNrwFXhPacatdudvmBaCYdnxkQTXpOsGI5HVvCN/qMpxrIuFuIjWKRGqoDMsM5B6hQBerOJ4YQ+OHHO1QjU2G227HrFaHOvliK04jFIMB5v1H0QLZjHAHDdNBBBUcqDKn7ByHxMdc8CqNFF7yohLyMa9+Ks2cw0Fanmw+9K9T8/Cdb41pELkxKBcHmiuK4wQBYmMBqTTreAjbwb4HVUVDAB2BZF9+gk8lSYzKtmUvSNb2CFXrqvhFLRMSHOu+LEAMo4CjTgBo61Q+YF2BtBNbwdAeFOBgj+90XZw==</ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </md:KeyDescriptor>
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" 
                                Location="urn:aws:lambda:saml-idp/sso"/>
        <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" 
                                Location="urn:aws:lambda:saml-idp/sso"/>
    </md:IDPSSODescriptor>
</md:EntityDescriptor>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/xml',
            'Access-Control-Allow-Origin': '*'
        },
        'body': metadata_xml
    }
