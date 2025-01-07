#page details pas bonne
import base64
from pdf2image import convert_from_path
import pandas as pd
import streamlit as st
import requests

# Clé API TMDb
api_key = 'dcc19539bb2aad10e600613bd95f3cd5'

# Configuration de l'application
st.set_page_config(page_title="Cin&Moi", page_icon="🎥", layout="wide")

# Charger les données avec mise en cache
@st.cache_data
def load_data():
    df = pd.read_parquet("Cinemoi.parquet")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")  # Conversion en datetime
    return df

data = load_data()

# Genres autorisés
allowed_genres = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
    'Music', 'Mystery', 'Romance', 'Science Fiction', 'TV Movie',
    'Thriller', 'War', 'Western'
]

# Ajouter des styles dynamiques
st.markdown(
    """
    <style>
    .header {
        background-color: #ffd700;
        padding: 10px;
        border-left: 5px solid red;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .title {
        font-size: 48px;
        font-weight: bold;
        color: black;
        text-align: center;
    }
    .highlight {
        color: red;
    }
    .note-red {
        color: #FF0000; /* Rouge */
        font-weight: bold;
    }
    .note-orange {
        color: #FFA500; /* Orange */
        font-weight: bold;
    }
    .note-green {
        color: #008000; /* Vert */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Fonction pour attribuer une classe CSS aux notes
def get_note_class(note):
    if note <= 3:
        return "note-red"
    elif 4 <= note <= 7:
        return "note-orange"
    else:
        return "note-green"

# Titre principal
st.markdown('<div class="header"><div class="title">Cin<span class="highlight">&</span>Moi</div></div>', unsafe_allow_html=True)

# Préparer les données
def prepare_data(df):
    df['combined_features'] = (df['genre'].fillna('') + " " + df['overview'].fillna('') + " " + df['title'].fillna(''))
    return df

data = prepare_data(data)

# Fonction pour récupérer les informations du film en français
def get_movie_info(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&language=fr&external_source=imdb_id"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'movie_results' in data and data['movie_results']:
            movie = data['movie_results'][0]
            return {
                'title': movie.get('title', 'N/A'),
                'overview': movie.get('overview', 'N/A')
            }
        else:
            return {'title': 'N/A', 'overview': 'N/A'}
    else:
        return {'title': 'Erreur', 'overview': 'Impossible de récupérer les informations du film.'}

# Gérer l'état pour les pages
if "page" not in st.session_state:
    st.session_state.page = "results"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Fonction pour naviguer vers une autre page
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# Fonction pour réinitialiser la page à l'état initial
def reset_to_home_page():
    st.session_state.page = "results"
    st.session_state.selected_movie = None
    st.session_state.search_query = ""
    st.session_state.current_page = 1
    st.rerun()

# Fonction pour afficher le bouton "Retour page principale"
def show_back_to_home_button():
    if st.button("Retour page principale"):
        reset_to_home_page()

# Barre de recherche et boutons en haut
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    search_query = st.text_input("Recherchez un film par titre", st.session_state.search_query)

# Si la recherche change, on met à jour le state
if search_query != st.session_state.search_query:
    st.session_state.search_query = search_query
    st.session_state.page = "results"

with col2:
    if st.button("Étude de marché en Creuse"):
        navigate_to("pdf1")

with col3:
    if st.button("Descriptif de la base Cin&moi"):
        navigate_to("pdf2")

with col4:
    st.markdown(
        '<a href="https://trello.com/b/Y5yM7uhR" target="_blank" style="text-decoration: none;">'
        '<button style="width: 100%; padding: 6px 12px; font-size: 14px; background-color: #ffd700; color: black; border: none; border-radius: 4px; cursor: pointer;">'
        'L\'équipe</button></a>',
        unsafe_allow_html=True
    )


# Gestion des pages PDF
if st.session_state.page == "pdf1":
    st.markdown("### Étude de marché en Creuse")
    pdf_path = "kpi1.pdf"
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}" width="700" height="900"></iframe>', unsafe_allow_html=True)
    show_back_to_home_button()

elif st.session_state.page == "pdf2":
    st.markdown("### Descriptif de la base Cin&moi")
    pdf_path = "kpi2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_data).decode()}" width="700" height="900"></iframe>', unsafe_allow_html=True)
    show_back_to_home_button()

elif st.session_state.page == "results":
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Filtres")
        selected_genre = st.selectbox("Genre", options=["Tous"] + allowed_genres)
        selected_year_min = st.number_input("À partir de:", min_value=1900, max_value=2024, value=1900, step=1)

    filtered_data = data.copy()

    if search_query:
        filtered_data = filtered_data[filtered_data["title"].str.contains(search_query, case=False, na=False) |
                                      filtered_data["overview"].str.contains(search_query, case=False, na=False)]

    if selected_genre != "Tous":
        filtered_data = filtered_data[filtered_data["genre"] == selected_genre]

    filtered_data = filtered_data[(filtered_data["release_date"].dt.year >= selected_year_min)]
    filtered_data = filtered_data.drop_duplicates(subset="title", keep="first")

    movies_per_page = 10
    with col2:
        st.subheader("Résultats")
        total_movies = len(filtered_data)

        if total_movies == 0:
            st.warning("Aucun film ne correspond à vos critères.")
            st.image("tipanic.jpg", caption="Film non trouvé", use_container_width=0.7)
        else:
            total_pages = max(1, (total_movies // movies_per_page) + (1 if total_movies % movies_per_page > 0 else 0))
            current_page = st.session_state.current_page

            col_left, col_right = st.columns([1, 1])
            with col_left:
                if st.button("⬅️ Page précédente") and current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
            with col_right:
                if st.button("➡️ Page suivante") and current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()

            start_idx = (current_page - 1) * movies_per_page
            end_idx = min(start_idx + movies_per_page, total_movies)

            for _, row in filtered_data.iloc[start_idx:end_idx].iterrows():
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    st.image(row['poster_path'], use_container_width=True)
                with col_info:
                    movie_info = get_movie_info(row['imdb_id'])  # Récupération des infos en français
                    st.markdown(f"### {movie_info['title']}")
                    st.markdown(f"**Genre**: {row['genre']}")
                    st.markdown(f"**Année**: {row['release_date'].year if pd.notna(row['release_date']) else 'Inconnu'}")
                    st.markdown(f"**Synopsis**: {movie_info['overview']}")
                    st.markdown(
                        f"**Note du public**: <span class='{get_note_class(row['vote_average'])}'>{row['vote_average']:.1f}</span>",
                        unsafe_allow_html=True
                    )
                    if st.button("Voir les détails", key=row['title']):
                        st.session_state.selected_movie = row.to_dict()
                        navigate_to("movie_detail")
        show_back_to_home_button()

elif st.session_state.page == "movie_detail":
    movie = st.session_state.selected_movie
    if movie:
        st.markdown(f"## {movie['title']}")
        st.markdown(f"### Genre: {movie['genre']}")
        st.markdown(f"### Année: {movie['release_date'].year if pd.notna(movie['release_date']) else 'Inconnu'}")
        st.markdown(f"### Synopsis: {movie['overview']}")
        st.markdown(
            f"**Note du public**: <span class='{get_note_class(movie['vote_average'])}'>{movie['vote_average']:.1f}</span>",
            unsafe_allow_html=True
        )
        st.image(movie['poster_path'], width=200)

        def get_movie_trailer(imdb_id):
            url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&language=fr&external_source=imdb_id"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'movie_results' in data and data['movie_results']:
                    movie_id = data['movie_results'][0]['id']
                    trailer_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=fr"
                    trailer_response = requests.get(trailer_url)
                    if trailer_response.status_code == 200:
                        trailer_data = trailer_response.json()
                        if trailer_data['results']:
                            for video in trailer_data['results']:
                                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                                    return f"https://www.youtube.com/watch?v={video['key']}"
            return None

        trailer_link = get_movie_trailer(movie['imdb_id'])
        if trailer_link:
            st.markdown(f"### Bande-annonce")
            st.video(trailer_link)
        else:
            st.write("Aucune bande-annonce disponible pour ce film.")

        recommended_movies = data[data['genre'] == movie['genre']].head(11)
        st.subheader("Films recommandés")
        movies_grid = recommended_movies.iloc[1:11]
        for row in range(0, len(movies_grid), 5):
            cols = st.columns(5)
            for col, (_, rec_movie) in zip(cols, movies_grid.iloc[row:row + 5].iterrows()):
                with col:
                    st.image(rec_movie['poster_path'], width=100)
                    st.markdown(f"**{rec_movie['title']}**")
                    st.markdown(f"Genre: {rec_movie['genre']}")
                    st.markdown(
                        f"**Note du public**: <span class='{get_note_class(rec_movie['vote_average'])}'>{rec_movie['vote_average']:.1f}</span>",
                        unsafe_allow_html=True
                    )
                    if st.button(f"Détails {rec_movie['title']}", key=rec_movie['title']):
                        st.session_state.selected_movie = rec_movie.to_dict()
                        navigate_to("movie_detail")

    if st.button("Retour aux résultats"):
        navigate_to("results")

    show_back_to_home_button()
