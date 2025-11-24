import json
from flask import current_app, redirect, url_for
from authlib.integrations.flask_client import OAuth
import requests

oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with the Flask app."""
    oauth.init_app(app)
    
    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    return oauth

def get_google_provider_cfg():
    """Fetch Google's provider configuration."""
    try:
        response = requests.get(current_app.config['GOOGLE_DISCOVERY_URL'])
        return response.json()
    except Exception as e:
        print(f"Error fetching Google provider config: {e}")
        return None

def get_authorization_url():
    """
    Generate Google OAuth authorization URL.
    
    Returns:
        Authorization URL string
    """
    google = oauth.create_client('google')
    redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']
    return google.authorize_redirect(redirect_uri)

def handle_callback(authorization_response):
    """
    Handle OAuth callback and exchange code for token.
    
    Args:
        authorization_response: Full callback URL with code
    
    Returns:
        User info dict if successful, None otherwise
    """
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        
        # Get user info from Google
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()
        
        return {
            'google_id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'email_verified': user_info.get('email_verified', False)
        }
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        return None

def get_user_info(token):
    """
    Fetch user information from Google using access token.
    
    Args:
        token: OAuth access token
    
    Returns:
        User info dict
    """
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers=headers
        )
        return response.json()
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None
