from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt
import os
import bcrypt
from werkzeug.security import check_password_hash as check_v1_hash

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hash.
    Supports both V2 (bcrypt) and V1 (Werkzeug/pbkdf2:sha256) hashes.
    """
    try:
        # 1. Try V2 (bcrypt)
        if hashed_password.startswith(('$2a$', '$2b$', '$2y$')):
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        
        # 2. Try V1 (Werkzeug) fallback
        if ":" in hashed_password:  # Werkzeug format usually pbkdf2:sha256:rounds$salt$hash
            return check_v1_hash(hashed_password, plain_password)
            
    except Exception:
        return False
        
    return False

def get_password_hash(password: str) -> str:
    """
    Generates a bcrypt hash for a password.
    Bcrypt has a 72-character limit, so we handle it gracefully here.
    """
    # Truncate to 72 chars to avoid bcrypt ValueError (V1 parity/safety)
    pw_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
