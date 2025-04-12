import streamlit as st
import pandas as pd
import pymongo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set page config
st.set_page_config(page_title="🎯 Describe an Anime", layout="wide")

# MongoDB Atlas connection
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
    df = df[df['score'] >= 7.0].reset_index(drop=True)
    df['synopsis'] = df['synopsis'].fillna('').str.lower()
    df['tags'] = df['tags'].fillna('')
    df['full_profile'] = df['tags'] + ' ' + df['synopsis']
    return df

df = load_data()

# App header
st.title("🕵️‍♂️ Describe an Anime")
st.write("Type a sentence describing an anime, and we’ll find an anime for you!")

# User description input
user_description = st.text_area("Describe the anime here:", placeholder="e.g. A teenager finds a mysterious notebook that can kill people")

# Recommend button
if st.button("Find Matching Anime") and user_description.strip():
    user_profile = user_description.lower()
    user_df = pd.DataFrame({'full_profile': [user_profile]})
    combined_df = pd.concat([df[['name', 'full_profile']], user_df], ignore_index=True)

    # TF-IDF & similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(combined_df['full_profile'])
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    top_indices = similarities[0].argsort()[-5:][::-1]
    matches = df.iloc[top_indices][['name', 'score', 'genres', 'synopsis', 'image_url', 'anime_url']]

    # Display matches
    st.subheader("🎬 Anime That Match Your Description:")
    for _, anime in matches.iterrows():
        st.markdown(f"### 🎞 {anime['name']} (Score: {anime['score']})")

        # Show image if available
        if pd.notnull(anime.get("image_url", "")):
            st.image(anime['image_url'], width=200)

        st.markdown(f"**Genres:** {anime.get('genres', 'N/A')}")
        st.markdown(f"**Synopsis:** {anime.get('synopsis', 'No synopsis available')[:400]}...")
        st.markdown(f"**More Info:** [MyAnimeList Page]({anime.get('anime_url', '#')})")
        st.markdown("---")
