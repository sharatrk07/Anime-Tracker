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

# Enhanced CSS with improved hover effects and spacing
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary: #8A4FFF;
    --primary-light: #9D6FFF;
    --primary-dark: #7A3FEF;
    --secondary: #4F9DFF;
    --secondary-light: #6BABFF;
    --secondary-dark: #3A7FE6;
    --accent: #4FFFB0;
    --accent-light: #6FFFC1;
    --accent-dark: #3AE69A;
    --bg-dark: #121212;
    --bg-card: #1E1E1E;
    --bg-input: #2D2D2D;
    --text-light: #FFFFFF;
    --text-muted: #AAAAAA;
    --border: #333333;
    --status-watching: #5D87FF;
    --status-planned: #FF6B8A;
    --status-completed: #56C568;
}

.stApp {
    background-color: var(--bg-dark);
    color: var(--text-light);
    font-family: 'Poppins', sans-serif;
}

/* Enhanced Header Styles */
.page-title {
    font-size: 4rem;
    font-weight: 800;
    text-align: center;
    margin: 40px 0;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(138, 79, 255, 0.4);
    letter-spacing: -1px;
    transform: scale(1);
    transition: transform 0.3s ease;
}

.page-title:hover {
    transform: scale(1.02);
}

.section-header {
    font-size: 2.2rem;
    margin-top: 60px;
    margin-bottom: 30px;
    font-weight: 700;
    color: var(--text-light);
    position: relative;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--primary);
    display: inline-block;
    transition: all 0.3s ease;
}

.section-header:hover {
    transform: translateY(-2px);
    text-shadow: 0 0 10px rgba(138, 79, 255, 0.3);
}

.section-header::after {
    content: "";
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 80px;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    transition: width 0.3s ease;
}

.section-header:hover::after {
    width: 100%;
}

/* Enhanced category line styling with animation */
.category-line {
    display: block;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    margin: 15px 0 30px 0;
    border-radius: 3px;
    box-shadow: 0 2px 10px rgba(138, 79, 255, 0.2);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.category-line:hover {
    height: 5px;
    box-shadow: 0 4px 15px rgba(138, 79, 255, 0.4);
}

.category-line::after {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(
        to right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.3) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    to {
        left: 100%;
    }
}

.section-container {
    margin-bottom: 50px;
    padding-bottom: 30px;
    border-bottom: 1px solid var(--border);
}

/* Improved Anime Card Styles with increased spacing */
.anime-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 35px;
}

.anime-card {
    background-color: var(--bg-card);
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--border);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    height: 100%;
    margin-bottom: 25px;
}

.anime-card:hover {
    transform: translateY(-10px);
    border-color: var(--primary);
    box-shadow: 0 15px 30px rgba(138, 79, 255, 0.4);
}

.anime-image {
    height: 240px;
    background-size: cover;
    background-position: center;
    position: relative;
    transition: all 0.4s ease;
    background-color: #000000;
}

.anime-card:hover .anime-image {
    filter: brightness(1.2);
}

.anime-card-content {
    padding: 30px; /* Increased padding */
}

.anime-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 25px; /* Increased spacing */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: color 0.3s ease;
}

.anime-card:hover .anime-title {
    color: var(--primary-light);
}

.anime-stats {
    display: flex;
    justify-content: space-between;
    font-size: 1rem;
    margin-top: 25px; /* Increased spacing */
    margin-bottom: 25px; /* Increased spacing */
    color: var(--text-muted);
}

.status-badge {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.9rem;
    text-transform: uppercase;
    font-weight: 600;
    position: absolute;
    top: 15px;
    right: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.anime-card:hover .status-badge {
    transform: scale(1.05);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
}

.status-watching {
    background-color: var(--status-watching);
    color: white;
}

.status-planned {
    background-color: var(--status-planned);
    color: white;
}

.status-completed {
    background-color: var(--status-completed);
    color: white;
}

.progress-container {
    background-color: var(--bg-input);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 25px; /* Increased spacing */
    margin-bottom: 20px; /* Increased spacing */
    height: 10px;
}

.progress-bar {
    height: 10px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    transition: width 0.8s cubic-bezier(0.19, 1, 0.22, 1);
}

/* Enhanced Button Styles with new hover effects - NO RED */
.action-buttons {
    display: flex;
    gap: 15px;
    margin-top: 30px; /* Increased spacing */
}

/* New button hover styles - completely removed red */
.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    padding: 12px 24px;
    font-size: 1.05rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: var(--bg-input);
    color: var(--text-light);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    background-color: var(--primary);
    color: white;
}

