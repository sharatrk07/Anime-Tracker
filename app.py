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
    st.session_state.auth_mode = None
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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #8A4FFF;
    --primary-light: #9D6FFF;
    --primary-dark: #7A3FEF;
    --bg-dark: #121212;
    --bg-card: #1E1E1E;
    --bg-input: #2D2D2D;
    --text-light: #FFFFFF;
    --text-muted: #AAAAAA;
    --border: #333333;
}

.stApp {
    background-color: var(--bg-dark);
    color: var(--text-light);
    font-family: 'Poppins', sans-serif;
}

/* Header Styles */
.page-title {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    margin: 20px 0;
    background: linear-gradient(90deg, #8A4FFF, #FF4F8A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(138, 79, 255, 0.3);
}

.section-header {
    font-size: 1.8rem;
    margin-top: 40px;
    margin-bottom: 20px;
    border-left: 5px solid var(--primary);
    padding-left: 12px;
    font-weight: 600;
}

/* Anime Card Styles */
.anime-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.anime-card {
    background-color: var(--bg-card);
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border);
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.anime-card:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
    box-shadow: 0 8px 16px rgba(138, 79, 255, 0.3);
}

.anime-image {
    height: 200px;
    background-size: cover;
    background-position: center;
    position: relative;
    transition: all 0.3s ease;
}

.anime-card:hover .anime-image {
    filter: brightness(1.1);
}

.anime-card-content {
    padding: 20px;
}

.anime-title {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.anime-stats {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    margin-top: 12px;
    color: var(--text-muted);
}

.status-badge {
    background-color: var(--primary);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    text-transform: uppercase;
    font-weight: 600;
    position: absolute;
    top: 10px;
    right: 10px;
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
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    transition: width 0.5s ease;
}

/* Form Styles */
.stTextInput > div > div > input, 
.stNumberInput > div > div > input {
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    color: var(--text-light);
    border-radius: 8px;
    padding: 10px 15px;
}

.stTextInput > div > div > input:focus, 
.stNumberInput > div > div > input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 1px var(--primary);
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 10px 20px;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Auth Styles */
.auth-container {
    max-width: 500px;
    margin: 40px auto;
    padding: 30px;
    background-color: var(--bg-card);
    border-radius: 16px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* Search Bar */
.search-container {
    position: relative;
    margin-bottom: 20px;
}

.search-input {
    width: 100%;
    padding: 12px 20px;
    padding-right: 40px;
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-light);
}

.search-clear {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-light);
    cursor: pointer;
}

/* User Menu */
.user-menu {
    position: absolute;
    right: 20px;
    top: 60px;
    background-color: var(--bg-card);
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    border: 1px solid var(--border);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .page-title {
        font-size: 2.2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
    }
    
    .anime-image {
        height: 160px;
    }
    
    .anime-title {
        font-size: 1.2rem;
    }
    
    .anime-card-content {
        padding: 15px;
    }
}

/* Button Styles */
.primary-btn {
    background-color: var(--primary);
    color: white;
}

.primary-btn:hover {
    background-color: var(--primary-dark);
}

.secondary-btn {
    background-color: transparent;
    border: 1px solid var(--primary);
    color: var(--primary);
}

.secondary-btn:hover {
    background-color: rgba(138, 79, 255, 0.1);
}

