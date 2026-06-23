from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, Session as AuthSession
from backend.schemas.auth import SignUpRequest, LoginRequest, AuthResponse, LogoutResponse, MeResponse
from backend.services.auth import hash_password, verify_password, generate_token, compute_expiry


router = APIRouter()


def get_current_user(token: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Token nao fornecido.")
    auth_session = db.query(AuthSession).filter(
        AuthSession.token == token,
        AuthSession.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
    ).first()
    if not auth_session:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado.")
    user = db.query(User).filter(User.id == auth_session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado.")
    return user


@router.post("/api/auth/signup", response_model=AuthResponse)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email ja cadastrado.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token()
    session = AuthSession(
        user_id=user.id,
        token=token,
        expires_at=compute_expiry(),
    )
    db.add(session)
    db.commit()

    return AuthResponse(token=token, email=user.email, user_id=user.id)


@router.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos.")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha invalidos.")

    token = generate_token()
    session = AuthSession(
        user_id=user.id,
        token=token,
        expires_at=compute_expiry(),
    )
    db.add(session)
    db.commit()

    return AuthResponse(token=token, email=user.email, user_id=user.id)


@router.post("/api/auth/logout", response_model=LogoutResponse)
def logout(token: str | None = Header(None), db: Session = Depends(get_db)):
    if not token:
        return LogoutResponse(message="Nenhuma sessao ativa.")
    auth_session = db.query(AuthSession).filter(AuthSession.token == token).first()
    if auth_session:
        db.delete(auth_session)
        db.commit()
    return LogoutResponse(message="Logout realizado com sucesso.")


@router.get("/api/auth/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return MeResponse(email=current_user.email, user_id=current_user.id)