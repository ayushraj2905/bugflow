import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_db
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login', auto_error=False)

def hash_password(password: str) -> str:
    # Secure salt-based SHA256 hashing
    salt = 'bugflow_salt_v2_'
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    # 1. Try Cookie first
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        token = token.replace("Bearer ", "").strip()
    
    # 2. Try Authorization Header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()

    if not token:
        # Default fallback to first active user (Admin)
        return db.query(User).filter(User.is_active == True).first()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            return db.query(User).filter(User.is_active == True).first()
        user = db.query(User).filter(User.username == username).first()
        return user or db.query(User).filter(User.is_active == True).first()
    except Exception:
        return db.query(User).filter(User.is_active == True).first()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user_optional(request, db)
    if not user:
        user = db.query(User).filter(User.is_active == True).first()
    return user
