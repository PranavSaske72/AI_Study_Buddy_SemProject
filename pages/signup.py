import streamlit as st
from services.database import create_user, get_or_create_dev_user


def render_signup_page():
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
            <div class="auth-title">Create Your Account</div>
            <div class="auth-subtitle">Join StudyHub AI to track quizzes and master your subjects</div>
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
        with st.form("signup_form"):
            full_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan").strip()
            email = st.text_input("Email Address", placeholder="alex@studyhub.ai").strip()
            password = st.text_input("Create Password", type="password", placeholder="•••••••• (min 6 chars)").strip()
            submit = st.form_submit_button("Create My Account →", use_container_width=True)

            if submit:
                if not full_name or not email or len(password) < 6:
                    st.warning("Please fill out all fields. Password must be at least 6 characters.")
                else:
                    success, user_id, message = create_user(full_name, email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.user_name = full_name
                        st.session_state.user_email = email
                        st.success(f"Account created successfully! Welcome, {full_name} 🎉")
                        st.rerun()
                    else:
                        st.error(message)

        # Switch to Login view
        st.markdown("<div style='text-align:center; font-size:0.85rem; color:#888; margin-top:12px;'>Already registered?</div>", unsafe_allow_html=True)
        if st.button("Log in to existing account", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()