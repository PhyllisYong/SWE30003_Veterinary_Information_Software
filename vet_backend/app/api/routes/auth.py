from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import getDb
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services import user_service
from app.services.authentication import authentication

router = APIRouter()
bearer_scheme = HTTPBearer()


# ── Dependency: get current user from token ────────────────────────────────────

def getCurrentUser(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(getDb),
) -> User:
    """FastAPI dependency — extract and validate the Bearer token, return User."""
    payload = authentication.validateToken(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = user_repository.getById(db, payload["sub"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def requireRole(*roles: str):
    """Dependency factory — restrict endpoint to specific roles."""
    def _check(currentUser: User = Depends(getCurrentUser)) -> User:
        if currentUser.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(roles)}",
            )
        return currentUser
    return _check


# ── POST /api/auth/register ────────────────────────────────────────────────────

@router.post("/auth/register", tags=["auth"])
def register(body: RegisterRequest, db: Session = Depends(getDb)):
    """createUser() — Register a new PetOwner, Veterinarian, or AssociationAdministrator."""
    user = user_service.register(db, body)
    token = authentication.issueSession(user.userID, body.role)
    return {
        "status": "ok",
        "data": {
            "token": token,
            "userID": user.userID,
            "name": body.name,
            "role": body.role,
        },
    }


# ── POST /api/auth/login ───────────────────────────────────────────────────────

@router.post("/auth/login", tags=["auth"])
def login(body: LoginRequest, db: Session = Depends(getDb)):
    """login() — Authenticate user by email + password, return JWT token."""
    user = user_service.login(db, body)
    token = authentication.issueSession(user.userID, user.role)
    return {
        "status": "ok",
        "data": {
            "token": token,
            "userID": user.userID,
            "name": user.name,
            "role": user.role,
        },
    }


# ── GET /api/auth/me ───────────────────────────────────────────────────────────

@router.get("/auth/me", tags=["auth"])
def getMe(currentUser: User = Depends(getCurrentUser)):
    """getRole() — Return the currently authenticated user's profile."""
    return {
        "status": "ok",
        "data": {
            "userID": currentUser.userID,
            "name": currentUser.getName(),
            "email": currentUser.getEmail(),
            "role": currentUser.getRole(),
        },
    }


@router.post("/auth/logout", tags=["auth"])
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    currentUser: User = Depends(getCurrentUser),
):
    """logout() — End the current session."""
    authentication.logout(credentials.credentials)
    authentication.invalidateSession(currentUser.userID)
    return {"status": "ok", "data": {"message": "Logged out successfully"}}
