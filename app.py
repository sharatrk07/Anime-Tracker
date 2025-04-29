import streamlit as st
from firebase_config import db
from PIL import Image
import base64
import time

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

st.set_page_config(page_title="Anime Tracker", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp {background-color: #121212; color: white; font-family: 'Inter', sans-serif;}
.page-title {font-size: 2.8rem; font-weight: 700; text-align: center; margin: 20px 0;}
.section-header {font-size: 1.8rem; margin-top: 40px; margin-bottom: 20px; border-left: 5px solid #8A4FFF; padding-left: 12px;}
.anime-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;}
.anime-card {background-color: #1E1E1E; border-radius: 12px; overflow: hidden; border: 1px solid #333;}
.anime-card:hover {border-color: #8A4FFF;}
.anime-image {height: 180px; background-size: cover; background-position: center;}
.anime-card-content {padding: 16px;}
.anime-title {font-size: 1.4rem; font-weight: 600; margin-bottom: 8px;}
.anime-stats {display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 8px;}
.status-badge {background-color: #8A4FFF; padding: 4px 10px; border-radius: 999px; font-size: 0.7rem; text-transform: uppercase;}
.progress-container {background-color: #2D2D2D; border-radius: 999px; overflow: hidden; margin-top: 8px; height: 8px;}
.progress-bar {height: 8px; background-color: #8A4FFF;}
.search-clear {position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: white;}
@media (max-width: 768px) {.anime-grid {grid-template-columns: 1fr;}}
</style>
""", unsafe_allow_html=True)

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
            elif isinstance(anime_copy.get('image'), str) and len(anime_copy.get('image')) > 1000000:
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

def auth_page():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("Login", key="login_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
    if col2.button("Sign Up", key="signup_tab_btn", use_container_width=True):
        st.session_state.auth_mode = "signup"
    if st.session_state.auth_mode == "signup":
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Create Account", key="submit_signup", use_container_width=True):
            if signup_password == signup_confirm and signup_username and signup_password:
                st.session_state.logged_in = True
                st.session_state.username = signup_username
                save_anime_collection()
                st.rerun()
    elif st.session_state.auth_mode == "login":
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="submit_login", use_container_width=True):
            if login_username and login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                load_anime_collection()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_anime_card(index, anime):
    progress = calculate_progress(anime)
    status = get_status(anime)
    status_text = {"watching": "Watching", "finished": "Completed", "upcoming": "Planned"}[status]
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
        <div class="anime-image" style="background-image: url('{image_url}');"></div>
        <div class="anime-card-content">
            <h3 class="anime-title">{anime['anime_name']}</h3>
            <div class="anime-stats">
                <span>Seasons: {anime['seasons']}</span>
                <span>Episodes: {anime['finished_episodes']}/{anime['total_episodes']}</span>
            </div>
            <div class="progress-container"><div class="progress-bar" style="width: {progress}%;"></div></div>
            <div style="text-align:center; margin-top:4px;">{progress}% complete</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button("✏️ Edit", key=f"edit_{index}", on_click=lambda: handle_action(f"edit_{index}", set_view, 'add', edit_index=index), use_container_width=True)
    with col2:
        st.button("🗑️ Delete", key=f"delete_{index}", on_click=lambda: handle_action(f"delete_{index}", delete_anime, index), use_container_width=True)

def display_section(title, anime_list):
    if not anime_list:
        return
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    for i in range(0, len(anime_list), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(anime_list):
                with cols[j]:
                    render_anime_card(anime_list[idx][0], anime_list[idx][1])

def display_home_view():
    filtered = filter_anime_collection()
    watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
    upcoming = [pair for pair in filtered if get_status(pair[1]) == "upcoming"]
    finished = [pair for pair in filtered if get_status(pair[1]) == "finished"]
    display_section("Currently Watching", watching)
    display_section("Upcoming Watchables", upcoming)
    display_section("Completed", finished)

def display_add_view():
    is_edit = st.session_state.edit_index is not None
    anime_data = st.session_state.anime_collection[st.session_state.edit_index] if is_edit else {'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None}
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        with col_img:
            image_file = st.file_uploader("Cover Image", type=["png", "jpg", "jpeg"])
            if image_file:
                anime_image = image_file.read()
                st.image(anime_image, use_container_width=True)
            else:
                anime_image = anime_data.get('image') if isinstance(anime_data.get('image'), bytes) else None
                if anime_image:
                    st.image(anime_image, use_container_width=True)
                else:
                    st.markdown("<div style='height:200px; background:#2D2D2D; display:flex; align-items:center; justify-content:center; border-radius:10px;'>No Image</div>", unsafe_allow_html=True)
        with col_form:
            anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''))
            col1, col2 = st.columns(2)
            with col1:
                seasons = st.number_input("Seasons", min_value=1, value=anime_data.get('seasons', 1))
            with col2:
                total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 12))
            finished_episodes = st.slider("Episodes Watched", 0, total_episodes, anime_data.get('finished_episodes', 0))
            progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            st.markdown(f"<div style='margin-top:16px;'>Progress: {progress:.1f}%</div>", unsafe_allow_html=True)
            st.progress(progress/100.0)
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.form_submit_button("Save Anime"):
                if not anime_name:
                    st.error("Please enter anime name")
                else:
                    new_anime = {'anime_name': anime_name, 'seasons': seasons, 'total_episodes': total_episodes, 'finished_episodes': finished_episodes, 'image': anime_image}
                    save_anime_data(new_anime, st.session_state.edit_index if is_edit else None)
                    st.rerun()
        with col_cancel:
            if st.form_submit_button("Cancel"):
                st.session_state.view = 'home'
                st.session_state.edit_index = None
                st.rerun()

def display_header():
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        search = st.text_input("", value=st.session_state.search_query, placeholder="Search your anime collection...", key="search_input", on_change=lambda: handle_action("search", lambda: None))
        if st.session_state.search_query:
            if st.button("✕ Clear", key="clear_search"):
                st.session_state.search_query = ""
                st.rerun()
    with col2:
        if st.button("➕ Add New", key="add_button", use_container_width=True):
            handle_action("add_new", set_view, 'add', edit_index=None)
    with col3:
        if st.button(f"👤 {st.session_state.username}", key="user_button", use_container_width=True):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    if st.session_state.user_menu_visible:
        st.markdown("<div style='padding:10px; background:#1E1E1E; border-radius:10px;'>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_button", use_container_width=True):
            handle_action("logout", logout)
        st.markdown("</div>", unsafe_allow_html=True)

def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    display_header()
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()

if not st.session_state.logged_in:
    auth_page()
else:
    load_anime_collection()
    main_page()