/* Edit button */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
    background-color: var(--primary-dark);
    color: white;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
    background-color: var(--primary);
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(138, 79, 255, 0.3);
}

/* Delete button */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
    background-color: var(--secondary-dark);
    color: white;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
    background-color: var(--secondary);
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(79, 157, 255, 0.3);
}

/* Login/Signup buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background-color: var(--bg-input);
    color: var(--text-light);
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background-color: var(--primary);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(138, 79, 255, 0.3);
}

/* Form submit buttons */
form .stButton > button {
    background-color: var(--primary-dark);
    color: white;
}

form .stButton > button:hover {
    background-color: var(--primary);
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(138, 79, 255, 0.3);
}

/* Enhanced Form Styles */
.stTextInput > div > div > input, 
.stNumberInput > div > div > input {
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    color: var(--text-light);
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 1.05rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus, 
.stNumberInput > div > div > input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(138, 79, 255, 0.3);
    transform: translateY(-2px);
}

/* Enhanced Auth Styles */
.auth-container {
    max-width: 550px;
    margin: 50px auto;
    padding: 40px;
    background-color: var(--bg-card);
    border-radius: 24px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
    border: 1px solid var(--border);
    transition: all 0.3s ease;
}

.auth-container:hover {
    box-shadow: 0 20px 40px rgba(138, 79, 255, 0.2);
    border-color: var(--primary-light);
}

.auth-tab {
    background-color: var(--bg-input);
    color: var(--text-light);
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
}

.auth-tab.active {
    background-color: var(--primary);
}

.auth-tab:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    background-color: var(--primary);
}

/* Enhanced Search Bar */
.search-container {
    position: relative;
    margin-bottom: 25px;
}

