import streamlit as st


def render_signup_page():
    # Top banner with immediate bypass option
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.info("💡 **Dev Mode**: Registration can be bypassed.")
    with top_col2:
        if st.button("⚡ Skip / Bypass →", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()

    # Aesthetic card styling
    st.markdown(
        """
        <style>
        .auth-container {
            max-width: 440px;
            margin: 2rem auto;
            background: #FFFFFF;
            padding: 2.5rem;
            border-radius: 24px;
            border: 1px solid #ECEEF3;
            box-shadow: 0 18px 40px rgba(87, 70, 139, 0.08);
            text-align: center;
        }
        .auth-logo {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            background: linear-gradient(135deg, #7d62e9, #aa8cff);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            box-shadow: 0 8px 18px rgba(118, 91, 231, 0.3);
            margin-bottom: 0.8rem;
        }
        .auth-title { font-size: 1.6rem; font-weight: 800; color: #211E30; margin-bottom: 0.2rem; }
        .auth-subtitle { font-size: 0.88rem; color: #7D798A; margin-bottom: 1.5rem; }
        </style>
        <div class="auth-container">
            <div class="auth-logo">✦</div>
            <div class="auth-title">Build Your Space</div>
            <div class="auth-subtitle">Create an account to track your progress</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("signup_form"):
            full_name = st.text_input("Full Name", placeholder="e.g. Alex Smith")
            email = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Create Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Create My Account →", use_container_width=True, type="primary")

            if submit:
                if not full_name or not email or len(password) < 6:
                    st.warning("Please fill out all fields with a valid password.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user_name = full_name
                    st.session_state.user_email = email
                    st.success("Account created successfully!")
                    st.rerun()

        # Switch to Login view
        st.markdown("<div style='text-align:center; font-size:0.85rem; color:#888;'>Already registered?</div>", unsafe_allow_html=True)
        if st.button("Log in to existing account", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()