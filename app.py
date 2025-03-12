import streamlit as st
from firebase_config import db
import base64

def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return ""

def decode_image(image_str):
    if image_str:
        return base64.b64decode(image_str)
    return None

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

st.set_page_config(
    page_title="Anime Tracker",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root {
    --background: #121212;
    --card-bg: #1E1E1E;
    --primary: #BB86FC;
    --secondary: #03DAC6;
    --error: #CF6679;
    --text: #FFFFFF;
    --border: #2D2D2D;
    --primary-font: #F5F5F5;
    --category-font: #FFDD55;
    --anime-title: #FF80AB;
    --button-bg: #BB86FC;
    --button-text: #121212;
    --button-hover: #9966CC;
}
.stApp { background-color: var(--background); color: var(--text); }
h1 { color: var(--primary-font); font-weight: 600; margin-bottom: 10px; text-align: center; }
h2 { color: var(--primary-font); }
h3 { color: var(--anime-title); }
.section-header {
    border-left: 4px solid var(--primary);
    padding: 10px;
    margin: 20px 0 10px 0;
    font-size: 1.8rem;
    color: var(--category-font);
    background-color: rgba(255, 221, 85, 0.1);
    border-radius: 4px;
}
.anime-card {
    background-color: var(--card-bg);
    border-radius: 8px;
    padding: 12px;
    margin: 12px auto;
    border: 1px solid var(--border);
    max-width: 800px;
    text-align: left;
}
.anime-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.2); }
.progress-container { width: 100%; background-color: #2D2D2D; border-radius: 4px; margin: 6px 0; height: 8px; }
.progress-bar { height: 8px; border-radius: 4px; }
.progress-low { background-color: var(--error); }
.progress-medium { background-color: #FFAB40; }
.progress-high { background-color: var(--secondary); }
.status-badge {
    padding: 4px 8px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text);
}
.status-watching { background-color: var(--primary); }
.status-finished { background-color: var(--secondary); }
.status-upcoming { background-color: #FFAB40; }
.user-info {
    position: fixed;
    top: 10px;
    right: 10px;
    text-align: right;
    background-color: var(--card-bg);
    padding: 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
}
.stButton>button, .stFormSubmit>button {
    background-color: var(--button-bg);
    color: var(--button-text);
    font-weight: bold;
    border: none;
    transition: background-color 0.3s;
}
.stButton>button:hover, .stFormSubmit>button:hover {
    background-color: var(--button-hover);
}
hr {
    border: 0;
    height: 1px;
    background-image: linear-gradient(to right, rgba(187,134,252,0), rgba(187,134,252,0.75), rgba(187,134,252,0));
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

def load_anime_collection():
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc = doc_ref.get()
        if doc.exists:
            st.session_state.anime_collection = doc.to_dict().get("anime_collection", [])
        else:
            st.session_state.anime_collection = [
                {'anime_name': 'Attack on Titan', 'seasons': 4, 'total_episodes': 87, 'finished_episodes': 87, 'image': ""},
                {'anime_name': 'My Hero Academia', 'seasons': 6, 'total_episodes': 138, 'finished_episodes': 75, 'image': ""},
                {'anime_name': 'Demon Slayer', 'seasons': 3, 'total_episodes': 55, 'finished_episodes': 55, 'image': ""}
            ]
            save_anime_collection()

def save_anime_collection():
    if st.session_state.username:
        doc_ref = db.collection("users").document(st.session_state.username)
        doc_ref.set({"anime_collection": st.session_state.anime_collection})

def calculate_progress(anime):
    if anime['total_episodes'] == 0:
        return 0
    return int((anime['finished_episodes'] / anime['total_episodes']) * 100)

def get_status(anime):
    if anime['finished_episodes'] == 0:
        return "upcoming"
    elif anime['finished_episodes'] >= anime['total_episodes']:
        return "finished"
    else:
        return "watching"

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

def filter_anime_collection():
    filtered = st.session_state.anime_collection
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        filtered = [anime for anime in filtered if query in anime['anime_name'].lower()]
    return filtered

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.view = 'home'
    st.session_state.edit_index = None
    st.session_state.edit_watched_index = None
    st.session_state.anime_collection = []
    st.set_query_params({})

def auth_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Welcome to the Anime Tracker</h1>", unsafe_allow_html=True)
    cols = st.columns(2)
    if cols[0].button("Login"):
        st.session_state.auth_mode = "login"
    if cols[1].button("Sign Up"):
        st.session_state.auth_mode = "signup"
    if st.session_state.auth_mode == "signup":
        st.subheader("Sign Up")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Submit Sign Up"):
            if signup_password != signup_confirm:
                st.error("Passwords do not match")
            elif signup_username and signup_password:
                st.session_state.logged_in = True
                st.session_state.username = signup_username
                save_anime_collection()
            else:
                st.error("Please fill in all fields")
    elif st.session_state.auth_mode == "login":
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Submit Login"):
            if login_username and login_password:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                load_anime_collection()
            else:
                st.error("Invalid credentials")

def display_home_view():
    collection = filter_anime_collection()
    if not collection:
        st.markdown("""
        <div style="text-align:left; padding:20px; background-color: var(--card-bg); border-radius:8px;">
            <h2 class="section-header">Your collection is empty</h2>
            <p>Add your first anime using the controls above.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        categories = [
            ("Currently Watching", [a for a in collection if get_status(a) == "watching"]),
            ("Finished", [a for a in collection if get_status(a) == "finished"]),
            ("Upcoming", [a for a in collection if get_status(a) == "upcoming"])
        ]
        for cat_name, anime_list in categories:
            if anime_list:
                st.markdown(f'<h2 class="section-header">{cat_name}</h2>', unsafe_allow_html=True)
                display_anime_list(anime_list, cat_name.lower().replace(" ", "_"))

def display_anime_list(anime_list, prefix):
    for i, anime in enumerate(anime_list):
        progress = calculate_progress(anime)
        progress_class = "progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"
        status = get_status(anime)
        status_text = {"watching": "Currently Watching", "finished": "Finished", "upcoming": "Upcoming"}[status]
        status_class = {"watching": "status-watching", "finished": "status-finished", "upcoming": "status-upcoming"}[status]
        with st.container():
            col_img, col_info = st.columns([1, 3])
            with col_img:
                if anime.get('image'):
                    st.image(decode_image(anime.get('image')), use_container_width=True)
                else:
                    st.write("")
            with col_info:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: var(--anime-title); margin: 0;">{anime['anime_name']}</h3>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:left;'>Seasons: {anime['seasons']}</p>", unsafe_allow_html=True)
                col_left, col_right = st.columns([5, 2])
                with col_left:
                    st.markdown(f"<p style='text-align:left;'>Episodes: {anime['finished_episodes']} / {anime['total_episodes']}</p>", unsafe_allow_html=True)
                with col_right:
                    if st.button("✏️ Edit Watched", key=f"{prefix}_editwatched_{i}"):
                        st.session_state.edit_watched_index = i
                        st.session_state.view = 'edit_watched'
                    if st.button("🖊️ Edit Details", key=f"{prefix}_edit_{i}"):
                        st.session_state.edit_index = i
                        st.session_state.view = 'add'
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar {progress_class}" style="width: {progress}%;"></div>
            </div>
            <p style="text-align:right;">{progress}% complete</p>
            """, unsafe_allow_html=True)
        st.markdown("---")

def display_add_view():
    is_edit = st.session_state.edit_index is not None
    if is_edit:
        st.markdown('<h2 class="section-header" style="text-align:center;">Edit Anime</h2>', unsafe_allow_html=True)
        anime_data = st.session_state.anime_collection[st.session_state.edit_index]
    else:
        st.markdown('<h2 class="section-header" style="text-align:center;">Add New Anime</h2>', unsafe_allow_html=True)
        anime_data = {'anime_name': '', 'seasons': 1, 'total_episodes': 1, 'finished_episodes': 0, 'image': ""}
    with st.form("anime_form"):
        cols = st.columns([1, 2])
        with cols[0]:
            image_file = st.file_uploader("Upload Anime Image", type=["png", "jpg", "jpeg"])
            if image_file is not None:
                anime_image = encode_image(image_file)
                st.image(image_file, use_container_width=True)
            else:
                anime_image = anime_data.get('image', "")
                if anime_image:
                    st.image(decode_image(anime_image), use_container_width=True)
                else:
                    st.write("")
        with cols[1]:
            anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''))
            seasons = st.number_input("Number of Seasons", min_value=1, value=anime_data.get('seasons', 1))
            total_episodes = st.number_input("Total Episodes", min_value=1, value=anime_data.get('total_episodes', 1))
            finished_episodes = st.number_input("Finished Episodes", min_value=0, value=anime_data.get('finished_episodes', 0))
        progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
        st.markdown(f"<p style='text-align:center;'>Progress: {progress:.1f}%</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='progress-container'>
            <div class='progress-bar {"progress-low" if progress < 33 else "progress-medium" if progress < 66 else "progress-high"}' style='width: {progress}%;'></div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        submit_button = col1.form_submit_button("Save")
        cancel_button = col2.form_submit_button("Cancel")
    if submit_button:
        if not anime_name:
            st.error("Please enter an anime name")
        elif finished_episodes > total_episodes:
            st.error("Finished episodes cannot exceed total episodes.")
        else:
            new_anime = {
                'anime_name': anime_name,
                'seasons': seasons,
                'total_episodes': total_episodes,
                'finished_episodes': finished_episodes,
                'image': anime_image
            }
            save_anime_data(new_anime, st.session_state.edit_index if is_edit else None)
    if cancel_button:
        st.session_state.view = 'home'
        st.session_state.edit_index = None

def display_edit_watched(index):
    anime = st.session_state.anime_collection[index]
    st.markdown(f"<div style='text-align:center;'><h2 class='section-header'>Edit Watched Episodes for {anime['anime_name']}</h2></div>", unsafe_allow_html=True)
    new_watched = st.number_input("Finished Episodes", min_value=0, value=anime['finished_episodes'], key="edit_watched_input")
    col1, col2 = st.columns(2)
    if col1.button("Save"):
        if new_watched > anime['total_episodes']:
            st.error("Finished episodes cannot exceed total episodes.")
        else:
            st.session_state.anime_collection[index]['finished_episodes'] = new_watched
            save_anime_collection()
            st.session_state.view = 'home'
    if col2.button("Cancel"):
        st.session_state.view = 'home'
    st.markdown("---")
    if st.button("🗑️ Delete Anime"):
        delete_anime(index)

def main_page():
    header_cols = st.columns([3, 3, 3])
    with header_cols[0]:
        st.text_input("Search Anime", key="search_query", placeholder="Search...")
    with header_cols[1]:
        if st.button("➕ Add Anime", key="add_new_top"):
            st.session_state.view = 'add'
    with header_cols[2]:
        if st.button("👤", key="user_logo"):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    if st.session_state.user_menu_visible:
        st.markdown(f"<div class='user-info'><p style='margin:0;'>Logged in as: {st.session_state.username}</p>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            logout()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Anime Tracker</h1>", unsafe_allow_html=True)
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()
    elif st.session_state.view == 'edit_watched':
        display_edit_watched(st.session_state.edit_watched_index)

if not st.session_state.logged_in:
    auth_page()
else:
    load_anime_collection()
    main_page()