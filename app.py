import streamlit as st

# Page Config MUST be the first Streamlit command
st.set_page_config(page_title="AI News Summarizer Pro", page_icon="📰", layout="wide")

import auth
import model
from db import InstantDB
import time

# Initialize DB
db = InstantDB()

# Custom CSS for a professional look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #F8FAFC;
    }
    
    .stSidebar {
        background-color: #0F172A;
        border-right: 1px solid #E2E8F0;
        color: white;
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #94A3B8;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #6366F1;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #4F46E5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        transform: translateY(-1px);
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
    
    .history-item {
        border-left: 4px solid #6366F1;
        padding: 1.5rem;
        background: white;
        margin-bottom: 1rem;
        border-radius: 4px 12px 12px 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    
    h1, h2, h3 {
        color: #1E293B;
        font-weight: 700;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }
    
    .stSelectbox>div>div>div {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

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
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
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
        st.markdown('</div>', unsafe_allow_html=True)

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
                    st.markdown(f'<div class="card">{final_output}</div>', unsafe_allow_html=True)
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
        if st.button("Logout"):
            auth.logout_user()
            st.rerun()
            
    if page == "Summarizer":
        show_summarizer()
    elif page == "History":
        show_history()
