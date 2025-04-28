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

# Enhanced CSS with better visual hierarchy and modern design
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
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
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
    padding: 0.5rem;
}

.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
    border: 1px solid var(--primary);
}

/* App components */
.app-header {
    background-color: var(--surface);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    margin-bottom: var(--spacing-lg);
    box-shadow: var(--elevation-1);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, var(--primary-light), var(--secondary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: var(--spacing-md) 0;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.category-title {
    font-size: 1.8rem;
    font-weight: 700;
    padding: var(--spacing-sm) var(--spacing-md);
    border-left: 6px solid var(--primary);
    margin: var(--spacing-lg) 0 var(--spacing-md);
    background-color: rgba(138, 79, 255, 0.15);
    border-radius: var(--radius-md);
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--primary-light);
    box-shadow: var(--elevation-1);
}

.auth-container {
    max-width: 500px;
    margin: 0 auto;
    padding: var(--spacing-lg);
    background-color: var(--surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--elevation-2);
}

.auth-title {
    color: var(--primary);
    text-align: center;
    font-size: 2rem;
    margin-bottom: var(--spacing-lg);
}

.auth-subtitle {
    color: var(--secondary);
    font-size: 1.5rem;
    margin: var(--spacing-lg) 0 var(--spacing-md);
}

/* Anime cards */
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
}

.anime-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--elevation-3);
}

.anime-image {
    width: 150px;
    height: 200px;
    object-fit: cover;
    background-color: var(--surface-variant);
}

.anime-card-content {
    padding: var(--spacing-md);
    flex: 1;
}

.anime-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
    color: var(--primary-light);
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
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05rem;
}

.status-watching {
    background-color: var(--status-watching);
    color: #000000;
}

.status-finished {
    background-color: var(--status-finished);
    color: #FFFFFF;
}

.status-upcoming {
    background-color: var(--status-upcoming);
    color: #000000;
}

.progress-container {
    width: 100%;
    background-color: var(--surface-variant);
    border-radius: var(--radius-sm);
    height: 8px;
    margin: var(--spacing-sm) 0;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: var(--radius-sm);
    transition: width 0.3s ease;
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
}

.user-menu {
    position: absolute;
    top: 60px;
    right: 10px;
    background-color: var(--surface);
    border-radius: var(--radius-md);
    box-shadow: var(--elevation-3);
    padding: var(--spacing-md);
    z-index: 1000;
    border: 1px solid var(--surface-variant);
    min-width: 200px;
}

.empty-state {
    text-align: center;
    padding: var(--spacing-xl);
    background-color: var(--surface);
    border-radius: var(--radius-md);
    margin: var(--spacing-lg) 0;
}

.empty-state-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
    color: var(--on-surface-disabled);
}

