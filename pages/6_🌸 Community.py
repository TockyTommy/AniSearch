import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Page setup (must be first Streamlit call) ---
st.set_page_config(page_title="🌸 Community", layout="wide")

# --- MongoDB setup ---
client = pymongo.MongoClient("mongodb+srv://streamlit2:ligma@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
db = client["AnimeDatabase"]
anime_collection = db["Anime"]
community_collection = db["CommunitySubmissions"]

# --- Load anime titles and genres for dropdowns ---
@st.cache_data
def get_dropdown_data():
    data = list(anime_collection.find({}, {"name": 1, "genres": 1}))
    anime_names = sorted(set(str(d["name"]).strip() for d in data if "name" in d and d["name"]))
    genre_set = set()
    for entry in data:
        if "genres" in entry and entry["genres"]:
            genre_set.update(g.strip() for g in entry["genres"].split(",") if g.strip())
    genre_list = sorted(genre_set)
    return anime_names, genre_list

anime_names, genre_list = get_dropdown_data()

# --- Page Title & Description ---
st.title("🌸 AniSearch Community Corner")
st.markdown("""
Help us learn more about our community by sharing your favorite anime and explore what others love!
""")

# --- Form for user submission ---
with st.form("community_form", clear_on_submit=True):
    name = st.text_input("Your Display Name")
    fav_anime = st.selectbox("Your favorite anime *", [""] + anime_names)
    fav_genre = st.selectbox("Your favorite genre *", [""] + genre_list)
    fav_character = st.text_input("Who is your favorite anime character?", placeholder="e.g. Lelouch, Mikasa, Gojo, etc.")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if fav_anime and fav_genre:
            doc = {
                "name": name.strip() or "Anonymous",
                "favorite_anime": fav_anime.strip(),
                "favorite_genre": fav_genre.strip(),
                "favorite_character": fav_character.strip(),
                "timestamp": datetime.now()
            }
            community_collection.insert_one(doc)
            st.success("Thanks for sharing with the community!")
        else:
            st.error("Please select both favorite anime and genre.")

# --- Load community submissions ---
st.divider()
st.subheader("📢 Community Favorites")

submissions = list(community_collection.find().sort("timestamp", -1))
if submissions:
    df = pd.DataFrame(submissions)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(
        df[["name", "favorite_anime", "favorite_genre", "favorite_character", "timestamp"]].rename(columns={
            "name": "Name",
            "favorite_anime": "Favorite Anime",
            "favorite_genre": "Genre",
            "favorite_character": "Favorite Character",
            "timestamp": "Submitted At"
        }),
        use_container_width=True
    )

    # --- Pie Chart: Top 10 Favorite Anime ---
    st.subheader("🥧 Top 10 Favorite Anime")
    anime_counts = df["favorite_anime"].value_counts().nlargest(10)
    fig1 = px.pie(
        values=anime_counts.values,
        names=anime_counts.index,
        title="Most Loved Anime by Community",
        hole=0.3
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Bar Chart: Favorite Genres ---
    st.subheader("📊 Favorite Genres in the Community")
    genre_counts = df["favorite_genre"].value_counts()
    fig2 = px.bar(
        x=genre_counts.values,
        y=genre_counts.index,
        orientation="h",
        title="Most Popular Genres",
        labels={"x": "Count", "y": "Genre"},
        color_discrete_sequence=["lightcoral"]
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

    # --- Word Cloud: Favorite Characters ---
    st.subheader("☁️ Favorite Characters Word Cloud")
    all_characters = " ".join(df["favorite_character"].dropna().astype(str).tolist())
    if all_characters.strip():
        wc = WordCloud(width=800, height=400, background_color="white", colormap="plasma").generate(all_characters)
        fig3, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig3)
    else:
        st.info("No characters submitted yet.")
else:
    st.info("No community submissions yet — be the first to share!")
