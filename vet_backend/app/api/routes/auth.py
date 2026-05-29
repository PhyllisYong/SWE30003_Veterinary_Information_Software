from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.services.authentication import authentication

router = APIRouter()
bearer_scheme = HTTPBearer()


# ── Dependency: get current user from token ────────────────────────────────────

def getCurrentUser(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency — extract and validate the Bearer token, return User."""
    payload = authentication.validate_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.userID == payload["sub"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def requireRole(*roles: str):
    """Dependency factory — restrict endpoint to specific roles."""
    def _check(current_user: User = Depends(getCurrentUser)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(roles)}",
            )
        return current_user
    return _check


# ── POST /api/auth/register ────────────────────────────────────────────────────

@router.post("/auth/register", tags=["auth"])
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    createUser() — Register a new PetOwner, Veterinarian, or AssociationAdministrator.
    """
    # Check duplicate email
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_pw = authentication.hash_password(body.password)

    if body.role == "pet_owner":
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="pet_owner",
            contactNumber=body.contactNumber,
        )

    elif body.role == "veterinarian":
        if not body.licenseNumber:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="licenseNumber is required for veterinarian registration",
            )
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="veterinarian",
            licenseNumber=body.licenseNumber,
            specialisation=body.specialisation,
        )

    elif body.role == "association_admin":
        if not body.workID:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="workID is required for association admin registration",
            )
        user = User.createUser(
            name=body.name,
            email=body.email,
            password=hashed_pw,
            role="association_admin",
            workID=body.workID,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be one of: pet_owner, veterinarian, association_admin",
        )

    db.add(user)
    db.commit()
    db.refresh(user)

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
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    login() — Authenticate user by email + password, return JWT token.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or not authentication.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

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
def getMe(current_user: User = Depends(getCurrentUser)):
    """
    getRole() — Return the currently authenticated user's profile.
    """
    return {
        "status": "ok",
        "data": {
            "userID": current_user.userID,
            "name": current_user.getName(),
            "email": current_user.getEmail(),
            "role": current_user.getRole(),
        },
    }


@router.post("/auth/logout", tags=["auth"])
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(getCurrentUser),
):
    """
    logout() — End the current session.

    JWTs are stateless in this implementation, so logout is acknowledged and
    the frontend clears the token.
    """
    authentication.logout(credentials.credentials)
    authentication.invalidateSession(current_user.userID)
    return {"status": "ok", "data": {"message": "Logged out successfully"}}
