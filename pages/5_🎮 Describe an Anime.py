import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymongo

st.set_page_config(page_title="🎮 Describe an Anime", layout="wide")

# MongoDB setup
client = MongoClient("mongodb+srv://streamlit:ligma@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
db = client["AnimeDatabase"]
collection = db["Anime"]

@st.cache_data
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)
    df = df.dropna(subset=['synopsis', 'tags', 'score'])
    return df

df = load_data()

# --------------------------------------------
# Sidebar filters
# --------------------------------------------
st.sidebar.header("🔍 Filters")

safe_search = st.sidebar.checkbox("Safe Search (Hide mature content)", value=True)
min_score = st.sidebar.slider("Minimum Score", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

# Apply safe search filter
if safe_search:
    mature_keywords = ['hentai', 'ecchi', 'erotica']
    df = df[~df['genres'].str.lower().fillna('').str.contains('|'.join(mature_keywords))]
    df = df[~df['tags'].str.lower().fillna('').str.contains('|'.join(mature_keywords))]

# Apply score filter
df = df[df['score'] >= min_score].reset_index(drop=True)

# --------------------------------------------
# Main Page Content
# --------------------------------------------
st.title("🎮 Describe an Anime")
st.markdown("Describe the kind of anime you're interested in, and we'll recommend titles that match your description!")

user_input = st.text_area("Enter a short description of an anime you'd like to watch (e.g. time travel, fantasy war, idol girl with dark secrets)", height=150)

if st.button("Recommend Anime"):
    if user_input.strip() == "":
        st.warning("Please enter a description before generating recommendations.")
    elif df.empty:
        st.error("No anime available after applying filters. Try adjusting them.")
    else:
        temp_df = df.copy()
        temp_df.loc[len(temp_df)] = {'synopsis': user_input, 'tags': '', 'score': 0}

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(temp_df["synopsis"])

        cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        similarity_scores = cosine_sim.flatten()

        top_indices = similarity_scores.argsort()[-5:][::-1]
        recommendations = df.iloc[top_indices]

        st.subheader("🎯 Recommended Anime")
        for idx, row in recommendations.iterrows():
            st.markdown(f"### {row['name']}")
            st.markdown(f"**Score:** {row['score']}")
            st.markdown(f"**Genres:** {row['genres']}")
            st.markdown(f"**Tags:** {row['tags']}")
            st.markdown(f"**Synopsis:** {row['synopsis']}")
            if pd.notna(row.get('image_url', None)):
                st.image(row['image_url'], width=250, use_container_width=False)
            st.markdown("---")
