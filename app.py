import streamlit as st
import time

# Page config for better wide layout and title
st.set_page_config(page_title="Anime Tracker", page_icon="🎴", layout="wide")

# Global CSS style injection for dark theme and custom styles
st.markdown("""<style>
/* Basic dark background and text */
body, .stApp {
    background-color: #1e1e1e;
    color: #e0e0e0;
}
/* Hide Streamlit default menu and footer for cleaner look */
#MainMenu, header, footer {visibility: hidden;}
/* Customize text inputs (login & search) */
.stTextInput>div>div>input {
    background-color: #2b2b2b;
    color: #e0e0e0;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 0.5rem;
}
.stTextInput>div>div>input:focus {
    border: 1px solid #6c63ff;
    outline: none;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.5);
}
/* Placeholder text color */
.stTextInput>div>div>input::placeholder {
    color: #888;
}
/* Global button style */
.stButton>button {
    background-color: #6c63ff;
    color: #fff;
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
    width: 100%;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.05s;
}
.stButton>button:hover {
    background-color: #5a54d1;
}
.stButton>button:active {
    transform: scale(0.98);
}
/* Clear search button (X) specific styling */
.clear-btn-container button {
    background-color: #555 !important;
    color: #fff !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    border: none !important;
    border-radius: 16px !important;
    font-size: 1rem !important;
    line-height: 32px !important;
    text-align: center !important;
}
.clear-btn-container button:hover {
    background-color: #777 !important;
}
/* Card grid layout */
.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    margin-top: 1rem;
}
@media (max-width: 600px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
/* Card styling */
.card {
    background-color: #2b2b2b;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
    transition: transform 0.3s, box-shadow 0.3s;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.6);
}
/* Card image */
.card-img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}
/* Placeholder image (if no image) */
.placeholder {
    background: linear-gradient(135deg, #3a3a3a 25%, #4a4a4a 50%, #3a3a3a 75%);
    background-size: 200% 200%;
    animation: placeholderShimmer 1.5s infinite;
}
@keyframes placeholderShimmer {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
/* Card content */
.card-body {
    padding: 1rem;
}
.card-body h3 {
    margin: 0 0 0.5rem;
    color: #fff;
    font-size: 1.25rem;
}
.card-body p {
    margin: 0;
    color: #ccc;
    font-size: 0.9rem;
}
/* Completed status text */
.status-completed {
    color: #4caf50;
    font-weight: bold;
}
/* Toast/Snackbar style */
.toast {
    visibility: visible;
    min-width: 200px;
    max-width: 80%;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 4px;
    padding: 0.75rem 1.25rem;
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    opacity: 1;
    transition: opacity 0.5s ease-in;
}
.toast.hide {
    opacity: 0;
    visibility: hidden;
}
</style>""", unsafe_allow_html=True)

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = {'demo': 'demo'}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if 'anime_list' not in st.session_state:
    st.session_state.anime_list = [
        {"id": 1, "title": "Naruto: Shippuuden", "seasons": 1, "episodes": 500, "status": "Completed", "image": "https://myanimelist.cdn-dena.com/images/anime/5/17407.jpg"},
        {"id": 2, "title": "One Piece", "seasons": 20, "episodes": 1000, "status": "Ongoing", "image": "https://myanimelist.cdn-dena.com/images/anime/6/73245.jpg"},
        {"id": 3, "title": "Attack on Titan", "seasons": 4, "episodes": 87, "status": "Completed", "image": "https://myanimelist.cdn-dena.com/images/anime/10/47347.jpg"},
        {"id": 4, "title": "Death Note", "seasons": 1, "episodes": 37, "status": "Completed", "image": "https://myanimelist.cdn-dena.com/images/anime/9/9453.jpg"},
        {"id": 5, "title": "Monster", "seasons": 1, "episodes": 74, "status": "Plan to Watch", "image": None}
    ]
if 'last_click_time' not in st.session_state:
    st.session_state.last_click_time = 0

