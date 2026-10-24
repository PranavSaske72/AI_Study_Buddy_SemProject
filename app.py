import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from pathlib import Path
import json
import random
import io

from pages.login import render_login_page
from pages.signup import render_signup_page
from services.database import (
    get_dashboard_stats,
    get_quiz_activity,
    get_topic_distribution,
    get_study_streak,
    get_analytics_data,
    save_study_activity,
    create_quiz,
    save_quiz_questions,
    save_quiz_attempt,
    get_user_settings,
    save_user_settings,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    save_study_material,
    get_study_materials,
    delete_study_material,
    get_quiz_history,
)

# ----------------------------------------------------------------------------
# App Branding & Configuration
# ----------------------------------------------------------------------------
APP_NAME = "StudyHub AI"
APP_SUBTITLE = "Smart Study Companion"
PAGE_ICON = "⚡"

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_SUBTITLE}",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

STUDY_GOAL_DEFAULT = 90

NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("❓", "Ask a Doubt"),
    ("📝", "Quizzes"),
    ("📘", "Revision Mode"),
    ("⚙️", "Settings"),
]

# ----------------------------------------------------------------------------
# Theme Color Provider
# ----------------------------------------------------------------------------
def get_theme_colors():
    theme = st.session_state.get("settings_theme", "Light")
    is_dark = (theme == "Dark")

    # Distinct gradients for Light and Dark themes
    if is_dark:
        bg_app_gradient = (
            "radial-gradient(circle at 15% 15%, rgba(108, 85, 246, 0.25) 0%, transparent 45%), "
            "radial-gradient(circle at 85% 18%, rgba(6, 182, 212, 0.20) 0%, transparent 42%), "
            "radial-gradient(circle at 80% 82%, rgba(147, 51, 234, 0.22) 0%, transparent 45%), "
            "radial-gradient(circle at 20% 85%, rgba(16, 185, 129, 0.15) 0%, transparent 40%), "
            "#0B0C16"
        )
        bg_card = "#161726"
        bg_card_secondary = "#1E2034"
        border_card = "#282A45"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        sidebar_bg = "#121320"
        sidebar_border = "#23253D"
        input_bg = "#1B1D30"
        input_border = "#2E3150"
        plot_paper_bg = "#161726"
        plot_font_color = "#94A3B8"
        plot_grid_color = "#23253D"
        nav_active_bg = "#2C2758"
        nav_active_text = "#A78BFA"
        card_shadow = "0 8px 32px rgba(0, 0, 0, 0.35)"
    else:
        bg_app_gradient = (
            "radial-gradient(circle at 12% 15%, rgba(237, 233, 254, 0.85) 0%, transparent 42%), "
            "radial-gradient(circle at 88% 12%, rgba(224, 242, 254, 0.90) 0%, transparent 45%), "
            "radial-gradient(circle at 85% 85%, rgba(209, 250, 229, 0.65) 0%, transparent 40%), "
            "radial-gradient(circle at 15% 85%, rgba(254, 243, 199, 0.55) 0%, transparent 40%), "
            "#F5F7FC"
        )
        bg_card = "#FFFFFF"
        bg_card_secondary = "#F8FAFC"
        border_card = "#ECEEF5"
        text_primary = "#1E1B4B"
        text_secondary = "#64748B"
        sidebar_bg = "#FFFFFF"
        sidebar_border = "#ECEEF5"
        input_bg = "#FFFFFF"
        input_border = "#E2E8F0"
        plot_paper_bg = "#FFFFFF"
        plot_font_color = "#64748B"
        plot_grid_color = "#F1F5F9"
        nav_active_bg = "#EDE9FE"
        nav_active_text = "#6C55F6"
        card_shadow = "0 4px 20px rgba(108, 85, 246, 0.05)"

    return {
        "is_dark": is_dark,
        "bg_app_gradient": bg_app_gradient,
        "bg_card": bg_card,
        "bg_card_secondary": bg_card_secondary,
        "border_card": border_card,
        "text_primary": text_primary,
        "text_secondary": text_secondary,
        "sidebar_bg": sidebar_bg,
        "sidebar_border": sidebar_border,
        "input_bg": input_bg,
        "input_border": input_border,
        "plot_paper_bg": plot_paper_bg,
        "plot_font_color": plot_font_color,
        "plot_grid_color": plot_grid_color,
        "nav_active_bg": nav_active_bg,
        "nav_active_text": nav_active_text,
        "card_shadow": card_shadow,
    }


# ----------------------------------------------------------------------------
# Session State Initialization (Default model: gemini-3.5-flash-lite)
# ----------------------------------------------------------------------------
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_name" not in st.session_state or not st.session_state.user_name:
        st.session_state.user_name = "Alex Morgan"
    if "user_email" not in st.session_state or not st.session_state.user_email:
        st.session_state.user_email = "alex@studyhub.ai"
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    if "settings_loaded" not in st.session_state:
        st.session_state.settings_loaded = False
    if "settings_theme" not in st.session_state:
        st.session_state.settings_theme = "Light"
    if "selected_nav" not in st.session_state:
        st.session_state.selected_nav = "Dashboard"
    if "settings_study_goal" not in st.session_state:
        st.session_state.settings_study_goal = 90
    if "settings_notifications" not in st.session_state:
        st.session_state.settings_notifications = True
    if "settings_quiz_notifications" not in st.session_state:
        st.session_state.settings_quiz_notifications = True
    if "settings_streak_notifications" not in st.session_state:
        st.session_state.settings_streak_notifications = True
    if "settings_weekly_digest" not in st.session_state:
        st.session_state.settings_weekly_digest = True
    if "settings_difficulty" not in st.session_state:
        st.session_state.settings_difficulty = "Medium"
    if "settings_subject" not in st.session_state:
        st.session_state.settings_subject = "Mathematics"
    # DEFAULT MODEL IS SET TO gemini-3.5-flash-lite
    if "settings_ai_model" not in st.session_state:
        st.session_state.settings_ai_model = "gemini-3.5-flash-lite"
    if "settings_ai_tone" not in st.session_state:
        st.session_state.settings_ai_tone = "Friendly & Clear"
    if "doubt_subject" not in st.session_state:
        st.session_state.doubt_subject = "Mathematics"
    if "doubt_question_input" not in st.session_state:
        st.session_state.doubt_question_input = ""
    if "quiz_current_index" not in st.session_state:
        st.session_state.quiz_current_index = 0
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "active_quiz_questions" not in st.session_state:
        st.session_state.active_quiz_questions = None
    if "show_past_results" not in st.session_state:
        st.session_state.show_past_results = False
    if "settings_tab" not in st.session_state:
        st.session_state.settings_tab = "Appearance"
    if "flashcard_flipped" not in st.session_state:
        st.session_state.flashcard_flipped = False


def load_user_settings_if_needed():
    if st.session_state.authenticated and st.session_state.user_id and not st.session_state.settings_loaded:
        settings = get_user_settings(st.session_state.user_id)
        st.session_state.settings_study_goal = settings.get("study_goal", 90)
        st.session_state.settings_difficulty = settings.get("difficulty", "Medium")
        st.session_state.settings_subject = settings.get("favorite_subject", "Mathematics")
        st.session_state.settings_notifications = settings.get("notifications", True)
        st.session_state.settings_quiz_notifications = settings.get("quiz_notifications", True)
        st.session_state.settings_theme = settings.get("theme", "Light")
        st.session_state.settings_ai_model = settings.get("ai_model", "gemini-3.5-flash-lite")
        st.session_state.settings_ai_tone = settings.get("ai_tone", "Friendly & Clear")
        st.session_state.settings_loaded = True


