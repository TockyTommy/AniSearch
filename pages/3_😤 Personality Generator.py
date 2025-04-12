import streamlit as st
from pymongo import MongoClient
import pandas as pd
from collections import Counter

# --- MongoDB Connection ---
client = MongoClient("mongodb+srv://mango:DBSassignment@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majority")
db = client["AnimeDatabase"]
collection = db["Anime"]
df = pd.DataFrame(collection.find())

# --- Page Title ---
st.title("😌 Anime Personality Generator")
st.write("Choose your favorite anime and let us tell you your anime soul ✨")

# --- Multiselect Anime ---
anime_choices = df["english_name"].dropna().unique()
selected_anime = st.multiselect("Pick 3–5 of your all-time favs", sorted(anime_choices))

# --- Analyze and Generate Personality ---
if st.button("🔮 Reveal My Personality") and 3 <= len(selected_anime) <= 5:
    selected_df = df[df["english_name"].isin(selected_anime)]

    # Gather genre tags
    genre_list = []
    for g in selected_df["genres"].dropna():
        genre_list.extend([tag.strip() for tag in g.split(",") if tag.strip()])

    # Count top genres
    genre_count = Counter(genre_list)
    top_genre = genre_count.most_common(1)[0][0] if genre_count else "Unknown"

    # Personality Mapping Based on Genre
    personality_types = {
        "Slice of Life": ("🌿 The Slice-of-Life Sage", "You're calm, observant, and find joy in simplicity. You probably cried during *Your Lie in April*."),
        "Action": ("🔥 The Hype King/Queen", "You live for fight scenes, epic comebacks, and jaw-dropping plot twists. You’re the type who says 'One more episode' at 2AM."),
        "Psychological": ("🧠 The Emotional Masochist", "You *choose* pain. Twists, trauma, and emotional damage are your jam."),
        "Mystery": ("🕵️ The Mystery Seeker", "You love mind games and complex storytelling. Plot twists make your soul dance."),
        "Romance": ("💘 The RomCom Dreamer", "You ship people before they even speak. Romance and awkward blushing are your fuel."),
        "Fantasy": ("🧝 The World Hopper", "You're drawn to magical lands, grand quests, and epic lore. Reality? Overrated."),
        "Comedy": ("🤣 The Chaos Goblin", "You thrive in absurdity. If it’s weird, chaotic, and hilarious — you're in."),
        "Supernatural": ("👻 The Beyond Believer", "You vibe with ghosts, demons, and powers beyond logic. Normal life? Nah."),
        "Drama": ("🎭 The Feels Dealer", "Emotional tension, deep characters, and powerful stories — you’re here for all of it.")
    }

    # Default fallback
    persona_name, description = personality_types.get(
        top_genre,
        ("✨ The Enigmatic Watcher", "You're hard to pin down — unpredictable and unique, just like your anime taste.")
    )

    # Display Result
    st.markdown(f"<h2 style='text-align:center'>{persona_name}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:18px'>{description}</p>", unsafe_allow_html=True)

else:
    st.info("Pick 3 to 5 anime before hitting the personality button!")