.search-input {
    width: 100%;
    padding: 14px 24px;
    padding-right: 50px;
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 12px;
    color: var(--text-light);
    font-size: 1.05rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-input:focus {
    border-color: var(--primary);
    box-shadow: 0 6px 12px rgba(138, 79, 255, 0.2);
    transform: translateY(-2px);
}

/* Enhanced User Menu */
.user-menu {
    position: absolute;
    right: 25px;
    top: 70px;
    background-color: var(--bg-card);
    border-radius: 16px;
    padding: 15px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    border: 1px solid var(--border);
    transition: all 0.3s ease;
    transform-origin: top right;
    animation: menuAppear 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes menuAppear {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.user-menu-button {
    background-color: transparent;
    border: 1px solid var(--primary);
    color: var(--primary);
    border-radius: 12px;
    padding: 10px;
    width: 100%;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.user-menu-button:hover {
    background-color: var(--primary);
    color: white;
    transform: translateY(-2px);
}

/* Enhanced Add Button */
.add-button {
    background: linear-gradient(45deg, var(--primary), var(--primary-light));
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 6px rgba(138, 79, 255, 0.3);
}

.add-button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 15px rgba(138, 79, 255, 0.4);
    background: linear-gradient(45deg, var(--primary-dark), var(--primary));
}

.add-button-icon {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
}

.add-button:hover .add-button-icon {
    transform: rotate(90deg);
}

/* Enhanced Empty State */
.empty-state {
    text-align: center;
    padding: 60px 30px;
    background-color: var(--bg-card);
    border-radius: 24px;
    margin: 50px 0;
    border: 1px dashed var(--border);
    transition: all 0.3s ease;
}

.empty-state:hover {
    border-color: var(--primary);
    box-shadow: 0 10px 20px rgba(138, 79, 255, 0.2);
    transform: translateY(-5px);
}

.empty-state-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 15px;
    color: var(--text-light);
}

.empty-state-text {
    color: var(--text-muted);
    margin-bottom: 25px;
    font-size: 1.1rem;
}

/* Enhanced Category Labels */
.category-label {
    display: inline-block;
    padding: 6px 14px;
    background: linear-gradient(45deg, var(--primary-dark), var(--primary));
    color: white;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    margin-right: 10px;
    margin-bottom: 10px;
    box-shadow: 0 4px 6px rgba(138, 79, 255, 0.3);
    transition: all 0.3s ease;
}

.category-label:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(138, 79, 255, 0.4);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .page-title {
        font-size: 3rem;
    }
    
    .section-header {
        font-size: 1.8rem;
    }
    
    .anime-image {
        height: 200px;
    }
    
    .anime-title {
        font-size: 1.4rem;
    }
    
    .anime-card-content {
        padding: 25px;
    }
    
    .auth-container {
        padding: 30px;
        margin: 30px auto;
    }
}

@media (max-width: 576px) {
    .page-title {
        font-size: 2.5rem;
    }
    
    .section-header {
        font-size: 1.6rem;
    }
    
    .anime-image {
        height: 180px;
    }
    
    .anime-title {
        font-size: 1.3rem;
    }
}

/* Image placeholder with animation */
.image-placeholder {
    height: 240px;
    background-color: #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-size: 1.2rem;
    border-radius: 20px 20px 0 0;
    position: relative;
    overflow: hidden;
}

.image-placeholder::after {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(
        to right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.05) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    to {
        left: 100%;
    }
}

/* Loading animation */
.loading {
    display: inline-block;
    width: 24px;
    height: 24px;
    border: 3px solid rgba(138, 79, 255, 0.3);
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
    border-radius: 12px;
    transition: all 0.3s ease;
}

.stFileUploader > div > button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(138, 79, 255, 0.3);
}

/* Custom slider */
.stSlider > div > div > div > div {
    background-color: var(--primary);
}

/* Custom progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}

/* Toast notification */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: var(--bg-card);
    color: var(--text-light);
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: toastIn 0.3s ease, toastOut 0.3s ease 2.7s forwards;
    border-left: 4px solid var(--primary);
}

.toast-success {
    border-left-color: var(--status-completed);
}

.toast-error {
    border-left-color: var(--status-planned);
}

.toast-info {
    border-left-color: var(--status-watching);
}

@keyframes toastIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes toastOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

