from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas import UserCreate, UserResponse, LoginRequest, Token
from ..services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["Authentication & RBAC"])

@router.post("/api/v1/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        team=user_in.team,
        core_skills=user_in.core_skills,
        proficiency=user_in.proficiency
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/api/v1/auth/login")
def login(creds: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == creds.username).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    
    # Set HTTP-only compatible cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=False,
        max_age=86400,
        path="/"
    )
    
    return {
        "message": f"Welcome back, {user.full_name}!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "team": user.team,
            "proficiency": user.proficiency
        }
    }

@router.get("/api/v1/auth/logout")
@router.post("/api/v1/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}

@router.post("/api/v1/auth/switch-user/{user_id}")
def switch_user(user_id: int, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=False,
        max_age=86400,
        path="/"
    )
    return {
        "message": f"Switched active account to {user.full_name} ({user.role})",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "team": user.team
        }
    }

@router.get("/api/v1/auth/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@router.get("/api/v1/auth/developers")
def list_developers(db: Session = Depends(get_db)):
    devs = db.query(User).all()
    return [{
        "id": d.id,
        "username": d.username,
        "full_name": d.full_name,
        "role": d.role,
        "team": d.team,
        "core_skills": d.core_skills,
        "proficiency": d.proficiency
    } for d in devs]
