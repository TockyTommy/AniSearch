import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter

# --- MongoDB Connection ---
client = MongoClient("mongodb+srv://mango:DBSassignment@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
db = client["AnimeDatabase"]
collection = db["Anime"]

# --- Fetch All Anime with Valid Rank ---
anime_data = list(
    collection.find({"rank": {"$gt": 0}})
    .sort("rank", 1)
)

# --- Convert to DataFrame ---
df = pd.DataFrame(anime_data)
df = df[df["score"].notna()]
df["rank"] = df["rank"].astype(int)
df["genres"] = df["genres"].fillna("")

# --- Genre List for Dropdown (with "All") ---
genre_set = set()
for g in df["genres"]:
    genre_set.update([genre.strip() for genre in g.split(",") if genre.strip()])
genre_list = ["All"] + sorted(genre_set)

# --- Genre Distribution Setup ---
flat_genres = []
for g in df["genres"]:
    flat_genres.extend([genre.strip() for genre in g.split(",") if genre.strip()])

genre_count = Counter(flat_genres)
genre_df = pd.DataFrame(genre_count.items(), columns=["Genre", "Count"]).sort_values(by="Count", ascending=False)

# Limit to top 8 genres + 'Others'
top_n = 8
if len(genre_df) > top_n:
    top_genres = genre_df.head(top_n)
    others_sum = genre_df["Count"][top_n:].sum()
    genre_df = pd.concat([top_genres, pd.DataFrame([{"Genre": "Others", "Count": others_sum}])], ignore_index=True)

# --- Streamlit Tabs ---
tab1, tab2, tab3 = st.tabs(["Top Tier Anime", "Genre Distribution", "Score vs Popularity"])

# --- Tab 1: Top Anime by Genre ---
with tab1:
    st.subheader("🎖 Top Rated Anime (Tier List)")
    st.caption("Select a genre to view the top 10 ranked anime in that category.")

    selected_genre = st.selectbox("Choose a genre:", genre_list)

    if selected_genre == "All":
        filtered_df = df.copy()
    else:
        filtered_df = df[df["genres"].str.contains(selected_genre, case=False, na=False)]

    top_10 = filtered_df.sort_values(by="rank").head(10)

    if top_10.empty:
        st.warning("No anime found for the selected genre.")
    else:
        fig = px.bar(
            top_10,
            x="score",
            y="name",
            orientation="h",
            hover_data={"score": True, "rank": True},
            color_discrete_sequence=["skyblue"]
        )
        fig.update_layout(
            title=f"Top 10 Anime in Genre: {selected_genre}",
            xaxis_title="Score",
            yaxis_title="Anime Title",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=150, r=50, t=50, b=50)
        )
        st.plotly_chart(fig)

# --- Tab 2: Genre Pie Chart ---
with tab2:
    st.subheader("🥧 Genre Distribution")
    st.caption("Genre distribution is based on all ranked anime available in the database.")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(genre_df["Count"], labels=genre_df["Genre"], autopct="%1.1f%%", startangle=140)
    ax.axis("equal")
    st.pyplot(fig)

# --- Tab 3: Score vs Members Scatter Plot ---
with tab3:
    st.subheader("📈 Score vs Members")
    st.caption("Based on all anime with both score and member count.")

    scatter_df = df[df["members"].notna()].copy()
    scatter_df["score"] = scatter_df["score"].astype(float)
    scatter_df["members"] = scatter_df["members"].astype(int)

    fig = px.scatter(
        scatter_df,
        x="members",
        y="score",
        hover_name="name",
        title="Anime Score vs. Member Count",
        labels={"members": "Number of Members", "score": "Score"},
        color_discrete_sequence=["seagreen"]
    )
    st.plotly_chart(fig)
