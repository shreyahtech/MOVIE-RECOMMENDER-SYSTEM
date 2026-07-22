import streamlit as st
import pickle
import pandas as pd
import os
import time
import requests
from dotenv import load_dotenv

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="MovieFlix",
    page_icon="🎬",
    layout="wide"
)

# --------------------------------------------------
# LOAD ENV
# --------------------------------------------------

load_dotenv()
api_key = os.getenv("TMDB_API_KEY")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* Background */
.stApp{
    background:
    radial-gradient(circle at top left,
    rgba(229,9,20,0.25) 0%,
    transparent 30%),

    radial-gradient(circle at top right,
    rgba(138,43,226,0.20) 0%,
    transparent 30%),

    radial-gradient(circle at bottom left,
    rgba(255,0,102,0.15) 0%,
    transparent 35%),

    #0B0B0B;

    color:white;
}
}

/* Remove top spacing */
.block-container{
    padding-top:2rem;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background-color:#000000;
}

/* Netflix Logo */
.netflix-logo{
    color:#E50914;
    font-size:60px;
    font-weight:900;
    text-align:center;
    letter-spacing:3px;
    margin-bottom:10px;
}

/* Hero Banner */
.hero{
    padding:60px;
    border-radius:20px;
    text-align:center;

    background:
    linear-gradient(
        rgba(0,0,0,0.8),
        rgba(0,0,0,0.8)
    ),
    linear-gradient(
        135deg,
        #E50914,
        #8B0000,
        #4B0082
    );

    box-shadow:0 0 40px rgba(229,9,20,0.3);
}
.hero h2{
    color:white;
    font-size:45px;
    margin-bottom:10px;
}

.hero p{
    color:#d1d1d1;
    font-size:18px;
}

/* Selectbox */
div[data-baseweb="select"] > div{
    background-color:#1f1f1f !important;
    color:white !important;
    border-radius:10px;
}

/* Buttons */
.stButton button{
    background:#E50914;
    color:white;
    border:none;
    border-radius:10px;
    font-weight:bold;
    width:100%;
    height:50px;
    font-size:16px;
}

.stButton button:hover{
    background:#ff1f1f;
}

/* Movie Card */
.movie-card{
    background:rgba(255,255,255,0.05);
    padding:10px;
    border-radius:12px;
    text-align:center;
    backdrop-filter:blur(10px);
    transition:0.3s;
}

.movie-card:hover{
    transform:translateY(-5px);
}

.movie-title{
    color:white;
    font-weight:600;
    margin-top:10px;
    min-height:60px;
}

/* Poster */
img{
    border-radius:12px;
}

/* Footer */
.footer{
    text-align:center;
    color:gray;
    margin-top:40px;
}

/* Scrollbar */
::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-thumb{
    background:#E50914;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FETCH POSTER
# --------------------------------------------------

def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={api_key}&language=en-US"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(5):

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            poster_path = data.get("poster_path")

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

            return "https://via.placeholder.com/500x750?text=No+Poster"

        except requests.exceptions.RequestException:
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=Error"

def fetch_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        return {
            "rating": data.get("vote_average", "N/A"),
            "release_date": data.get("release_date", "N/A"),
            "overview": data.get("overview", "No description available.")
        }

    except:
        return {
            "rating": "N/A",
            "release_date": "N/A",
            "overview": "No description available."
        }


def fetch_trailer(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        for video in data["results"]:

            if (
                video["site"] == "YouTube"
                and video["type"] == "Trailer"
            ):
                return f"https://www.youtube.com/watch?v={video['key']}"

    except:
        pass

    return None

# --------------------------------------------------
# RECOMMENDATION FUNCTION
# --------------------------------------------------

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:

        movie_id = int(movies.iloc[i[0]].movie_id)

        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        recommended_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_posters

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    "<div class='netflix-logo'>MOVIEFLIX</div>",
    unsafe_allow_html=True
)

st.markdown("""
<div class='hero'>
    <h2>Unlimited Movies. Unlimited Recommendations.</h2>
    <p>Discover your next favorite movie with AI-powered suggestions.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# MOVIE SELECTOR
# --------------------------------------------------

st.markdown("### 🍿 Choose a Movie")

selected_movie = st.selectbox(
    "",
    movies['title'].values
)

# --------------------------------------------------
# RECOMMEND BUTTON
# --------------------------------------------------

if st.button("🎬 Get Recommendations"):

    with st.spinner("Finding movies you'll love... 🍿"):
        names, posters = recommend(selected_movie)

    movie_id = int(
        movies[movies['title'] == selected_movie]
        .iloc[0]
        .movie_id
    )

    details = fetch_movie_details(movie_id)

    trailer_url = fetch_trailer(movie_id)

    st.markdown(f"""
    <div style="
    background:rgba(255,255,255,0.05);
    padding:25px;
    border-radius:15px;
    margin-top:20px;
    margin-bottom:20px;
    ">

    <h2>🎬 {selected_movie}</h2>

    <p>⭐ Rating: {details['rating']}/10</p>

    <p>📅 Release Date: {details['release_date']}</p>

    <p>{details['overview']}</p>

    </div>
    """, unsafe_allow_html=True)

    if trailer_url:
        st.link_button("▶️ Watch Trailer", trailer_url)

    st.markdown(
        "<h2 style='margin-top:30px;'>🔥 Recommended For You</h2>",
        unsafe_allow_html=True
    )

    cols = st.columns(5)

    for col, name, poster in zip(cols, names, posters):

        with col:

            st.image(
                poster,
                use_container_width=True
            )

            st.markdown(
                f"<div class='movie-title'>{name}</div>",
                unsafe_allow_html=True
            )

            rec_movie_id = int(
                movies[movies['title'] == name]
                .iloc[0]
                .movie_id
            )

            rec_details = fetch_movie_details(rec_movie_id)

            st.caption(f"⭐ {rec_details['rating']}/10")

            release_year = (
                rec_details['release_date'][:4]
                if rec_details['release_date'] != "N/A"
                else "N/A"
            )

            st.caption(f"📅 {release_year}")

            overview = rec_details['overview']

            if len(overview) > 80:
                overview = overview[:80] + "..."

            st.caption(overview)