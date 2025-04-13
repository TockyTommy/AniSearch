import streamlit as st
from pymongo import MongoClient
import pandas as pd
from collections import Counter

# --- MongoDB Connection ---
client = MongoClient("mongodb+srv://streamlit:ligma@anime-cluster.tgb1j32.mongodb.net/?retryWrites=true&w=majorityy")
db = client["AnimeDatabase"]
collection = db["Anime"]
df = pd.DataFrame(collection.find())

# --- Page Title ---
st.title("😌 Anime Personality Generator")
st.write("Choose your favorite anime and let us tell you your anime soul ✨")

# --- Prepare Anime Choices ---
df = df[df["genres"].notna() & df["name"].notna()]
anime_choices = df["name"].dropna().astype(str).unique()

# --- Form for Anime Selection ---
with st.form("anime_form"):
    selected_anime = st.multiselect("Pick 3–5 of your all-time favs", sorted(anime_choices))
    submitted = st.form_submit_button("🔮 Reveal My Personality")

# --- Analyze and Generate Personality ---
if submitted and 3 <= len(selected_anime) <= 5:
    selected_df = df[df["name"].isin(selected_anime)]

    # Gather genre tags
    genre_list = []
    for g in selected_df["genres"].dropna():
        genre_list.extend([tag.strip().lower() for tag in g.split(",") if tag.strip()])

    # Count top genres
    genre_count = Counter(genre_list)
    top_genre = genre_count.most_common(1)[0][0] if genre_count else "unknown"

    # Personality Mapping
    personality_types = {
        "slice of life": ("🌿 The Slice-of-Life Sage", "You're calm, observant, and find joy in simplicity. You probably cried during *Your Lie in April*."),
        "action": ("🔥 The Hype King/Queen", "You live for fight scenes, epic comebacks, and jaw-dropping plot twists. You’re the type who says 'One more episode' at 2AM."),
        "psychological": ("🧠 The Emotional Masochist", "You *choose* pain. Twists, trauma, and emotional damage are your jam."),
        "mystery": ("🕵️ The Mystery Seeker", "You love mind games and complex storytelling. Plot twists make your soul dance."),
        "romance": ("💘 The RomCom Dreamer", "You ship people before they even speak. Romance and awkward blushing are your fuel."),
        "fantasy": ("🧝 The World Hopper", "You're drawn to magical lands, grand quests, and epic lore. Reality? Overrated."),
        "comedy": ("🤣 The Chaos Goblin", "You thrive in absurdity. If it’s weird, chaotic, and hilarious — you're in."),
        "supernatural": ("👻 The Beyond Believer", "You vibe with ghosts, demons, and powers beyond logic. Normal life? Nah."),
        "drama": ("🎭 The Feels Dealer", "Emotional tension, deep characters, and powerful stories — you’re here for all of it."),
        "sci-fi": ("🚀 The Future Dreamer", "You're fascinated by advanced technology, space-time twists, and exploring what's beyond. Your mind lives in tomorrow."),
        "award winning": ("🏆 The Prestige Seeker", "You value quality, artistry, and impact. If it's critically acclaimed, you’re watching it first."),
        "suspense": ("⏳ The Edge-Lurker", "You live for tension and cliffhangers. You can’t sit still if there's a mystery unresolved — you *have* to know what happens next.")
    }

    # Get the matching personality
    persona_name, description = personality_types.get(
        top_genre,
        ("✨ The Enigmatic Watcher", "You're hard to pin down — unpredictable and unique, just like your anime taste.")
    )

    # Display Result
    st.markdown(f"<h2 style='text-align:center'>{persona_name}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:18px'>{description}</p>", unsafe_allow_html=True)

elif submitted:
    st.warning("Please select between 3 to 5 anime.")