.empty-state-text {
    color: var(--on-surface-medium);
    font-size: 1.1rem;
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

.button-icon {
    padding: 6px !important;
    min-width: 36px !important;
}

.search-container {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.search-input {
    flex: 1;
}

.search-cancel-button {
    width: 40px;
}

.form-row {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.form-group {
    flex: 1;
}

/* Default image placeholder */
.image-placeholder {
    background: linear-gradient(135deg, var(--surface-variant), var(--surface));
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--on-surface-disabled);
    font-size: 2rem;
}

/* Responsive design */
@media (max-width: 992px) {
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

def clear_search():
    """Clear search query"""
    st.session_state.search_query = ""
    st.rerun()

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
    """Render a single anime card with image"""
    progress = calculate_progress(anime)
    progress_class = "progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Plan to Watch"}[status]
    status_class = {"watching": "status-watching", "finished": "status-finished", "upcoming": "status-upcoming"}[status]
    
    with st.container():
        st.markdown(f"""
        <div class="anime-card">
            <div class="image-placeholder" style="width:150px; height:200px; display:flex; justify-content:center; align-items:center;">
                <span>🎬</span>
            </div>
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
                <div style="text-align:center; font-size:0.8rem; margin:4px 0 12px;">{progress}% complete</div>
                <div style="display:flex; gap:8px; margin-top:12px;">
                    <button style="flex:1; background-color:var(--primary); border:none; color:white; padding:8px; border-radius:4px; cursor:pointer;" 
                            onclick="handleEdit_{index}()">✏️ Edit</button>
                    <button style="flex:1; background-color:var(--secondary-dark); border:none; color:white; padding:8px; border-radius:4px; cursor:pointer;" 
                            onclick="handleDelete_{index}()">🗑️ Delete</button>
                </div>
            </div>
        </div>
        <script>
            function handleEdit_{index}() {{
                const elements = parent.document.getElementsByTagName('button');
                for (let i = 0; i < elements.length; i++) {{
                    if (elements[i].innerText.includes('✏️ Edit') && elements[i].key === 'edit_{index}') {{
                        elements[i].click();
                        break;
                    }}
                }}
            }}
            function handleDelete_{index}() {{
                const elements = parent.document.getElementsByTagName('button');
                for (let i = 0; i < elements.length; i++) {{
                    if (elements[i].innerText.includes('🗑️ Delete') && elements[i].key === 'delete_{index}') {{
                        elements[i].click();
                        break;
                    }}
                }}
            }}
        </script>
        """, unsafe_allow_html=True)
        
        # Hidden buttons for JavaScript to click
        col1, col2 = st.columns(2)
        with col1:
            st.button("✏️ Edit", key=f"edit_{index}", use_container_width=True, on_click=handle_action, args=(f"edit_{index}", set_view, 'add'), kwargs={"edit_index": index})
        with col2:
            st.button("🗑️ Delete", key=f"delete_{index}", use_container_width=True, on_click=handle_action, args=(f"delete_{index}", delete_anime, index))
        
        # Display image if available
        if anime.get('image'):
            st.image(anime['image'], use_column_width=True)

def display_section(title, anime_list):
    """Display a section of anime cards in a 2-column grid"""
    if not anime_list:
        return
    
    st.markdown(f'<h2 class="category-title">{title}</h2>', unsafe_allow_html=True)
    
    # Create a grid of anime cards, 2 per row
    rows = []
    for i in range(0, len(anime_list), 2):
        row = anime_list[i:i+2]
        rows.append(row)
    
    for row in rows:
        cols = st.columns(2)
        for i, (idx, anime) in enumerate(row):
            with cols[i]:
                render_anime_card(idx, anime)

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

def display_add_view():
    """Display add/edit anime form"""
    is_edit = st.session_state.edit_index is not None
    
    if is_edit:
        st.markdown('<h2 class="category-title">Edit Anime</h2>', unsafe_allow_html=True)
        anime_data = st.session_state.anime_collection[st.session_state.edit_index]
    else:
        st.markdown('<h2 class="category-title">Add New Anime</h2>', unsafe_allow_html=True)
        anime_data = {'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None}
    
    with st.form("anime_form", clear_on_submit=False):
        anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            seasons = st.number_input("Seasons", min_value=1, value=anime_data.get('seasons', 1))
        with col2:
            total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 12))
        
        finished_episodes = st.slider("Episodes Watched", 0, max(total_episodes, 1), anime_data.get('finished_episodes', 0))
        
        image_file = st.file_uploader("Cover Image (optional)", type=["png", "jpg", "jpeg"])
        
        if image_file is not None:
            anime_image = image_file.read()
            st.image(anime_image, width=150)
        else:
            anime_image = anime_data.get('image')
            if anime_image:
                st.image(anime_image, width=150)
        
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
            submit = st.form_submit_button("Save", use_container_width=True)
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
    """Display application header with search and user menu"""
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        search_col1, search_col2 = st.columns([5, 1])
        with search_col1:
            search = st.text_input("", value=st.session_state.search_query, 
                                  placeholder="Search your anime collection...", 
                                  key="search_input",
                                  on_change=lambda: st.rerun())
            if search != st.session_state.search_query:
                st.session_state.search_query = search
        
        with search_col2:
            if st.session_state.search_query:
                if st.button("❌", key="clear_search", use_container_width=True):
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
