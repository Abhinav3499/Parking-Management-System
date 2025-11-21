import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify

def create_access_token(user_id, is_admin=False):
    """
    Create a short-lived JWT access token.
    
    Args:
        user_id: User's database ID
        is_admin: Whether user has admin privileges
    
    Returns:
        Encoded JWT token string
    """
    expiration = datetime.utcnow() + timedelta(
        minutes=current_app.config['ACCESS_TOKEN_EXPIRE_MINUTES']
    )
    
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    return token

def create_refresh_token(user_id):
    """
    Create a long-lived JWT refresh token.
    
    Args:
        user_id: User's database ID
    
    Returns:
        Encoded JWT token string
    """
    expiration = datetime.utcnow() + timedelta(
        days=current_app.config['REFRESH_TOKEN_EXPIRE_DAYS']
    )
    
    payload = {
        'user_id': user_id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )
    
    return token

def verify_token(token, token_type='access'):
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')
    
    Returns:
        Decoded payload dict if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        
        # Verify token type matches expected
        if payload.get('type') != token_type:
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_header():
    """
    Extract JWT token from Authorization header.
    
    Returns:
        Token string if present, None otherwise
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    try:
        # Expected format: "Bearer <token>"
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            return None
        return token
    except ValueError:
        return None

def jwt_required(f):
    """
    Decorator to protect routes with JWT authentication.
    Extracts user_id from token and makes it available to the route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = verify_token(token, 'access')
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Make user_id and is_admin available to the route
        request.user_id = payload.get('user_id')
        request.is_admin = payload.get('is_admin', False)
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorator to protect admin-only routes.
    Requires valid JWT token with admin flag.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = verify_token(token, 'access')
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if not payload.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        
        request.user_id = payload.get('user_id')
        request.is_admin = True
        
        return f(*args, **kwargs)
    
    return decorated_function
