import requests
import base64
from datetime import datetime, timedelta

class TokenHandler:
    def __init__(self, client_id, client_secret, token_endpoint):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self.token = None
        self.expires_at = None
    
    def get_auth_header(self, scope=None):
        token = self._get_oauth_token(scope)
        return {"Authorization": f"Bearer {token}"}
    
    def _get_oauth_token(self, scope):
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        
        data = {'grant_type': 'client_credentials'}
        if scope:
            data['scope'] = scope
            
        response = requests.post(
            self.token_endpoint,
            auth=(self.client_id, self.client_secret),
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            return self.token
        else:
            raise Exception(f"OAuth2 failed: {response.status_code} - {response.text}")
