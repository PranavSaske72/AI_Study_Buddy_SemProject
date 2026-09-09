import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# ---------- SIDEBAR ----------

with st.sidebar:
    st.title("📚 AI Study Buddy")
    st.caption("Your Intelligent Learning Assistant")

    st.divider()

    st.page_link("app.py", label="🏠 Dashboard")

    st.page_link(
        "pages/study_material.py",
        label="📚 Study Materials"
    )

    st.page_link(
        "pages/chat.py",
        label="🤖 AI Tutor"
    )

    st.page_link(
        "pages/quiz.py",
        label="📝 Quiz"
    )

    st.divider()

    st.page_link(
        "pages/login.py",
        label="🔐 Login"
    )

    st.page_link(
        "pages/signup.py",
        label="📝 Sign Up"
    )

# ---------- MAIN DASHBOARD ----------

st.title("Good Afternoon, Student 👋")

st.write(
    "Welcome back! Let's continue your learning journey."
)

st.divider()

# ---------- STATISTICS ----------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📚 Study Materials",
        value="0"
    )

with col2:
    st.metric(
        label="📝 Quizzes Completed",
        value="0"
    )

with col3:
    st.metric(
        label="🎯 Average Score",
        value="0%"
    )

st.divider()

# ---------- QUICK ACTIONS ----------

st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📤 Upload Study Material")
    st.write("Upload your PDF notes and study materials.")

with col2:
    st.info("🤖 Ask AI Tutor")
    st.write("Ask questions and get AI-powered explanations.")

with col3:
    st.info("📝 Generate Quiz")
    st.write("Create a quiz from your study material.")

st.divider()

# ---------- GETTING STARTED ----------

st.subheader("🚀 Getting Started")

st.write(
    "Upload your first study material to begin using AI Study Buddy."
)

st.success(
    "Your AI Study Buddy dashboard is ready!"
)
