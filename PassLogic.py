from fastapi import HTTPException, status, Depends
from models import settings
import jwt
from datetime import datetime, timedelta
import bcrypt
        
        
def hash_password(password: str) -> str:
    """Securely hash a password using direct bcrypt library."""
    # Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
        
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against the stored hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
    



def create_access_token(data: dict) -> str:
    """Generate a secure JWT token containing user data with an expiration time."""
    to_encode = data.copy()
    
    # Calculate when the token expires 
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """Decode JWT token and return the username (subject)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )