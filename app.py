import streamlit as st
from firebase_config import db
from PIL import Image
import base64
import time
import io

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

st.set_page_config(
    page_title="Anime Tracker", 
    page_icon="🎬", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0F0F13; 
        color: #EAEAEA; 
        font-family: 'Poppins', sans-serif;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1E1E2E;
    }
    ::-webkit-scrollbar-thumb {
        background: #6B46C1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #805AD5;
    }
    
    .page-title {
        font-size: 3rem; 
        font-weight: 700; 
        text-align: center; 
        margin: 24px 0;
        background: linear-gradient(90deg, #6B46C1, #D53F8C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(107, 70, 193, 0.2);
    }
    
    .section-header {
        font-size: 1.8rem; 
        margin-top: 40px; 
        margin-bottom: 24px; 
        border-left: 5px solid #6B46C1; 
        padding-left: 12px;
        color: #EAEAEA;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .anime-grid-container {
        padding: 0 10px;
        margin-bottom: 40px;
    }
    
    .anime-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 30px;
        width: 100%;
    }
    
    .anime-card {
        background: linear-gradient(145deg, #1A1A27, #28293D);
        border-radius: 12px; 
        overflow: hidden; 
        border: 1px solid #28293D;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .anime-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(107, 70, 193, 0.4);
        border-color: #6B46C1;
    }
    
    .anime-image {
        height: 180px; 
        background-size: cover; 
        background-position: center;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .anime-card:hover .anime-image {
        filter: brightness(1.1);
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
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    
    .anime-title {
        font-size: 1.4rem; 
        font-weight: 700; 
        margin-bottom: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #FFFFFF;
    }
    
    .anime-stats {
        display: flex; 
        justify-content: space-between; 
        font-size: 0.9rem; 
        margin-top: 12px;
        color: #B9B9C3;
    }
    
    .status-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        background-color: #6B46C1; 
        color: white;
        padding: 4px 12px; 
        border-radius: 999px; 
        font-size: 0.7rem; 
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 3px 10px rgba(107, 70, 193, 0.4);
        transition: all 0.3s ease;
    }
    
    .anime-card:hover .status-badge {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(107, 70, 193, 0.6);
    }
    
    .badge-watching {
        background: linear-gradient(90deg, #6B46C1, #805AD5);
    }
    
    .badge-finished {
        background: linear-gradient(90deg, #48BB78, #38A169);
    }
    
    .badge-upcoming {
        background: linear-gradient(90deg, #DD6B20, #ED8936);
    }
    
    .progress-container {
        background-color: #2D2D3D; 
        border-radius: 999px; 
        overflow: hidden; 
        margin-top: 12px; 
        height: 8px;
    }
    
    .progress-bar {
        height: 8px; 
        background: linear-gradient(90deg, #6B46C1, #D53F8C);
        border-radius: 999px;
        transition: width 0.5s ease;
    }
    
    .stTextInput > div > div > input {
        background-color: #1A1A27;
        color: #EAEAEA;
        border: 1px solid #2D2D3D;
        border-radius: 8px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6B46C1;
        box-shadow: 0 0 0 2px rgba(107, 70, 193, 0.3);
    }
    
    .stFileUploader > div {
        background-color: #1A1A27;
        border: 1px dashed #6B46C1;
        border-radius: 8px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        background-color: #28293D;
        border-color: #805AD5;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #6B46C1, #805AD5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #805AD5, #6B46C1);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(107, 70, 193, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(107, 70, 193, 0.4);
    }
    
    .auth-container {
        max-width: 500px;
        margin: 60px auto;
        padding: 40px;
        background: linear-gradient(145deg, #1A1A27, #28293D);
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .auth-container:hover {
        box-shadow: 0 15px 40px rgba(107, 70, 193, 0.3);
    }
    
    .auth-tab {
        background-color: #28293D;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .search-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    .search-clear {
        position: absolute; 
        right: 10px; 
        top: 50%; 
        transform: translateY(-50%); 
        background: none; 
        border: none; 
        color: #EAEAEA;
        cursor: pointer;
        font-size: 18px;
    }
    
    .user-menu {
        position: absolute;
        right: 20px;
        top: 60px;
        background: #1A1A27;
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
        z-index: 1000;
        min-width: 150px;
        border: 1px solid #2D2D3D;
        animation: fadeIn 0.2s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-menu-item {
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .user-menu-item:hover {
        background-color: #2D2D3D;
        color: #6B46C1;
    }
    
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
        border-top-color: #6B46C1;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #28293D;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }
    
    .toast-success {
        border-left: 4px solid #48BB78;
    }
    
    .toast-error {
        border-left: 4px solid #E53E3E;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    .card-actions {
        margin-top: auto;
    }
    
    @media (max-width: 768px) {
        .page-title {
            font-size: 2.2rem;
        }
        
        .section-header {
            font-size: 1.5rem;
        }
        
        .anime-grid {
            grid-template-columns: 1fr;
        }
        
        .auth-container {
            padding: 20px;
            margin: 30px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

def process_image(image_data):
    if not image_data:
        return None
        
    try:
        if isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            return None
            
        max_size = (800, 600)
        img.thumbnail(max_size, Image.LANCZOS)
        
        output = io.BytesIO()
        img.convert('RGB').save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return None

def image_to_base64(image_bytes):
    if not image_bytes:
        return None
    try:
        return base64.b64encode(image_bytes).decode()
    except:
        return None

def base64_to_bytes(base64_str):
    if not base64_str:
        return None
    try:
        return base64.b64decode(base64_str)
    except:
        return None

def show_toast(message, type="success"):
    st.session_state.toasts.append({"message": message, "type": type})

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
    st.session_state.view = view_name
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

def auth_page():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("Login", key="login_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
    if col2.button("Sign Up", key="signup_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "signup"
    
    if st.session_state.auth_mode == "login":
        with st.container():
            st.markdown("### Login to Your Account")
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                login_button = st.button("Login", key="submit_login", use_container_width=True)
                if login_button:
                    if login_username and login_password:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        load_anime_collection()
                        show_toast(f"Welcome back, {login_username}!")
                        st.rerun()
                    else:
                        st.error("Please enter both username and password")
            with col2:
                guest_button = st.button("Guest Login", key="guest_login")
                if guest_button:
                    st.session_state.logged_in = True
                    st.session_state.username = "guest_user"
                    load_anime_collection()
                    show_toast("Logged in as guest")
                    st.rerun()
    
    elif st.session_state.auth_mode == "signup":
        with st.container():
            st.markdown("### Create New Account")
            signup_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
            signup_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Confirm your password")
            
            if st.button("Create Account", key="submit_signup", use_container_width=True):
                if not signup_username:
                    st.error("Please enter a username")
                elif not signup_password:
                    st.error("Please enter a password")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = signup_username
                    save_anime_collection()
                    show_toast(f"Welcome, {signup_username}! Account created successfully")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_anime_card(index, anime):
    progress = calculate_progress(anime)
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Planned"}[status]
    status_class = {"watching": "badge-watching", "finished": "badge-finished", "upcoming": "badge-upcoming"}[status]
    
    image_url = "/api/placeholder/400/180"
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
        <div class="anime-image" style="background-image: url('{image_url}');">
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
            <div style="text-align:center; margin-top:8px; font-size:0.9rem; color:#B9B9C3;">{progress}% complete</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
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

def display_responsive_section(title, anime_list):
    if not anime_list:
        return
        
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="anime-grid-container">', unsafe_allow_html=True)
    st.markdown('<div class="anime-grid">', unsafe_allow_html=True)
    
    for i, (idx, anime) in enumerate(anime_list):
        with st.container():
            render_anime_card(idx, anime)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_home_view():
    filtered = filter_anime_collection()
    
    if not filtered:
        if st.session_state.search_query:
            st.markdown("""
            <div style="text-align:center; padding:50px 0;">
                <h3>No anime found matching your search</h3>
                <p>Try a different search term or clear the search</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:50px 0;">
                <h3>Your anime collection is empty</h3>
                <p>Add your favorite anime by clicking the "+ Add New" button above</p>
            </div>
            """, unsafe_allow_html=True)
        return
        
    watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
    upcoming = [pair for pair in filtered if get_status(pair[1]) == "upcoming"]
    finished = [pair for pair in filtered if get_status(pair[1]) == "finished"]
    
    display_responsive_section("Currently Watching", watching)
    display_responsive_section("Planned to Watch", upcoming)
    display_responsive_section("Completed", finished)

def display_add_view():
    is_edit = st.session_state.edit_index is not None
    anime_data = st.session_state.anime_collection[st.session_state.edit_index] if is_edit else {
        'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None
    }
    
    st.markdown(f"<h2 class='section-header'>{'Edit' if is_edit else 'Add New'} Anime</h2>", unsafe_allow_html=True)
    
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            image_file = st.file_uploader("Cover Image", type=["png", "jpg", "jpeg"])
            
            if image_file:
                anime_image = image_file.read()
                processed_image = process_image(anime_image)
                if processed_image:
                    st.image(processed_image, use_container_width=True)
                    anime_image = processed_image
                else:
                    st.error("Image processing failed")
                    anime_image = None
            else:
                anime_image = anime_data.get('image') if isinstance(anime_data.get('image'), bytes) else None
                if anime_image:
                    st.image(anime_image, use_container_width=True)
                else:
                    st.markdown("""
                    <div style='height:200px; background:#2D2D3D; display:flex; align-items:center; 
                    justify-content:center; border-radius:10px; color:#B9B9C3;'>
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
            
            st.markdown(f"""
            <div style='margin-top:20px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                    <span>Progress</span>
                    <span>{progress:.1f}%</span>
                </div>
                <div class='progress-container'>
                    <div class='progress-bar' style='width:{progress}%;'></div>
                </div>
            </div>
            """,  style='width:{progress}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        search_container = st.container()
        search = st.text_input("", value=st.session_state.search_query, 
                              placeholder="Search your anime collection...", 
                              key="search_input", 
                              on_change=lambda: setattr(st.session_state, 'search_query', st.session_state.search_input))
        
        if st.session_state.search_query:
            clear_search = st.button("✕", key="clear_search", help="Clear search")
            if clear_search:
                st.session_state.search_query = ""
                st.rerun()
    
    with col2:
        if st.button("➕ Add New", key="add_button", use_container_width=True):
            handle_action("add_new", set_view, 'add', edit_index=None)
    
    with col3:
        if st.button(f"👤 {st.session_state.username}", key="user_button", use_container_width=True):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    
    if st.session_state.user_menu_visible:
        st.markdown('''
        <div class="user-menu">
            <div class="user-menu-item" onclick="document.getElementById('logout_button').click();">
                Logout
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button", help="Logout from your account"):
            handle_action("logout", logout)

def render_toasts():
    if st.session_state.toasts:
        for i, toast in enumerate(st.session_state.toasts):
            st.markdown(f'''
                <div class="toast toast-{toast['type']}" style="bottom: {20 + i*60}px">
                    {toast['message']}
                </div>
            ''', unsafe_allow_html=True)
        st.session_state.toasts = []


def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    display_header()
    
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()
    
    render_toasts()

if not st.session_state.logged_in:
    auth_page()
else:
    load_anime_collection()
    main_page()
