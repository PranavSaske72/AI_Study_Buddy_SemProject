import streamlit as st
from google import genai

st.set_page_config(page_title="Ask a Doubt", page_icon="💬", layout="wide")

st.title("💬 Ask a Doubt")
st.caption("Your AI-powered personal tutor")

# Check API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("Gemini API key not found. Check .streamlit/secrets.toml")
    st.stop()

client = genai.Client(api_key=api_key)

subject = st.selectbox(
    "Select Subject",
    ["General", "Physics", "Chemistry", "Biology", "Mathematics", "Computer Science"]
)

question = st.text_area(
    "Your Question",
    placeholder="Type your doubt here...",
    height=150
)

if st.button("✨ Submit Doubt", type="primary"):
    if not question.strip():
        st.warning("Please enter your question first.")
    else:
        prompt = f"""
        You are a friendly AI tutor for a college student.
        Subject: {subject}
        Answer the student's question clearly and accurately.
        Use simple language, steps, and examples where helpful.
        If the question is ambiguous, ask for clarification.

        Student's question: {question}
        """

        with st.spinner("AI tutor is preparing your answer..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.subheader("📘 AI Tutor's Answer")
                st.markdown(response.text or "No answer was returned. Please try again.")
            except Exception:
                st.error(
                    "Could not generate an answer. Check your internet "
                    "connection, API key, API access, and model availability."
                )