/* Image placeholder */
.image-placeholder {
    height: 200px;
    background: linear-gradient(135deg, #2D2D2D 25%, #252525 25%, #252525 50%, #2D2D2D 50%, #2D2D2D 75%, #252525 75%);
    background-size: 20px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-size: 1.2rem;
    border-radius: 8px 8px 0 0;
}

/* Loading animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,.3);
    border-radius: 50%;
    border-top-color: var(--primary);
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}

/* Custom file uploader */
.stFileUploader > div > button {
    background-color: var(--primary);
    color: white;
}

.stFileUploader > div > button:hover {
    background-color: var(--primary-dark);
}

/* Custom slider */
.stSlider > div > div > div > div {
    background-color: var(--primary);
}

/* Custom progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
}
</style>
""", unsafe_allow_html=True)

# Helper functions
def compress_image(image_bytes, max_size_mb=2):
    """Compress image to reduce size"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Calculate current size in MB
        current_size_mb = len(image_bytes) / (1024 * 1024)
        
        if current_size_mb <= max_size_mb:
            return image_bytes
        
        # Calculate compression quality based on size
        quality = int(90 * (max_size_mb / current_size_mb))
        quality = max(10, min(quality, 85))  # Keep quality between 10 and 85
        
        # Resize if image is very large
        max_dimension = 1200
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Convert to RGB if RGBA
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        # Save with compression
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error compressing image: {e}")
        return None

def handle_action(action_name, callback_func, *args, **kwargs):
    current_time = time.time()
    if current_time - st.session_state.last_action_time > 0.5:
        st.session_state.last_action_time = current_time
        callback_func(*args, **kwargs)
        st.rerun()

def filter_anime_collection():
    filtered = []
    for idx, anime in enumerate(st.session_state.anime_collection):
        if not st.session_state.search_query or st.session_state.search_query.lower() in anime['anime_name'].lower():
            filtered.append((idx, anime))
    return filtered

def get_status(anime):
    if anime['finished_episodes'] == 0:
        return "upcoming"
    elif anime['finished_episodes'] >= anime['total_episodes']:
        return "finished"
    else:
        return "watching"

def calculate_progress(anime):
    if anime['total_episodes'] == 0:
        return 0
    return int((anime['finished_episodes'] / anime['total_episodes']) * 100)

def load_anime_collection():
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc = doc_ref.get()
        if hasattr(doc, 'exists') and doc.exists:
            anime_collection = doc.to_dict().get("anime_collection", [])
            for anime in anime_collection:
                if isinstance(anime.get('image'), str) and anime['image']:
                    try:
                        anime['image'] = base64.b64decode(anime['image'])
                    except:
                        anime['image'] = None
                else:
                    anime['image'] = None
            st.session_state.anime_collection = anime_collection
        else:
            st.session_state.anime_collection = []

def save_anime_collection():
    if st.session_state.username:
        anime_collection_serializable = []
        for anime in st.session_state.anime_collection:
            anime_copy = anime.copy()
            if isinstance(anime_copy.get('image'), bytes):
                anime_copy['image'] = base64.b64encode(anime_copy['image']).decode('utf-8')
            elif anime_copy.get('image') is None:
                anime_copy['image'] = ""
            anime_collection_serializable.append(anime_copy)
        doc_ref = db.collection("users").document(st.session_state.username)
        doc_ref.set({"anime_collection": anime_collection_serializable})

def save_anime_data(anime_data, edit_index=None):
    if edit_index is not None:
        st.session_state.anime_collection[edit_index] = anime_data
    else:
        st.session_state.anime_collection.append(anime_data)
    save_anime_collection()
    st.session_state.view = 'home'
    st.session_state.edit_index = None

def delete_anime(index):
    st.session_state.anime_collection.pop(index)
    save_anime_collection()
    st.session_state.view = 'home'

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.view = 'home'
    st.session_state.edit_index = None
    st.session_state.edit_watched_index = None
    st.session_state.anime_collection = []
    st.session_state.user_menu_visible = False
    st.set_query_params({})

def set_view(view_name, **kwargs):
    st.session_state.view = view_name
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

# Authentication page
def auth_page():
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
    
    if col1.button("Login", key="login_tab_btn", use_container_width=True, 
                  help="Login with your existing account"):
        st.session_state.auth_mode = "login"
    
    if col2.button("Sign Up", key="signup_tab_btn", use_container_width=True,
                  help="Create a new account"):
        st.session_state.auth_mode = "signup"
    
    st.markdown('<div style="margin: 20px 0; border-bottom: 1px solid #333;"></div>', unsafe_allow_html=True)
    
    # Login form
    if st.session_state.auth_mode == "login":
        st.markdown('<h3 style="text-align: center; margin-bottom: 20px;">Welcome Back!</h3>', unsafe_allow_html=True)
        login_username = st.text_input("Username", key="login_username", 
                                     placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_password",
                                     placeholder="Enter your password")
        
        login_btn = st.button("Login", key="submit_login", use_container_width=True)
        
        if login_btn:
            if login_username and login_password:
                with st.spinner("Logging in..."):
                    # Add a small delay to simulate authentication
                    time.sleep(0.5)
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    load_anime_collection()
                    st.rerun()
            else:
                st.error("Please enter both username and password")
    
    # Signup form
    elif st.session_state.auth_mode == "signup":
        st.markdown('<h3 style="text-align: center; margin-bottom: 20px;">Create Your Account</h3>', unsafe_allow_html=True)
        signup_username = st.text_input("Username", key="signup_username", 
                                      placeholder="Choose a username")
        signup_password = st.text_input("Password", type="password", key="signup_password",
                                      placeholder="Create a password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm",
                                     placeholder="Confirm your password")
        
        signup_btn = st.button("Create Account", key="submit_signup", use_container_width=True)
        
        if signup_btn:
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
                    st.success("Account created successfully!")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Render anime card
def render_anime_card(index, anime):
    progress = calculate_progress(anime)
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Planned"}[status]
    status_colors = {
        "watching": "#4F8AFF", 
        "finished": "#4FFF8A", 
        "upcoming": "#FF4F8A"
    }
    
    # Default placeholder image
    image_url = "https://i.imgur.com/JIoMJWD.png"
    
    # Try to use the anime's image if available
    if anime.get('image'):
        try:
            image_bytes = anime['image']
            if isinstance(image_bytes, bytes):
                image_b64 = base64.b64encode(image_bytes).decode()
                image_url = f"data:image/jpeg;base64,{image_b64}"
        except:
            pass
    
    # Create the anime card with enhanced styling
    card_html = f"""
    <div class="anime-card">
        <div class="anime-image" style="background-image: url('{image_url}');">
            <div class="status-badge" style="background-color: {status_colors[status]};">{status_text}</div>
        </div>
        <div class="anime-card-content">
            <h3 class="anime-title">{anime['anime_name']}</h3>
            <div class="anime-stats">
                <span>Seasons: {anime['seasons']}</span>
                <span>Episodes: {anime['finished_episodes']}/{anime['total_episodes']}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress}%;"></div>
            </div>
            <div style="text-align:center; margin-top:8px; font-size: 0.9rem; color: #AAAAAA;">
                {progress}% complete
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("✏️ Edit", key=f"edit_{index}", 
                on_click=lambda: handle_action(f"edit_{index}", set_view, 'add', edit_index=index), 
                use_container_width=True)
    with col2:
        st.button("🗑️ Delete", key=f"delete_{index}", 
                on_click=lambda: handle_action(f"delete_{index}", delete_anime, index), 
                use_container_width=True)

# Display anime sections
def display_section(title, anime_list):
    if not anime_list:
        return
    
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    
    # Create a responsive grid layout
    cols = st.columns(3)
    for i, (idx, anime) in enumerate(anime_list):
        with cols[i % 3]:
            render_anime_card(idx, anime)

# Home view
def display_home_view():
    filtered = filter_anime_collection()
    
    if not filtered:
        st.markdown("""
        <div style="text-align: center; padding: 50px 20px; background-color: #1E1E1E; border-radius: 16px; margin: 40px 0;">
            <img src="https://i.imgur.com/XJyemeI.png" alt="Empty collection" style="max-width: 200px; margin-bottom: 20px;">
            <h3>Your anime collection is empty</h3>
            <p style="color: #AAAAAA; margin-bottom: 20px;">Start tracking your favorite anime by adding them to your collection.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Add Your First Anime", key="add_first", use_container_width=True):
            handle_action("add_first", set_view, 'add', edit_index=None)
        return
    
    # Filter by status
    watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
    upcoming = [pair for pair in filtered if get_status(pair[1]) == "upcoming"]
    finished = [pair for pair in filtered if get_status(pair[1]) == "finished"]
    
    # Display sections
    display_section("Currently Watching", watching)
    display_section("Planned to Watch", upcoming)
    display_section("Completed", finished)

# Add/Edit anime view
def display_add_view():
    is_edit = st.session_state.edit_index is not None
    anime_data = st.session_state.anime_collection[st.session_state.edit_index] if is_edit else {
        'anime_name': '', 
        'seasons': 1, 
        'total_episodes': 12, 
        'finished_episodes': 0, 
        'image': None
    }
    
    st.markdown(f'<h2 class="section-header">{"Edit" if is_edit else "Add New"} Anime</h2>', unsafe_allow_html=True)
    
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            st.markdown('<p style="margin-bottom: 10px;">Cover Image</p>', unsafe_allow_html=True)
            
            image_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            
            if image_file:
                try:
                    anime_image_bytes = image_file.read()
                    # Compress image to avoid size issues
                    anime_image = compress_image(anime_image_bytes)
                    if anime_image:
                        st.image(anime_image, use_container_width=True)
                    else:
                        st.error("Failed to process image. Please try a smaller image.")
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
                    <div class="image-placeholder">
                        <div>No Image Selected</div>
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
            
            finished_episodes = st.slider("Episodes Watched", 0, total_episodes, anime_data.get('finished_episodes', 0))
            
            progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            st.markdown(f"""
            <div style="margin-top:16px; display: flex; justify-content: space-between; align-items: center;">
                <span>Progress:</span>
                <span style="font-weight: 600; color: #8A4FFF;">{progress:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress/100.0)
        
        # Form buttons
        col_save, col_cancel = st.columns(2)
        with col_save:
            save_btn = st.form_submit_button("Save Anime", use_container_width=True)
        with col_cancel:
            cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
        
        if save_btn:
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
                st.success(f"Anime {'updated' if is_edit else 'added'} successfully!")
                st.rerun()
        
        if cancel_btn:
            st.session_state.view = 'home'
            st.session_state.edit_index = None
            st.rerun()

# Header with search and user menu
def display_header():
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        # Enhanced search input
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        search = st.text_input("", value=st.session_state.search_query, 
                             placeholder="🔍 Search your anime collection...", 
                             key="search_input", 
                             on_change=lambda: handle_action("search", lambda: None),
                             label_visibility="collapsed")
        
        # Update search query in session state
        st.session_state.search_query = search
        
        # Clear search button
        if st.session_state.search_query:
            st.markdown(
                f"""
                <button class="search-clear" onclick="document.querySelector('input[aria-label="search_input"]').value = ''; 
                document.querySelector('input[aria-label="search_input"]').dispatchEvent(new Event('input'));">
                    ✕
                </button>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Add new anime button
        if st.button("➕ Add", key="add_button", use_container_width=True,
                   help="Add a new anime to your collection"):
            handle_action("add_new", set_view, 'add', edit_index=None)
    
    with col3:
        # User menu button
        if st.button(f"👤", key="user_button", use_container_width=True,
                   help=f"Logged in as {st.session_state.username}"):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    
    # User menu dropdown
    if st.session_state.user_menu_visible:
        st.markdown("""
        <div class="user-menu">
            <div style="padding: 10px; text-align: center; border-bottom: 1px solid #333; margin-bottom: 10px;">
                <span style="font-weight: 600;">👤 {}</span>
            </div>
            <div style="padding: 5px 10px;">
                <button class="stButton secondary-btn" style="width: 100%;">Logout</button>
            </div>
        </div>
        """.format(st.session_state.username), unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button", use_container_width=True):
            handle_action("logout", logout)

# Main page with header and content
def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    display_header()
    
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()

# Main app logic
def main():
    if not st.session_state.logged_in:
        auth_page()
    else:
        load_anime_collection()
        main_page()

if __name__ == "__main__":
    main()
