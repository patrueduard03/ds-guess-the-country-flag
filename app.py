import streamlit as st
import requests
import random

# Set page configuration for custom title and logo
st.set_page_config(
    page_title="Guess the Country Flag Game",
    page_icon="logo.png",
)

# Initialize session state variables efficiently
def init_session_state():
    defaults = {
        "score": 0,
        "random_country": None,
        "already_guessed": False,
        "wrong_guess": False,
        "first_guess": True,
        "first_partial_guess": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


@st.cache_data
def fetch_countries():
    """Fetch all country data and cache it to minimize API calls."""
    url = "https://restcountries.com/v3.1/all"
    return requests.get(url).json()


def get_random_country(continent, difficulty):
    countries = fetch_countries()

    # Normalize Americas mapping
    continent_mapping = ["North America", "South America", "Central America"] if continent == "Americas" else [
        continent]

    if continent != "All":
        countries = [c for c in countries if
                     'continents' in c and any(cont in c['continents'][0] for cont in continent_mapping)]

    if difficulty == "1 Word Country":
        countries = [c for c in countries if len(c['name']['common'].split()) == 1]
    elif difficulty == "Multiple Words Country":
        countries = [c for c in countries if len(c['name']['common'].split()) >= 2]

    return random.choice(countries) if countries else random.choice(fetch_countries())


def next_country():
    st.session_state.random_country = get_random_country(st.session_state.continent, st.session_state.difficulty)
    st.session_state.already_guessed = False
    st.session_state.wrong_guess = False
    st.session_state.first_guess = True
    st.session_state.first_partial_guess = False


st.title("🌍 Guess the Country Flag Game")

# Add "Choose" as the first option in the continent dropdown
continent = st.selectbox("Choose a continent:", ["Choose", "All", "Africa", "Asia", "Europe", "Americas", "Oceania"], key="continent")
difficulty = st.selectbox("Choose difficulty:", ["1 Word Country", "Multiple Words Country"], key="difficulty")

# Only show the flag and initiate the game if a continent has been selected or if "All" is selected
if continent != "Choose":
    if st.session_state.random_country is None or st.button("Next Country 🎲"):
        next_country()

    random_country = st.session_state.random_country
    st.image(random_country['flags']['png'], width=200)

    if st.session_state.difficulty == "Multiple Words Country":
        hint = "Hint: " + " ".join([word[0].upper() for word in random_country['name']['common'].split()])
        st.write(hint)

    user_guess = st.text_input("Guess the country:", key=f"guess_{random_country['name']['common']}").strip().lower()
    correct_country = random_country['name']['common'].lower()

    if user_guess:
        if st.session_state.first_guess:
            if user_guess == correct_country:
                st.session_state.score += 1
                st.success(f"✅ Correct! It's {random_country['name']['common']}.")
            else:
                st.session_state.wrong_guess = True
                st.warning("❌ Incorrect! One more try.")
            st.session_state.first_guess = False
        elif st.session_state.wrong_guess:
            if user_guess == correct_country:
                st.session_state.score += 0.5
                st.success(f"✅ Correct on second try! It's {random_country['name']['common']}.")
            else:
                st.error(f"❌ Incorrect. The correct answer was {random_country['name']['common']}.")
            st.session_state.already_guessed = True
            st.session_state.wrong_guess = False

    st.write(f"🏆 Score: {st.session_state.score}")
else:
    st.write("Please select a continent to start the game.")

if st.button("🔄 Restart Game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
    st.rerun()
