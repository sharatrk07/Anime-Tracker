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
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'anime_collection' not in st.session_state:
    st.session_state.anime_collection = []
if 'user_menu_visible' not in st.session_state:
    st.session_state.user_menu_visible = False
if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = 0
if 'search_active' not in st.session_state:
    st.session_state.search_active = False

# Configure page settings
st.set_page_config(
    page_title="Anime Tracker",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with better visual hierarchy and modern design
st.markdown("""
<style>
:root {
    --primary: #6C63FF;
    --primary-light: #8F88FF;
    --primary-dark: #4A41FF;
    --secondary: #FF6584;
    --secondary-light: #FF8FA2;
    --secondary-dark: #FF3A66;
    --accent: #00C896;
    --accent-light: #33D3AC;
    --accent-dark: #00A67E;
    
    --background: #F7F9FD;
    --surface: #FFFFFF;
    --surface-variant: #EDF2F7;
    --on-surface: #2D3748;
    --on-surface-medium: #4A5568;
    --on-surface-disabled: #A0AEC0;
    
    --status-watching: #00C896;
    --status-finished: #6C63FF;
    --status-upcoming: #FF6584;
    
    --elevation-1: 0 2px 10px rgba(0,0,0,0.05);
    --elevation-2: 0 4px 15px rgba(0,0,0,0.08);
    --elevation-3: 0 8px 20px rgba(0,0,0,0.12);
    
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 20px;
    
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
}

/* Base styles */
.stApp {
    background-color: var(--background);
    color: var(--on-surface);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Fix Streamlit elements */
.stButton>button, .stFormSubmit>button {
    background-color: var(--primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: var(--elevation-1);
}

.stButton>button:hover, .stFormSubmit>button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--elevation-2);
}

.stButton>button:active, .stFormSubmit>button:active {
    transform: translateY(0);
}

.stTextInput>div>div>input, .stNumberInput>div>div>input {
    background-color: var(--surface);
    border: 1px solid var(--surface-variant);
    border-radius: var(--radius-md);
    color: var(--on-surface);
    padding: 0.7rem;
    box-shadow: var(--elevation-1);
}

.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
    border: 1px solid var(--primary);
    box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2);
}

/* App components */
.app-header {
    background-color: var(--surface);
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--radius-md);
    margin-bottom: var(--spacing-lg);
    box-shadow: var(--elevation-1);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.page-title {
    font-size: 2.4rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: var(--spacing-lg) 0;
    letter-spacing: -0.5px;
}

.section-header {
    font-size: 1.7rem;
    font-weight: 700;
    padding: var(--spacing-md) var(--spacing-lg);
    border-left: 4px solid var(--primary);
    margin: var(--spacing-lg) 0 var(--spacing-md);
    background-color: rgba(108, 99, 255, 0.08);
    border-radius: var(--radius-sm);
    color: var(--primary-dark);
    letter-spacing: -0.5px;
}

.auth-container {
    max-width: 500px;
    margin: 2rem auto;
    padding: var(--spacing-xl);
    background-color: var(--surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--elevation-2);
}

.auth-title {
    color: var(--primary);
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: var(--spacing-lg);
    font-weight: 700;
}

.auth-subtitle {
    color: var(--secondary);
    font-size: 1.6rem;
    margin: var(--spacing-lg) 0 var(--spacing-md);
    font-weight: 600;
}

/* Anime cards */
.anime-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.anime-card {
    background-color: var(--surface);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid var(--surface-variant);
    height: 100%;
    box-shadow: var(--elevation-1);
    display: flex;
    flex-direction: column;
}

.anime-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--elevation-3);
}

.anime-image-container {
    height: 180px;
    overflow: hidden;
    position: relative;
    background-color: var(--surface-variant);
}

.anime-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    transition: transform 0.3s ease;
}

.anime-card:hover .anime-image {
    transform: scale(1.05);
}

.anime-card-content {
    padding: var(--spacing-lg);
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.anime-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: var(--spacing-xs);
    color: var(--primary-dark);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.anime-stats {
    display: flex;
    justify-content: space-between;
    margin: var(--spacing-sm) 0;
    font-size: 0.95rem;
    color: var(--on-surface-medium);
}

.status-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-watching {
    background-color: var(--status-watching);
    color: white;
}

.status-finished {
    background-color: var(--status-finished);
    color: white;
}

.status-upcoming {
    background-color: var(--status-upcoming);
    color: white;
}

.progress-container {
    width: 100%;
    background-color: var(--surface-variant);
    border-radius: 10px;
    height: 8px;
    margin: var(--spacing-md) 0;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

.progress-low {
    background-color: var(--status-upcoming);
}

.progress-medium {
    background-color: var(--primary);
}

.progress-high {
    background-color: var(--status-watching);
}

.anime-card-actions {
    display: flex;
    justify-content: space-between;
    margin-top: var(--spacing-md);
    gap: var(--spacing-sm);
}

.anime-card-actions button {
    flex: 1;
}

.user-menu {
    position: absolute;
    top: 70px;
    right: 16px;
    background-color: var(--surface);
    border-radius: var(--radius-md);
    box-shadow: var(--elevation-3);
    padding: var(--spacing-md);
    z-index: 1000;
    border: 1px solid var(--surface-variant);
    min-width: 220px;
}

.empty-state {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-lg);
    background-color: var(--surface);
    border-radius: var(--radius-lg);
    margin: var(--spacing-xl) 0;
    box-shadow: var(--elevation-1);
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: var(--spacing-md);
    color: var(--primary-light);
}

.empty-state-text {
    color: var(--on-surface-medium);
    font-size: 1.2rem;
    margin-top: var(--spacing-md);
}

.search-container {
    position: relative;
    width: 100%;
}

.search-input {
    width: 100%;
    padding-right: 40px !important;
}

.search-cancel {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--on-surface-medium);
    cursor: pointer;
    font-weight: bold;
    font-size: 1.2rem;
    z-index: 10;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}

.search-cancel:hover {
    color: var(--secondary);
}

.button-primary {
    background-color: var(--primary) !important;
}

.button-secondary {
    background-color: var(--secondary) !important;
}

.button-danger {
    background-color: var(--secondary-dark) !important;
}

.button-success {
    background-color: var(--accent) !important;
}

.button-icon {
    padding: 6px !important;
    min-width: 36px !important;
}

/* Responsive design */
@media (max-width: 992px) {
    .anime-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .section-header {
        font-size: 1.4rem;
        padding: var(--spacing-sm) var(--spacing-md);
    }
    
    .page-title {
        font-size: 2rem;
        margin: var(--spacing-md) 0;
    }
    
    .auth-container {
        padding: var(--spacing-lg);
        margin: 1rem;
        max-width: none;
    }
}

@media (max-width: 576px) {
    .anime-grid {
        grid-template-columns: 1fr;
    }
    
    .anime-card-actions {
        flex-direction: column;
    }
    
    .anime-image-container {
        height: 140px;
    }
    
    .anime-title {
        font-size: 1.2rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def handle_action(action_name, callback_func, *args, **kwargs):
    """Handle button actions with debounce to prevent double presses"""
    current_time = time.time()
    if current_time - st.session_state.last_action_time > 0.8:
        st.session_state.last_action_time = current_time
        callback_func(*args, **kwargs)
        st.rerun()

def filter_anime_collection():
    """Filter anime collection based on search query"""
    filtered = []
    search_term = st.session_state.search_query.lower()
    for idx, anime in enumerate(st.session_state.anime_collection):
        if not search_term or search_term in anime['anime_name'].lower():
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
    st.session_state.anime_collection = []
    st.session_state.user_menu_visible = False
    st.set_query_params({})

def set_view(view_name, **kwargs):
    """Set the current view with optional parameters"""
    st.session_state.view = view_name
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

def clear_search():
    """Clear search query"""
    st.session_state.search_query = ""
    st.session_state.search_active = False
    st.rerun()

# UI Components
def auth_page():
    """Display authentication page"""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">Anime Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; margin-bottom:32px; font-size:1.2rem;">Keep track of your anime journey in one beautiful place</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="login_tab_btn", use_container_width=True):
            st.session_state.auth_mode = "login"
    with col2:
        if st.button("Sign Up", key="signup_tab_btn", use_container_width=True):
            st.session_state.auth_mode = "signup"
    
    if st.session_state.auth_mode == "signup":
        st.markdown('<h2 class="auth-subtitle">Create Account</h2>', unsafe_allow_html=True)
        signup_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
        signup_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a strong password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Re-enter your password")
        
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
        login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
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
    """Render a single anime card"""
    progress = calculate_progress(anime)
    progress_class = "progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Plan to Watch"}[status]
    status_class = {"watching": "status-watching", "finished": "status-finished", "upcoming": "status-upcoming"}[status]
    
    # Prepare image HTML
    image_html = ""
    if anime.get('image'):
        image_html = f"""
        <div class="anime-image-container">
            <img src="data:image/jpeg;base64,{anime['image']}" alt="{anime['anime_name']}" class="anime-image">
        </div>
        """
    else:
        # Default image container with gradient
        image_html = f"""
        <div class="anime-image-container" style="background: linear-gradient(135deg, var(--primary-light), var(--secondary-light));">
            <div style="height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: white; opacity: 0.6;">
                📺
            </div>
        </div>
        """
    
    st.markdown(f"""
    <div class="anime-card">
        {image_html}
        <div class="anime-card-content">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h3 class="anime-title">{anime['anime_name']}</h3>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="anime-stats">
                <span>Seasons: {anime['seasons']}</span>
                <span>Episodes: {anime['finished_episodes']}/{anime['total_episodes']}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar {progress_class}" style="width: {progress}%;"></div>
            </div>
            <div style="text-align:center; font-size:0.9rem; margin:6px 0 16px; color: var(--on-surface-medium);">
                {progress}% complete
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the button handlers in two columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Edit", key=f"edit_{index}", use_container_width=True, help="Edit this anime"):
            handle_action(f"edit_{index}", set_view, 'add', edit_index=index)
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{index}", use_container_width=True, help="Delete this anime"):
            handle_action(f"delete_{index}", delete_anime, index)

def display_section(title, anime_list):
    """Display a section of anime cards"""
    if not anime_list:
        return False
    
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    
    # Create a grid of anime cards (2 per row)
    cols = st.columns(2)
    for i, (idx, anime) in enumerate(anime_list):
        with cols[i % 2]:
            render_anime_card(idx, anime)
    
    return True

def display_home_view():
    """Display home view with categorized anime lists"""
    filtered = filter_anime_collection()
    
    if not filtered:
        if st.session_state.search_active:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No results found</h3>
                <p class="empty-state-text">Try a different search term or clear your search</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📺</div>
                <h3>Your anime collection is empty</h3>
                <p class="empty-state-text">Add your first anime using the "Add New" button above</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Group anime by status
        watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
        upcoming = [pair for pair in filtered if get_status(pair[1]) == "upcoming"]
        finished = [pair for pair in filtered if get_status(pair[1]) == "finished"]
        
        # Display sections in the preferred order
        has_content = False
        if display_section("Currently Watching", watching):
            has_content = True
        if display_section("Plan to Watch", upcoming):
            has_content = True
        if display_section("Completed", finished):
            has_content = True
        
        if not has_content and st.session_state.search_active:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No results found</h3>
                <p class="empty-state-text">Try a different search term or clear your search</p>
            </div>
            """, unsafe_allow_html=True)

def display_add_view():
    """Display add/edit anime form"""
    is_edit = st.session_state.edit_index is not None
    
    if is_edit:
        st.markdown('<h2 class="section-header">Edit Anime</h2>', unsafe_allow_html=True)
        anime_data = st.session_state.anime_collection[st.session_state.edit_index]
    else:
        st.markdown('<h2 class="section-header">Add New Anime</h2>', unsafe_allow_html=True)
        anime_data = {'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None}
    
    with st.form("anime_form", clear_on_submit=False):
        anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''), placeholder="Enter anime title")
        
        col1, col2 = st.columns(2)
        with col1:
            seasons = st.number_input("Seasons", min_value=1, value=anime_data.get('seasons', 1))
        with col2:
            total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 12))
        
        finished_episodes = st.slider("Episodes Watched", 0, max(total_episodes, 1), anime_data.get('finished_episodes', 0))
        
        image_file = st.file_uploader("Cover Image (optional)", type=["png", "jpg", "jpeg"])
        
        if image_file is not None:
            anime_image = image_file.read()
            st.image(anime_image, use_column_width=True, caption="Preview")
        else:
            anime_image = anime_data.get('image')
            if anime_image:
                st.image(anime_image, use_column_width=True, caption="Current Image")
        
        progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
        progress_class = "progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"
        
        st.markdown(f"""
        <div style="margin-top:24px;">
            <p style="text-align:center; margin-bottom:8px; font-weight:600;">Progress: {progress:.1f}%</p>
            <div class="progress-container">
                <div class="progress-bar {progress_class}" style="width: {progress}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
    
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
            st.success(f"{'Updated' if is_edit else 'Added'} \"{anime_name}\" successfully!")
            time.sleep(1)
            st.rerun()
    
    if cancel:
        st.session_state.view = 'home'
        st.session_state.edit_index = None
        st.rerun()

def display_header():
    """Display application header with search and user menu"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_col, clear_col = st.columns([6, 1])
        with search_col:
            search = st.text_input("", value=st.session_state.search_query, 
                                placeholder="Search anime titles...", 
                                key="search_input",
                                on_change=lambda: setattr(st.session_state, 'search_active', bool(st.session_state.search_query)))
        
        with clear_col:
            if st.session_state.search_query:
                if st.button("❌", key="clear_search", help="Clear search"):
                    clear_search()
    
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

def main_page():
    """Main application page"""
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
