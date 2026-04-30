"""
Authentication API router
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AdminUser
from app.schemas import AdminLogin
from app.security import hash_password, verify_password, create_admin_session, \
    verify_admin_session, delete_admin_session

router = APIRouter()


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
