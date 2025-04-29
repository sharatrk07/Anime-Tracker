import streamlit as st
from firebase_config import db
from PIL import Image
import base64
import time
import io

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'edit_watched_index' not in st.session_state:
    st.session_state.edit_watched_index = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'anime_collection' not in st.session_state:
    st.session_state.anime_collection = []
if 'user_menu_visible' not in st.session_state:
    st.session_state.user_menu_visible = False
if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = 0
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None
if 'toasts' not in st.session_state:
    st.session_state.toasts = []

# Page configuration
st.set_page_config(
    page_title="Anime Tracker", 
    page_icon="🎬", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    /* Main theme */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #6B46C1;
        --primary-light: #805AD5;
        --primary-dark: #553C9A;
        --bg-dark: #0F0F13;
        --bg-card: #1A1A27;
        --bg-input: #28293D;
        --text-light: #EAEAEA;
        --text-muted: #B9B9C3;
        --border: #2D2D3D;
        --status-watching: #5D87FF;
        --status-planned: #FF6B8A;
        --status-completed: #56C568;
    }
    
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-light);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-card);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-light);
    }
    
    /* Headers */
    .page-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 30px 0;
        background: linear-gradient(90deg, var(--primary), #D53F8C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(107, 70, 193, 0.3);
        letter-spacing: -1px;
    }
    
    .section-header {
        font-size: 2rem;
        margin-top: 50px;
        margin-bottom: 25px;
        font-weight: 700;
        color: var(--text-light);
        position: relative;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--primary);
        display: inline-block;
    }
    
    .section-header::after {
        content: "";
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background-color: var(--primary);
    }
    
    .section-container {
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }
    
    /* Cards */
    .anime-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 25px;
    }
    
    .anime-card {
        background: linear-gradient(145deg, var(--bg-card), var(--bg-input));
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--border);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .anime-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(107, 70, 193, 0.3);
        border-color: var(--primary);
    }
    
    .anime-image {
        height: 220px;
        background-size: cover;
        background-position: center;
        position: relative;
        transition: all 0.3s ease;
        background-color: #000000;
    }
    
    .anime-image-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0,0,0,0.8));
        height: 50%;
    }
    
    .anime-card-content {
        padding: 20px;
    }
    
    .anime-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .anime-stats {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        margin-top: 12px;
        color: var(--text-muted);
    }
    
    .status-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4);
    }
    
    .status-watching {
        background: linear-gradient(90deg, var(--status-watching), #7B9EFF);
        color: white;
    }
    
    .status-completed {
        background: linear-gradient(90deg, var(--status-completed), #78D485);
        color: white;
    }
    
    .status-planned {
        background: linear-gradient(90deg, var(--status-planned), #FF8DA3);
        color: white;
    }
    
    .progress-container {
        background-color: var(--bg-input);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 12px;
        height: 8px;
    }
    
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, var(--primary), #D53F8C);
        border-radius: 999px;
    }
    
    /* Forms and inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: var(--bg-card);
        color: var(--text-light);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 15px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 1px var(--primary);
    }
    
    .stFileUploader > div {
        background-color: var(--bg-card);
        border: 1px dashed var(--primary);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary), var(--primary-light));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, var(--primary-light), var(--primary));
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(107, 70, 193, 0.4);
    }
    
    /* Auth container */
    .auth-container {
        max-width: 500px;
        margin: 60px auto;
        padding: 40px;
        background: linear-gradient(145deg, var(--bg-card), var(--bg-input));
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .auth-tab {
        background-color: var(--bg-input);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    /* Search */
    .search-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    /* User menu */
    .user-menu {
        position: absolute;
        right: 20px;
        top: 60px;
        background: var(--bg-card);
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
        z-index: 1000;
        min-width: 150px;
        border: 1px solid var(--border);
    }
    
    .user-menu-item {
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .user-menu-item:hover {
        background-color: var(--bg-input);
    }
    
    /* Loading */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid transparent;
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Toast messages */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--bg-input);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }
    
    .toast-success {
        border-left: 4px solid var(--status-completed);
    }
    
    .toast-error {
        border-left: 4px solid var(--status-planned);
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    /* Image placeholder */
    .image-placeholder {
        height: 220px;
        background-color: #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        font-size: 1.2rem;
        border-radius: 8px 8px 0 0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .page-title {
            font-size: 2.5rem;
        }
        
        .section-header {
            font-size: 1.6rem;
        }
        
        .anime-grid {
            grid-template-columns: 1fr;
        }
        
        .auth-container {
            padding: 20px;
            margin: 30px 20px;
        }
        
        .anime-image {
            height: 180px;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom slider */
    .stSlider > div > div > div > div {
        background-color: var(--primary);
    }
    
    /* Custom progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), #D53F8C);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for image processing
def process_image(image_data):
    """Process and resize images to prevent size issues"""
    if not image_data:
        return None
        
    try:
        # Convert to PIL Image
        if isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            return None
            
        # Resize to reasonable dimensions while maintaining aspect ratio
        max_size = (800, 600)
        img.thumbnail(max_size, Image.LANCZOS)
        
        # Convert to JPEG with reduced quality
        output = io.BytesIO()
        img.convert('RGB').save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return None

def image_to_base64(image_bytes):
    """Convert image bytes to base64 string"""
    if not image_bytes:
        return None
    try:
        return base64.b64encode(image_bytes).decode()
    except:
        return None

def base64_to_bytes(base64_str):
    """Convert base64 string to bytes"""
    if not base64_str:
        return None
    try:
        return base64.b64decode(base64_str)
    except:
        return None

# Toast notification system
def show_toast(message, type="success"):
    """Show a toast notification"""
    st.session_state.toasts.append({"message": message, "type": type})

def handle_action(action_name, callback_func, *args, **kwargs):
    """Handle actions with debounce to prevent duplicate submissions"""
    current_time = time.time()
    if current_time - st.session_state.last_action_time > 0.5:
        st.session_state.last_action_time = current_time
        callback_func(*args, **kwargs)
        st.rerun()

def filter_anime_collection():
    """Filter anime collection based on search query"""
    filtered = []
    for idx, anime in enumerate(st.session_state.anime_collection):
        if not st.session_state.search_query or st.session_state.search_query.lower() in anime['anime_name'].lower():
            filtered.append((idx, anime))
    return filtered

def get_status(anime):
    """Get status of an anime based on episode progress"""
    if anime['finished_episodes'] == 0:
        return "planned"
    elif anime['finished_episodes'] >= anime['total_episodes']:
        return "completed"
    else:
        return "watching"

def calculate_progress(anime):
    """Calculate progress percentage"""
    if anime['total_episodes'] == 0:
        return 0
    return int((anime['finished_episodes'] / anime['total_episodes']) * 100)

def load_anime_collection():
    """Load anime collection from Firebase"""
    try:
        if st.session_state.username:
            doc_ref = db.collection("users").document(st.session_state.username)
            doc = doc_ref.get()
            if hasattr(doc, 'exists') and doc.exists:
                anime_collection = doc.to_dict().get("anime_collection", [])
                for anime in anime_collection:
                    if isinstance(anime.get('image'), str) and anime['image']:
                        try:
                            anime['image'] = base64_to_bytes(anime['image'])
                        except:
                            anime['image'] = None
                    else:
                        anime['image'] = None
                st.session_state.anime_collection = anime_collection
            else:
                st.session_state.anime_collection = []
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.anime_collection = []

def save_anime_collection():
    """Save anime collection to Firebase"""
    try:
        if st.session_state.username:
            anime_collection_serializable = []
            for anime in st.session_state.anime_collection:
                anime_copy = anime.copy()
                if isinstance(anime_copy.get('image'), bytes):
                    anime_copy['image'] = image_to_base64(anime_copy['image'])
                else:
                    anime_copy['image'] = ""
                anime_collection_serializable.append(anime_copy)
            
            doc_ref = db.collection("users").document(st.session_state.username)
            doc_ref.set({"anime_collection": anime_collection_serializable})
            return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def save_anime_data(anime_data, edit_index=None):
    """Save or update anime data"""
    try:
        if edit_index is not None:
            st.session_state.anime_collection[edit_index] = anime_data
            action = "updated"
        else:
            st.session_state.anime_collection.append(anime_data)
            action = "added"
            
        if save_anime_collection():
            show_toast(f"Anime {action} successfully!")
        else:
            show_toast("Error saving data", "error")
            
        st.session_state.view = 'home'
        st.session_state.edit_index = None
    except Exception as e:
        show_toast(f"Error: {str(e)}", "error")

def delete_anime(index):
    """Delete anime from collection"""
    try:
        anime_name = st.session_state.anime_collection[index]['anime_name']
        st.session_state.anime_collection.pop(index)
        if save_anime_collection():
            show_toast(f"'{anime_name}' has been deleted")
        else:
            show_toast("Error deleting anime", "error")
        st.session_state.view = 'home'
    except Exception as e:
        show_toast(f"Error: {str(e)}", "error")

def logout():
    """Logout user and clear session state"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.view = 'home'
    st.session_state.edit_index = None
    st.session_state.edit_watched_index = None
    st.session_state.anime_collection = []
    st.session_state.user_menu_visible = False
    show_toast("Logged out successfully")
    st.set_query_params({})

def set_view(view_name, **kwargs):
    """Set current view and update session state"""
    st.session_state.view = view_name
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

def auth_page():
    """Authentication page with login and signup forms"""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    # Anime image for decoration
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <img src="https://i.imgur.com/XJyemeI.png" alt="Anime" style="max-width: 200px; border-radius: 10px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for login/signup
    col1, col2 = st.columns(2)
    
    if col1.button("Login", key="login_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
    
    if col2.button("Sign Up", key="signup_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "signup"
    
    st.markdown('<div style="margin: 20px 0; border-bottom: 1px solid #333;"></div>', unsafe_allow_html=True)
    
    # Login form
    if st.session_state.auth_mode == "login":
        st.markdown('<h3 style="text-align: center; margin-bottom: 20px;">Welcome Back!</h3>', unsafe_allow_html=True)
        login_username = st.text_input("Username", key="login_username", 
                                     placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_password",
                                     placeholder="Enter your password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Sign In", key="submit_login", use_container_width=True):
                if login_username and login_password:
                    with st.spinner("Logging in..."):
                        # Add a small delay to simulate authentication
                        time.sleep(0.5)
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        load_anime_collection()
                        show_toast(f"Welcome back, {login_username}!")
                        st.rerun()
                else:
                    st.error("Please enter both username and password")
        with col2:
            if st.button("Guest", key="guest_login"):
                st.session_state.logged_in = True
                st.session_state.username = "guest_user"
                load_anime_collection()
                show_toast("Logged in as guest")
                st.rerun()
    
    # Signup form
    elif st.session_state.auth_mode == "signup":
        st.markdown('<h3 style="text-align: center; margin-bottom: 20px;">Create Your Account</h3>', unsafe_allow_html=True)
        signup_username = st.text_input("Username", key="signup_username", 
                                      placeholder="Choose a username")
        signup_password = st.text_input("Password", type="password", key="signup_password",
                                      placeholder="Create a password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm",
                                     placeholder="Confirm your password")
        
        if st.button("Create Account", key="submit_signup", use_container_width=True):
            if not signup_username:
                st.error("Please enter a username")
            elif not signup_password:
                st.error("Please enter a password")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match")
            else:
                with st.spinner("Creating your account..."):
                    # Add a small delay to simulate account creation
                    time.sleep(0.5)
                    st.session_state.logged_in = True
                    st.session_state.username = signup_username
                    save_anime_collection()
                    show_toast(f"Welcome, {signup_username}! Account created successfully")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_anime_card(index, anime):
    """Render an anime card with improved styling"""
    progress = calculate_progress(anime)
    status = get_status(anime)
    status_text = {"watching": "Watching", "completed": "Completed", "planned": "Planned"}[status]
    status_class = {"watching": "status-watching", "completed": "status-completed", "planned": "status-planned"}[status]
    
    # Handle image display
    image_url = None
    if anime.get('image'):
        try:
            image_bytes = anime['image']
            if isinstance(image_bytes, bytes):
                image_b64 = base64.b64encode(image_bytes).decode()
                image_url = f"data:image/jpeg;base64,{image_b64}"
        except:
            pass
    
    card_html = f"""
    <div class="anime-card">
        <div class="anime-image" style="background-image: url('{image_url if image_url else ""}');">
            <div class="anime-image-overlay"></div>
            <div class="status-badge {status_class}">{status_text}</div>
        </div>
        <div class="anime-card-content">
            <h3 class="anime-title">{anime['anime_name']}</h3>
            <div class="anime-stats">
                <span>Seasons: {anime['seasons']}</span>
                <span>Episodes: {anime['finished_episodes']}/{anime['total_episodes']}</span>
            </div>
            <div class="progress-container"><div class="progress-bar" style="width: {progress}%;"></div></div>
            <div style="text-align:center; margin-top:8px; font-size:0.9rem; color:var(--text-muted);">{progress}% complete</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Card actions
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("✏️ Edit", key=f"edit_{index}", on_click=lambda: handle_action(f"edit_{index}", set_view, 'add', edit_index=index), use_container_width=True):
            pass
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{index}", on_click=lambda: handle_action(f"delete_{index}", delete_anime, index), use_container_width=True):
            pass
    with col3:
        if status == "watching" and anime['finished_episodes'] < anime['total_episodes']:
            if st.button("➕", key=f"add_ep_{index}", help="Add episode watched"):
                anime_copy = anime.copy()
                anime_copy['finished_episodes'] = min(anime_copy['finished_episodes'] + 1, anime_copy['total_episodes'])
                save_anime_data(anime_copy, index)
                st.rerun()

def display_section(title, anime_list):
    """Display a section of anime cards with 2 per row"""
    if not anime_list:
        return
        
    st.markdown(f'<div class="section-container">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="anime-grid">', unsafe_allow_html=True)
    
    # Create a container for each anime card
    for i, (idx, anime) in enumerate(anime_list):
        with st.container():
            render_anime_card(idx, anime)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_home_view():
    """Display home view with anime sections"""
    filtered = filter_anime_collection()
    
    if not filtered:
        if st.session_state.search_query:
            st.markdown("""
            <div style="text-align:center; padding:50px 0; background:linear-gradient(145deg, var(--bg-card), var(--bg-input)); border-radius:16px; margin:40px 0;">
                <h3>No anime found matching your search</h3>
                <p style="color:var(--text-muted);">Try a different search term or clear the search</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:50px 0; background:linear-gradient(145deg, var(--bg-card), var(--bg-input)); border-radius:16px; margin:40px 0;">
                <img src="https://i.imgur.com/XJyemeI.png" alt="Empty collection" style="max-width: 200px; margin-bottom: 20px;">
                <h3>Your anime collection is empty</h3>
                <p style="color:var(--text-muted); margin-bottom:20px;">Start tracking your favorite anime by adding them to your collection</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("➕ Add Your First Anime", key="add_first", use_container_width=True):
                handle_action("add_first", set_view, 'add', edit_index=None)
        return
        
    # Filter by status
    watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
    planned = [pair for pair in filtered if get_status(pair[1]) == "planned"]
    completed = [pair for pair in filtered if get_status(pair[1]) == "completed"]
    
    # Display sections with spacing between them
    display_section("Currently Watching", watching)
    display_section("Planned to Watch", planned)
    display_section("Completed", completed)

def display_add_view():
    """Display add/edit anime form with enhanced UI"""
    is_edit = st.session_state.edit_index is not None
    anime_data = st.session_state.anime_collection[st.session_state.edit_index] if is_edit else {
        'anime_name': '', 
        'seasons': 1, 
        'total_episodes': 12, 
        'finished_episodes': 0, 
        'image': None
    }
    
    st.markdown(f"<h2 class='section-header'>{'Edit' if is_edit else 'Add New'} Anime</h2>", unsafe_allow_html=True)
    
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            st.markdown('<p style="margin-bottom: 10px;">Cover Image</p>', unsafe_allow_html=True)
            
            image_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            
            if image_file:
                try:
                    anime_image_bytes = image_file.read()
                    # Process the image to reduce size
                    processed_image = process_image(anime_image_bytes)
                    if processed_image:
                        st.image(processed_image, use_container_width=True)
                        anime_image = processed_image
                    else:
                        st.error("Image processing failed")
                        anime_image = None
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    anime_image = None
            else:
                anime_image = anime_data.get('image') if isinstance(anime_data.get('image'), bytes) else None
                if anime_image:
                    st.image(anime_image, use_container_width=True)
                else:
                    st.markdown("""
                    <div style='height:200px; background:#000000; display:flex; align-items:center; 
                    justify-content:center; border-radius:10px; color:var(--text-muted);'>
                        <div style='text-align:center;'>
                            <div style='font-size:24px; margin-bottom:10px;'>📷</div>
                            <div>No Image</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_form:
            anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''), 
                                       placeholder="Enter anime name")
            
            col1, col2 = st.columns(2)
            with col1:
                seasons = st.number_input("Seasons", min_value=1, value=anime_data.get('seasons', 1))
            with col2:
                total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 12))
            
            finished_episodes = st.slider("Episodes Watched", 0, max(1, total_episodes), 
                                         anime_data.get('finished_episodes', 0))
            
            progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            
            # Show progress bar
            st.markdown(f"""
            <div style='margin-top:20px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                    <span>Progress</span>
                    <span style="font-weight:600; color:var(--primary);">{progress:.1f}%</span>
                </div>
                <div class='progress-container'>
                    <div class='progress-bar' style='width:{progress}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Form buttons
        col_cancel, col_save = st.columns([1, 2])
        with col_cancel:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.view = 'home'
                st.session_state.edit_index = None
                st.rerun()
                
        with col_save:
            submit_button = st.form_submit_button("Save Anime", use_container_width=True)
            
            if submit_button:
                if not anime_name:
                    st.error("Please enter anime name")
                else:
                    new_anime = {
                        'anime_name': anime_name, 
                        'seasons': seasons, 
                        'total_episodes': total_episodes, 
                        'finished_episodes': finished_episodes, 
                        'image': anime_image
                    }
                    save_anime_data(new_anime, st.session_state.edit_index if is_edit else None)
                    st.rerun()

def display_header():
    """Display app header with search and user controls"""
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        # Search input
        search = st.text_input("", value=st.session_state.search_query, 
                              placeholder="🔍 Search your anime collection...", 
                              key="search_input", 
                              on_change=lambda: setattr(st.session_state, 'search_query', st.session_state.search_input),
                              label_visibility="collapsed")
        
        # Update search query in session state
        st.session_state.search_query = search
        
        # Clear search button (separate button instead of inline JavaScript)
        if st.session_state.search_query:
            if st.button("Clear", key="clear_search", help="Clear search"):
                st.session_state.search_query = ""
                st.rerun()
    
    with col2:
        if st.button("➕ Add New", key="add_button", use_container_width=True):
            handle_action("add_new", set_view, 'add', edit_index=None)
    
    with col3:
        if st.button(f"👤 {st.session_state.username}", key="user_button", use_container_width=True):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    
    # User menu dropdown
    if st.session_state.user_menu_visible:
        st.markdown("""
        <div class="user-menu">
            <div class="user-menu-item" onclick="document.getElementById('logout_button').click();">
                Logout
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden button to handle click
        if st.button("Logout", key="logout_button", help="Logout from your account"):
            handle_action("logout", logout)

def render_toasts():
    """Render toast notifications"""
    if st.session_state.toasts:
        for i, toast in enumerate(st.session_state.toasts):
            st.markdown(f"""
            <div class="toast toast-{toast['type']}" style="bottom: {20 + i*60}px">
                {toast['message']}
            </div>
            """, unsafe_allow_html=True)
        
        # Clear toasts after display
        st.session_state.toasts = []

def main_page():
    """Main page rendering"""
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    # Display header with search and user menu
    display_header()
    
    # Display current view
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()
    
    # Display toast notifications
    render_toasts()

# Main app flow
def main():
    if not st.session_state.logged_in:
        auth_page()
    else:
        load_anime_collection()
        main_page()

if __name__ == "__main__":
    main()
