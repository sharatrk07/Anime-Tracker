import streamlit as st
from firebase_config import db
from PIL import Image
import time

# Initialize session state variables
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

# Configure page settings
st.set_page_config(
    page_title="Anime Tracker",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root {
    --primary: #8A4FFF;
    --primary-light: #B088FF;
    --primary-dark: #6A2FFF;
    --secondary: #FF4F8A;
    --secondary-light: #FF88B0;
    --secondary-dark: #FF2F6A;
    --accent: #4FFF8A;
    --accent-light: #88FFB0;
    --accent-dark: #2FFF6A;
    
    --background: #121212;
    --surface: #1E1E1E;
    --surface-variant: #2D2D2D;
    --on-surface: #FFFFFF;
    --on-surface-medium: rgba(255, 255, 255, 0.8);
    --on-surface-disabled: rgba(255, 255, 255, 0.5);
    
    --status-watching: #4FFF8A;
    --status-finished: #4F8AFF;
    --status-upcoming: #FF8A4F;
    
    --elevation-1: 0 2px 4px rgba(0,0,0,0.2);
    --elevation-2: 0 4px 8px rgba(0,0,0,0.3);
    --elevation-3: 0 8px 16px rgba(0,0,0,0.4);
    
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 16px;
    
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
}

.stApp {
    background-color: var(--background);
    color: var(--on-surface);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stButton>button, .stFormSubmit>button {
    background-color: var(--primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton>button:hover, .stFormSubmit>button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--elevation-2);
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, var(--primary-light), var(--secondary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: var(--spacing-md) 0;
    padding: var(--spacing-md);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.section-header {
    font-size: 1.8rem;
    font-weight: 700;
    padding: var(--spacing-sm) var(--spacing-md);
    border-left: 6px solid var(--primary);
    margin: var(--spacing-lg) 0 var(--spacing-md) 0;
    background-color: rgba(138, 79, 255, 0.15);
    border-radius: var(--radius-sm);
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--primary-light);
}

.anime-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.anime-card {
    background-color: var(--surface);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid var(--surface-variant);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.anime-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--elevation-3);
    border-color: var(--primary-light);
}

.anime-image {
    height: 180px;
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    background-color: var(--surface-variant);
    position: relative;
}

.status-overlay {
    position: absolute;
    top: 8px;
    right: 8px;
}

.anime-card-content {
    padding: var(--spacing-md);
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.anime-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
    color: var(--primary-light);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.anime-stats {
    display: flex;
    justify-content: space-between;
    margin: var(--spacing-xs) 0;
    font-size: 0.9rem;
    color: var(--on-surface-medium);
}

.status-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: var(--radius-lg);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    box-shadow: var(--elevation-1);
}

.search-container {
    position: relative;
    margin-bottom: var(--spacing-md);
}

.search-clear {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--on-surface-medium);
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.search-clear:hover {
    color: var(--secondary);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .anime-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def handle_action(action_name, callback_func, *args, **kwargs):
    """Handle button actions with debounce to prevent double presses"""
    current_time = time.time()
    # Prevent double presses by requiring a minimum time between actions
    if current_time - st.session_state.last_action_time > 0.5:
        st.session_state.last_action_time = current_time
        callback_func(*args, **kwargs)
        # Force a rerun after state change
        st.rerun()

def filter_anime_collection():
    """Filter anime collection based on search query"""
    filtered = []
    for idx, anime in enumerate(st.session_state.anime_collection):
        if not st.session_state.search_query or st.session_state.search_query.lower() in anime['anime_name'].lower():
            filtered.append((idx, anime))
    return filtered

def get_status(anime):
    """Determine anime status based on episode progress"""
    if anime['finished_episodes'] == 0:
        return "upcoming"
    elif anime['finished_episodes'] >= anime['total_episodes']:
        return "finished"
    else:
        return "watching"

def calculate_progress(anime):
    """Calculate percentage of completed episodes"""
    if anime['total_episodes'] == 0:
        return 0
    return int((anime['finished_episodes'] / anime['total_episodes']) * 100)

def load_anime_collection():
    """Load user's anime collection from database"""
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc = doc_ref.get()
        if hasattr(doc, 'exists') and doc.exists:
            st.session_state.anime_collection = doc.to_dict().get("anime_collection", [])
        else:
            # Demo data for new users
            st.session_state.anime_collection = [
                {'anime_name': 'Attack on Titan', 'seasons': 4, 'total_episodes': 87, 'finished_episodes': 87, 'image': None},
                {'anime_name': 'My Hero Academia', 'seasons': 6, 'total_episodes': 138, 'finished_episodes': 75, 'image': None},
                {'anime_name': 'Demon Slayer', 'seasons': 3, 'total_episodes': 55, 'finished_episodes': 55, 'image': None},
                {'anime_name': 'Jujutsu Kaisen', 'seasons': 2, 'total_episodes': 36, 'finished_episodes': 0, 'image': None}
            ]
            save_anime_collection()

def save_anime_collection():
    """Save anime collection to database"""
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc_ref.set({"anime_collection": st.session_state.anime_collection})

def save_anime_data(anime_data, edit_index=None):
    """Save new or edited anime data"""
    if edit_index is not None:
        st.session_state.anime_collection[edit_index] = anime_data
    else:
        st.session_state.anime_collection.append(anime_data)
    save_anime_collection()
    st.session_state.view = 'home'
    st.session_state.edit_index = None

def delete_anime(index):
    """Delete anime from collection"""
    st.session_state.anime_collection.pop(index)
    save_anime_collection()
    st.session_state.view = 'home'

def logout():
    """Handle user logout"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.view = 'home'
    st.session_state.edit_index = None
    st.session_state.edit_watched_index = None
    st.session_state.anime_collection = []
    st.session_state.user_menu_visible = False
    st.set_query_params({})

def set_view(view_name, **kwargs):
    """Set the current view with optional parameters"""
    st.session_state.view = view_name
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

# UI Components
def auth_page():
    """Display authentication page"""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">Anime Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; margin-bottom:24px;">Track your favorite anime series in one place</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("Login", key="login_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
    if col2.button("Sign Up", key="signup_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "signup"
    
    if st.session_state.auth_mode == "signup":
        st.markdown('<h2 class="auth-subtitle">Create Account</h2>', unsafe_allow_html=True)
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Create Account", key="submit_signup", use_container_width=True):
            if signup_password != signup_confirm:
                st.error("Passwords do not match")
            elif signup_username and signup_password:
                st.session_state.logged_in = True
                st.session_state.username = signup_username
                save_anime_collection()
                st.rerun()
            else:
                st.error("Please fill in all fields")
    
    elif st.session_state.auth_mode == "login":
        st.markdown('<h2 class="auth-subtitle">Welcome Back</h2>', unsafe_allow_html=True)
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="submit_login", use_container_width=True):
            if login_username and login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                load_anime_collection()
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_anime_card(index, anime):
    progress = calculate_progress(anime)
    progress_class = "progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Plan to Watch"}[status]
    status_class = {"watching": "status-watching", "finished": "status-finished", "upcoming": "status-upcoming"}[status]
    
    # Create placeholder image if none exists
    image_url = "/api/placeholder/400/180"
    if anime.get('image'):
        try:
            image_bytes = anime['image']
            # If image is already in bytes format
            if isinstance(image_bytes, bytes):
                import base64
                image_b64 = base64.b64encode(image_bytes).decode()
                image_url = f"data:image/jpeg;base64,{image_b64}"
        except:
            # If any issue, fall back to placeholder
            pass
    
    # Format the card HTML with proper string substitution
    card_html = f"""
    <div class="anime-card">
        <div class="anime-image" style="background-image: url('{image_url}');">
            <div class="status-overlay">
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
        </div>
        <div class="anime-card-content">
            <h3 class="anime-title">{anime['anime_name']}</h3>
            <div class="anime-stats">
                <span>Seasons: {anime['seasons']}</span>
                <span>Episodes: {anime['finished_episodes']}/{anime['total_episodes']}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar {progress_class}" style="width: {progress}%;"></div>
            </div>
            <div style="text-align:center; font-size:0.8rem; margin:4px 0 12px;">{progress}% complete</div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Create separate buttons directly with Streamlit instead of HTML
    col1, col2 = st.columns(2)
    with col1:
        st.button("✏️ Edit", key=f"edit_visible_{index}", on_click=lambda: handle_action(f"edit_{index}", set_view, 'add', edit_index=index), use_container_width=True)
    with col2:
        st.button("🗑️ Delete", key=f"delete_visible_{index}", on_click=lambda: handle_action(f"delete_{index}", delete_anime, index), use_container_width=True)

def display_section(title, anime_list):
    if not anime_list:
        return
    
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    
    # Create a grid for anime cards (2 columns)
    for i in range(0, len(anime_list), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(anime_list):
                with cols[j]:
                    render_anime_card(anime_list[idx][0], anime_list[idx][1])

def display_home_view():
    """Display home view with categorized anime lists"""
    filtered = filter_anime_collection()
    
    if not filtered:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📺</div>
            <h3>Your collection is empty</h3>
            <p class="empty-state-text">Add your first anime using the button above</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Group anime by status
        watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
        upcoming = [pair for pair in filtered if get_status(pair[1]) == "upcoming"]
        finished = [pair for pair in filtered if get_status(pair[1]) == "finished"]
        
        # Display sections in the preferred order
        display_section("Currently Watching", watching)
        display_section("Upcoming Watchables", upcoming)
        display_section("Completed", finished)

# Enhanced add view with image preview
def display_add_view():
    is_edit = st.session_state.edit_index is not None
    
    if is_edit:
        st.markdown('<h2 class="section-header">Edit Anime</h2>', unsafe_allow_html=True)
        anime_data = st.session_state.anime_collection[st.session_state.edit_index]
    else:
        st.markdown('<h2 class="section-header">Add New Anime</h2>', unsafe_allow_html=True)
        anime_data = {'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None}
    
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            image_file = st.file_uploader("Cover Image", type=["png", "jpg", "jpeg"])
            if image_file is not None:
                anime_image = image_file.read()
                st.image(anime_image, use_container_width=True)
            else:
                anime_image = anime_data.get('image')
                if anime_image:
                    st.image(anime_image, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="height:200px; display:flex; align-items:center; justify-content:center; 
                                background-color:var(--surface-variant); border-radius:var(--radius-md);">
                        <span style="color:var(--on-surface-disabled);">No Image</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_form:
            anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                seasons = st.number_input("Seasons", min_value=1, value=anime_data.get('seasons', 1))
            with col2:
                total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 12))
            
            finished_episodes = st.slider("Episodes Watched", 0, max(total_episodes, 1), anime_data.get('finished_episodes', 0))
            
            progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            st.markdown(f"""
            <div style="margin-top:16px;">
                <p style="text-align:center; margin-bottom:4px;">Progress: {progress:.1f}%</p>
                <div class="progress-container">
                    <div class="progress-bar {"progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"}" style="width: {progress}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Save Anime", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
    
    if submit:
        if not anime_name:
            st.error("Please enter an anime name")
        elif finished_episodes > total_episodes:
            st.error("Episodes watched cannot exceed total episodes")
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
    
    if cancel:
        st.session_state.view = 'home'
        st.session_state.edit_index = None
        st.rerun()

def display_header():
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        search_container = st.container()
        with search_container:
            search_col1, search_col2 = st.columns([6, 1])
            with search_col1:
                search = st.text_input("", value=st.session_state.search_query, 
                                    placeholder="Search your anime collection...", 
                                    key="search_input", 
                                    on_change=lambda: handle_action("search", lambda: None))
            
            if st.session_state.search_query:
                with search_col2:
                    if st.button("✕", key="clear_search"):
                        st.session_state.search_query = ""
                        st.rerun()
    
    with col2:
        if st.button("➕ Add New", key="add_button", use_container_width=True):
            handle_action("add_new", set_view, 'add', edit_index=None)
    
    with col3:
        if st.button(f"👤 {st.session_state.username}", key="user_button", use_container_width=True):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    
    if st.session_state.user_menu_visible:
        st.markdown("""
        <div class="user-menu">
            <div style="font-weight:600; margin-bottom:8px;">User Menu</div>
            <hr style="margin:8px 0; opacity:0.2;">
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="logout_button", use_container_width=True):
            handle_action("logout", logout)

# Updated main_page function
def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    display_header()
    
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()

# Main application flow
if not st.session_state.logged_in:
    auth_page()
else:
    load_anime_collection()
    main_page()
