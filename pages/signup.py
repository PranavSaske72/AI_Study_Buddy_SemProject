import streamlit as st
from services.database import create_user


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
                st.success(message)
                st.info("Your account has been created. You can now log in.")
            else:
                st.error(message)


show_signup()