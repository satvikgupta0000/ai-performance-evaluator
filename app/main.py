import streamlit as st
from app.core.auth import login, set_session, get_session, logout
from app.views import employee_view, manager_view, hr_view
from app.scheduler import start_scheduler

st.set_page_config(
    page_title="Performance Evaluation System",
    page_icon="📊",
    layout="wide",
)

if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state["scheduler_started"] = True

def render_login():
    st.title("Performance Evaluation System")
    st.markdown("---")

    col, _ = st.columns([1, 1])
    with col:
        st.subheader("Sign in")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please enter email and password.")
                return

            user = login(email.strip().lower(), password)
            if user:
                set_session(user)
                st.rerun()
            else:
                st.error("Invalid credentials or account inactive.")

def render_sidebar(user: dict):
    with st.sidebar:
        st.markdown(f"**{user['name']}**")
        st.caption(f"Role: {user['role'].capitalize()}")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

def main():
    user = get_session()

    if not user:
        render_login()
        return

    render_sidebar(user)

    role = user["role"]
    if role == "employee":
        employee_view.render(user)
    elif role == "manager":
        manager_view.render(user)
    elif role == "hr":
        hr_view.render(user)
    else:
        st.error("Unknown role. Contact HR.")

if __name__ == "__main__":
    main()
