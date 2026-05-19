import bcrypt
import streamlit as st
from app.core.db import fetch_one

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def login(email: str, password: str) -> dict | None:
    user = fetch_one("""
        SELECT u.id, u.name, u.email, u.password_hash,
               r.name AS role, u.department_id, u.manager_id, u.is_active
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.email = :email
    """, {"email": email})

    if not user or not user["is_active"]:
        return None
    if not verify_password(password, user["password_hash"]):
        return None

    user.pop("password_hash")
    return user

def set_session(user: dict):
    st.session_state["user"] = user

def get_session() -> dict | None:
    return st.session_state.get("user")

def logout():
    st.session_state.pop("user", None)

def require_role(*roles: str):
    user = get_session()
    if not user or user["role"] not in roles:
        st.error("Access denied.")
        st.stop()
    return user
