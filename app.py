import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from pages.login import render_login_page
from pages.signup import render_signup_page

# ... your other imports and component definitions ...

def main():
    inject_css()

    # 1. State setup: Set to True to bypass login right away
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True  # Toggle to False to test the login/signup screens
    
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"

    # 2. Gate: If unauthenticated, show login or signup view
    if not st.session_state.authenticated:
        if st.session_state.auth_view == "login":
            render_login_page()
        else:
            render_signup_page()
        return

    # 3. Authenticated: Render dashboard & pages
    selected_page, demo_mode = render_sidebar()
    # (Render your selected pages here...)

# ----------------------------------------------------------------------------
# App Branding & Config (Change Name Here)
# ----------------------------------------------------------------------------
APP_NAME = "StudyHub AI"  # <--- Change your app name here
APP_SUBTITLE = "Smart Study Companion"
PAGE_ICON = "⚡"

st.set_page_config(
    page_title=f"{APP_NAME} — Laerning Assistant",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

STUDY_GOAL = 90

PALETTE = {
    "blue": ("#DBEAFE", "#2563EB"),
    "green": ("#DCFCE7", "#16A34A"),
    "purple": ("#F3E8FF", "#9333EA"),
    "orange": ("#FFEDD5", "#EA580C"),
    "teal": ("#CCFBF1", "#0D9488"),
}

TOPIC_COLORS = ["#2563EB", "#16A34A", "#9333EA", "#EA580C", "#0D9488", "#DB2777"]

# ----------------------------------------------------------------------------
# Sidebar Navigation Options (Add, edit, or remove items here)
# Format: (Icon, Display Label)
# ----------------------------------------------------------------------------
NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("❓", "Ask Doubt"),
    ("📝", "Quizzes"),
    ("📘", "Revision Mode"),
    ("⚙️", "Settings"),  # Example of an added item
]


# ----------------------------------------------------------------------------
# Sample Data
# ----------------------------------------------------------------------------
@st.cache_data
def generate_sample_data(seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    topics = ["Math", "Science", "History", "English", "Programming"]
    rows = []
    today = datetime.now().date()
    for days_ago in range(13, -1, -1):
        d = today - timedelta(days=days_ago)
        n_quizzes = rng.integers(0, 3)
        for _ in range(n_quizzes):
            rows.append(
                {
                    "date": d,
                    "topic": rng.choice(topics),
                    "score": int(np.clip(rng.normal(75, 15), 30, 100)),
                    "duration_minutes": int(rng.integers(8, 35)),
                }
            )
    return pd.DataFrame(rows)


def compute_streak(dates: pd.Series) -> int:
    if dates.empty:
        return 0
    unique_days = sorted(set(dates), reverse=True)
    today = datetime.now().date()
    streak = 0
    expected = today
    for d in unique_days:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d < expected:
            break
    return streak


def compute_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"study_minutes": 0, "quizzes_taken": 0, "avg_score": 0, "day_streak": 0}
    return {
        "study_minutes": int(df["duration_minutes"].sum()),
        "quizzes_taken": int(len(df)),
        "avg_score": float(df["score"].mean()),
        "day_streak": compute_streak(df["date"]),
    }