/* Image upload preview */
.image-preview {
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

.image-preview:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

/* Upload button enhancement */
.upload-container {
    position: relative;
    width: 100%;
    height: 240px;
    border: 2px dashed var(--border);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background-color: rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.upload-container:hover {
    border-color: var(--primary);
    background-color: rgba(138, 79, 255, 0.05);
}

.upload-icon {
    font-size: 2.5rem;
    color: var(--primary);
    margin-bottom: 10px;
}

.upload-text {
    color: var(--text-muted);
    font-size: 1rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Helper functions
def compress_image(image_bytes, max_size_mb=1):
    """Compress image to reduce size"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Calculate current size in MB
        current_size_mb = len(image_bytes) / (1024 * 1024)
        
        if current_size_mb <= max_size_mb:
            return image_bytes
        
        # Calculate compression quality based on size
        quality = int(85 * (max_size_mb / current_size_mb))
        quality = max(10, min(quality, 80))  # Keep quality between 10 and 80
        
        # Resize if image is very large
        max_dimension = 1000
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
        if not st.session_state.search_query or st.session_state.search_query.lower() in anime.get('anime_name', '').lower():
            filtered.append((idx, anime))
    return filtered

def get_status(anime):
    # Fix for the TypeError - Add proper error handling for missing keys
    try:
        finished_episodes = int(anime.get('finished_episodes', 0))
        total_episodes = int(anime.get('total_episodes', 0))
        
        if finished_episodes == 0:
            return "planned"
        elif total_episodes > 0 and finished_episodes >= total_episodes:
            return "completed"
        else:
            return "watching"
    except (TypeError, ValueError):
        # If there's any error in conversion or missing keys, default to planned
        return "planned"

def calculate_progress(anime):
    try:
        finished_episodes = int(anime.get('finished_episodes', 0))
        total_episodes = int(anime.get('total_episodes', 1))  # Default to 1 to avoid division by zero
        
        if total_episodes == 0:
            return 0
        return int((finished_episodes / total_episodes) * 100)
    except (TypeError, ValueError):
        return 0

def load_anime_collection():
    if st.session_state.username:
        try:
            doc_ref = db.collection("users").document(st.session_state.username)
            doc = doc_ref.get()
            if hasattr(doc, 'exists') and doc.exists:
                anime_collection = doc.to_dict().get("anime_collection", [])
                for anime in anime_collection:
                    # Ensure all required fields exist
                    if not isinstance(anime, dict):
                        continue
                        
                    # Set default values for missing fields
                    if 'anime_name' not in anime:
                        anime['anime_name'] = 'Untitled Anime'
                    if 'seasons' not in anime:
                        anime['seasons'] = 1
                    if 'total_episodes' not in anime:
                        anime['total_episodes'] = 12
                    if 'finished_episodes' not in anime:
                        anime['finished_episodes'] = 0
                    
                    # Handle image data
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
        except Exception as e:
            st.error(f"Error loading anime collection: {e}")
            st.session_state.anime_collection = []

def save_anime_collection():
    if st.session_state.username:
        try:
            anime_collection_serializable = []
            for anime in st.session_state.anime_collection:
                if not isinstance(anime, dict):
                    continue
                    
                anime_copy = anime.copy()
                
                # Ensure all required fields exist
                if 'anime_name' not in anime_copy:
                    anime_copy['anime_name'] = 'Untitled Anime'
                if 'seasons' not in anime_copy:
                    anime_copy['seasons'] = 1
                if 'total_episodes' not in anime_copy:
                    anime_copy['total_episodes'] = 12
                if 'finished_episodes' not in anime_copy:
                    anime_copy['finished_episodes'] = 0
                
                # Handle image data
                if isinstance(anime_copy.get('image'), bytes):
                    try:
                        compressed_image = compress_image(anime_copy['image'])
                        if compressed_image:
                            anime_copy['image'] = base64.b64encode(compressed_image).decode('utf-8')
                        else:
                            anime_copy['image'] = ""
                    except:
                        anime_copy['image'] = ""
                elif anime_copy.get('image') is None:
                    anime_copy['image'] = ""
                
                anime_collection_serializable.append(anime_copy)
            
            doc_ref = db.collection("users").document(st.session_state.username)
            doc_ref.set({"anime_collection": anime_collection_serializable})
            return True
        except Exception as e:
            st.error(f"Error saving anime collection: {e}")
            return False

def save_anime_data(anime_data, edit_index=None):
    try:
        # Validate data
        if not anime_data.get('anime_name'):
            st.error("Anime name is required")
            return False
            
        # Ensure numeric fields are integers
        anime_data['seasons'] = int(anime_data.get('seasons', 1))
        anime_data['total_episodes'] = int(anime_data.get('total_episodes', 12))
        anime_data['finished_episodes'] = int(anime_data.get('finished_episodes', 0))
        
        # Update or add the anime
        if edit_index is not None and 0 <= edit_index < len(st.session_state.anime_collection):
            st.session_state.anime_collection[edit_index] = anime_data
        else:
            st.session_state.anime_collection.append(anime_data)
        
        # Save to database
        if save_anime_collection():
            st.session_state.view = 'home'
            st.session_state.edit_index = None
            return True
        return False
    except Exception as e:
        st.error(f"Error saving anime data: {e}")
        return False

def delete_anime(index):
    try:
        if 0 <= index < len(st.session_state.anime_collection):
            st.session_state.anime_collection.pop(index)
            save_anime_collection()
            st.session_state.view = 'home'
            return True
        return False
    except Exception as e:
        st.error(f"Error deleting anime: {e}")
        return False

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

# Enhanced Authentication page - removed image
def auth_page():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    
    # Tabs for login/signup with enhanced styling
    col1, col2 = st.columns(2)
    
    with col1:
        login_btn_style = "auth-tab active" if st.session_state.auth_mode == "login" else "auth-tab"
        if st.button("Login", key="login_tab_btn", use_container_width=True, 
                    help="Login with your existing account"):
            st.session_state.auth_mode = "login"
    
    with col2:
        signup_btn_style = "auth-tab active" if st.session_state.auth_mode == "signup" else "auth-tab"
        if st.button("Sign Up", key="signup_tab_btn", use_container_width=True,
                    help="Create a new account"):
            st.session_state.auth_mode = "signup"
    
    st.markdown('<div style="margin: 25px 0; border-bottom: 1px solid #333;"></div>', unsafe_allow_html=True)
    
    # Login form with enhanced styling
    if st.session_state.auth_mode == "login":
        st.markdown('<h3 style="text-align: center; margin-bottom: 25px; font-size: 1.8rem; background: linear-gradient(90deg, #8A4FFF, #4F9DFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Welcome Back!</h3>', unsafe_allow_html=True)
        login_username = st.text_input("Username", key="login_username", 
                                     placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_password",
                                     placeholder="Enter your password")
        
        login_btn = st.button("Login", key="submit_login", use_container_width=True)
        
        if login_btn:
            if login_username and login_password:
                with st.spinner("Logging in..."):
                    time.sleep(0.5)
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    load_anime_collection()
                    st.rerun()
            else:
                st.error("Please enter both username and password")
    
    # Signup form with enhanced styling
    elif st.session_state.auth_mode == "signup":
        st.markdown('<h3 style="text-align: center; margin-bottom: 25px; font-size: 1.8rem; background: linear-gradient(90deg, #8A4FFF, #4F9DFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Create Your Account</h3>', unsafe_allow_html=True)
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
                    time.sleep(0.5)
                    st.session_state.logged_in = True
                    st.session_state.username = signup_username
                    save_anime_collection()
                    st.success("Account created successfully!")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced anime card rendering with increased spacing
def render_anime_card(index, anime):
    progress = calculate_progress(anime)
    status = get_status(anime)
    status_text = {"watching": "Watching", "completed": "Completed", "planned": "Planned"}[status]
    
    # Default placeholder image (black background)
    image_url = None
    
    # Try to use the anime's image if available
    if anime.get('image'):
        try:
            image_bytes = anime['image']
            if isinstance(image_bytes, bytes):
                image_b64 = base64.b64encode(image_bytes).decode()
                image_url = f"data:image/jpeg;base64,{image_b64}"
        except:
            pass
    
    # Create the anime card with enhanced spacing
    card_html = f"""
    <div class="anime-card">
        <div class="anime-image" style="background-image: url('{image_url if image_url else ""}'); background-color: #000000;">
            <div class="status-badge status-{status}">{status_text}</div>
        </div>
        <div class="anime-card-content">
            <h3 class="anime-title">{anime.get('anime_name', 'Untitled Anime')}</h3>
            <div class="anime-stats">
                <span>Seasons: {anime.get('seasons', 1)}</span>
                <span>Episodes: {anime.get('finished_episodes', 0)}/{anime.get('total_episodes', 0)}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress}%;"></div>
            </div>
            <div style="text-align:center; margin-top:20px; margin-bottom:20px; font-size: 1rem; color: #AAAAAA;">
                {progress}% complete
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Enhanced action buttons with icons and better spacing
    col1, col2 = st.columns(2)
    with col1:
        st.button("✏️ Edit", key=f"edit_{index}", 
                on_click=lambda: handle_action(f"edit_{index}", set_view, 'add', edit_index=index), 
                use_container_width=True,
                help="Edit this anime entry")
    with col2:
        st.button("🗑️ Delete", key=f"delete_{index}", 
                on_click=lambda: handle_action(f"delete_{index}", delete_anime, index), 
                use_container_width=True,
                help="Delete this anime from your collection")

# Display anime sections with enhanced category styling
def display_section(title, anime_list):
    if not anime_list:
        return
    
    st.markdown(f'<div class="section-container">', unsafe_allow_html=True)
    
    # Enhanced section header with category styling
    category_icon = {
        "Currently Watching": "📺",
        "Planned to Watch": "📝",
        "Completed": "✅"
    }.get(title, "")
    
    st.markdown(f'<h2 class="section-header">{category_icon} {title}</h2>', unsafe_allow_html=True)
    
    # Add category line effect with animation
    st.markdown(f'<div class="category-line"></div>', unsafe_allow_html=True)
    
    # Create a responsive grid layout with better spacing
    cols = st.columns(2)
    for i, (idx, anime) in enumerate(anime_list):
        with cols[i % 2]:
            render_anime_card(idx, anime)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced home view
def display_home_view():
    filtered = filter_anime_collection()
    
    if not filtered:
        st.markdown("""
        <div class="empty-state">
            <h3 class="empty-state-title">Your anime collection is empty</h3>
            <p class="empty-state-text">Start tracking your favorite anime by adding them to your collection.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Add Your First Anime", key="add_first", use_container_width=True):
            handle_action("add_first", set_view, 'add', edit_index=None)
        return
    
    # Filter by status
    watching = [pair for pair in filtered if get_status(pair[1]) == "watching"]
    planned = [pair for pair in filtered if get_status(pair[1]) == "planned"]
    completed = [pair for pair in filtered if get_status(pair[1]) == "completed"]
    
    # Display sections with enhanced spacing
    display_section("Currently Watching", watching)
    display_section("Planned to Watch", planned)
    display_section("Completed", completed)

# Enhanced Add/Edit anime view with improved image handling
def display_add_view():
    is_edit = st.session_state.edit_index is not None
    
    # Initialize default anime data
    default_anime = {
        'anime_name': '', 
        'seasons': 1, 
        'total_episodes': 12, 
        'finished_episodes': 0, 
        'image': None
    }
    
    # Get anime data if editing
    if is_edit and 0 <= st.session_state.edit_index < len(st.session_state.anime_collection):
        anime_data = st.session_state.anime_collection[st.session_state.edit_index]
    else:
        anime_data = default_anime
    
    st.markdown(f'<h2 class="section-header">{"✏️ Edit" if is_edit else "➕ Add New"} Anime</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="category-line"></div>', unsafe_allow_html=True)
    
    with st.form("anime_form", clear_on_submit=False):
        col_img, col_form = st.columns([1, 2])
        
        with col_img:
            st.markdown('<p style="margin-bottom: 15px; font-size: 1.1rem; font-weight: 500;">Cover Image</p>', unsafe_allow_html=True)
            
            # Improved image uploader with better error handling
            image_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            
            # Variable to store the image for saving
            anime_image = None
            
            if image_file:
                try:
                    anime_image_bytes = image_file.read()
                    # Compress image to avoid size issues
                    anime_image = compress_image(anime_image_bytes)
                    if anime_image:
                        # Display the image with enhanced styling
                        st.markdown('<div class="image-preview">', unsafe_allow_html=True)
                        st.image(anime_image, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Failed to process image. Please try a smaller image.")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
            else:
                # Use existing image if available
                existing_image = anime_data.get('image') if isinstance(anime_data.get('image'), bytes) else None
                if existing_image:
                    anime_image = existing_image
                    st.markdown('<div class="image-preview">', unsafe_allow_html=True)
                    st.image(existing_image, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Show placeholder
                    st.markdown("""
                    <div class="image-placeholder">
                        <div>📷 No Image Selected</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_form:
            anime_name = st.text_input("Anime Name", value=anime_data.get('anime_name', ''),
                                     placeholder="Enter anime name")
            
            col1, col2 = st.columns(2)
            with col1:
                # Ensure seasons is an integer
                try:
                    seasons_value = int(anime_data.get('seasons', 1))
                except (ValueError, TypeError):
                    seasons_value = 1
                    
                seasons = st.number_input("Seasons", min_value=1, value=seasons_value)
            with col2:
                # Ensure total_episodes is an integer
                try:
                    total_episodes_value = int(anime_data.get('total_episodes', 12))
                except (ValueError, TypeError):
                    total_episodes_value = 12
                    
                total_episodes = st.number_input("Total Episodes", min_value=1, value=total_episodes_value)
            
            # Ensure finished_episodes is an integer
            try:
                finished_episodes_value = int(anime_data.get('finished_episodes', 0))
                # Make sure it doesn't exceed total episodes
                finished_episodes_value = min(finished_episodes_value, total_episodes)
            except (ValueError, TypeError):
                finished_episodes_value = 0
                
            finished_episodes = st.slider("Episodes Watched", 0, total_episodes, finished_episodes_value)
            
            # Calculate progress
            progress = (finished_episodes / total_episodes) * 100 if total_episodes > 0 else 0
            st.markdown(f"""
            <div style="margin-top:25px; margin-bottom:15px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.1rem;">Progress:</span>
                <span style="font-weight: 600; color: #8A4FFF; font-size: 1.1rem;">{progress:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress/100.0)
        
        # Enhanced form buttons
        col_save, col_cancel = st.columns(2)
        with col_save:
            save_btn = st.form_submit_button("💾 Save Anime", use_container_width=True)
        with col_cancel:
            cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
        
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
                
                if save_anime_data(new_anime, st.session_state.edit_index if is_edit else None):
                    st.success(f"Anime {'updated' if is_edit else 'added'} successfully!")
                    st.rerun()
        
        if cancel_btn:
            st.session_state.view = 'home'
            st.session_state.edit_index = None
            st.rerun()

# Enhanced header with search and user menu - removed image
def display_header():
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        # Enhanced search input with icon
        search = st.text_input("", value=st.session_state.search_query, 
                             placeholder="🔍 Search your anime collection...", 
                             key="search_input", 
                             on_change=lambda: handle_action("search", lambda: None),
                             label_visibility="collapsed")
        
        # Update search query in session state
        st.session_state.search_query = search
    
    with col2:
        # Enhanced add new anime button
        if st.button("➕ Add", key="add_button", use_container_width=True,
                   help="Add a new anime to your collection"):
            handle_action("add_new", set_view, 'add', edit_index=None)
    
    with col3:
        # Enhanced user menu button
        if st.button(f"👤", key="user_button", use_container_width=True,
                   help=f"Logged in as {st.session_state.username}"):
            st.session_state.user_menu_visible = not st.session_state.user_menu_visible
    
    # Enhanced user menu dropdown
    if st.session_state.user_menu_visible:
        st.markdown(f"""
        <div class="user-menu">
            <div style="padding: 12px; text-align: center; border-bottom: 1px solid #333; margin-bottom: 12px;">
                <span style="font-weight: 600; font-size: 1.1rem;">👤 {st.session_state.username}</span>
            </div>
            <div style="padding: 5px 10px;">
                <button class="user-menu-button">🚪 Logout</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button", use_container_width=True):
            handle_action("logout", logout)

# Enhanced main page with header and content
def main_page():
    st.markdown('<h1 class="page-title">Anime Tracker</h1>', unsafe_allow_html=True)
    display_header()
    
    if st.session_state.view == 'home':
        display_home_view()
    elif st.session_state.view == 'add':
        display_add_view()

# Main app logic with improved error handling
def main():
    try:
        if not st.session_state.logged_in:
            # Set default auth mode if not set
            if not st.session_state.auth_mode:
                st.session_state.auth_mode = "login"
            auth_page()
        else:
            # Load anime collection with error handling
            if not st.session_state.anime_collection:
                load_anime_collection()
            main_page()
    except Exception as e:
        st.error(f"An unexpected error occurred. Please try refreshing the page.")
        st.error(f"Error details: {str(e)}")

if __name__ == "__main__":
    main()
