import streamlit as st
from services.database import create_user, authenticate_user


def show_signup():
    st.title("📝 Create Your Account")
    st.write("Create an account to start using AI Study Buddy.")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account", use_container_width=True):

        if not name or not email or not password or not confirm_password:
            st.error("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif len(password) < 6:
            st.error("Password must contain at least 6 characters.")

        else:
            success, message = create_user(name, email, password)

            if success:
                user = authenticate_user(email,password)

        

            if user:
                st.success(message)
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user[0]
                st.session_state["user_name"] = user[1]
                st.session_state["user_email"] = user[2]
                st.switch_page("app.py")
            else:
                st.error(message)


show_signup()