def filter_by_range(df: pd.DataFrame, time_range: str) -> pd.DataFrame:
    if df.empty or time_range == "All time":
        return df
    today = datetime.now().date()
    cutoff = {"Today": 0, "This week": 6, "This month": 29}.get(time_range, 10_000)
    return df[df["date"] >= today - timedelta(days=cutoff)]


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .stApp { background: #F5F6FA; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem; max-width: 1200px; }

        /* Sidebar */
        section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #ECEEF3; }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            padding: 0.55rem 0.8rem; border-radius: 10px; margin-bottom: 2px; width: 100%;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: #EFF6FF; color: #2563EB; font-weight: 600;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] input { display: none; }

        /* Containers & Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid #ECEEF3 !important;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
            background: #FFFFFF;
        }
        .kpi-card {
            background: #FFFFFF; border: 1px solid #ECEEF3; border-radius: 16px;
            padding: 1.1rem 1.2rem; display: flex; align-items: center; gap: 0.9rem;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
        }
        .kpi-icon {
            width: 44px; height: 44px; border-radius: 12px; display: flex;
            align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
        }
        .kpi-value { font-size: 1.6rem; font-weight: 700; color: #111827; line-height: 1.1; }
        .kpi-label { font-size: 0.85rem; color: #6B7280; margin-top: 2px; }

        .header-card {
            background: #FFFFFF; border: 1px solid #ECEEF3; border-radius: 16px;
            padding: 1.2rem 1.4rem; box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
            display: flex; align-items: center; gap: 0.9rem;
        }
        .header-title { font-size: 1.35rem; font-weight: 700; color: #111827; margin: 0; }
        .header-subtitle { font-size: 0.85rem; color: #6B7280; margin: 0; }
        .goal-pill {
            background: #DCFCE7; color: #16A34A; font-weight: 600; font-size: 0.85rem;
            padding: 0.5rem 0.9rem; border-radius: 999px; text-align: center; white-space: nowrap;
        }

        .panel-title { font-size: 1.05rem; font-weight: 700; color: #111827; margin-bottom: 0.2rem; }
        .empty-state { text-align: center; padding: 2.5rem 0; color: #9CA3AF; }
        .empty-state .big { font-size: 1.6rem; }
        .empty-state .msg { color: #374151; font-weight: 600; margin-top: 0.5rem; }
        .empty-state .sub { font-size: 0.85rem; margin-top: 0.15rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def icon_badge(icon: str, color_key: str) -> str:
    bg, fg = PALETTE[color_key]
    return f'<div class="kpi-icon" style="background:{bg}; color:{fg};">{icon}</div>'


# ----------------------------------------------------------------------------
# Sidebar Component
# ----------------------------------------------------------------------------
def render_sidebar() -> tuple[str, bool]:
    with st.sidebar:
        # Dynamic Brand Logo & App Name
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:0.6rem; padding: 0.4rem 0 1rem 0;">
                <div style="width:40px;height:40px;border-radius:10px;background:#2563EB;
                            display:flex;align-items:center;justify-content:center;font-size:20px;">{PAGE_ICON}</div>
                <div>
                    <div style="font-weight:700; font-size:1.05rem; color:#111827;">{APP_NAME}</div>
                    <div style="font-size:0.78rem; color:#6B7280;">{APP_SUBTITLE}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        labels = [f"{icon}  {name}" for icon, name in NAV_ITEMS]
        choice = st.radio(
            "Navigate", labels, index=0, label_visibility="collapsed"
        )
        page = choice.split("  ", 1)[1]

        st.markdown("---")
        demo_mode = st.toggle(
            "Load sample data",
            value=False,
            help="Preview the dashboard populated with example quiz history",
        )
    return page, demo_mode


# ----------------------------------------------------------------------------
# Analytics Components
# ----------------------------------------------------------------------------
def render_header(title: str, subtitle: str) -> str:
    col1, col2, col3 = st.columns([3, 1, 1.1])
    with col1:
        st.markdown(
            f"""
            <div class="header-card">
                {icon_badge("📊", "teal")}
                <div>
                    <p class="header-title">{title}</p>
                    <p class="header-subtitle">{subtitle}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        time_range = st.selectbox(
            "Range", ["All time", "Today", "This week", "This month"],
            label_visibility="collapsed",
        )
    with col3:
        st.markdown(
            f'<div class="goal-pill">🎯 Study Goal: {STUDY_GOAL}%</div>',
            unsafe_allow_html=True,
        )
    return time_range


def render_kpi_cards(stats: dict):
    c1, c2, c3, c4 = st.columns(4)
    h, m = divmod(stats["study_minutes"], 60)

    with c1:
        st.markdown(
            f'<div class="kpi-card">{icon_badge("🕐", "blue")}'
            f'<div><div class="kpi-value">{h}h {m}m</div>'
            f'<div class="kpi-label">Study Time</div></div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card">{icon_badge("📖", "green")}'
            f'<div><div class="kpi-value">{stats["quizzes_taken"]}</div>'
            f'<div class="kpi-label">Quizzes Taken</div></div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card">{icon_badge("🎯", "purple")}'
            f'<div><div class="kpi-value">{stats["avg_score"]:.0f}%</div>'
            f'<div class="kpi-label">Avg Score</div></div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="kpi-card">{icon_badge("🔥", "orange")}'
            f'<div><div class="kpi-value">{stats["day_streak"]}</div>'
            f'<div class="kpi-label">Day Streak</div></div></div>',
            unsafe_allow_html=True,
        )


def render_quiz_activity(df: pd.DataFrame):
    with st.container(border=True):
        top_l, top_r = st.columns([3, 1])
        top_l.markdown('<p class="panel-title">Quiz Activity</p>', unsafe_allow_html=True)
        top_r.markdown(
            '<div style="text-align:right; color:#2563EB; font-size:0.85rem;">'
            '● Last 7 days</div>',
            unsafe_allow_html=True,
        )

        today = datetime.now().date()
        last_7 = [today - timedelta(days=i) for i in range(6, -1, -1)]
        week_df = df[df["date"].isin(last_7)] if not df.empty else df

        if week_df.empty:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="big">⚠️</div>
                    <div class="msg">No quiz activity this week</div>
                    <div class="sub">Take some quizzes to see your activity</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            counts = week_df.groupby("date").size().reindex(last_7, fill_value=0)
            fig = go.Figure(
                go.Bar(
                    x=[d.strftime("%a") for d in last_7],
                    y=counts.values,
                    marker_color="#2563EB",
                    marker_line_width=0,
                    width=0.5,
                )
            )
            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="#F0F1F5", zeroline=False, tickformat="d"),
                xaxis=dict(showgrid=False),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_topic_distribution(df: pd.DataFrame, avg_score: float):
    with st.container(border=True):
        st.markdown('<p class="panel-title">Topic Distribution</p>', unsafe_allow_html=True)
        if df.empty:
            fig = go.Figure(go.Pie(values=[1], hole=0.72, marker_colors=["#E5E7EB"], showlegend=False))
            fig.update_traces(textinfo="none", hoverinfo="skip")
        else:
            counts = df["topic"].value_counts()
            fig = go.Figure(
                go.Pie(
                    labels=counts.index,
                    values=counts.values,
                    hole=0.72,
                    marker_colors=TOPIC_COLORS[: len(counts)],
                    textinfo="none",
                )
            )
            fig.update_layout(legend=dict(orientation="h", y=-0.1))

        fig.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b>{avg_score:.0f}%</b><br><span style='font-size:11px;color:#6B7280'>Avg Score</span>",
                    x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="#111827"),
                )
            ],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_weak_points(df: pd.DataFrame):
    if df.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="big">✅</div>
                <div class="msg">No weak points identified yet</div>
                <div class="sub">Take a few quizzes and we'll flag topics that need work</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    by_topic = df.groupby("topic")["score"].mean().sort_values()
    weak = by_topic[by_topic < 70]
    if weak.empty:
        st.success("No weak topics right now — nice work!")
        return
    for topic, score in weak.items():
        st.markdown(f"**{topic}** — {score:.0f}% average")
        st.progress(int(score))


def render_reports(df: pd.DataFrame):
    if df.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="big">📅</div>
                <div class="msg">No reports yet</div>
                <div class="sub">Your quiz history will show up here</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    st.dataframe(
        df.sort_values("date", ascending=False).rename(
            columns={"date": "Date", "topic": "Topic", "score": "Score (%)", "duration_minutes": "Minutes"}
        ),
        use_container_width=True,
        hide_index=True,
    )


# ----------------------------------------------------------------------------
# Separate Page Views
# ----------------------------------------------------------------------------
def render_dashboard_page(df: pd.DataFrame):
    time_range = render_header("Study Dashboard", "Overview of your recent activity and goals")
    filtered_df = filter_by_range(df, time_range)
    stats = compute_stats(filtered_df)

    st.markdown("")
    render_kpi_cards(stats)
    st.markdown("")
    col1, col2 = st.columns([2, 1])
    with col1:
        render_quiz_activity(filtered_df)
    with col2:
        render_topic_distribution(filtered_df, stats["avg_score"])


def render_ask_doubt_page():
    st.markdown("## ❓ Ask a Doubt")
    st.caption("Ask your study-related questions to get instant AI explanations.")
    
    with st.container(border=True):
        topic = st.selectbox("Subject / Topic", ["Mathematics", "Physics", "Chemistry", "Computer Science", "General"])
        doubt_text = st.text_area("What is your doubt or question?", placeholder="Type your doubt or paste problem text here...", height=120)
        uploaded_file = st.file_uploader("Upload an image or document (optional)", type=["png", "jpg", "pdf"])
        
        if st.button("Submit Doubt", type="primary"):
            if doubt_text.strip():
                st.success("Doubt submitted! (Connect your LLM backend here to stream the answer)")
            else:
                st.warning("Please type a question before submitting.")


def render_quizzes_page():
    st.markdown("## 📝 Quizzes & Practice Tests")
    st.caption("Test your knowledge and retain concepts faster.")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Create a Custom Quiz")
            st.selectbox("Select Subject", ["Math", "Science", "History", "Programming"])
            st.slider("Number of Questions", 5, 30, 10)
            st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
            st.button("Start Practice Quiz", type="primary")
            
    with col2:
        with st.container(border=True):
            st.subheader("Active Quizzes")
            st.info("No active tests right now. Start a new quiz from the left panel.")


def render_revision_page():
    st.markdown("## 📘 Revision Mode")
    st.caption("Flashcards, summaries, and spaced-repetition notes.")
    
    with st.container(border=True):
        st.markdown("### 💡 Quick Flashcards")
        st.write("Review key concepts flagged for review today:")
        st.info("**Concept:** Gradient Descent in Machine Learning\n\n*Tap to reveal definition and formulas.*")
        st.button("Next Flashcard")


def render_analytics_page(df: pd.DataFrame):
    time_range = render_header("Learning Analytics", "Deep dive into your performance patterns")
    filtered_df = filter_by_range(df, time_range)
    stats = compute_stats(filtered_df)

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Overview", 
            f"⚠️ Weak Points ({0 if filtered_df.empty else len(filtered_df.groupby('topic')['score'].mean()[lambda s: s < 70])})", 
            "📅 Reports"
        ]
    )

    with tab1:
        render_kpi_cards(stats)
        st.markdown("")
        c_left, c_right = st.columns([2, 1])
        with c_left:
            render_quiz_activity(filtered_df)
        with c_right:
            render_topic_distribution(filtered_df, stats["avg_score"])
    with tab2:
        render_weak_points(filtered_df)
    with tab3:
        render_reports(filtered_df)


# ----------------------------------------------------------------------------
# App Entry Point & Page Router
# ----------------------------------------------------------------------------
def main():
    inject_css()
    selected_page, demo_mode = render_sidebar()

    # Load data source
    df_all = generate_sample_data() if demo_mode else pd.DataFrame(
        columns=["date", "topic", "score", "duration_minutes"]
    )

    # Route based on selected sidebar item
    if selected_page == "Dashboard":
        render_dashboard_page(df_all)
    elif selected_page == "Ask Doubt":
        render_ask_doubt_page()
    elif selected_page == "Quizzes":
        render_quizzes_page()
    elif selected_page == "Revision Mode":
        render_revision_page()
    elif selected_page == "Analytics":
        render_analytics_page(df_all)
    elif selected_page == "Settings":
        st.markdown("## ⚙️ Settings")
        st.write("Customize your platform preferences and profile.")
    else:
        st.warning("Page not found.")


if __name__ == "__main__":
    main()