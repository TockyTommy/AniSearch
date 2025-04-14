import streamlit as st
import random
import time
from pymongo import MongoClient
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="🎲 Random Anime Generator", layout="wide")

# --- MongoDB Connection with Caching ---
@st.cache_data
def load_anime_data():
    try:
        client = MongoClient("mongodb+srv://streamlit:ligma@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
        db = client["AnimeDatabase"]
        collection = db["Anime"]
        data = list(collection.find())
        return data
    except Exception as e:
        st.error(f"❌ Failed to connect to MongoDB: {e}")
        return []

# --- Load and Clean Data ---
anime_data = load_anime_data()
if not anime_data:
    st.stop()

df = pd.DataFrame(anime_data)
if "_id" in df.columns:
    df.drop(columns=["_id"], inplace=True)

df = df[df["image_url"].notna() & df["name"].notna()]

# --- Title ---
st.title("🎲 Random Anime Generator")
st.write("Don't know where to start? Generate a random anime with these filters for a surprise!")

# --- Anime Spin Form ---
with st.form("spin_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        genres = sorted(set(g.strip() for sublist in df["genres"].dropna().str.split(",") for g in sublist))
        selected_genre = st.selectbox("🎭 Genre", options=["Any"] + genres)

    with col2:
        selected_type = st.selectbox("📺 Type", options=["Any"] + sorted(df["type"].dropna().unique()))

    with col3:
        selected_rating = st.selectbox("🔞 Rating", options=["Any"] + sorted(df["rating"].dropna().unique()))

    spin = st.form_submit_button("🔄 Spin!")

# --- Filtering Logic ---
if spin:
    filtered_df = df.copy()

    if selected_genre != "Any":
        filtered_df = filtered_df[filtered_df["genres"].str.contains(selected_genre, na=False, case=False)]

    if selected_type != "Any":
        filtered_df = filtered_df[filtered_df["type"] == selected_type]

    if selected_rating != "Any":
        filtered_df = filtered_df[filtered_df["rating"] == selected_rating]

    st.markdown("### 🎰 Spinning the Wheel...")

    if not filtered_df.empty:
        spin_placeholder = st.empty()
        for _ in range(20):
            temp_anime = filtered_df.sample(1).iloc[0]
            spin_placeholder.markdown(f"### **{temp_anime['name']}**")
            time.sleep(0.1)

        # Final result
        st.success("✨ Your Anime Is Ready!")
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src="{temp_anime.get("image_url", "")}" width="500"><br><br>
                <h3>Japanese Name</h3>
                <p style='font-size:20px;'><strong>{temp_anime.get("japanese_names", "N/A")}</strong></p><br>
                <h3>English Name</h3>
                <p style='font-size:20px;'><strong>{temp_anime.get("english_name") or temp_anime.get("name")}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("No anime found matching your filters 😢")
