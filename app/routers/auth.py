""" Authentication API router """
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AdminUser, User
from app.schemas import AdminLogin, UserRegister, UserRegisterResponse
from app.security import (
    create_admin_session,
    delete_admin_session,
    hash_password,
    verify_admin_session,
    verify_password,
)

router = APIRouter()

# Frontend routes
@router.get("/register", include_in_schema=False)
async def register_page(request: Request):
    """Страница регистрации пользователя."""
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    """Страница восстановления пароля."""
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@router.post("/register", response_model=UserRegisterResponse)
def register_user(register_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == register_data.username) | (User.email == register_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует")

    # Create new user
    user = User(
        username=register_data.username,
        email=register_data.email,
        password_hash=hash_password(register_data.password[:72]),
        created_at=datetime.now(UTC)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "success", "message": "Пользователь успешно зарегистрирован"}


@router.post("/login")
def login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Authenticate admin user and create session."""
    # For first-time setup, create default admin if no users exist
    admin = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
    if not admin:
        # Check if this is the first admin (no users in database)
        admin_count = db.query(AdminUser).count()
        if admin_count == 0 and login_data.username == "admin" and login_data.password == "admin":
            # Create default admin for first setup (should be changed immediately)
            admin = AdminUser(
                username="admin",
                password_hash=hash_password("admin")
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    if not verify_password(login_data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    session_id = create_admin_session(admin.username, db)
    return {"status": "success", "session_id": session_id}


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    """Logout admin user by deleting session."""
    session_id = request.cookies.get("admin_session")
    if session_id:
        delete_admin_session(session_id, db)
    return {"status": "logged out"}


@router.get("/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated admin user."""
    session_id = request.cookies.get("admin_session")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = verify_admin_session(session_id, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": admin.username,
        "is_active": admin.is_active,
        "created_at": admin.created_at.isoformat() if admin.created_at else None
    }


@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Change admin password."""
    session_id = request.cookies.get("admin_session")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = verify_admin_session(session_id, db)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not verify_password(old_password, admin.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Update password
    admin.password_hash = hash_password(new_password)
    db.commit()

    return {"status": "Password changed successfully"}