# Authentication flow
if not st.session_state.logged_in:
    col_left, col_mid, col_right = st.columns([1,2,1])
    with col_mid:
        # Create tabs for Login and Sign Up
        tabs = st.tabs(["Login", "Sign Up"])
        with tabs[0]:
            st.subheader("Login to Anime Tracker")
            login_user = st.text_input("Username", placeholder="Username", key="login_user", label_visibility="collapsed")
            login_pass = st.text_input("Password", placeholder="Password", type="password", key="login_pass", label_visibility="collapsed")
            login_btn = st.button("Login", key="login_btn")
            if login_btn:
                # Debounce double-click
                if time.time() - st.session_state.last_click_time < 1:
                    st.stop()
                st.session_state.last_click_time = time.time()
                if login_user in st.session_state.users and st.session_state.users[login_user] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
        with tabs[1]:
            st.subheader("Create a New Account")
            new_user = st.text_input("Username", placeholder="Username", key="signup_user", label_visibility="collapsed")
            new_pass = st.text_input("Password", placeholder="Password", type="password", key="signup_pass", label_visibility="collapsed")
            signup_btn = st.button("Sign Up", key="signup_btn")
            if signup_btn:
                # Debounce double-click
                if time.time() - st.session_state.last_click_time < 1:
                    st.stop()
                st.session_state.last_click_time = time.time()
                if new_user == "" or new_pass == "":
                    st.warning("Please enter a username and password.")
                elif new_user in st.session_state.users:
                    st.warning("Username already exists.")
                else:
                    # Create new user and log in
                    st.session_state.users[new_user] = new_pass
                    st.session_state.logged_in = True
                    st.session_state.current_user = new_user
                    st.session_state.login_user = ""
                    st.session_state.login_pass = ""
                    st.experimental_rerun()
else:
    # Main App UI
    st.title(f"Welcome, {st.session_state.current_user}!")
    # Search bar with clear (X) button
    col1, col2 = st.columns([10,1])
    with col1:
        query = st.text_input("", placeholder="Search anime...", key="search", label_visibility="collapsed")
    with col2:
        st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
        clear_clicked = st.button("✕", key="clear_search")
        st.markdown('</div>', unsafe_allow_html=True)
    if clear_clicked:
        query = ""
        st.session_state.search = ""
    # Filter anime list based on search query
    anime_list = st.session_state.anime_list
    if query:
        q_lower = query.lower()
        anime_list = [anime for anime in anime_list if q_lower in anime['title'].lower()]
    # Display anime cards in a responsive grid
    grid_html = "<div class='grid'>"
    for anime in anime_list:
        img_part = ""
        if anime['image']:
            img_part = f"<img src='{anime['image']}' class='card-img' alt='{anime['title']} poster'>"
        else:
            img_part = "<div class='card-img placeholder'></div>"
        status_text = anime['status']
        status_class = "status-completed" if anime['status'].lower()=="completed" else ""
        status_span = f"<span class='{status_class}'>{status_text}</span>" if status_class else status_text
        grid_html += f"<div class='card'>{img_part}<div class='card-body'><h3>{anime['title']}</h3><p>Seasons: {anime['seasons']} | Episodes: {anime['episodes']}<br>Status: {status_span}</p>"
        if anime['status'].lower() != "completed":
            grid_html += f"<div style='margin-top:0.5rem;'><button class='mark-btn' onclick=\"window.location.href='?complete={anime['id']}'\">Mark as Completed</button></div>"
        grid_html += "</div></div>"
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)
    # Style for mark as completed buttons
    st.markdown("""<style>
    .mark-btn {
        background-color: #6c63ff;
        color: #fff;
        padding: 0.5rem;
        border: none;
        border-radius: 4px;
        width: 100%;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .mark-btn:hover {
        background-color: #5a54d1;
    }
    .mark-btn:active {
        transform: scale(0.98);
    }
    </style>""", unsafe_allow_html=True)
    # Handle mark as completed via query param
    params = st.experimental_get_query_params()
    if 'complete' in params:
        try:
            comp_id = int(params['complete'][0])
            for anime in st.session_state.anime_list:
                if anime['id'] == comp_id:
                    anime['status'] = 'Completed'
            st.session_state.success_msg = "Anime marked as completed!"
            st.experimental_set_query_params()
            st.experimental_rerun()
        except:
            st.experimental_set_query_params()
    # Show success toast if set
    if 'success_msg' in st.session_state:
        msg = st.session_state.success_msg
        st.markdown(f"""<div class='toast'>{msg}</div>
        <script>
        setTimeout(function() {{
            var t = document.getElementsByClassName('toast')[0];
            if(t) {{ t.classList.add('hide'); }}
        }}, 3000);
        </script>""", unsafe_allow_html=True)
        del st.session_state['success_msg']