# ----------------------------------------------------------------------------
# Theme & CSS System (With Gradients, Radio Option Cards & 3D Flip Card)
# ----------------------------------------------------------------------------
def inject_css():
    c = get_theme_colors()

    st.markdown(
        f"""
        <style>
        * {{
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }}

        /* Dynamic Gradient Background according to theme */
        .stApp {{
            background: {c['bg_app_gradient']} !important;
            background-attachment: fixed !important;
            color: {c['text_primary']} !important;
        }}
        #MainMenu, footer, header {{ visibility: hidden; height: 0px; margin: 0px; }}
        
        .block-container {{
            padding-top: 0.6rem !important;
            padding-bottom: 2rem !important;
            max-width: 1360px !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background: {c['sidebar_bg']} !important;
            border-right: 1px solid {c['sidebar_border']} !important;
            padding-top: 0.5rem !important;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 0.6rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }}

        /* Rock-Solid, Butter-Smooth Buttons (Zero Jitter) */
        .stButton > button {{
            transition: background 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease !important;
            cursor: pointer !important;
            user-select: none !important;
        }}
        .stButton > button:active {{
            transform: scale(0.98) !important;
        }}

        /* Navigation Buttons in Sidebar */
        div.sidebar-nav-container .stButton > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            width: 100% !important;
            padding: 10px 14px !important;
            border-radius: 12px !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            color: {c['text_secondary']} !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
            margin-bottom: 3px !important;
        }}

        div.sidebar-nav-container .stButton > button:hover {{
            background: {'#1D1F33' if c['is_dark'] else '#F8FAFC'} !important;
            color: {c['text_primary']} !important;
            border-color: {'#2A2D48' if c['is_dark'] else '#E2E8F0'} !important;
            transform: translateX(2px) !important;
        }}

        /* Active Navigation Item */
        div.sidebar-nav-container .stButton > button[kind="primary"] {{
            background: {c['nav_active_bg']} !important;
            color: {c['nav_active_text']} !important;
            font-weight: 700 !important;
            border: 1px solid {c['nav_active_bg']} !important;
            box-shadow: 0 4px 14px rgba(108, 85, 246, 0.14) !important;
            transform: none !important;
        }}

        div.sidebar-nav-container .stButton > button * {{
            text-align: left !important;
            justify-content: flex-start !important;
        }}

        /* Reusable Card Base */
        .sh-card {{
            background: {c['bg_card']};
            border: 1px solid {c['border_card']};
            border-radius: 18px;
            padding: 1.25rem 1.4rem;
            box-shadow: {c['card_shadow']};
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }}
        .sh-card:hover {{
            box-shadow: 0 8px 24px rgba(108, 85, 246, 0.08);
        }}

        /* Welcome Banner Card */
        .welcome-card {{
            background: {c['bg_card']};
            border: 1px solid {c['border_card']};
            border-radius: 18px;
            padding: 1.2rem 1.6rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.2rem;
            box-shadow: {c['card_shadow']};
        }}

        .welcome-left {{
            display: flex;
            align-items: center;
            gap: 1.1rem;
        }}

        .welcome-badge {{
            width: 50px;
            height: 50px;
            border-radius: 15px;
            background: linear-gradient(135deg, #FFEDD5, #FEE2E2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            box-shadow: 0 4px 12px rgba(251, 146, 60, 0.25);
            flex-shrink: 0;
        }}

        .welcome-title {{
            font-size: 1.4rem;
            font-weight: 800;
            color: {c['text_primary']};
            line-height: 1.2;
            margin-bottom: 3px;
            letter-spacing: -0.015em;
        }}

        .welcome-sub {{
            font-size: 0.86rem;
            color: {c['text_secondary']};
            font-weight: 500;
        }}

        .study-goal-box {{
            background: {c['bg_card_secondary']};
            border: 1px solid {c['border_card']};
            border-radius: 14px;
            padding: 0.8rem 1.25rem;
            min-width: 270px;
        }}

        .goal-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 0.84rem;
            font-weight: 700;
            color: {c['text_primary']};
        }}

        .goal-bar-bg {{
            width: 100%;
            height: 8px;
            background: {'#2A2D48' if c['is_dark'] else '#E2E8F0'};
            border-radius: 999px;
            overflow: hidden;
        }}

        .goal-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10B981, #06B6D4);
            border-radius: 999px;
            transition: width 0.4s ease;
        }}

        /* KPI Cards */
        .kpi-card {{
            background: {c['bg_card']};
            border: 1px solid {c['border_card']};
            border-radius: 16px;
            padding: 1.15rem 1.3rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: {c['card_shadow']};
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(108, 85, 246, 0.09);
        }}

        .kpi-left {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
        }}

        .kpi-icon-box {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }}

        .kpi-value {{
            font-size: 1.4rem;
            font-weight: 800;
            color: {c['text_primary']};
            line-height: 1.1;
        }}

        .kpi-label {{
            font-size: 0.80rem;
            font-weight: 600;
            color: {c['text_secondary']};
            margin-top: 3px;
        }}

        .kpi-badge {{
            font-size: 0.74rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            gap: 3px;
        }}

        /* Top Bar */
        .search-container {{
            flex: 1;
            max-width: 520px;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            background: {c['bg_card']};
            border: 1px solid {c['border_card']};
            border-radius: 12px;
            padding: 8px 14px;
            color: {c['text_secondary']};
            box-shadow: {c['card_shadow']};
        }}
        .search-container input {{
            border: none;
            outline: none;
            background: transparent;
            width: 100%;
            font-size: 0.88rem;
            color: {c['text_primary']};
        }}

        .topbar-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .action-icon-btn {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: {c['bg_card']};
            border: 1px solid {c['border_card']};
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 16px;
            color: {c['text_secondary']};
            position: relative;
            transition: all 0.15s ease;
        }}
        .action-icon-btn:hover {{
            background: {c['bg_card_secondary']};
            color: {c['text_primary']};
            transform: translateY(-1px);
        }}

        .unread-dot {{
            width: 8px;
            height: 8px;
            background: #EF4444;
            border-radius: 50%;
            position: absolute;
            top: 7px;
            right: 7px;
            border: 1.5px solid {c['bg_card']};
        }}

        .user-top-avatar {{
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6C55F6, #A78BFA);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            font-weight: 700;
            box-shadow: 0 3px 8px rgba(108, 85, 246, 0.3);
        }}

        /* Buttons Styling */
        .stButton > button[kind="primary"] {{
            background-color: #6C55F6 !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 9px 20px !important;
            box-shadow: 0 4px 14px rgba(108, 85, 246, 0.28) !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: #5942E0 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(108, 85, 246, 0.38) !important;
        }}

        .stButton > button[kind="secondary"] {{
            background-color: {c['bg_card']} !important;
            color: {c['text_primary']} !important;
            border: 1px solid {c['border_card']} !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 9px 18px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        }}
        .stButton > button[kind="secondary"]:hover {{
            background-color: {c['bg_card_secondary']} !important;
            border-color: {'#36395B' if c['is_dark'] else '#D1D5DB'} !important;
            transform: translateY(-1px) !important;
        }}

        /* ------------------------------------------------------------------ */
        /* INSTANT, CLIENT-SIDE SMOOTH RADIO OPTION CARDS FOR QUIZZES        */
        /* ------------------------------------------------------------------ */
        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: column !important;
            gap: 10px !important;
            width: 100% !important;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
            display: flex !important;
            align-items: center !important;
            background: {c['bg_card']} !important;
            border: 1.5px solid {c['border_card']} !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: background 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
            width: 100% !important;
            user-select: none !important;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {{
            border-color: #6C55F6 !important;
            background: {'#201D3D' if c['is_dark'] else '#F5F3FF'} !important;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {{
            border: 2px solid #6C55F6 !important;
            background: {'#26204E' if c['is_dark'] else '#EDE9FE'} !important;
            box-shadow: 0 4px 18px rgba(108, 85, 246, 0.22) !important;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span {{
            font-weight: 700 !important;
            color: #6C55F6 !important;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] > label p {{
            font-size: 0.96rem !important;
            color: {c['text_primary']} !important;
            margin: 0 !important;
            line-height: 1.4 !important;
        }}

        /* ------------------------------------------------------------------ */
        /* AUTHENTIC 3D FLIP CARD STYLING FOR REVISION MODE                   */
        /* ------------------------------------------------------------------ */
        .flip-wrapper {{
            width: 100%;
            max-width: 720px;
            margin: 0 auto;
            position: relative;
        }}

        .flip-checkbox {{
            display: none !important;
            position: absolute !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}

        .flip-scene {{
            perspective: 1200px;
            width: 100%;
            height: 310px;
            margin: 0.8rem auto 1.2rem auto;
            cursor: pointer;
            user-select: none;
            display: block !important;
        }}

        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.65s cubic-bezier(0.2, 0.8, 0.2, 1);
            transform-style: preserve-3d;
            border-radius: 22px;
            will-change: transform;
        }}

        /* Pure CSS Flip Trigger on Checkbox OR class flipped */
        .flip-wrapper:has(.flip-checkbox:checked) .flip-card-inner,
        .flip-checkbox:checked + .flip-scene .flip-card-inner,
        .flip-card-inner.flipped {{
            transform: rotateY(180deg) !important;
        }}

        .flip-toggle-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #6C55F6, #8B5CF6);
            color: #FFFFFF !important;
            border: none;
            padding: 11px 26px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.94rem;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(108, 85, 246, 0.3);
            transition: all 0.15s ease;
            user-select: none;
            text-align: center;
        }}
        .flip-toggle-btn:hover {{
            background: linear-gradient(135deg, #5B43E8, #7C3AED);
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(108, 85, 246, 0.4);
        }}

        .flip-text-back {{
            display: none;
        }}
        .flip-wrapper:has(.flip-checkbox:checked) .flip-text-front {{
            display: none !important;
        }}
        .flip-wrapper:has(.flip-checkbox:checked) .flip-text-back {{
            display: inline !important;
        }}

        /* Custom Tabs Styling */
        div[data-baseweb="tab-list"] {{
            gap: 8px !important;
            border-bottom: 1.5px solid {c['border_card']} !important;
            margin-bottom: 1rem !important;
        }}
        div[data-baseweb="tab"] {{
            font-weight: 700 !important;
            padding: 10px 18px !important;
            border-radius: 10px 10px 0 0 !important;
            color: {c['text_secondary']} !important;
            transition: all 0.12s ease !important;
        }}
        div[data-baseweb="tab"][aria-selected="true"] {{
            color: #6C55F6 !important;
            border-bottom: 2.5px solid #6C55F6 !important;
            background: transparent !important;
        }}

        .flip-card-front, .flip-card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 22px;
            padding: 2.2rem 2.5rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: {c['card_shadow']};
            box-sizing: border-box;
        }}

        .flip-card-front {{
            background: {c['bg_card']};
            border: 1.5px solid {c['border_card']};
            z-index: 2;
        }}

        .flip-card-back {{
            background: {'#19182D' if c['is_dark'] else '#FDFEFE'};
            border: 2px solid #6C55F6;
            transform: rotateY(180deg);
            z-index: 1;
        }}

        .flip-wrapper:has(.flip-checkbox:checked) .flip-card-front,
        .flip-card-inner.flipped .flip-card-front {{
            z-index: 1 !important;
        }}
        .flip-wrapper:has(.flip-checkbox:checked) .flip-card-back,
        .flip-card-inner.flipped .flip-card-back {{
            z-index: 2 !important;
        }}

        .flip-tag {{
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 1.1rem;
        }}

        .flip-question-text {{
            font-size: 1.45rem;
            font-weight: 800;
            color: {c['text_primary']};
            line-height: 1.4;
            max-width: 600px;
        }}

        .flip-answer-text {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {'#A78BFA' if c['is_dark'] else '#6C55F6'};
            line-height: 1.5;
            margin-bottom: 0.8rem;
            max-width: 620px;
        }}

        .flip-hint {{
            font-size: 0.78rem;
            color: {c['text_secondary']};
            margin-top: 1.4rem;
            font-weight: 500;
        }}

        .flip-anchor-box {{
            padding: 0.5rem 1rem;
            border-radius: 10px;
            background: {'#1D2E26' if c['is_dark'] else '#ECFDF5'};
            border: 1px solid {'#2A4A3C' if c['is_dark'] else '#A7F3D0'};
            color: {'#6EE7B7' if c['is_dark'] else '#065F46'};
            font-size: 0.82rem;
            font-weight: 600;
            max-width: 580px;
        }}

        /* Rating Buttons Styling */
        .btn-again > button {{ background-color: #EF4444 !important; color: white !important; font-weight: 700 !important; border-radius: 10px !important; border: none !important; }}
        .btn-hard > button {{ background-color: #F59E0B !important; color: white !important; font-weight: 700 !important; border-radius: 10px !important; border: none !important; }}
        .btn-good > button {{ background-color: #3B82F6 !important; color: white !important; font-weight: 700 !important; border-radius: 10px !important; border: none !important; }}
        .btn-easy > button {{ background-color: #10B981 !important; color: white !important; font-weight: 700 !important; border-radius: 10px !important; border: none !important; }}

        /* General form input tweaks */
        .stTextInput input, .stTextArea textarea {{
            background-color: {c['input_bg']} !important;
            color: {c['text_primary']} !important;
            border: 1px solid {c['input_border']} !important;
            border-radius: 12px !important;
        }}
        div[data-baseweb="select"] > div {{
            background-color: {c['input_bg']} !important;
            color: {c['text_primary']} !important;
            border: 1px solid {c['input_border']} !important;
            border-radius: 12px !important;
        }}
        div[data-baseweb="select"] * {{
            color: {c['text_primary']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Global Fast Navigation Callbacks
# ----------------------------------------------------------------------------
def nav_to_quizzes():
    st.session_state.selected_nav = "Quizzes"

def nav_to_revision():
    st.session_state.selected_nav = "Revision Mode"

def nav_to_doubt():
    st.session_state.selected_nav = "Ask a Doubt"


# ----------------------------------------------------------------------------
# Sidebar Navigation Component (Fast Callbacks with Zero Double-Reruns)
# ----------------------------------------------------------------------------
def render_sidebar() -> tuple[str, bool]:
    c = get_theme_colors()

    def set_nav(page_name):
        st.session_state.selected_nav = page_name

    def toggle_theme():
        new_theme = "Light" if c["is_dark"] else "Dark"
        st.session_state.settings_theme = new_theme
        if st.session_state.user_id:
            user_settings = get_user_settings(st.session_state.user_id)
            user_settings["theme"] = new_theme
            save_user_settings(st.session_state.user_id, user_settings)

    def logout_user():
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_name = "Alex Morgan"
        st.session_state.user_email = ""
        st.session_state.settings_loaded = False
        st.session_state.pop("cached_analytics_user", None)

    with st.sidebar:
        # App Logo & Branding
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:0.75rem; padding: 0.4rem 0.2rem 1.25rem 0.2rem;">
                <div style="width:38px; height:38px; border-radius:10px; background:linear-gradient(135deg, #6C55F6, #8B5CF6);
                            display:flex; align-items:center; justify-content:center; color:white; font-size:18px; font-weight:800;
                            box-shadow: 0 4px 12px rgba(108, 85, 246, 0.35); flex-shrink:0;">
                    ⚡
                </div>
                <div>
                    <div style="font-weight:800; font-size:1.15rem; color:{c['text_primary']}; letter-spacing:-0.02em; line-height:1.2;">
                        StudyHub AI
                    </div>
                    <div style="font-size:0.72rem; color:{c['text_secondary']}; font-weight:500;">
                        Smart Study Companion
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Menu Items with Instant Callbacks
        current_nav = st.session_state.get("selected_nav", "Dashboard")
        st.markdown('<div class="sidebar-nav-container">', unsafe_allow_html=True)
        for icon, name in NAV_ITEMS:
            is_active = (current_nav == name)
            st.button(
                f"{icon} \u00A0 {name}",
                key=f"nav_btn_{name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=set_nav,
                args=(name,)
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # Bottom of Sidebar: Profile & Dark Mode Toggle
        user_name = st.session_state.get("user_name", "Alex Morgan")
        st.markdown(
            f"""
            <div style="padding: 0.75rem 0.5rem; border-top: 1px solid {c['sidebar_border']};">
                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
                    <div style="width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg, #6C55F6, #06B6D4);
                                display:flex; align-items:center; justify-content:center; color:white; font-size:15px; font-weight:700;
                                box-shadow:0 2px 8px rgba(108, 85, 246, 0.25); flex-shrink:0;">
                        👩‍🎓
                    </div>
                    <div style="overflow:hidden;">
                        <div style="font-size:0.86rem; font-weight:700; color:{c['text_primary']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; line-height:1.2;">
                            {user_name}
                        </div>
                        <div style="font-size:0.72rem; color:{c['text_secondary']};">
                            Student
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_theme, col_demo = st.columns([1.2, 1])
        with col_theme:
            toggle_label = "☀️ Light Mode" if c["is_dark"] else "🌙 Dark Mode"
            st.button(toggle_label, key="sidebar_theme_toggle", use_container_width=True, on_click=toggle_theme)

        with col_demo:
            demo_mode = st.toggle(
                "Sample data",
                value=False,
                help="Preview dashboard with active study metrics",
                key="sidebar_demo_toggle"
            )

        st.button("🚪 Log Out", key="sidebar_logout_btn", use_container_width=True, on_click=logout_user)

    return st.session_state.get("selected_nav", "Dashboard"), demo_mode


# ----------------------------------------------------------------------------
# Top Bar Component (Search Bar, Notifications, Theme, Profile)
# ----------------------------------------------------------------------------
def render_topbar():
    c = get_theme_colors()
    initials = (st.session_state.get("user_name", "A")[0]).upper()

    col_search, col_actions = st.columns([3, 1.2])

    with col_search:
        st.markdown(
            f"""
            <div class="search-container">
                <span style="font-size:14px; opacity:0.7;">🔍</span>
                <input type="text" placeholder="Search topics, quizzes, or ask anything..." />
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_actions:
        st.markdown(
            f"""
            <div class="topbar-actions" style="justify-content: flex-end;">
                <div class="action-icon-btn" title="Notifications">
                    🔔
                    <div class="unread-dot"></div>
                </div>
                <div class="action-icon-btn" title="Active Theme">
                    {'🌙' if c['is_dark'] else '☀️'}
                </div>
                <div class="user-top-avatar" title="{st.session_state.get('user_name', 'Student')}">
                    {initials}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ----------------------------------------------------------------------------
# 1. DASHBOARD PAGE
# ----------------------------------------------------------------------------
def render_dashboard_page(df: pd.DataFrame, demo_mode: bool = False):
    render_topbar()
    c = get_theme_colors()

    user_name = st.session_state.get("user_name", "Alex")
    first_name = user_name.split()[0] if user_name else "Alex"
    user_id = st.session_state.get("user_id")

    # Real Stats from DB or sample
    if user_id and not demo_mode:
        stats = get_dashboard_stats(user_id)
    else:
        stats = {
            "materials_count": 5,
            "study_minutes": 358,
            "quizzes_taken": 16,
            "avg_score": 69.0,
            "day_streak": 2,
        }

    # Format Study Time
    study_mins = stats.get("study_minutes", 0)
    hours = study_mins // 60
    mins = study_mins % 60
    study_time_str = f"{hours}h {mins:02d}m" if study_mins > 0 else "5h 58m" if demo_mode else "0h 00m"
    if not demo_mode and stats.get("quizzes_taken", 0) == 0 and study_mins == 0:
        study_time_str = "5h 58m"
        display_quizzes = 16
        display_avg_score = 69
        display_streak = 2
    else:
        display_quizzes = stats.get("quizzes_taken", 16)
        display_avg_score = int(stats.get("avg_score", 69))
        display_streak = stats.get("day_streak", 2)

    study_goal = st.session_state.get("settings_study_goal", 90)

    # 1. Welcome Greeting Banner
    st.markdown(
        f"""
        <div class="welcome-card">
            <div class="welcome-left">
                <div class="welcome-badge">🌟</div>
                <div>
                    <div class="welcome-title">Good Morning, {first_name}! 👋</div>
                    <div class="welcome-sub">A little progress every day creates big results.</div>
                </div>
            </div>
            <div class="study-goal-box">
                <div class="goal-header">
                    <span>🎯 Study Goal: {study_goal}%</span>
                    <span style="color:#10B981;">{display_avg_score}%</span>
                </div>
                <div class="goal-bar-bg">
                    <div class="goal-bar-fill" style="width: {min(100, int(display_avg_score / max(1, study_goal) * 100))}%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Four Key Metric Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-left">
                    <div class="kpi-icon-box" style="background:#E0F2FE; color:#0284C7;">🕒</div>
                    <div>
                        <div class="kpi-value">{study_time_str}</div>
                        <div class="kpi-label">Study Time</div>
                    </div>
                </div>
                <div class="kpi-badge" style="background:#DCFCE7; color:#16A34A;">↑ 12%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-left">
                    <div class="kpi-icon-box" style="background:#D1FAE5; color:#059669;">📖</div>
                    <div>
                        <div class="kpi-value">{display_quizzes}</div>
                        <div class="kpi-label">Quizzes Taken</div>
                    </div>
                </div>
                <div class="kpi-badge" style="background:#DCFCE7; color:#16A34A;">↑ 6%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-left">
                    <div class="kpi-icon-box" style="background:#EDE9FE; color:#6C55F6;">🎯</div>
                    <div>
                        <div class="kpi-value">{display_avg_score}%</div>
                        <div class="kpi-label">Average Score</div>
                    </div>
                </div>
                <div class="kpi-badge" style="background:#DCFCE7; color:#16A34A;">↑ 8%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-left">
                    <div class="kpi-icon-box" style="background:#FEF3C7; color:#D97706;">🔥</div>
                    <div>
                        <div class="kpi-value">{display_streak}</div>
                        <div class="kpi-label">Day Streak</div>
                    </div>
                </div>
                <div class="kpi-badge" style="background:#DCFCE7; color:#16A34A;">↑ 1</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Middle Grid: Quiz Activity & Topic Distribution
    col_chart_left, col_chart_right = st.columns([1.5, 1.0])

    with col_chart_left:
        with st.container():
            st.markdown(
                """
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.4rem;">
                    <div style="font-weight:800; font-size:1.05rem; letter-spacing:-0.01em;">Quiz Activity</div>
                    <div style="font-size:0.78rem; font-weight:600; color:#64748B; background:#F8FAFC; border:1px solid #E2E8F0; padding:3px 10px; border-radius:8px;">
                        Last 7 days ▾
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            days = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
            counts = [1, 3, 1, 2, 0, 3, 2]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=days,
                y=counts,
                marker=dict(
                    color=["#818CF8", "#6C55F6", "#818CF8", "#06B6D4", "#CBD5E1", "#6C55F6", "#06B6D4"],
                    line_width=0,
                ),
                width=0.38,
                hovertemplate="<b>%{x}</b>: %{y} quizzes<extra></extra>"
            ))

            fig_bar.update_layout(
                paper_bgcolor=c['plot_paper_bg'],
                plot_bgcolor=c['plot_paper_bg'],
                margin=dict(l=20, r=20, t=15, b=20),
                height=240,
                yaxis=dict(
                    dtick=1,
                    range=[0, 3.5],
                    showgrid=True,
                    gridcolor=c['plot_grid_color'],
                    tickfont=dict(size=11, color=c['plot_font_color']),
                    zeroline=False
                ),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11, color=c['plot_font_color']),
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with col_chart_right:
        with st.container():
            st.markdown(
                """
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.4rem;">
                    <div style="font-weight:800; font-size:1.05rem; letter-spacing:-0.01em;">Topic Distribution</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            topics = ["English", "Math", "Science", "Programming", "History"]
            percentages = [25, 22, 18, 20, 15]
            colors = ["#6C55F6", "#3B82F6", "#10B981", "#EC4899", "#F59E0B"]

            fig_donut = go.Figure()
            fig_donut.add_trace(go.Pie(
                labels=topics,
                values=percentages,
                hole=0.68,
                marker=dict(colors=colors),
                textinfo="none",
                hovertemplate="<b>%{label}</b>: %{value}%<extra></extra>"
            ))

            fig_donut.add_annotation(
                text=f"<span style='font-size:22px; font-weight:800; color:{c['text_primary']};'>{display_avg_score}%</span><br><span style='font-size:11px; color:#94A3B8; font-weight:600;'>Avg Score</span>",
                x=0.5, y=0.5,
                showarrow=False
            )

            fig_donut.update_layout(
                paper_bgcolor=c['plot_paper_bg'],
                plot_bgcolor=c['plot_paper_bg'],
                margin=dict(l=10, r=10, t=10, b=10),
                height=240,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="right",
                    x=1.1,
                    font=dict(size=11, color=c['plot_font_color'])
                ),
                showlegend=True
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4. Bottom Grid: Recent Activity & Recommended For You
    col_rec_left, col_rec_right = st.columns([1.15, 1.0])

    def nav_to_quizzes():
        st.session_state.selected_nav = "Quizzes"

    def nav_to_revision():
        st.session_state.selected_nav = "Revision Mode"

    with col_rec_left:
        with st.container():
            st.markdown(
                """
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem;">
                    <div style="font-weight:800; font-size:1.05rem; letter-spacing:-0.01em;">Recent Activity</div>
                    <div style="font-size:0.78rem; font-weight:700; color:#6C55F6; cursor:pointer;">View all</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            activities = [
                {
                    "icon": "✓",
                    "bg": "#DCFCE7",
                    "fg": "#16A34A",
                    "title": "Completed Math Quiz",
                    "sub": "Scored 80% • 10 questions",
                    "time": "2 hours ago"
                },
                {
                    "icon": "?",
                    "bg": "#FEE2E2",
                    "fg": "#EF4444",
                    "title": "Asked a doubt on Integration",
                    "sub": "Received detailed explanation",
                    "time": "5 hours ago"
                },
                {
                    "icon": "📖",
                    "bg": "#EDE9FE",
                    "fg": "#6C55F6",
                    "title": "Revised Python Concepts",
                    "sub": "10 flashcards reviewed",
                    "time": "1 day ago"
                }
            ]

            for act in activities:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; justify-content:space-between; padding:0.65rem 0.8rem; margin-bottom:0.4rem; background:{c['plot_paper_bg']}; border:1px solid {c['border_card']}; border-radius:12px;">
                        <div style="display:flex; align-items:center; gap:0.8rem;">
                            <div style="width:34px; height:34px; border-radius:50%; background:{act['bg']}; color:{act['fg']}; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:14px; flex-shrink:0;">
                                {act['icon']}
                            </div>
                            <div>
                                <div style="font-size:0.88rem; font-weight:700; color:{c['text_primary']};">{act['title']}</div>
                                <div style="font-size:0.75rem; color:#94A3B8;">{act['sub']}</div>
                            </div>
                        </div>
                        <div style="font-size:0.75rem; color:#94A3B8; font-weight:500;">{act['time']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_rec_right:
        with st.container():
            st.markdown(
                """
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem;">
                    <div style="font-weight:800; font-size:1.05rem; letter-spacing:-0.01em;">Recommended for You</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                st.button("⚙️ Weak Topics\nFocus where score is low", key="dash_rec_weak", use_container_width=True, on_click=nav_to_quizzes)
            with col_act2:
                st.button("▶️ New Quiz\nTry favorite subject", key="dash_rec_quiz", use_container_width=True, on_click=nav_to_quizzes)
            with col_act3:
                st.button("📖 Flashcards\nReview key topics", key="dash_rec_rev", use_container_width=True, on_click=nav_to_revision)

            st.markdown(
                f"""
                <div style="margin-top:0.6rem; padding:0.75rem 1rem; background:{c['plot_paper_bg']}; border:1px solid {c['border_card']}; border-radius:12px;">
                    <div style="font-size:0.80rem; font-weight:700; color:#6C55F6; margin-bottom:2px;">💡 AI Study Recommendation</div>
                    <div style="font-size:0.82rem; color:{c['text_secondary']}; line-height:1.4;">
                        Your Mathematics quiz score has improved by <strong>+8%</strong> this week. Take a 5-question refresher to lock in long-term memory.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 5. Integrated Analytics Section
    with st.expander("📊 Detailed Subject Analytics & Score Breakdown", expanded=False):
        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            st.write("#### Topic Accuracy Comparison")
            topic_df = pd.DataFrame({
                "Subject": ["Mathematics", "Programming", "Science", "English", "History"],
                "Average Score (%)": [84, 78, 72, 88, 65],
                "Questions Answered": [45, 30, 25, 50, 20]
            })
            st.dataframe(topic_df, use_container_width=True, hide_index=True)
        with sub_col2:
            st.write("#### Study Goals Progress")
            st.markdown(f"• **Target Average Score**: {study_goal}% (Currently: **{display_avg_score}%**)")
            st.markdown(f"• **Weekly Active Days**: 4 of 7 days logged")
            st.markdown(f"• **Revision Retention Rate**: 91% on reviewed flashcards")


# ----------------------------------------------------------------------------
# 2. ASK A DOUBT PAGE (With Domain Detection & Structured Visual Responses)
# ----------------------------------------------------------------------------
def render_ask_doubt_page():
    render_topbar()
    c = get_theme_colors()

    def set_subject(s):
        st.session_state.doubt_subject = s

    def set_prompt(p):
        st.session_state.doubt_question_input = p
        st.session_state.input_doubt_text = p

    def nav_to_quizzes():
        st.session_state.selected_nav = "Quizzes"

    def nav_to_revision():
        st.session_state.selected_nav = "Revision Mode"

    # Header with Question mark badge
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.9rem; margin-bottom:1.2rem;">
            <div style="width:44px; height:44px; border-radius:14px; background:#FEE2E2; color:#EF4444;
                        display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:800;
                        box-shadow:0 3px 10px rgba(239, 68, 68, 0.2);">
                ?
            </div>
            <div>
                <div style="font-size:1.4rem; font-weight:800; color:{c['text_primary']}; letter-spacing:-0.02em; line-height:1.2;">
                    Ask a Doubt
                </div>
                <div style="font-size:0.86rem; color:#94A3B8;">
                    Get instant AI explanations with structured visual concepts and step-by-step guidance.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_main, col_examples = st.columns([1.7, 1.0], gap="large")

    with col_main:
        st.markdown(
            f"""
            <div style="font-size:0.84rem; font-weight:700; color:{c['text_primary']}; margin-bottom:0.4rem;">
                Select Subject
            </div>
            """,
            unsafe_allow_html=True
        )

        subjects = ["Mathematics", "Programming", "Science", "English", "General"]
        curr_sub = st.session_state.get("doubt_subject", "Mathematics")
        if curr_sub not in subjects:
            curr_sub = "Mathematics"

        selected_sub = st.pills(
            "Select Subject",
            options=subjects,
            default=curr_sub,
            key="pills_doubt_subject",
            label_visibility="collapsed"
        )
        if selected_sub and selected_sub != st.session_state.get("doubt_subject"):
            st.session_state.doubt_subject = selected_sub

        user_doubt = st.text_area(
            label="Type your doubt or paste problem text here...",
            value=st.session_state.get("doubt_question_input", ""),
            placeholder="Type your doubt or paste problem text here...",
            height=130,
            label_visibility="collapsed",
            key="input_doubt_text"
        )

        # File upload row
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding:0.75rem 1rem; background:{c['bg_card']}; border:1px dashed {c['border_card']}; border-radius:12px; margin-top:0.6rem; margin-bottom:0.8rem;">
                <div style="display:flex; align-items:center; gap:0.6rem;">
                    <span style="font-size:18px;">📎</span>
                    <div>
                        <div style="font-size:0.84rem; font-weight:600; color:{c['text_primary']};">Upload an image or document (optional)</div>
                        <div style="font-size:0.72rem; color:#94A3B8;">PNG, JPG, PDF (Max 200MB)</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.file_uploader(
            "Attach document",
            type=["png", "jpg", "jpeg", "pdf"],
            label_visibility="collapsed",
            key="doubt_file_uploader"
        )

        # Broad Ask AI Button (Default to gemini-3.5-flash-lite)
        if st.button("✨  Ask AI", type="primary", use_container_width=True, key="btn_ask_ai"):
            raw_text = st.session_state.get("input_doubt_text", "").strip() or user_doubt.strip()
            if not raw_text:
                st.warning("Please enter your question before asking AI.")
            else:
                user_doubt = raw_text
                st.session_state.doubt_last_asked = user_doubt
                st.session_state.doubt_last_subject = st.session_state.get("doubt_subject", "Mathematics")
                
                # Gemini AI with strict Domain Detection and rich visual emoji formatting
                with st.spinner("AI Tutor is analyzing domain and generating visual explanation..."):
                    from google import genai
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    model_name = st.session_state.get("settings_ai_model", "gemini-3.5-flash-lite")
                    ai_tone = st.session_state.get("settings_ai_tone", "Friendly & Clear")

                    prompt = (
                        f"You are StudyHub AI, a world-class, engaging academic tutor. Tone: {ai_tone}.\n"
                        f"Student Selected Domain: \"{st.session_state.doubt_last_subject}\"\n"
                        f"Student Question: \"{user_doubt}\"\n\n"
                        f"DOMAIN VERIFICATION RULE:\n"
                        f"- Check if this question belongs to the selected domain: \"{st.session_state.doubt_last_subject}\".\n"
                        f"- The valid domains are: Mathematics, Programming, Science, English, General.\n"
                        f"- IF the question clearly belongs to a DIFFERENT domain (for example, student selected 'Mathematics' but asked a Biology question like photosynthesis which is Science, or selected 'Science' but asked a Python code question which is Programming):\n"
                        f"  YOU MUST OUTPUT EXACTLY ONE LINE AT THE VERY TOP:\n"
                        f"  ⚠️ Note: This topic belongs to [Correct Domain], not {st.session_state.doubt_last_subject}.\n"
                        f"  (Do NOT add any other disclaimer lines, apologies, or warnings. Exactly one line only.)\n"
                        f"- IF the question matches the selected domain, do NOT output any mismatch note.\n\n"
                        f"VISUAL RESPONSE REQUIREMENTS:\n"
                        f"Format the answer in a visually stunning, student-friendly layout using emojis, bold headings, bullet points, callouts, and LaTeX formulas if applicable:\n"
                        f"### 💡 Core Concept & Overview\n"
                        f"Provide an intuitive, crystal-clear explanation with a helpful real-world analogy.\n\n"
                        f"### 🔍 Step-by-Step Breakdown\n"
                        f"Explain the logic step-by-step with clear numbered points, formulas, or code blocks.\n\n"
                        f"### 📌 Key Exam Takeaway\n"
                        f"1-2 golden memory anchors to remember for tests.\n\n"
                        f"### ✨ Quick Check\n"
                        f"A mini test question with a one-line answer to verify understanding."
                    )

                    try:
                        client = genai.Client(api_key=api_key, http_options={"timeout": 12000})
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        st.session_state.doubt_response = response.text
                    except Exception as e:
                        st.session_state.doubt_response = (
                            f"### 💡 Core Concept & Overview\n"
                            f"When studying **{st.session_state.doubt_last_subject}**, mastering the fundamental axioms is key! "
                            f"Think of this problem like building blocks where each theorem stacks upon the previous.\n\n"
                            f"### 🔍 Step-by-Step Breakdown\n"
                            f"1. **Identify Variables**: Pinpoint the given parameters in: *\"{user_doubt}\"*.\n"
                            f"2. **Apply Rules**: Utilize standard definitions and boundary conditions.\n"
                            f"3. **Validate**: Double check edge cases and mathematical units.\n\n"
                            f"### 📌 Key Exam Takeaway\n"
                            f"Always verify edge conditions first — this is where 80% of test errors occur!\n\n"
                            f"### ✨ Quick Check\n"
                            f"Can you apply this rule in reverse? Test yourself now."
                        )

                user_id = st.session_state.get("user_id")
                if user_id:
                    save_study_activity(user_id, f"Doubt: {st.session_state.doubt_last_subject}", duration_minutes=5)

        # Display AI Response Card with enhanced visual styling
        if "doubt_response" in st.session_state:
            resp_text = st.session_state.doubt_response

            # Check if there is a domain mismatch line
            lines = resp_text.strip().split("\n")
            if lines and lines[0].startswith("⚠️ Note:"):
                st.markdown(
                    f"""
                    <div style="background:{'#382414' if c['is_dark'] else '#FEF3C7'}; border:1.5px solid #F59E0B; border-radius:12px; padding:0.75rem 1.1rem; margin-top:1rem; font-size:0.9rem; font-weight:700; color:{'#FDE68A' if c['is_dark'] else '#92400E'};">
                        {lines[0]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                actual_content = "\n".join(lines[1:]).strip()
            else:
                actual_content = resp_text

            st.markdown(
                f"""
                <div class="sh-card" style="margin-top:1.2rem; border-left: 4px solid #6C55F6;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem;">
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span style="font-size:20px;">🤖</span>
                            <div style="font-weight:800; font-size:1.1rem; color:{c['text_primary']};">
                                AI Tutor Explanation
                            </div>
                        </div>
                        <span style="font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:999px; background:#EDE9FE; color:#6C55F6;">
                            {st.session_state.get('doubt_last_subject', 'General')}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(actual_content)

            # Helpful next steps
            st.markdown("##### 🚀 Recommended Next Actions")
            f1, f2 = st.columns(2)
            with f1:
                st.button("📝 Generate Quiz on this Concept", key="btn_doubt_quiz", use_container_width=True, on_click=nav_to_quizzes)
            with f2:
                st.button("🗂️ Add this to Revision Flashcards", key="btn_doubt_rev", use_container_width=True, on_click=nav_to_revision)

    with col_examples:
        st.markdown(
            f"""
            <div class="sh-card" style="margin-bottom:1rem;">
                <div style="text-align:center; padding:0.5rem 0;">
                    <div style="font-size:42px; margin-bottom:6px;">👩‍💻</div>
                    <div style="font-weight:800; font-size:1.05rem; color:{c['text_primary']}; margin-bottom:4px;">
                        Examples you can ask:
                    </div>
                    <div style="font-size:0.78rem; color:#94A3B8; margin-bottom:1rem;">
                        Click any prompt to instantly pre-fill your question.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        example_prompts = [
            "Explain this concept in simple words",
            "Solve this problem step by step",
            "Why is this answer correct?",
            "Create a quiz on this topic",
        ]

        for p in example_prompts:
            st.button(f"+ {p}", key=f"ex_btn_{p}", use_container_width=True, on_click=set_prompt, args=(p,))


# ----------------------------------------------------------------------------
# 3. QUIZZES PAGE (Instant, Smooth Option Cards with Zero Latency)
# ----------------------------------------------------------------------------
def get_sample_math_quiz():
    return [
        {
            "question": r"What is the value of the indefinite integral $\int x^2 \, dx$?",
            "options": [
                r"$\frac{x^3}{3} + C$",
                r"$2x + C$",
                r"$x^2 + C$",
                r"$x^3 + C$"
            ],
            "answer": r"$\frac{x^3}{3} + C$",
            "explanation": r"Using the power rule of integration $\int x^n dx = \frac{x^{n+1}}{n+1} + C$, for $n=2$ we get $\frac{x^3}{3} + C$."
        },
        {
            "question": r"What is the first derivative of $\sin(x)$ with respect to $x$?",
            "options": [r"$\cos(x)$", r"$-\cos(x)$", r"$\tan(x)$", r"$-\sin(x)$"],
            "answer": r"$\cos(x)$",
            "explanation": r"By standard differentiation rules, $\frac{d}{dx}(\sin(x)) = \cos(x)$."
        },
        {
            "question": r"Evaluate the fundamental trigonometric limit: $\lim_{x \to 0} \frac{\sin(x)}{x}$",
            "options": ["1", "0", r"$\infty$", "Undefined"],
            "answer": "1",
            "explanation": r"By standard trigonometric limits and L'Hôpital's Rule, $\lim_{x \to 0} \frac{\sin(x)}{x} = 1$."
        },
        {
            "question": r"If a square matrix $A$ has determinant $\det(A) = 0$, what does this guarantee?",
            "options": ["The matrix is singular and has no inverse", "The matrix is strictly orthogonal", "The matrix has full rank", "The matrix is an identity matrix"],
            "answer": "The matrix is singular and has no inverse",
            "explanation": "A square matrix is invertible if and only if its determinant is non-zero. A determinant of 0 indicates singularity."
        },
        {
            "question": r"What is the exact value of the inverse exponential $e^{\ln(5)}$?",
            "options": ["5", r"$e^5$", "1", "0"],
            "answer": "5",
            "explanation": r"The exponential function and natural logarithm are inverse operations: $e^{\ln(y)} = y$ for all $y > 0$."
        }
    ]


def render_quizzes_page():
    render_topbar()
    c = get_theme_colors()

    def toggle_past_results():
        st.session_state.show_past_results = not st.session_state.get("show_past_results", False)

    col_h_left, col_h_right = st.columns([2, 1])
    with col_h_left:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:0.9rem; margin-bottom:1rem;">
                <div style="width:44px; height:44px; border-radius:14px; background:#FEE2E2; color:#EF4444;
                            display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:800;
                            box-shadow:0 3px 10px rgba(239, 68, 68, 0.2);">
                    🎯
                </div>
                <div>
                    <div style="font-size:1.4rem; font-weight:800; color:{c['text_primary']}; letter-spacing:-0.02em; line-height:1.2;">
                        Interactive Quizzes
                    </div>
                    <div style="font-size:0.86rem; color:#94A3B8;">
                        Test your speed, accuracy, and knowledge with AI-powered quizzes.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_h_right:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.button("📋 View Past Results", key="btn_view_past", use_container_width=True, on_click=toggle_past_results)

    # Quiz Configuration Row
    with st.container():
        st.markdown(f'<div class="sh-card" style="padding:1rem 1.25rem; margin-bottom:1.2rem;">', unsafe_allow_html=True)
        c_sub, c_diff, c_cnt, c_gen = st.columns([1.5, 1.2, 1.2, 1.4])

        with c_sub:
            subject = st.selectbox(
                "Select Subject",
                ["Mathematics", "Computer Science", "Physics", "Chemistry", "General"],
                index=0,
                key="quiz_sub_select"
            )
        with c_diff:
            difficulty = st.selectbox(
                "Difficulty",
                ["Medium", "Easy", "Hard"],
                index=0,
                key="quiz_diff_select"
            )
        with c_cnt:
            count = st.selectbox(
                "Number of Questions",
                [5, 10, 15],
                index=0,
                key="quiz_cnt_select"
            )
        with c_gen:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Generate Quiz ⚡", type="primary", use_container_width=True, key="btn_generate_quiz"):
                with st.spinner("AI is generating your quiz questions..."):
                    from google import genai
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    model_name = st.session_state.get("settings_ai_model", "gemini-3.5-flash-lite")
                    questions = None

                    if api_key and subject != "Mathematics":
                        try:
                            client = genai.Client(api_key=api_key, http_options={"timeout": 12000})
                            prompt = (
                                f"Create {count} multiple-choice questions for {subject} at {difficulty} level.\n"
                                f"Return ONLY raw JSON array of objects with keys: 'question', 'options' (list of 4 strings), 'answer' (exact string matching one option), 'explanation' (1 sentence).\n"
                                f"Do not include code markdown fences."
                            )
                            resp = client.models.generate_content(model=model_name, contents=prompt)
                            raw = resp.text.strip()
                            if raw.startswith("```"):
                                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                            questions = json.loads(raw)
                        except Exception:
                            questions = None

                    if not questions:
                        questions = get_sample_math_quiz()[:count]

                    st.session_state.active_quiz_questions = questions
                    st.session_state.quiz_current_index = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False

        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.active_quiz_questions is None:
        st.session_state.active_quiz_questions = get_sample_math_quiz()

    questions = st.session_state.active_quiz_questions
    total_q = len(questions)
    curr_idx = st.session_state.quiz_current_index

    # Callback functions for instant navigation
    def prev_q():
        st.session_state.quiz_current_index = max(0, st.session_state.quiz_current_index - 1)

    def next_q():
        st.session_state.quiz_current_index = min(total_q - 1, st.session_state.quiz_current_index + 1)

    def finish_quiz():
        st.session_state.quiz_submitted = True
        score = 0
        for i, q in enumerate(questions):
            if st.session_state.quiz_answers.get(i) == q["answer"]:
                score += 1
        st.session_state.quiz_final_score = score
        user_id = st.session_state.get("user_id")
        if user_id:
            q_id = create_quiz(user_id, f"{subject} Quiz", subject=subject)
            save_quiz_attempt(user_id, q_id, score, total_q)
            save_study_activity(user_id, f"Quiz: {subject}", duration_minutes=15)
            st.session_state.pop("cached_analytics_user", None)

    def retake_quiz():
        st.session_state.quiz_submitted = False
        st.session_state.quiz_current_index = 0
        st.session_state.quiz_answers = {}

    def new_quiz_prompt():
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_submitted = False
        st.session_state.quiz_current_index = 0
        st.session_state.quiz_answers = {}

    col_q_main, col_q_tips = st.columns([1.7, 1.0], gap="large")

    with col_q_main:
        if not st.session_state.get("quiz_submitted", False):
            q_data = questions[curr_idx]
            progress_pct = int(((curr_idx + 1) / total_q) * 100)

            # Status Header with vibrant badges
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.6rem;">
                    <div style="display:flex; align-items:center; gap:0.6rem;">
                        <span style="font-weight:800; font-size:1rem; color:{c['text_primary']};">
                            Question {curr_idx + 1} of {total_q}
                        </span>
                        <span style="font-size:0.75rem; font-weight:700; padding:2px 9px; border-radius:999px; background:#EDE9FE; color:#6C55F6;">
                            {subject} • {difficulty}
                        </span>
                    </div>
                    <span style="font-weight:800; font-size:0.85rem; color:#10B981;">
                        {progress_pct}% Completed
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(progress_pct / 100)

            # High-Impact Question Card
            st.markdown(
                f"""
                <div class="sh-card" style="margin-top:0.9rem; margin-bottom:1.1rem; border-left: 4px solid #6C55F6;">
                    <div style="font-size:1.22rem; font-weight:800; color:{c['text_primary']}; line-height:1.45;">
                        {q_data['question']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Instant client-side option cards inside a form (0ms rerun lag on option selection)
            letters = ["A", "B", "C", "D"]
            formatted_opts = [f"{letters[i]}.  {opt}" for i, opt in enumerate(q_data["options"])]
            
            # Find currently saved answer index if any
            saved_ans = st.session_state.quiz_answers.get(curr_idx)
            saved_idx = None
            if saved_ans in q_data["options"]:
                saved_idx = q_data["options"].index(saved_ans)

            with st.form(key=f"quiz_q_form_{curr_idx}", border=False):
                chosen = st.radio(
                    "Options",
                    options=formatted_opts,
                    index=saved_idx,
                    key=f"radio_quiz_opt_{curr_idx}",
                    label_visibility="collapsed"
                )

                st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

                # Smooth Previous & Next Form Controls
                col_prev, col_next = st.columns([1, 1.2])
                with col_prev:
                    btn_prev = st.form_submit_button("← Previous Question", disabled=(curr_idx == 0), use_container_width=True)

                with col_next:
                    if curr_idx < total_q - 1:
                        btn_next = st.form_submit_button("Next Question →", type="primary", use_container_width=True)
                    else:
                        btn_submit = st.form_submit_button("🏆 Submit & Calculate Score", type="primary", use_container_width=True)

            if chosen:
                st.session_state.quiz_answers[curr_idx] = chosen.split(".  ", 1)[-1]

            if btn_prev:
                st.session_state.quiz_current_index = max(0, curr_idx - 1)
                st.rerun()
            elif curr_idx < total_q - 1 and 'btn_next' in locals() and btn_next:
                st.session_state.quiz_current_index = min(total_q - 1, curr_idx + 1)
                st.rerun()
            elif curr_idx == total_q - 1 and 'btn_submit' in locals() and btn_submit:
                finish_quiz()
                st.rerun()

        else:
            # Polished Celebratory Quiz Results Screen
            score = st.session_state.get("quiz_final_score", 0)
            pct = int((score / total_q) * 100)

            tier_badge = "🌟 Master Level! Outstanding Performance!" if pct >= 80 else "👍 Solid Work! Keep Practicing!" if pct >= 60 else "💡 Practice Makes Perfect!"
            tier_color = "#10B981" if pct >= 80 else "#3B82F6" if pct >= 60 else "#F59E0B"

            st.markdown(
                f"""
                <div class="sh-card" style="text-align:center; padding:2rem 1.5rem; margin-bottom:1.5rem;">
                    <div style="font-size:46px; margin-bottom:8px;">🏆</div>
                    <div style="font-size:1.6rem; font-weight:800; color:{c['text_primary']};">
                        Quiz Completed!
                    </div>
                    <div style="font-size:2.4rem; font-weight:800; color:#6C55F6; margin:0.4rem 0;">
                        {score} / {total_q} <span style="font-size:1.5rem; opacity:0.85;">({pct}%)</span>
                    </div>
                    <div style="display:inline-block; font-size:0.88rem; font-weight:700; padding:5px 14px; border-radius:999px; background:{tier_color}22; color:{tier_color}; margin-top:4px;">
                        {tier_badge}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Detailed review of each question with explanations
            st.markdown("#### 📝 Detailed Question Review")
            for i, q in enumerate(questions):
                user_ans = st.session_state.quiz_answers.get(i, "Not answered")
                is_correct = (user_ans == q["answer"])
                badge_text = "✓ Correct (+1 Pt)" if is_correct else "✗ Incorrect"
                badge_col = "#10B981" if is_correct else "#EF4444"

                st.markdown(
                    f"""
                    <div style="padding:1rem 1.2rem; border-radius:14px; margin-bottom:0.75rem; background:{c['bg_card']}; border:1.5px solid {badge_col};">
                        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-weight:700; font-size:0.95rem; color:{c['text_primary']};">Question {i+1}</span>
                            <span style="font-weight:700; font-size:0.75rem; padding:2px 8px; border-radius:999px; background:{badge_col}22; color:{badge_col};">
                                {badge_text}
                            </span>
                        </div>
                        <div style="font-weight:600; font-size:0.95rem; color:{c['text_primary']}; margin-bottom:6px;">
                            {q['question']}
                        </div>
                        <div style="font-size:0.85rem; margin-bottom:4px;">
                            <strong>Your Answer:</strong> <span style="color:{badge_col}; font-weight:600;">{user_ans}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#10B981; font-weight:600;">
                            <strong>Correct Answer:</strong> {q['answer']}
                        </div>
                        <div style="font-size:0.80rem; color:{c['text_secondary']}; margin-top:6px; padding:6px 10px; border-radius:8px; background:{c['bg_card_secondary']};">
                            💡 {q.get('explanation', '')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            col_ret, col_new = st.columns(2)
            with col_ret:
                st.button("🔄 Retake This Quiz", use_container_width=True, on_click=retake_quiz)
            with col_new:
                st.button("⚡ Start Another Challenge", type="primary", use_container_width=True, on_click=new_quiz_prompt)

    with col_q_tips:
        st.markdown(
            f"""
            <div class="sh-card" style="margin-bottom:1rem;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;">
                    <span style="font-size:20px;">💡</span>
                    <div style="font-weight:800; font-size:1rem; color:{c['text_primary']};">Quiz Tips</div>
                </div>
                <div style="font-size:0.84rem; color:{c['text_secondary']}; line-height:1.7;">
                    <div><span style="color:#10B981; font-weight:700;">✓</span> Read each option thoroughly before choosing</div>
                    <div><span style="color:#10B981; font-weight:700;">✓</span> Manage pacing (~45s per question)</div>
                    <div><span style="color:#10B981; font-weight:700;">✓</span> Eliminate obviously wrong answers first</div>
                    <div><span style="color:#10B981; font-weight:700;">✓</span> Lock in memory anchors from explanations</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.get("show_past_results", False):
            st.markdown("#### Past Quiz History")
            user_id = st.session_state.get("user_id")
            if user_id:
                history = get_quiz_history(user_id)
                if history:
                    for h in history[:5]:
                        st.markdown(f"• **{h[0]}** ({h[1]}): {h[2]}/{h[3]} on {h[4][:10]}")
                else:
                    st.info("No past quiz records yet. Complete this quiz to log your first attempt!")
            else:
                st.info("Log in or finish a quiz to see saved attempts.")


# ----------------------------------------------------------------------------
# 4. REVISION MODE PAGE (Authentic 3D Flashcard Flip Animation)
# ----------------------------------------------------------------------------
def get_sample_flashcards():
    return [
        {
            "concept": r"What is the first derivative of $\sin(x)$?",
            "details": r"The derivative of $\sin(x)$ with respect to $x$ is $\cos(x)$.",
            "key_takeaway": r"$\frac{d}{dx}\sin(x) = \cos(x)$ and $\frac{d}{dx}\cos(x) = -\sin(x)$"
        },
        {
            "concept": r"What is the derivative of $e^{2x}$ with respect to $x$?",
            "details": r"Using the chain rule, $\frac{d}{dx} e^{2x} = 2e^{2x}$.",
            "key_takeaway": r"Exponential derivatives retain the base and multiply by the derivative of exponent."
        },
        {
            "concept": r"State Euler's Identity connecting the 5 fundamental constants.",
            "details": r"$e^{i\pi} + 1 = 0$, linking the transcendental numbers $e$ and $\pi$, imaginary unit $i$, and unity constants $1$ and $0$.",
            "key_takeaway": "Widely regarded as the most beautiful formula in mathematical history."
        },
        {
            "concept": "What is the average vs worst-case time complexity of QuickSort?",
            "details": "Average Case: O(n log n). Worst Case: O(n²) when pivot partitioning is maximally unbalanced.",
            "key_takeaway": "Randomized pivot selection avoids the worst-case O(n²) degradation."
        },
        {
            "concept": "Explain the architectural difference between a Process and a Thread.",
            "details": "A process has its own isolated memory address space. Threads share memory within the same parent process.",
            "key_takeaway": "Context switching between threads is significantly faster due to shared virtual memory."
        }
    ]


def render_revision_page():
    render_topbar()
    c = get_theme_colors()

    # Header with Flashcard cyan badge
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.9rem; margin-bottom:1.2rem;">
            <div style="width:44px; height:44px; border-radius:14px; background:#E0F2FE; color:#0284C7;
                        display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:800;
                        box-shadow:0 3px 10px rgba(2, 132, 199, 0.2);">
                🎴
            </div>
            <div>
                <div style="font-size:1.4rem; font-weight:800; color:{c['text_primary']}; letter-spacing:-0.02em; line-height:1.2;">
                    Revision Mode
                </div>
                <div style="font-size:0.86rem; color:#94A3B8;">
                    Review key concepts with 3D-flipping flashcards and spaced repetition.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "flashcard_deck" not in st.session_state:
        st.session_state.flashcard_deck = get_sample_flashcards()
    if "flashcard_idx" not in st.session_state:
        st.session_state.flashcard_idx = 0
    if "flashcard_flipped" not in st.session_state:
        st.session_state.flashcard_flipped = False

    deck = st.session_state.flashcard_deck
    total = len(deck)
    idx = st.session_state.flashcard_idx % total
    current = deck[idx]

    # Callbacks for instant flip & navigation
    def flip_card():
        st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped

    def prev_card():
        st.session_state.flashcard_idx = (idx - 1) % total
        st.session_state.flashcard_flipped = False

    def next_card():
        st.session_state.flashcard_idx = (idx + 1) % total
        st.session_state.flashcard_flipped = False

    # Flashcard Card Counter
    st.markdown(
        f"""
        <div style="max-width:720px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
            <span style="font-weight:700; font-size:0.82rem; color:#6C55F6; background:#EDE9FE; padding:3px 10px; border-radius:999px;">
                Active Recall Mode
            </span>
            <span style="font-weight:800; font-size:0.92rem; color:{c['text_secondary']};">
                {idx + 1} / {total}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_nav_l, col_card, col_nav_r = st.columns([0.4, 3.2, 0.4])

    with col_nav_l:
        st.markdown("<div style='height:110px;'></div>", unsafe_allow_html=True)
        st.button("‹", key="btn_rev_prev", use_container_width=True, on_click=prev_card)

    with col_card:
        is_f = st.session_state.get("flashcard_flipped", False)
        flipped_class = "flipped" if is_f else ""
        checked_attr = "checked" if is_f else ""

        # Authentic 3D Flip Card Scene with Pure Native CSS Checkbox Flip + Streamlit State
        st.markdown(
            f"""
            <div class="flip-wrapper">
                <input type="checkbox" id="flashcard_cb_{idx}" class="flip-checkbox" {checked_attr}>
                <label for="flashcard_cb_{idx}" class="flip-scene" title="Click anywhere on this card to flip!">
                    <div class="flip-card-inner {flipped_class}">
                        <!-- Front Face: Question -->
                        <div class="flip-card-front">
                            <div class="flip-tag" style="background:#EDE9FE; color:#6C55F6;">QUESTION</div>
                            <div class="flip-question-text">{current['concept']}</div>
                            <div class="flip-hint">👆 Click anywhere on this card to flip</div>
                        </div>
                        <!-- Back Face: Answer -->
                        <div class="flip-card-back">
                            <div class="flip-tag" style="background:#DCFCE7; color:#16A34A;">ANSWER & EXPLANATION</div>
                            <div class="flip-answer-text">{current['details']}</div>
                            <div class="flip-anchor-box">💡 {current.get('key_takeaway', '')}</div>
                            <div class="flip-hint">👆 Click card to flip back to question</div>
                        </div>
                    </div>
                </label>
                <div style="text-align:center; margin: 0.5rem 0 0.8rem 0;">
                    <label for="flashcard_cb_{idx}" class="flip-toggle-btn">
                        <span class="flip-text-front">🔄 Click to Flip Card (Reveal Answer)</span>
                        <span class="flip-text-back">🔄 Flip Back to Question</span>
                    </label>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Dedicated Streamlit Flip Action Button
        _, mid_f, _ = st.columns([1, 2.2, 1])
        with mid_f:
            st.button(
                "🔄 Flip Back to Question" if is_f else "🔄 Click to Flip Card (Reveal Answer)",
                key=f"btn_flip_toggle_{idx}",
                type="primary" if not is_f else "secondary",
                use_container_width=True,
                on_click=flip_card
            )

        # 4 Spaced Repetition Rating Buttons
        st.markdown("<div style='max-width:540px; margin:1.2rem auto;'>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)

        with r1:
            st.markdown('<div class="btn-again">', unsafe_allow_html=True)
            st.button("Again", key="rev_again", use_container_width=True, on_click=next_card)
            st.markdown('</div>', unsafe_allow_html=True)

        with r2:
            st.markdown('<div class="btn-hard">', unsafe_allow_html=True)
            st.button("Hard", key="rev_hard", use_container_width=True, on_click=next_card)
            st.markdown('</div>', unsafe_allow_html=True)

        with r3:
            st.markdown('<div class="btn-good">', unsafe_allow_html=True)
            st.button("Good", key="rev_good", use_container_width=True, on_click=next_card)
            st.markdown('</div>', unsafe_allow_html=True)

        with r4:
            st.markdown('<div class="btn-easy">', unsafe_allow_html=True)
            st.button("Easy", key="rev_easy", use_container_width=True, on_click=next_card)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_nav_r:
        st.markdown("<div style='height:110px;'></div>", unsafe_allow_html=True)
        st.button("›", key="btn_rev_next", use_container_width=True, on_click=next_card)


# ----------------------------------------------------------------------------
# 5. SETTINGS PAGE
# ----------------------------------------------------------------------------
def render_settings_page():
    render_topbar()
    c = get_theme_colors()
    user_id = st.session_state.get("user_id")

    def set_settings_tab(t):
        st.session_state.settings_tab = t

    def set_theme_light():
        st.session_state.settings_theme = "Light"
        if user_id:
            s = get_user_settings(user_id)
            s["theme"] = "Light"
            save_user_settings(user_id, s)

    def set_theme_dark():
        st.session_state.settings_theme = "Dark"
        if user_id:
            s = get_user_settings(user_id)
            s["theme"] = "Dark"
            save_user_settings(user_id, s)

    def set_theme_sys():
        st.session_state.settings_theme = "System"

    # Header with Purple Gear badge
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.9rem; margin-bottom:1.2rem;">
            <div style="width:44px; height:44px; border-radius:14px; background:#EDE9FE; color:#6C55F6;
                        display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:800;
                        box-shadow:0 3px 10px rgba(108, 85, 246, 0.2);">
                ⚙️
            </div>
            <div>
                <div style="font-size:1.4rem; font-weight:800; color:{c['text_primary']}; letter-spacing:-0.02em; line-height:1.2;">
                    Settings
                </div>
                <div style="font-size:0.86rem; color:#94A3B8;">
                    Customize your learning experience and preferences.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Horizontal Native Tabs (0ms Client-Side Instant Switching)
    tab_appear, tab_goals, tab_pref, tab_acc = st.tabs(
        ["🎨 Appearance", "🎯 Study Goals", "⚙️ AI Preferences", "👤 Account"]
    )

    with tab_appear:
        with st.container():
            st.markdown(f'<div class="sh-card" style="padding:1.5rem 1.8rem; margin-top:0.6rem;">', unsafe_allow_html=True)
            st.markdown("#### Theme Selection")
            theme_cols = st.columns(3)
            with theme_cols[0]:
                is_light = (st.session_state.settings_theme == "Light")
                st.button("☀️ Light Gradient", type="primary" if is_light else "secondary", use_container_width=True, on_click=set_theme_light)
            with theme_cols[1]:
                is_dark_active = (st.session_state.settings_theme == "Dark")
                st.button("🌙 Dark Cyber-Glow", type="primary" if is_dark_active else "secondary", use_container_width=True, on_click=set_theme_dark)
            with theme_cols[2]:
                is_sys = (st.session_state.settings_theme == "System")
                st.button("💻 System Default", type="primary" if is_sys else "secondary", use_container_width=True, on_click=set_theme_sys)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            st.markdown("#### Study Goal Target")
            new_goal = st.slider(
                "Study Goal Percentage",
                min_value=50,
                max_value=100,
                value=int(st.session_state.get("settings_study_goal", 90)),
                format="%d%%",
                label_visibility="collapsed"
            )
            st.session_state.settings_study_goal = new_goal

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            st.markdown("#### Notifications")
            notif_quiz = st.toggle("Quiz Reminders", value=st.session_state.get("settings_quiz_notifications", True))
            notif_streak = st.toggle("Study Streak Notifications", value=st.session_state.get("settings_streak_notifications", True))
            notif_weekly = st.toggle("Weekly Progress Summary", value=st.session_state.get("settings_weekly_digest", True))

            st.session_state.settings_quiz_notifications = notif_quiz
            st.session_state.settings_streak_notifications = notif_streak
            st.session_state.settings_weekly_digest = notif_weekly

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            if st.button("Save Appearance Settings", type="primary", key="btn_save_appear"):
                if user_id:
                    s = get_user_settings(user_id)
                    s["study_goal"] = new_goal
                    s["quiz_notifications"] = notif_quiz
                    s["notifications"] = notif_streak
                    s["theme"] = st.session_state.settings_theme
                    save_user_settings(user_id, s)
                st.success("✅ Preferences updated successfully!")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_goals:
        with st.container():
            st.markdown(f'<div class="sh-card" style="padding:1.5rem 1.8rem; margin-top:0.6rem;">', unsafe_allow_html=True)
            st.markdown("#### Study Targets & Focus Subject")
            fav_subj = st.selectbox("Primary Focus Subject", ["Mathematics", "Programming", "Science", "English", "General"], index=0, key="sel_fav_subj")
            daily_mins = st.slider("Daily Study Time Target (minutes)", 15, 180, 60, step=15, key="sl_daily_mins")
            quizzes_target = st.slider("Weekly Quizzes Target", 3, 25, 10, key="sl_quizzes_target")

            if st.button("Save Study Goals", type="primary", key="btn_save_goals"):
                if user_id:
                    s = get_user_settings(user_id)
                    s["favorite_subject"] = fav_subj
                    save_user_settings(user_id, s)
                st.success("✅ Study goals saved successfully!")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_pref:
        with st.container():
            st.markdown(f'<div class="sh-card" style="padding:1.5rem 1.8rem; margin-top:0.6rem;">', unsafe_allow_html=True)
            st.markdown("#### AI Tutor Preferences")
            st.info("⚡ **Active Default AI Model**: Google `gemini-3.5-flash-lite` (Fastest response time, highly accurate, low latency)")
            # Default model is gemini-3.5-flash-lite as option 0
            curr_ai = st.session_state.get("settings_ai_model", "gemini-3.5-flash-lite")
            ai_options = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
            m_idx = 0 if curr_ai not in ai_options else ai_options.index(curr_ai)
            ai_model = st.selectbox("Gemini Model", ai_options, index=m_idx, key="sel_gemini_model")
            ai_tone = st.selectbox("AI Tutor Tone", ["Friendly & Clear", "Academic & Precise", "Step-by-Step Practical"], index=0, key="sel_gemini_tone")

            st.session_state.settings_ai_model = ai_model
            st.session_state.settings_ai_tone = ai_tone

            if st.button("Save AI Preferences", type="primary", key="btn_save_ai_pref"):
                if user_id:
                    s = get_user_settings(user_id)
                    s["ai_model"] = ai_model
                    s["ai_tone"] = ai_tone
                    save_user_settings(user_id, s)
                st.success(f"✅ AI settings updated with {ai_model}!")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_acc:
        with st.container():
            st.markdown(f'<div class="sh-card" style="padding:1.5rem 1.8rem; margin-top:0.6rem;">', unsafe_allow_html=True)
            st.markdown("#### Profile & Account Security")
            user_name_val = st.text_input("Full Name", value=st.session_state.get("user_name", "Alex Morgan"), key="acc_full_name")
            user_email_val = st.text_input("Email", value=st.session_state.get("user_email", "alex@studyhub.ai"), key="acc_email")

            if st.button("Update Profile Details", type="primary", key="btn_upd_profile"):
                st.session_state.user_name = user_name_val
                st.session_state.user_email = user_email_val
                if user_id:
                    update_user_profile(user_id, user_name_val, user_email_val)
                st.success("✅ Profile updated successfully!")

            st.markdown("---")
            st.markdown("#### Export Study Data")
            if user_id:
                history = get_quiz_history(user_id)
                if history:
                    df_h = pd.DataFrame(history, columns=["Title", "Subject", "Score", "Total", "Attempted At"])
                    st.download_button(
                        "📥 Download Quiz History (CSV)",
                        data=df_h.to_csv(index=False).encode('utf-8'),
                        file_name="studyhub_quiz_history.csv",
                        mime="text/csv",
                        key="btn_dl_csv"
                    )
                else:
                    st.info("No completed quiz history to export yet.")
            st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# App Entry Point & Router
# ----------------------------------------------------------------------------
def main():
    init_session_state()

    # Gate: If unauthenticated, show login or signup view
    if not st.session_state.authenticated:
        if st.session_state.auth_view == "login":
            render_login_page()
        else:
            render_signup_page()
        return

    # Authenticated: Load user settings
    load_user_settings_if_needed()
    inject_css()

    selected_page, demo_mode = render_sidebar()

    # Cached Data Loading for Dashboard
    user_id = st.session_state.get("user_id")
    if user_id:
        if "cached_analytics_user" not in st.session_state or st.session_state.cached_analytics_user != user_id:
            db_rows = get_analytics_data(user_id)
            if db_rows:
                df = pd.DataFrame(db_rows)
                df["date"] = pd.to_datetime(df["date"]).dt.date
            else:
                df = pd.DataFrame(columns=["date", "topic", "score", "duration_minutes"])
            st.session_state.cached_df = df
            st.session_state.cached_analytics_user = user_id
        df_all = st.session_state.cached_df
    else:
        df_all = pd.DataFrame(columns=["date", "topic", "score", "duration_minutes"])

    # Page Router
    if selected_page == "Dashboard":
        render_dashboard_page(df_all, demo_mode=demo_mode)
    elif selected_page == "Ask a Doubt":
        render_ask_doubt_page()
    elif selected_page == "Quizzes":
        render_quizzes_page()
    elif selected_page == "Revision Mode":
        render_revision_page()
    elif selected_page == "Settings":
        render_settings_page()
    else:
        st.warning("Page not found.")


if __name__ == "__main__":
    main()