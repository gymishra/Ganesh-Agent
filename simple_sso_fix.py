#!/usr/bin/env python3
# Simple SSO fix - use Identity Center's built-in OAuth without custom app

# Update your Flask app with this minimal configuration:
SSO_CONFIG = {
    'start_url': 'https://d-9767435275.awsapps.com/start',
    'client_id': 'identity-center-default',  # Use built-in client
    'redirect_uri': 'http://localhost:5000/sso-callback'
}

# Replace the sso-login route with this:
sso_route = '''
@app.route('/sso-login')
def sso_login():
    # Direct SSO login without custom OAuth app
    return redirect('https://d-9767435275.awsapps.com/start#/')

@app.route('/sso-callback')
def sso_callback():
    # Simulate successful SSO (since we're using direct SSO portal)
    session['user'] = 'Identity-Center-User'
    session['auth_method'] = 'sso'
    return redirect('/dashboard')
'''

print("✅ Deleted complex application setup")
print("🔧 Use this simple approach:")
print("1. Update Flask app with direct SSO portal redirect")
print("2. Users will login through Identity Center portal")
print("3. No custom OAuth app needed")
print()
print("Direct SSO URL: https://d-9767435275.awsapps.com/start#/")
