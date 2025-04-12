import streamlit as st
import pandas as pd
import pymongo
import base64

# Page setup
st.set_page_config(page_title="Anime Database", layout="wide")

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
MONGO_URI = "mongodb+srv://VincentPhang:PLJ5U3ZnkWR39DHJ@anime-cluster.tgb1j32.mongodb.net/anime_db?retryWrites=true&w=majority"

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

st.title("📚 AniSearch Database")
st.markdown("""
Welcome to the AniSearch Database Web App!

Built by Anime lovers for anime lovers, this database allows users to explore, search, and receive recommendations based on anime content.  
Try out our fun activities and discover potential anime to watch!

### 🤔 What is Anime?
**Anime** refers to a style of animation originating from Japan, characterized by colorful graphics, fantastical themes, and vibrant characters.  
It spans a wide range of genres, from action and adventure to romance, horror, and slice-of-life.
""")

st.image("anime-girl-3840x2160-15604.jpg", width=700)
st.markdown("**Source:** [4KWallpapers - Anime Girl](https://4kwallpapers.com/anime/anime-girl-15604.html)")

st.markdown("""
### ⚠️ Disclaimer
We do not own any of the data presented her. The dataset used in this application was obtained from:
- Kaggle: [Top 15000 Ranked Anime Dataset](https://www.kaggle.com/datasets/quanthan/top-15000-ranked-anime-dataset-update-to-32025)
- The actual anime metadata originates from [MyAnimeList](https://myanimelist.net/), a widely-used anime catalog and community platform.

This database is also not fully updated with the latest anime released. The cutoff period is Winter 2025.
""")

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

