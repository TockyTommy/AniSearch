import streamlit as st
import pandas as pd
import pymongo
import base64

# Page setup
st.set_page_config(page_title="Anime Database", layout="wide")

st.markdown("""
<style>
/* Full-page dark transparent overlay */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);  /* adjust the opacity here */
    z-index: -1;
}
</style>
""", unsafe_allow_html=True)


def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    background_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: top right;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

# Apply background
set_background("zevcb0355ht81.jpg")
# MongoDB connection
MONGO_URI = "mongodb+srv://streamlit:ligma@anime-cluster.tgb1j32.mongodb.net/anime_db?retryWrites=true&w=majority"

@st.cache_data
def load_data():
    client = pymongo.MongoClient(MONGO_URI)
    db = client['AnimeDatabase']
    collection = db['Anime']
    data = list(collection.find())
    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    return df

df = load_data()

# ----------------- MAIN PAGE CONTENT ----------------- #
st.components.v1.html("""
    <div style="
        background-color: rgba(0, 0, 0, 0.5);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        line-height: 1.6;
        font-size: 18px;
        margin-bottom: 2rem;
    ">
        <h1 style='margin-top: 0;'>📚 AniSearch Database</h1>
        <p>Welcome to the AniSearch Database Web App!</p>
        <p>Built by Anime lovers for anime lovers, this database allows users to explore, search, and receive recommendations based on anime content.<br>
        Try out our fun activities and discover potential anime to watch!</p>

        <h2>🤔 What is Anime?</h2>
        <p><b>Anime</b> is a distinctive style of animated entertainment that originated in Japan and has since gained widespread popularity across the globe. While often compared to Western animation, anime stands apart due to its unique artistic techniques, complex storytelling, cultural depth, and diverse genres. The word "anime" itself is derived from the English word "animation," but in Japan, it refers to all forms of animated media — not just Japanese productions.</p>

        <div style="margin-top: 2rem;">
            <img src="https://4kwallpapers.com/images/walls/thumbs_3t/15604.jpg" width="700px" style="border-radius: 8px;">
            <p style="margin-top: 0.5rem;"><b>Source:</b> <a href="https://4kwallpapers.com/anime/anime-girl-15604.html" style="color: lightblue;" target="_blank">4KWallpapers - Anime Girl</a></p>
        </div>

        <p>What makes anime particularly appealing is its ability to tackle a wide range of themes — from lighthearted adventures and romantic comedies to philosophical dramas, science fiction epics, psychological thrillers, and gritty tales of war and survival. Some anime are aimed at children, while others are crafted specifically for teenagers or adults, making it an incredibly versatile form of media that caters to various age groups and interests.</p>
        
        <h3 style="margin-top: 2rem;">⚠️ Disclaimer</h3>
        <p>We do not own any of the data presented here. The dataset used in this application was obtained from:</p>
        <ul>
            <li><a href="https://www.kaggle.com/datasets/quanthan/top-15000-ranked-anime-dataset-update-to-32025" style="color: lightblue;" target="_blank">Kaggle: Top 15000 Ranked Anime Dataset</a></li>
            <li>Metadata originates from <a href="https://myanimelist.net/" style="color: lightblue;" target="_blank">MyAnimeList</a>, a widely-used anime catalog and community platform.</li>
        </ul>
        <p>This database is also not fully updated with the latest anime released. The cutoff period is Winter 2025.</p>
        <p>This database only displays the top 15,000 anime listed on MyAnimeList. Anime ranked 15,001 and below are not listed here.</p>
    </div>
""", height=1200)

st.divider()

# ----------------- AUTOCOMPLETE SEARCH ----------------- #

st.subheader("🔍 Search Anime")

# Sorted list with blank default
anime_names = df['name'].dropna().astype(str).sort_values().unique().tolist()
anime_names.insert(0, "")  # default blank option

selected_title = st.selectbox("Start typing to search for an anime title:", anime_names)

if selected_title != "":
    selected_anime = df[df['name'] == selected_title].iloc[0]

    st.image(selected_anime.get('image_url', ""), width=250)

    st.markdown(f"### {selected_anime['name']} (Score: {selected_anime.get('score', 'N/A')})")
    st.markdown(f"**Genres:** {selected_anime.get('genres', 'N/A')}")
    st.markdown(f"**Type:** {selected_anime.get('type', 'N/A')} | **Episodes:** {int(selected_anime['episodes']) if pd.notnull(selected_anime.get('episodes')) else 'N/A'}")
    st.markdown(f"**Synopsis:** {selected_anime.get('synopsis', 'No synopsis available')}")
    st.markdown(f"**More Info:** [MyAnimeList Page]({selected_anime.get('anime_url', '#')})")
    st.markdown("---")

