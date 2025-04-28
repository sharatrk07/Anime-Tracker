import streamlit as st
from firebase_config import db
from PIL import Image
import time

# Session State Initialization
for key, default in {
    'logged_in': False, 'username': "", 'auth_mode': None, 'view': 'home',
    'edit_index': None, 'edit_watched_index': None, 'search_query': "",
    'anime_collection': [], 'user_menu_visible': False,
    'last_action_time': 0, 'pending_action': None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.set_page_config(page_title="Anime Tracker", page_icon="🎬", layout="wide")

st.markdown("""
<style>
:root {
    --primary: #8A4FFF;
    --secondary: #FF4F8A;
    --background: #111;
    --surface: #1C1C1C;
    --surface-variant: #2B2B2B;
    --on-surface: #FFFFFF;
    --accent: #4FFF8A;
    --radius-md: 10px;
    --spacing-md: 16px;
    --spacing-sm: 8px;
}

.stApp { background: var(--background); color: var(--on-surface); font-family: 'Inter', sans-serif; }

h1.page-title {
    font-size: 2.5rem;
    color: var(--primary);
    text-align: center;
    margin: 1rem 0;
}
.section-header {
    font-size: 1.8rem;
    font-weight: bold;
    color: var(--secondary);
    margin: 1.5rem 0 1rem;
    border-bottom: 2px solid var(--secondary);
    padding-bottom: 0.5rem;
}

.anime-card {
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
}
.anime-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
}

.anime-image {
    width: 100%;
    height: 200px;
    background-color: var(--surface-variant);
    background-size: cover;
    background-position: center;
    border-radius: var(--radius-md);
    margin-bottom: var(--spacing-sm);
}

.anime-title {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    color: var(--primary);
    text-align: center;
}

.search-container {
    position: relative;
    width: 100%;
}
.search-input {
    width: 100%;
    padding: 0.8rem 2.5rem 0.8rem 1rem;
    border-radius: var(--radius-md);
    border: none;
    font-size: 1rem;
    background-color: var(--surface-variant);
    color: var(--on-surface);
}
.search-clear {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    color: var(--on-surface);
    font-size: 1.2rem;
    cursor: pointer;
}

.anime-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-md);
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Utilities
def handle_action(action_name, callback_func, *args, **kwargs):
    current_time = time.time()
    if st.session_state.pending_action == action_name and current_time - st.session_state.last_action_time < 0.8:
        return
    st.session_state.pending_action = action_name
    st.session_state.last_action_time = current_time
    callback_func(*args, **kwargs)
    st.rerun()

def show_success(message):
    st.success(message)

def load_anime_collection():
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc = doc_ref.get()
        if hasattr(doc, 'exists') and doc.exists:
            st.session_state.anime_collection = doc.to_dict().get("anime_collection", [])
        else:
            st.session_state.anime_collection = []
            save_anime_collection()

def save_anime_collection():
    if st.session_state.username:
        db.collection("users").document(st.session_state.username).set({"anime_collection": st.session_state.anime_collection})

def filter_anime_collection():
    return [
        (i, anime) for i, anime in enumerate(st.session_state.anime_collection)
        if not st.session_state.search_query or st.session_state.search_query.lower() in anime['anime_name'].lower()
    ]

def get_status(anime):
    if anime['finished_episodes'] == 0:
        return "Upcoming"
    elif anime['finished_episodes'] >= anime['total_episodes']:
        return "Completed"
    else:
        return "Watching"

def set_view(view_name, **kwargs):
    st.session_state.view = view_name
    for key, value in kwargs.items():
        st.session_state[key] = value

def save_anime_data(anime_data, edit_index=None):
    if edit_index is not None:
        st.session_state.anime_collection[edit_index] = anime_data
        show_success("Anime updated successfully!")
    else:
        st.session_state.anime_collection.append(anime_data)
        show_success("New anime added!")
    save_anime_collection()
    set_view('home')

def delete_anime(index):
    st.session_state.anime_collection.pop(index)
    save_anime_collection()
    st.session_state.view = 'home'

# Components
def display_search_bar():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_col1, search_col2 = st.columns([10,1])
    with search_col1:
        search_input = st.text_input(
            "", value=st.session_state.search_query,
            placeholder="Search your favorite anime...", label_visibility="collapsed", key="search_input"
        )
        st.session_state.search_query = search_input
    with search_col2:
        if st.session_state.search_query:
            if st.button('✕', key="clear_search", use_container_width=True):
                st.session_state.search_query = ""
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_anime_card(index, anime):
    img_url = anime.get('image')
    st.markdown('<div class="anime-card">', unsafe_allow_html=True)
    if img_url:
        st.image(img_url, use_column_width=True)
    else:
        st.markdown('<div class="anime-image" style="display:flex;align-items:center;justify-content:center;">🎬</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="anime-title">{anime['anime_name']}</div>
        <div style="text-align:center; margin-bottom:8px;">
            Seasons: {anime['seasons']}<br>
            Episodes: {anime['finished_episodes']}/{anime['total_episodes']}<br>
            Status: {get_status(anime)}
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Edit", key=f"edit_{index}", use_container_width=True):
            handle_action(f"edit_{index}", lambda: set_view('add', edit_index=index))
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{index}", use_container_width=True):
            handle_action(f"delete_{index}", delete_anime, index)
    st.markdown('</div>', unsafe_allow_html=True)

def display_home_view():
    st.markdown('<h2 class="section-header">My Anime Collection</h2>', unsafe_allow_html=True)
    filtered = filter_anime_collection()
    if not filtered:
        st.info("No anime found. Add a new one!")
    else:
        st.markdown('<div class="anime-grid">', unsafe_allow_html=True)
        for idx, (anime_idx, anime) in enumerate(filtered):
            with st.container():
                render_anime_card(anime_idx, anime)
        st.markdown('</div>', unsafe_allow_html=True)

def display_add_view():
    is_edit = st.session_state.edit_index is not None
    anime_data = st.session_state.anime_collection[st.session_state.edit_index] if is_edit else {
        'anime_name': '', 'seasons': 1, 'total_episodes': 12, 'finished_episodes': 0, 'image': None
    }
    
    st.markdown(f'<h2 class="section-header">{"Edit Anime" if is_edit else "Add New Anime"}</h2>', unsafe_allow_html=True)
    
    with st.form("anime_form", clear_on_submit=False):
        anime_name = st.text_input("Anime Name", value=anime_data['anime_name'])
        col1, col2 = st.columns(2)
        with col1:
            seasons = st.number_input("Seasons", min_value=1, value=anime_data['seasons'])
        with col2:
            total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data['total_episodes'])
        finished_episodes = st.slider("Episodes Watched", 0, total_episodes, anime_data['finished_episodes'])
        
        image_file = st.file_uploader("Cover Image (optional)", type=["jpg", "jpeg", "png"])
        if image_file:
            anime_image = image_file.read()
        else:
            anime_image = anime_data.get('image')
        
        submit_col1, submit_col2 = st.columns(2)
        with submit_col1:
            if st.form_submit_button("Save"):
                new_anime = {
                    'anime_name': anime_name,
                    'seasons': seasons,
                    'total_episodes': total_episodes,
                    'finished_episodes': finished_episodes,
                    'image': anime_image
                }
                save_anime_data(new_anime, st.session_state.edit_index if is_edit else None)
        with submit_col2:
            if st.form_submit_button("Cancel"):
                set_view('home')

def display_header():
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        display_search_bar()
    with col2:
        if st.button("➕ Add Anime", use_container_width=True):
            set_view('add', edit_index=None)
    with col3:
        if st.button(f"👤 {st.session_state.username}", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.anime_collection = []
            st.rerun()

def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    display_header()
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()

def auth_page():
    st.title("🎬 Anime Tracker")
    mode = st.radio("Select Mode", ["Login", "Sign Up"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = None
    if mode == "Sign Up":
        confirm_password = st.text_input("Confirm Password", type="password")
    if st.button(mode):
        if username and password:
            if mode == "Sign Up":
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    save_anime_collection()
                    st.rerun()
            else:
                st.session_state.logged_in = True
                st.session_state.username = username
                load_anime_collection()
                st.rerun()
        else:
            st.error("Please fill all fields")

# Main
if not st.session_state.logged_in:
    auth_page()
else:
    load_anime_collection()
    main_page()
