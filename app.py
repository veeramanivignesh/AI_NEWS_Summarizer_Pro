import streamlit as st

# Page Config MUST be the first Streamlit command
st.set_page_config(page_title="AI News Summarizer Pro", page_icon="📰", layout="wide")

import auth
import model
from db import InstantDB
import time

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'theme' not in st.session_state:
    st.session_state['theme'] = "Light"

# Theme Configuration
themes = {
    "Light": {
        "bg": "#F8FAFC",
        "sidebar": "#0F172A",
        "card": "#FFFFFF",
        "text": "#1E293B",
        "subtext": "#64748B",
        "border": "#E2E8F0",
        "accent": "#6366F1",
        "history_bg": "#FFFFFF"
    },
    "Dark": {
        "bg": "#020617",
        "sidebar": "#0F172A",
        "card": "#0F172A",
        "text": "#F8FAFC",
        "subtext": "#94A3B8",
        "border": "#1E293B",
        "accent": "#818CF8",
        "history_bg": "#0F172A"
    }
}

t = themes[st.session_state['theme']]

# Custom CSS for a professional look
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: {t['bg']};
        color: {t['text']};
    }}
    
    /* Main Content Contrast */
    [data-testid="stAppViewContainer"] h1, 
    [data-testid="stAppViewContainer"] h2, 
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span {{
        color: {t['text']} !important;
    }}
    
    .stSidebar {{
        background-color: {t['sidebar']};
        border-right: 1px solid {t['border']};
    }}
    
    /* Sidebar Specific Text (Always Light) */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stRadio label p {{
        color: #F1F5F9 !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #94A3B8 !important;
    }}
    
    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        background-color: {t['accent']};
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }}
    
    .card {{
        background: {t['card']};
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid {t['border']};
        margin-bottom: 1.5rem;
    }}
    
    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {t['card']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 8px;
    }}
    
    .stSelectbox>div>div>div {{
        background-color: {t['card']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 8px;
    }}
    
    .history-item {{
        border-left: 4px solid {t['accent']};
        padding: 1.5rem;
        background: {t['card']};
        margin-bottom: 1rem;
        border-radius: 4px 12px 12px 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid {t['border']};
    }}
    
    small {{
        color: {t['subtext']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize DB
db = InstantDB()

# Navigation
def show_login_signup():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Welcome Back")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, msg = auth.login_user(email, password)
            if success:
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)
                
    with tab2:
        st.subheader("Create Account")
        new_username = st.text_input("Username", key="signup_user")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            success, msg = auth.signup_user(new_username, new_email, new_password)
            if success:
                st.success(msg)
            else:
                st.error(msg)

def show_summarizer():
    st.title("🚀 AI News Summarizer")
    st.write(f"Hello, **{st.session_state['username']}**! Paste your article below.")
    
    with st.container(border=True):
        
        # URL Input
        article_url = st.text_input("🔗 News Article URL", placeholder="https://news.example.com/article...")
        
        # Divider or "OR" text
        st.markdown("<p style='text-align: center; color: #6c757d; margin: 10px 0;'>— OR —</p>", unsafe_allow_html=True)
        
        # Text Area
        article_text = st.text_area("📄 Article Content", height=200, placeholder="Paste long news text here...")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            length = st.selectbox("Summary Length", ["Extra Short", "Short", "Medium", "Detailed"], index=1)
        with col2:
            target_lang = st.selectbox("Target Language", ["English", "Hindi", "Tamil"])
        with col3:
            st.write("") # Spacer
            st.write("") # Spacer
            generate_btn = st.button("✨ Generate Summary", use_container_width=True)

    if generate_btn:
        final_text = ""
        
        # Prioritize URL if provided
        if article_url.strip():
            with st.spinner("🔍 Fetching article from URL..."):
                extracted_text = model.extract_text_from_url(article_url)
                if extracted_text:
                    final_text = extracted_text
                    st.toast("✅ Article extracted successfully!", icon="🌐")
                else:
                    st.error("❌ Failed to extract text from URL. Please check the link or paste the text manually.")
        else:
            final_text = article_text

        if not final_text.strip():
            st.warning("Please provide a URL or paste some text.")
        elif len(final_text.split()) < 20:
            st.error("Article too short (min 20 words).")
        else:
            with st.spinner("Processing with AI..."):
                try:
                    # 1. Summarize
                    summary = model.generate_summary(final_text, length)
                    
                    # 2. Translate if needed
                    final_output = summary
                    if target_lang != "English":
                        with st.status(f"Translating to {target_lang}..."):
                            final_output = model.translate_text(summary, target_lang)
                    
                    # 3. Save to DB
                    db.save_summary(st.session_state['user_id'], article_text, final_output)
                    
                    st.markdown("### Result")
                    st.write(final_output)
                    if target_lang != "English":
                        st.info(f"Summary originally generated in English and translated to {target_lang}.")
                    
                    st.success("Summary saved to history!")
                except Exception as e:
                    st.error(f"Error: {e}")

def show_history():
    st.title("📜 Your History")
    try:
        history = db.get_user_history(st.session_state['user_id'])
        if not history:
            st.info("No history found. Start summarizing!")
        else:
            for item in history:
                summary_id = item.get('id')
                with st.container():
                    st.markdown(f"""
                        <div class="history-item">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <small>{item.get('created_at', 'Unknown Date')}</small>
                            </div>
                            <div style="margin-top: 10px;">
                                <strong>Summary:</strong><br>
                                {item.get('summary_text', '')}
                            </div>
                            <hr style="margin: 10px 0;">
                            <details>
                                <summary>Show Original Text</summary>
                                <p style="font-size: 0.9em; color: #666;">{item.get('original_text', '')[:500]}...</p>
                            </details>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Delete Button
                    if st.button(f"🗑️ Delete Item", key=f"del_{summary_id}"):
                        with st.spinner("Deleting..."):
                            db.delete_summary(summary_id)
                            st.toast("Item deleted successfully!")
                            time.sleep(0.5)
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to fetch history: {e}")

# Main Logic
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📰 News Summarizer Pro")
        show_login_signup()
else:
    # Sidebar
    with st.sidebar:
        st.title("Menu")
        page = st.radio("Navigate", ["Summarizer", "History"])
        st.markdown("---")
        
        # Theme Toggle
        theme_icon = "🌙" if st.session_state['theme'] == "Light" else "☀️"
        selected_theme = st.selectbox(
            f"{theme_icon} Appearance", 
            ["Light", "Dark"], 
            index=0 if st.session_state['theme'] == "Light" else 1
        )
        
        if selected_theme != st.session_state['theme']:
            st.session_state['theme'] = selected_theme
            st.rerun()
            
        st.markdown("---")
        if st.button("Logout"):
            auth.logout_user()
            st.rerun()
            
    if page == "Summarizer":
        show_summarizer()
    elif page == "History":
        show_history()
