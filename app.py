import streamlit as st
from database import *
from utils import *
from pages import *

def get_user_id():
    """Get current user ID from session state"""
    return st.session_state.get('user_id')

def get_username():
    """Get current username from session state"""
    return st.session_state.get('username')

def show_login_page():
    st.title("🔐 Smart Study Buddy - Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.logged_in = True
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Create Account")
            
            if signup_btn:
                if new_username and email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        if create_user(new_username, email, new_password):
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Username or email already exists")
                else:
                    st.warning("Please fill in all fields")

def show_main_app():
    st.set_page_config(page_title="Smart Study Buddy", page_icon="📚", layout="wide")
    st.title(f"📚 Smart Study Buddy - Welcome {get_username()}!")
    
    if 'current_note_id' not in st.session_state:
        st.session_state.current_note_id = None
    if 'current_note_topic' not in st.session_state:
        st.session_state.current_note_topic = ""
    if 'current_note_content' not in st.session_state:
        st.session_state.current_note_content = ""

    menu = st.sidebar.radio("Menu", ["Learn & Summarize", "My Notes", "Study Goals", "Progress", "Study Tips"])
    
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Logged in as:** {get_username()}")
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if menu == "Learn & Summarize":
        show_learn_summarize_page()
    elif menu == "My Notes":
        show_notes_page()
    elif menu == "Study Goals":
        show_goals_page()
    elif menu == "Progress":
        show_progress_page()
    elif menu == "Study Tips":
        show_tips_page()

def main():
    if not st.session_state.get('logged_in'):
        show_login_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()