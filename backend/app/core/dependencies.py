from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
import jwt
from app.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

bearer = HTTPBearer()

def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(User, int(payload["sub"]))
    except (InvalidTokenError, KeyError, ValueError, TypeError):
        user = None
    if user is None:
        raise HTTPException(401, "Invalid or expired token")
    return user

def admin_only(user: User = Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user

def customer_only(user: User = Depends(current_user)):
    if user.role != "customer":
        raise HTTPException(403, "Customer access required")
    return user
