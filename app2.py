import pickle
import streamlit as st
import requests
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# ------------------ BASE PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ------------------ LOAD MODEL ------------------
movies = pickle.load(open(os.path.join(MODEL_DIR, "movie_list.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(MODEL_DIR, "similarity.pkl"), "rb"))

movie_list = movies["title"].values

# ------------------ TMDB POSTER (ID BASED – PERMANENT) ------------------
@st.cache_data(show_spinner=False)
def fetch_poster(tmdb_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": "8265bd1679663a7ea12ac168da84d2e8"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        poster_path = data.get("poster_path")
        if poster_path:
            poster_url = "https://image.tmdb.org/t/p/w500" + poster_path
            img = requests.get(poster_url, timeout=5)
            return img.content   # ✅ BYTES

    except:
        pass

    # fallback image as BYTES
    with open(os.path.join(ASSETS_DIR, "no_poster.png"), "rb") as f:
        return f.read()

# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names = []
    posters = []

    for i in distances[1:6]:
        row = movies.iloc[i[0]]
        names.append(row["title"])
        posters.append(fetch_poster(int(row["id"])))  # ✅ TMDB ID

    return names, posters

# st.write(movies.head())
# st.write(movies.columns)


# ------------------ HERO SECTION ------------------
st.markdown(
    """
    <h1 style='text-align:center;'>🎬 Movie Recommender System</h1>
    <p style='text-align:center; font-size:18px; color:#aaa;'>
    Discover movies similar to your favorites using Machine Learning
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ------------------ MOVIE SELECTOR ------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie = st.selectbox("🎥 Select a movie", movie_list)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ SHOW RECOMMENDATION ------------------
if st.button("✨ Show Recommendations"):
    with st.spinner("Finding the best recommendations for you..."):
        names, posters = recommend(selected_movie)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎯 Recommended Movies")

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.markdown(
                f"<p style='text-align:center; font-weight:600;'>{names[i]}</p>",
                unsafe_allow_html=True
            )

# ------------------ FOOTER ------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray;'>
    Built with ❤️ using Machine Learning & Streamlit
    </p>
    """,
    unsafe_allow_html=True
)
