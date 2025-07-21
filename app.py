# app.py
import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    """Fetches a movie poster URL from the TMDB API."""
    # IMPORTANT: Get your own free API key from https://www.themoviedb.org/
    api_key = "YOUR_TMDB_API_KEY_HERE"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception:
        return None

# Function to get movie recommendations
def recommend(movie):
    """Recommends 5 similar movies."""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []
        
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        
    return recommended_movies, recommended_posters

# Load data (cached for performance)
@st.cache_data
def load_data():
    movies_df = pd.DataFrame(pickle.load(open('movies_dict.pkl', 'rb')))
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity_matrix

try:
    movies, similarity = load_data()
except FileNotFoundError:
    st.error("Model files not found. Please run `prepare_data.py` first.")
    st.stop()

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title('🎬 Movie Recommender System')

selected_movie = st.selectbox(
    'Select a movie you like, and we will recommend similar ones:',
    movies['title'].values
)

if st.button('Recommend', type="primary"):
    with st.spinner('Finding recommendations...'):
        names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                if posters[i]:
                    st.image(posters[i])
                else:
                    st.write("Poster not available")