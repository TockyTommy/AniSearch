import streamlit as st
import random
from pymongo import MongoClient
import pandas as pd

# --- MongoDB Setup ---
client = MongoClient("mongodb+srv://streamlit:ligma@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
db = client["AnimeDatabase"]
collection = db["Anime"]
df = pd.DataFrame(collection.find())

# --- Title ---
st.title("📋 Find Your Anime Match")
st.write("Answer these questions and get anime that match your vibe 🎯")

# --- Survey Form ---
with st.form("anime_survey"):
    q1 = st.radio("1. What kind of story are you in the mood for?", ["Wholesome", "Dark", "Adventurous", "Chill", "Mysterious"])
    q2 = st.radio("2. Do you enjoy deep plots and twists?", ["Yes", "Somewhat", "Nope"])
    q3 = st.radio("3. How much action do you want?", ["High", "Medium", "Low"])
    q4 = st.radio("4. How do you feel about romance?", ["Love it", "A little", "Skip it"])
    q5 = st.radio("5. Which comedy style do you enjoy?", ["Chaotic", "Slice-of-life", "Deadpan", "Not into comedy"])
    q6 = st.radio("6. How okay are you with violence or dark themes?", ["Love it", "Some", "Peaceful only"])
    q7 = st.radio("7. Preferred setting?", ["Modern", "Fantasy", "Sci-fi", "Historical", "School"])
    q8 = st.radio("8. Do you enjoy superpowers or magic?", ["Yes", "Maybe", "No"])
    q9 = st.radio("9. Favorite character type?", ["Underdog", "Anti-hero", "Friend group", "Overpowered", "Quirky"])
    q10 = st.radio("10. How much anime have you watched?", ["Newbie", "Seen some", "Certified weeb"])
    
    submitted = st.form_submit_button("🎯 Show My Anime")

# --- Mapping Survey Answers to Tags ---
if submitted:
    st.markdown("### 🧠 Survey Complete! Finding your match...")

    # Build a tag pool based on answers
    tags = []

    # Match answers to traits
    if q1 == "Wholesome": tags += ["Slice of Life", "Romance"]
    if q1 == "Dark": tags += ["Psychological", "Drama"]
    if q1 == "Adventurous": tags += ["Action", "Adventure"]
    if q1 == "Chill": tags += ["Slice of Life"]
    if q1 == "Mysterious": tags += ["Mystery", "Supernatural"]

    if q2 == "Yes": tags += ["Psychological", "Thriller"]
    if q2 == "Somewhat": tags += ["Drama"]
    
    if q3 == "High": tags += ["Action", "Shounen"]
    if q3 == "Medium": tags += ["Fantasy"]
    
    if q4 == "Love it": tags += ["Romance", "Drama"]
    if q4 == "A little": tags += ["Slice of Life"]
    
    if q5 == "Chaotic": tags += ["Comedy"]
    if q5 == "Slice-of-life": tags += ["Slice of Life"]
    
    if q6 == "Love it": tags += ["Seinen", "Psychological"]
    if q6 == "Some": tags += ["Action"]
    
    if q7 == "Fantasy": tags += ["Fantasy"]
    if q7 == "Sci-fi": tags += ["Sci-Fi"]
    if q7 == "Historical": tags += ["Historical"]
    if q7 == "School": tags += ["School"]

    if q8 == "Yes": tags += ["Supernatural", "Magic"]
    if q8 == "Maybe": tags += ["Fantasy"]
    
    if q9 == "Anti-hero": tags += ["Seinen"]
    if q9 == "Friend group": tags += ["Shounen"]
    if q9 == "Overpowered": tags += ["Action"]

    # --- Filter and Recommend ---
    tag_pattern = "|".join(set(tags))
    matched = df[df["genres"].str.contains(tag_pattern, na=False, case=False)]

    if matched.empty:
        st.warning("Sorry! No matching anime found 😢 Try adjusting your answers.")
    else:
        anime = matched.sample(1).iloc[0]
        st.success("✨ Here's your match!")
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src="{anime['image_url']}" width="300"><br><br>
                <h3>{anime['english_name'] or anime['name']}</h3>
                <p style='font-size:18px;'>{anime['japanese_names']}</p>
                <p style='font-size:16px;'>Genres: {anime['genres']}</p>
                <p style='font-size:14px;'>{anime['synopsis'][:300]}...</p>
            </div>
            """,
            unsafe_allow_html=True
        )
