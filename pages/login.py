import streamlit as st
from services.database import authenticate_user, get_or_create_dev_user


def render_login_page():
    # Aesthetic card styling
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
        .stApp { background-color: #F5F7FC !important; }
        
        .auth-container {
            max-width: 440px;
            margin: 1.5rem auto 1rem auto;
            background: #FFFFFF;
            padding: 2.2rem 2.2rem;
            border-radius: 20px;
            border: 1px solid #ECEEF5;
            box-shadow: 0 10px 30px rgba(108, 85, 246, 0.06);
            text-align: center;
        }
        .auth-logo {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            background: linear-gradient(135deg, #6C55F6, #8B5CF6);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 8px 20px rgba(108, 85, 246, 0.35);
            margin-bottom: 0.9rem;
        }
        .auth-title { font-size: 1.55rem; font-weight: 800; color: #1E1B4B; margin-bottom: 0.3rem; letter-spacing: -0.02em; }
        .auth-subtitle { font-size: 0.88rem; color: #64748B; margin-bottom: 0.5rem; }
        
        .stButton > button[kind="primary"], div[data-testid="stForm"] .stButton > button {
            background-color: #6C55F6 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(108, 85, 246, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button[kind="primary"]:hover, div[data-testid="stForm"] .stButton > button:hover {
            background-color: #5942E0 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(108, 85, 246, 0.4) !important;
        }
        </style>
        <div class="auth-container">
            <div class="auth-logo">⚡</div>
            <div class="auth-title">Welcome to StudyHub AI</div>
            <div class="auth-subtitle">Your intelligent companion for smarter study & revision</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top dev-bypass option
    _, mid_top, _ = st.columns([1, 1.2, 1])
    with mid_top:
        if st.button("⚡ Quick Dev Login →", type="primary", use_container_width=True):
            dev_id, dev_name, dev_email = get_or_create_dev_user()
            st.session_state.authenticated = True
            st.session_state.user_id = dev_id
            st.session_state.user_name = dev_name
            st.session_state.user_email = dev_email
            st.rerun()

    # Form centered in main column
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="alex@studyhub.ai").strip()
            password = st.text_input("Password", type="password", placeholder="••••••••").strip()
            submit = st.form_submit_button("Log In to StudyHub AI →", use_container_width=True)

            if submit:
                if not email or not password:
                    st.warning("Please enter both your email address and password.")
                else:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_name = user[1]
                        st.session_state.user_email = user[2]
                        st.success(f"Welcome back, {user[1]}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please check your credentials or create an account.")

        # Switch to Signup view
        st.markdown("<div style='text-align:center; font-size:0.85rem; color:#888; margin-top:12px;'>New to StudyHub AI?</div>", unsafe_allow_html=True)
        if st.button("Create an account", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()