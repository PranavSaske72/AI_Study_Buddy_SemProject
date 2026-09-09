import streamlit as st
from services.database import authenticate_user


def show_login():
    st.title("🔐 Login")
    st.write("Welcome back to AI Study Buddy!")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        if not email or not password:
            st.error("Please enter your email and password.")

        else:
            user = authenticate_user(email, password)

            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user[0]
                st.session_state["user_name"] = user[1]
                st.session_state["user_email"] = user[2]

                st.success(f"Welcome back, {user[1]}! 👋")
                st.switch_page("app.py")

            else:
                st.error("Invalid email or password.")


show_login()