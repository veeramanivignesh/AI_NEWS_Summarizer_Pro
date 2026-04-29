import bcrypt
import streamlit as st
from db import InstantDB

db = InstantDB()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def signup_user(username, email, password):
    if not username or not email or not password:
        return False, "All fields are required"
    
    # Check if user already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return False, "User with this email already exists"
    
    try:
        password_hash = hash_password(password)
        db.create_user(username, email, password_hash)
        return True, "Signup successful! Please login."
    except Exception as e:
        return False, f"Signup failed: {str(e)}"

def login_user(email, password):
    if not email or not password:
        return False, "Email and password are required"
    
    try:
        user = db.get_user_by_email(email)
        if user and check_password(password, user['password_hash']):
            # Set session state
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['email'] = user['email']
            st.session_state['logged_in'] = True
            return True, f"Welcome back, {user['username']}!"
        else:
            return False, "Invalid email or password"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state.clear()
