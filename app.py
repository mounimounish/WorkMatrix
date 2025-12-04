import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from io import BytesIO
import base64
import plotly.express as px

# Streamlit Page Config
st.set_page_config(
    page_title="TaskFlow - Enterprise Workflow Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional enterprise UI
st.markdown("""
<style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f2940 0%, #1a3a52 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(135deg, #0f2940 0%, #1a3a52 100%);
    }
    
    /* Text Colors */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    /* Radio Buttons */
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 8px;
    }
    
    [data-testid="stSidebar"] [role="radio"] {
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin: 4px 0 !important;
        border: 2px solid #2d5a8c !important;
        background: rgba(45, 90, 140, 0.3) !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] [role="radio"]:hover {
        background: rgba(45, 90, 140, 0.6) !important;
        border-color: #5a8fcc !important;
    }
    
    /* Buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        font-weight: 600;
        padding: 12px 16px;
        margin-top: 8px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #ff5252 0%, #e74c3c 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
    }
    
    /* Dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
        margin: 16px 0 !important;
    }
    
    /* Main content */
    .metric-card {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #1a3a52;
    }
    
    .role-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .role-admin {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
    }
    
    .role-manager {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
    }
    
    .role-employee {
        background: linear-gradient(135deg, #95e1d3 0%, #7fdbca 100%);
        color: #333;
        box-shadow: 0 2px 8px rgba(149, 225, 211, 0.3);
    }
    
    /* Enhanced containers */
    .stContainer {
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #eef2f8 100%);
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #4ecdc4;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 8px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_URL = "http://localhost:4000/api"

# Session State Initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# Helper Functions
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def api_call(method, endpoint, data=None):
    """Make API calls with proper error handling"""
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=get_headers(), timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=get_headers(), timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=get_headers(), timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=get_headers(), timeout=10)

        # If backend returns a client/server error with JSON body, raise so callers see it
        if 400 <= response.status_code < 600:
            # let raise_for_status produce an exception that will be caught below
            response.raise_for_status()

        # No Content
        if response.status_code == 204:
            return None

        # Try parsing JSON, fall back to plain text when response isn't JSON
        try:
            return response.json()
        except ValueError:
            text = response.text
            return text if text else None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure the server is running on http://localhost:4000")
        return None
    except requests.exceptions.Timeout:
        st.error("API request timed out (check backend status)")
        return None
    except Exception as e:
        # Show a brief error to the user but log full exception to console for debugging
        st.error(f"API Error: {str(e)[:120]}")
        return None

def get_role_badge(role):
    """Return HTML badge for role"""
    role_colors = {
        'ADMIN': 'role-admin',
        'MANAGER': 'role-manager',
        'EMPLOYEE': 'role-employee'
    }
    return f"<span class='role-badge {role_colors.get(role, '')}'>{role}</span>"

# LOGIN PAGE
def login_page():
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
    <h1 style='font-size: 48px; margin-bottom: 10px;'>TaskFlow</h1>
    <p style='font-size: 18px; color: #666; margin: 0;'>Enterprise Workflow Management System</p>
    <p style='font-size: 14px; color: #999; margin-top: 5px;'>Real-time task tracking, analytics & team collaboration</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Your Account")
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Logging in..."):
                    result = api_call("POST", "/auth/login", {"email": email, "password": password})
                    if result and isinstance(result, dict) and 'token' in result:
                        st.session_state.token = result['token']
                        st.session_state.user = result['user']
                        st.success("Login successful")
                        st.rerun()
                    elif result is None:
                        st.error("Could not connect to the server. Please check backend status.")
                    else:
                        st.error("Invalid credentials or server error")
        
        st.divider()
        # Add employee-only sign up option (no demo credentials shown in UI)
        with st.expander("Create an Employee Account", expanded=False):
            st.markdown("Only employees may create accounts here. Managers and Admins should be added by an Admin.")
            new_name = st.text_input("Full Name", key="signup_name", placeholder="John Doe")
            new_email = st.text_input("Email", key="signup_email", placeholder="you@company.com")
            new_password = st.text_input("Password", key="signup_password", type="password")
            new_password_confirm = st.text_input("Confirm Password", key="signup_password_confirm", type="password")

            if st.button("Create Employee Account", use_container_width=True, key="create_account"):
                if not new_name or not new_email or not new_password:
                    st.error("Name, email and password are required")
                elif new_password != new_password_confirm:
                    st.error("Passwords do not match")
                else:
                    payload = {
                        "fullName": new_name,
                        "email": new_email,
                        "password": new_password,
                        "role": "EMPLOYEE"
                    }

                    # Try to create user via backend first and handle 403/connection failures by saving a local pending request
                    # Note: signup endpoint does NOT require auth (allow new employees to self-register)
                    try:
                        resp = requests.post(f"{API_URL}/users/signup", json=payload, timeout=10, headers={})
                        if resp.status_code in (200, 201):
                            st.success("Account created successfully. You can now login.")
                        elif resp.status_code == 403:
                            # Backend forbids public user creation — save request for admin review
                            try:
                                import os, json as _json
                                pending_path = os.path.join('data', 'pending_signups.json')
                                os.makedirs(os.path.dirname(pending_path), exist_ok=True)
                                entry = {
                                    "fullName": new_name,
                                    "email": new_email,
                                    "requestedAt": datetime.utcnow().isoformat() + 'Z'
                                }
                                if os.path.exists(pending_path):
                                    with open(pending_path, 'r', encoding='utf-8') as f:
                                        try:
                                            data_list = _json.load(f)
                                        except Exception:
                                            data_list = []
                                else:
                                    data_list = []
                                data_list.append(entry)
                                with open(pending_path, 'w', encoding='utf-8') as f:
                                    _json.dump(data_list, f, indent=2)
                                st.info("Signup request saved and pending admin approval. An admin can review data/pending_signups.json.")
                            except Exception as e:
                                st.error("Could not save signup request locally. Please ask an admin to create your account.")
                        else:
                            # Other failures — show backend message
                            msg = resp.text if resp is not None else ''
                            st.error(f"Could not create account: {resp.status_code} {str(msg)[:150]}")
                    except requests.exceptions.ConnectionError:
                        # Backend unavailable — save locally and inform user
                        try:
                            import os, json as _json
                            pending_path = os.path.join('data', 'pending_signups.json')
                            os.makedirs(os.path.dirname(pending_path), exist_ok=True)
                            entry = {
                                "fullName": new_name,
                                "email": new_email,
                                "requestedAt": datetime.utcnow().isoformat() + 'Z',
                                "note": "backend-unreachable"
                            }
                            if os.path.exists(pending_path):
                                with open(pending_path, 'r', encoding='utf-8') as f:
                                    try:
                                        data_list = _json.load(f)
                                    except Exception:
                                        data_list = []
                            else:
                                data_list = []
                            data_list.append(entry)
                            with open(pending_path, 'w', encoding='utf-8') as f:
                                _json.dump(data_list, f, indent=2)
                            st.info("Backend is unreachable — signup request saved locally for admin review.")
                        except Exception:
                            st.error("Backend unreachable and failed to save signup locally. Ask an admin to create your account.")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)[:150]}")

# DASHBOARD PAGE - Role Based Views
def dashboard_page():
    user = st.session_state.user
    role = user.get('role', 'EMPLOYEE')
    
    st.markdown(f"### Welcome, {user.get('fullName', 'User')}! {get_role_badge(role)}", unsafe_allow_html=True)
    
    # Fetch data
    tasks = api_call("GET", "/tasks")
    summary = api_call("GET", "/dashboard/summary")
    
    # Only fetch employees for ADMIN and MANAGER roles
    employees = None
    if role in ['ADMIN', 'MANAGER']:
        employees = api_call("GET", "/users")
    
    if not (summary and tasks):
        st.warning("No data available")
        return
    
    # Convert byStatus array to dict
    total = summary.get('totalTasks', 0)
    by_status = {}
    if isinstance(summary.get('byStatus'), list):
        for item in summary['byStatus']:
            by_status[item['status']] = item['cnt']
    
    # ADMIN DASHBOARD
    if role == 'ADMIN':
        st.markdown("#### System Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", total)
        with col2:
            st.metric("Total Users", summary.get('users', 0))
        with col3:
            st.metric("Completed", by_status.get('DONE', 0))
        with col4:
            pending = by_status.get('TODO', 0) + by_status.get('IN_PROGRESS', 0)
            st.metric("Pending", pending)
        
        st.divider()
        st.markdown("#### Team Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Task Status Distribution (Pie Chart)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.pie(df_status, values='Count', names='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        title='Task Status Breakdown')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Task Status Distribution (Bar Chart)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.bar(df_status, x='Status', y='Count',
                        color='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        title='Task Count by Status')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**Employee Count (Pie Chart)**")
            if employees:
                role_counts = {}
                for emp in employees:
                    role_counts[emp.get('role', 'UNKNOWN')] = role_counts.get(emp.get('role', 'UNKNOWN'), 0) + 1
                df_roles = pd.DataFrame(list(role_counts.items()), columns=['Role', 'Count'])
                fig = px.pie(df_roles, values='Count', names='Role',
                             color_discrete_map={'ADMIN': '#ff6b6b', 'MANAGER': '#4ecdc4', 'EMPLOYEE': '#95e1d3'},
                             title='Team Composition')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.markdown("**Employee Count (Bar Chart)**")
            if employees:
                role_counts = {}
                for emp in employees:
                    role_counts[emp.get('role', 'UNKNOWN')] = role_counts.get(emp.get('role', 'UNKNOWN'), 0) + 1
                df_roles = pd.DataFrame(list(role_counts.items()), columns=['Role', 'Count'])
                fig = px.bar(df_roles, x='Role', y='Count',
                            color='Role',
                            color_discrete_map={'ADMIN': '#ff6b6b', 'MANAGER': '#4ecdc4', 'EMPLOYEE': '#95e1d3'},
                            title='Users by Role')
                st.plotly_chart(fig, use_container_width=True)
    
    # MANAGER DASHBOARD
    elif role == 'MANAGER':
        st.markdown("#### Team Tasks")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", total)
        with col2:
            st.metric("To Do", by_status.get('TODO', 0))
        with col3:
            st.metric("In Progress", by_status.get('IN_PROGRESS', 0))
        with col4:
            st.metric("Completed", by_status.get('DONE', 0))
        
        st.divider()
        st.markdown("#### Team Workload")
        
        # Row 1: Task Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Task Distribution (Pie Chart)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.pie(df_status, values='Count', names='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        title='Workload Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Task Distribution (Bar Chart)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.bar(df_status, x='Status', y='Count',
                        color='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        title='Tasks by Status')
            st.plotly_chart(fig, use_container_width=True)
        
        # Row 2: Priority Levels
        st.divider()
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**Priority Levels (Pie Chart)**")
            if tasks:
                priority_counts = {}
                for task in tasks:
                    priority = task.get('priority', 3)
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                df_priority = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
                fig = px.pie(df_priority, values='Count', names='Priority',
                            color_discrete_sequence=['#FF6B6B', '#FF8E72', '#FFB84D', '#A29BFE', '#6C5CE7'],
                            title='Priority Breakdown')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.markdown("**Priority Levels (Bar Chart)**")
            if tasks:
                priority_counts = {}
                for task in tasks:
                    priority = task.get('priority', 3)
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                df_priority = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
                fig = px.bar(df_priority, x='Priority', y='Count',
                            color='Priority',
                            color_discrete_sequence=['#FF6B6B', '#FF8E72', '#FFB84D', '#A29BFE', '#6C5CE7'],
                            title='Tasks by Priority')
                st.plotly_chart(fig, use_container_width=True)
    
    # EMPLOYEE DASHBOARD
    else:
        st.markdown("#### My Tasks Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("My Tasks", total)
        with col2:
            st.metric("Completed", by_status.get('DONE', 0))
        with col3:
            pending = by_status.get('TODO', 0) + by_status.get('IN_PROGRESS', 0)
            st.metric("Pending", pending)
        
        st.divider()
        st.markdown("#### Task Distribution")
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**My Tasks by Status (Pie)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.pie(df_status, values='Count', names='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        title='Task Status Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col5:
            st.markdown("**My Tasks by Status (Bar)**")
            df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
            fig = px.bar(df_status, x='Status', y='Count',
                        color='Status',
                        color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                        text='Count',
                        title='Task Count by Status')
            fig.update_traces(textposition='auto')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.markdown("#### Recent Tasks")
    
    if tasks:
        for task in tasks[:10]:
            status_icon = {"TODO": "[TODO]", "IN_PROGRESS": "[IN PROGRESS]", "DONE": "[DONE]"}.get(task['status'], "[UNKNOWN]")
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.markdown(f"**{task['title']}**")
                st.caption(task.get('description', ''))
            with col2:
                st.markdown(f"{status_icon}")
            with col3:
                st.caption(f"Priority: {task['priority']}/5")
            with col4:
                if task['status'] != 'DONE':
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Start", key=f"start-{task['id']}", use_container_width=True):
                            api_call("PATCH", f"/tasks/{task['id']}", {"status": "IN_PROGRESS"})
                            st.rerun()
                    with col_b:
                        if st.button("Done", key=f"done-{task['id']}", use_container_width=True):
                            api_call("PATCH", f"/tasks/{task['id']}", {"status": "DONE"})
                            st.rerun()
                else:
                    st.markdown("Completed")
            st.divider()

# TASKS PAGE
def tasks_page():
    st.markdown("### Task Management")
    
    tab1, tab2 = st.tabs(["All Tasks", "Create Task"])
    
    with tab1:
        tasks = api_call("GET", "/tasks")
        
        if tasks:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect("Filter by Status", ["TODO", "IN_PROGRESS", "DONE"], default=["TODO", "IN_PROGRESS"])
            
            filtered_tasks = [t for t in tasks if t['status'] in status_filter]
            
            if filtered_tasks:
                df = pd.DataFrame([
                    {
                        "Title": t['title'],
                        "Status": t['status'],
                        "Priority": f"{t['priority']}/5",
                        "Created": datetime.fromtimestamp(t['createdAt']/1000).strftime('%Y-%m-%d'),
                    }
                    for t in filtered_tasks
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No tasks found with selected filters")
        else:
            st.warning("No tasks available")
    
    with tab2:
        st.markdown("**Create New Task**")
        
        title = st.text_input("Task Title *", placeholder="Enter task title")
        description = st.text_area("Description", placeholder="Enter task description", height=100)
        priority = st.slider("Priority", 1, 5, 3)
        
        if st.button("Create Task", use_container_width=True, type="primary"):
            if title:
                result = api_call("POST", "/tasks", {
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": "TODO"
                })
                if result:
                    st.success("Task created successfully!")
                    st.rerun()
            else:
                st.error("Task title is required")

# FILES PAGE
def files_page():
    st.markdown("### File Management")
    
    tab1, tab2 = st.tabs(["All Files", "Upload File"])
    
    with tab1:
        files = api_call("GET", "/files")
        
        if files:
            df = pd.DataFrame([
                {
                    "Filename": f['name'],
                    "Versions": f.get('versions', 1),
                    "Uploaded": datetime.fromtimestamp(f['createdAt']/1000).strftime('%Y-%m-%d %H:%M'),
                }
                for f in files
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No files uploaded yet")
    
    with tab2:
        st.markdown("**Upload New File**")
        
        filename = st.text_input("Filename *")
        uploaded_file = st.file_uploader("Choose file")
        
        if st.button("Upload", use_container_width=True, type="primary"):
            if filename and uploaded_file:
                import base64
                file_content = base64.b64encode(uploaded_file.read()).decode()
                
                result = api_call("POST", "/files", {
                    "name": filename,
                    "contentBase64": file_content
                })
                if result:
                    st.success("File uploaded successfully!")
                    st.rerun()
            else:
                st.error("Filename and file are required")

# MESSAGES PAGE - Enhanced Communication
def messages_page():
    st.markdown("### Team Communication")
    
    tab1, tab2 = st.tabs(["All Messages", "Post Update"])
    
    with tab1:
        messages = api_call("GET", "/messages")
        
        if messages:
            st.markdown(f"#### {len(messages)} Message(s) in Channel")
            for msg in reversed(messages):  # Show newest first
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{msg.get('userId', 'Unknown')}**")
                        st.markdown(msg.get('text', ''))
                    with col2:
                        timestamp = datetime.fromtimestamp(msg.get('createdAt', 0)/1000)
                        st.caption(timestamp.strftime('%Y-%m-%d %H:%M'))
        else:
            st.info("No messages yet. Be the first to communicate!")
    
    with tab2:
        st.markdown("#### Post a Message")
        
        message_title = st.text_input("Message Title (optional)")
        message_text = st.text_area("Message Content", height=100, placeholder="Share updates with your team...")
        
        if st.button("Send Message", use_container_width=True, type="primary"):
            if message_text.strip():
                full_message = f"{message_title}: {message_text}" if message_title else message_text
                result = api_call("POST", "/messages", {
                    "taskId": "",
                    "text": full_message
                })
                if result:
                    st.success("Message sent to team!")
                    st.rerun()
            else:
                st.error("Message cannot be empty")

# REPORTS PAGE - Enhanced with multiple formats
def reports_page():
    st.markdown("### Reports & Analytics")
    
    user = st.session_state.user
    role = user.get('role', 'EMPLOYEE')
    
    tab1, tab2, tab3 = st.tabs(["Export Reports", "Analytics", "Performance"])
    
    with tab1:
        st.markdown("#### Export Task Reports")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("CSV Export", use_container_width=True, type="primary"):
                try:
                    response = requests.get(f"{API_URL}/reports/tasks?format=csv", headers=get_headers(), timeout=5)
                    st.download_button(
                        label="Download CSV",
                        data=response.text,
                        file_name=f"tasks_report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("JSON Export", use_container_width=True):
                try:
                    data = api_call("GET", "/reports/tasks")
                    if data:
                        st.download_button(
                            label="Download JSON",
                            data=json.dumps(data, indent=2),
                            file_name=f"tasks_report_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col3:
            if st.button("Excel-Style", use_container_width=True):
                try:
                    data = api_call("GET", "/reports/tasks")
                    if data and 'rows' in data:
                        df = pd.DataFrame(data['rows'])
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="Download Excel",
                            data=csv_buffer.getvalue(),
                            file_name=f"tasks_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.ms-excel"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.markdown("#### Task Statistics")
        tasks = api_call("GET", "/tasks")
        if tasks:
            status_counts = {}
            priority_counts = {}
            
            for task in tasks:
                status = task.get('status', 'TODO')
                priority = task.get('priority', 3)
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Row 1: Status charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Task Status - Pie Chart**")
                df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                fig = px.pie(df_status, values='Count', names='Status',
                            color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                            title='Status Overview')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Task Status - Bar Chart**")
                df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                fig = px.bar(df_status, x='Status', y='Count',
                            color='Status',
                            color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                            title='Count by Status',
                            text='Count')
                fig.update_traces(textposition='auto')
                st.plotly_chart(fig, use_container_width=True)
            
            # Row 2: Priority charts
            st.divider()
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**Priority Distribution - Pie Chart**")
                df_priority = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
                fig = px.pie(df_priority, values='Count', names='Priority',
                            color_discrete_sequence=['#FF6B6B', '#FF8E72', '#FFB84D', '#A29BFE', '#6C5CE7'],
                            title='Priority Breakdown')
                st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                st.markdown("**Priority Distribution - Bar Chart**")
                df_priority = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
                fig = px.bar(df_priority, x='Priority', y='Count',
                            color='Priority',
                            color_discrete_sequence=['#FF6B6B', '#FF8E72', '#FFB84D', '#A29BFE', '#6C5CE7'],
                            title='Count by Priority',
                            text='Count')
                fig.update_traces(textposition='auto')
                st.plotly_chart(fig, use_container_width=True)
            
            # Row 3: Combined analysis
            st.divider()
            st.markdown("**Combined Task Overview - Sunburst Chart**")
            if tasks:
                analysis_data = []
                for task in tasks:
                    analysis_data.append({
                        'Status': task.get('status', 'TODO'),
                        'Priority': f"Priority {task.get('priority', 3)}",
                        'Count': 1
                    })
                df_analysis = pd.DataFrame(analysis_data)
                df_agg = df_analysis.groupby(['Status', 'Priority']).size().reset_index(name='Count')
                
                fig = px.sunburst(df_agg, labels='Status', parents='', values='Count',
                                color='Count', color_continuous_scale='Viridis',
                                title='Task Distribution Overview')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if role in ['ADMIN', 'MANAGER']:
            st.markdown("#### Performance Metrics")
            summary = api_call("GET", "/dashboard/summary")
            if summary:
                col1, col2, col3 = st.columns(3)
                
                total = summary.get('totalTasks', 0)
                by_status = {}
                if isinstance(summary.get('byStatus'), list):
                    for item in summary['byStatus']:
                        by_status[item['status']] = item['cnt']
                
                completed = by_status.get('DONE', 0)
                completion_rate = (completed / total * 100) if total > 0 else 0
                
                with col1:
                    st.metric("Total Tasks", total)
                with col2:
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
                with col3:
                    st.metric("Pending Tasks", total - completed)
                
                st.divider()
                st.markdown("#### Completion Rate Visualization")
                
                # Row 1: Gauge and Progress
                col4, col5 = st.columns(2)
                
                with col4:
                    st.markdown("**Completion Rate - Gauge Chart**")
                    fig = px.indicator(mode="gauge+number+delta",
                                     value=completion_rate,
                                     title={'text': "Task Completion %"},
                                     domain={'x': [0, 100], 'y': [0, 100]},
                                     gauge={'axis': {'range': [None, 100]},
                                           'bar': {'color': '#00B894'},
                                           'steps': [
                                               {'range': [0, 33], 'color': '#FFB84D'},
                                               {'range': [33, 66], 'color': '#FFB84D'},
                                               {'range': [66, 100], 'color': '#00B894'}
                                           ],
                                           'threshold': {'line': {'color': 'red', 'width': 4},
                                                       'thickness': 0.75,
                                                       'value': 90}})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col5:
                    st.markdown("**Task Completion - Horizontal Bar**")
                    completion_data = pd.DataFrame({
                        'Category': ['Completed', 'Pending'],
                        'Count': [completed, total - completed]
                    })
                    fig = px.bar(completion_data, y='Category', x='Count',
                               orientation='h',
                               color='Category',
                               color_discrete_map={'Completed': '#00B894', 'Pending': '#FFB84D'},
                               text='Count',
                               title='Task Completion Status')
                    fig.update_traces(textposition='auto')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Row 2: Status breakdown
                st.divider()
                st.markdown("**Status Breakdown - All Chart Types**")
                col6, col7 = st.columns(2)
                
                with col6:
                    st.markdown("**Status Distribution**")
                    df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
                    fig = px.pie(df_status, values='Count', names='Status',
                                color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                                title='Task Status Pie')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col7:
                    st.markdown("**Status Count - Donut Chart**")
                    df_status = pd.DataFrame(list(by_status.items()), columns=['Status', 'Count'])
                    fig = px.pie(df_status, values='Count', names='Status',
                                color_discrete_map={'TODO': '#FFB84D', 'IN_PROGRESS': '#6C5CE7', 'DONE': '#00B894'},
                                hole=0.4,
                                title='Task Status Donut')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Performance metrics available for managers and admins")

# EMPLOYEES PAGE (Admin & Manager)
def employees_page():
    user = st.session_state.user
    role = user.get('role', 'EMPLOYEE')
    
    if role not in ['ADMIN', 'MANAGER']:
        st.error("Admin and Manager access only")
        return

    # initialize confirmation state
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = None
    if 'confirm_delete_name' not in st.session_state:
        st.session_state.confirm_delete_name = None
    
    if role == 'ADMIN':
        st.markdown("### Employee Management")
    else:
        st.markdown("### Team Management")
    
    tab1, tab2 = st.tabs(["All Employees", "Add Employee"])
    
    with tab1:
        employees = api_call("GET", "/users")

        if employees is None:
            st.error("Unable to load team members. Please ensure you have proper permissions.")
            st.info("Note: Only Admin and Manager roles can view the team list.")
            return

        if employees:
            st.markdown("#### Employees")

            # If a delete is pending confirmation, show a prominent confirmation block
            if st.session_state.get('confirm_delete'):
                cid = st.session_state.confirm_delete
                cname = st.session_state.confirm_delete_name or ''
                st.warning(f"Confirm deletion of user: {cname} (id: {cid})")
                ccol1, ccol2 = st.columns([1,1])
                with ccol1:
                    if st.button("Confirm Delete", key="confirm-delete-yes"):
                        res = api_call("DELETE", f"/users/{cid}")
                        # clear confirmation state
                        st.session_state.confirm_delete = None
                        st.session_state.confirm_delete_name = None
                        if res is not None:
                            st.success("User deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete user. Check permissions or backend status.")
                with ccol2:
                    if st.button("Cancel", key="confirm-delete-no"):
                        st.session_state.confirm_delete = None
                        st.session_state.confirm_delete_name = None
                        st.info("Delete cancelled")

            for emp in employees:
                with st.container(border=True):
                    cols = st.columns([3, 3, 2, 1])
                    with cols[0]:
                        st.markdown(f"**{emp.get('fullName', '')}**")
                        st.caption(emp.get('email', ''))
                    with cols[1]:
                        st.markdown(get_role_badge(emp.get('role', 'EMPLOYEE')), unsafe_allow_html=True)
                    with cols[2]:
                        eid = emp.get('id', '') or ''
                        st.caption(eid[:8] + '...' if len(eid) > 8 else eid)
                    with cols[3]:
                        # Determine if current user can delete this employee (frontend guard; backend enforces rules too)
                        can_delete = False
                        if role == 'ADMIN':
                            can_delete = True
                        elif role == 'MANAGER' and emp.get('role') == 'EMPLOYEE':
                            can_delete = True

                        if can_delete:
                            # two-step delete: set confirmation state first
                            if st.button("Delete", key=f"delete-{emp.get('id', '')}", use_container_width=True):
                                st.session_state.confirm_delete = emp.get('id')
                                st.session_state.confirm_delete_name = emp.get('fullName')
                                st.experimental_rerun()

            st.caption(f"Total: {len(employees)} employee(s)")
        else:
            st.info("No employees found")

        # Admin: Pending signups (local fallback)
        if role == 'ADMIN':
            st.divider()
            with st.expander("Pending Signups (Local)", expanded=False):
                import os as _os, json as _json
                pending_path = _os.path.join('data', 'pending_signups.json')
                if _os.path.exists(pending_path):
                    try:
                        with open(pending_path, 'r', encoding='utf-8') as f:
                            pending = _json.load(f)
                    except Exception:
                        pending = []
                else:
                    pending = []

                if pending:
                    for idx, entry in enumerate(list(pending)):
                        pcols = st.columns([3, 3, 1, 1])
                        with pcols[0]:
                            st.markdown(f"**{entry.get('fullName', '')}**")
                            st.caption(entry.get('email', ''))
                        with pcols[1]:
                            st.caption(entry.get('requestedAt', ''))
                        with pcols[2]:
                            if st.button("Approve", key=f"approve-{idx}"):
                                payload = {
                                    "fullName": entry.get('fullName'),
                                    "email": entry.get('email'),
                                    "role": "EMPLOYEE",
                                    "password": "TaskFlow@123"
                                }
                                created = api_call("POST", "/users", payload)
                                if created is not None:
                                    # remove the approved entry
                                    try:
                                        pending.remove(entry)
                                        with open(pending_path, 'w', encoding='utf-8') as f:
                                            _json.dump(pending, f, indent=2)
                                    except Exception:
                                        pass
                                    st.success("Account created and removed from pending list")
                                    st.rerun()
                                else:
                                    st.error("Failed to create account. Check backend or permissions.")
                        with pcols[3]:
                            if st.button("Reject", key=f"reject-{idx}"):
                                try:
                                    pending.remove(entry)
                                    with open(pending_path, 'w', encoding='utf-8') as f:
                                        _json.dump(pending, f, indent=2)
                                except Exception:
                                    pass
                                st.info("Signup request rejected and removed")
                                st.rerun()
                else:
                    st.info("No pending signups found")
    
    with tab2:
        st.markdown("#### Add New Employee")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
        with col2:
            email = st.text_input("Email *", placeholder="john@company.com")
        
        role_opt = st.selectbox("Role", ["EMPLOYEE", "MANAGER", "ADMIN"])
        
        if st.button("Add Employee", use_container_width=True, type="primary"):
            if name and email:
                result = api_call("POST", "/users", {
                    "fullName": name,
                    "email": email,
                    "role": role_opt,
                    "password": "TaskFlow@123"
                })
                if result:
                    st.success(f"Employee '{name}' added successfully!")
                    st.info(f"Email: {email}\nDefault Password: TaskFlow@123")
                    st.rerun()
            else:
                st.error("Name and email are required")

# AUDIT PAGE (Admin Only)
def audit_page():
    user = st.session_state.user
    
    if user.get('role') != 'ADMIN':
        st.error("Admin access only")
        return
    
    st.markdown("### Audit Logs")
    
    logs = api_call("GET", "/audit")
    
    if logs:
        df = pd.DataFrame([
            {
                "Action": log.get('action', ''),
                "By": log.get('by', ''),
                "Target": log.get('target', 'N/A'),
                "Timestamp": datetime.fromtimestamp(log.get('at', 0)/1000).strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in logs
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No audit logs available")

# MAIN APP
def main():
    if not st.session_state.token:
        login_page()
    else:
        # Professional Sidebar Navigation
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; padding: 20px 0;'>
                <h2 style='margin: 8px 0 0 0; font-size: 24px;'>TaskFlow</h2>
                <p style='font-size: 12px; color: #ccc; margin: 4px 0;'>Enterprise Edition v1.0</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # User Info Card
            user = st.session_state.user
            role = user.get('role', 'EMPLOYEE')
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin-bottom: 16px;'>
                <p style='margin: 0; font-size: 13px; color: #ccc;'>Current User</p>
                <p style='margin: 4px 0 0 0; font-weight: 600; font-size: 14px;'>{user.get('fullName', 'User')}</p>
                <p style='margin: 4px 0 0 0; font-size: 12px; color: #ddd;'>{role}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Navigation menu
            pages = {
                "Dashboard": "dashboard",
                "Tasks": "tasks",
                "Files": "files",
                "Communication": "messages",
                "Reports": "reports",
            }
            
            # Add role-specific pages
            if role == 'ADMIN':
                pages["Employees"] = "employees"
                pages["Audit Logs"] = "audit"
            elif role == 'MANAGER':
                pages["Team"] = "employees"
            
            st.markdown("<p style='font-size: 12px; color: #ccc; margin-bottom: 12px;'>NAVIGATION</p>", unsafe_allow_html=True)
            
            selected = st.radio("", list(pages.keys()), label_visibility="collapsed", key="nav_radio")
            st.session_state.page = pages[selected]
            
            st.divider()
            
            # Additional Info
            st.markdown("""
            <p style='font-size: 11px; color: #888; margin-top: 20px;'>
            Security: All actions logged and audited
            </p>
            """, unsafe_allow_html=True)
            
            # Logout button
            if st.button("Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
        
        # Page Routing
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "tasks":
            tasks_page()
        elif st.session_state.page == "files":
            files_page()
        elif st.session_state.page == "messages":
            messages_page()
        elif st.session_state.page == "reports":
            reports_page()
        elif st.session_state.page == "employees":
            employees_page()
        elif st.session_state.page == "audit":
            audit_page()

if __name__ == "__main__":
    main()
