import pandas as pd
import streamlit as st
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from faker import Faker
import random
import ast

# Initialize Faker for generating fake data
fake = Faker()

# Load KDrama dataset
kdrama_data = pd.read_csv('data/kdrama.csv')

# Function to get title from index
def get_title_from_index(index):
    return kdrama_data.loc[kdrama_data.index == index, "Name"].values[0]

# Function to get index from title
def get_index_from_title(title):
    return kdrama_data.loc[kdrama_data["Name"].str.lower() == title.lower()].index.tolist()

# Function to combine features into a single string for cosine similarity
def combined_features(row):
    return f"{row['Name']} {row['Year of release']} {row['Original Network']} {row['Aired On']} {row['Duration']} {row['Content Rating']} {row['Genre']} {row['Rating']}"

# Apply combined_features function to create a new combined_feature column
kdrama_data["combined_feature"] = kdrama_data.apply(combined_features, axis=1)

# Instantiate CountVectorizer
cv = CountVectorizer()

# Fit and transform the combined_feature column to create a count matrix
count_matrix = cv.fit_transform(kdrama_data["combined_feature"])

# Calculate cosine similarity
cosine_sim = cosine_similarity(count_matrix)

# Function to get IMDb ID using OMDb API (replace with your actual OMDb API key)
def get_imdb_id(title):
    base_url = "http://www.omdbapi.com/"
    api_key = "7b5e6a2b"  # Replace with your OMDb API key
    params = {
        "apikey": api_key,
        "t": title,
        "type": "series"  # Assuming KDramas are considered as series
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            return data.get('imdbID')
    return None

# Load user data or create an empty DataFrame if the file doesn't exist
users_file_path = 'data/users.csv'
if os.path.exists(users_file_path):
    users_df = pd.read_csv(users_file_path)
    # Ensure 'watchlist' and 'ratings' columns are properly initialized
    if 'watchlist' not in users_df.columns:
        users_df['watchlist'] = users_df.apply(lambda _: "[]", axis=1)
    if 'ratings' not in users_df.columns:
        users_df['ratings'] = users_df.apply(lambda _: "{}", axis=1)
else:
    users_df = pd.DataFrame(columns=['username', 'password', 'age', 'gender', 'preferences', 'watchlist', 'ratings'])

# Save user data to the CSV file
def save_users(users_df):
    users_df.to_csv(users_file_path, index=False)

# Register a new user
def register_user(username, password, age, gender, preferences):
    global users_df  # Declare users_df as global
    if users_df[users_df['username'] == username].empty:
        new_user = pd.DataFrame({
            'username': [username], 
            'password': [password], 
            'age': [age], 
            'gender': [gender], 
            'preferences': [preferences],
            'watchlist': ["[]"],  # Initialize with an empty watchlist as string
            'ratings': ["{}"]     # Initialize with an empty ratings dictionary as string
        })
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        save_users(users_df)
        return True, users_df  # Return updated users_df
    else:
        return False, users_df  # Return existing users_df

# Log in an existing user
def login_user(username, password):
    user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
    if not user.empty:
        return user.iloc[0]
    else:
        return None

# Streamlit interface
st.title("🌟 KDrama Recommendation System 🌟")

# Main interface
auth_choice = st.sidebar.selectbox("Choose an option", ["Login", "Register"])

if auth_choice == "Register":
    st.sidebar.write("### Register")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    age = st.sidebar.number_input("Age", min_value=1, max_value=120)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    preferences = st.sidebar.multiselect("Preferences", kdrama_data['Genre'].unique().tolist())

    if st.sidebar.button("Register"):
        success, users_df = register_user(username, password, age, gender, preferences)
        if success:
            st.sidebar.success("User registered successfully!")
        else:
            st.sidebar.error("User already exists.")

if auth_choice == "Login":
    st.sidebar.write("### Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login_user(username, password)
        if user is not None:
            st.session_state.user = user.to_dict()  # Store user info in session state
            st.sidebar.success(f"Logged in as {user['username']}")

if 'user' in st.session_state:
    user = st.session_state.user
    st.write(f"Welcome, {user['username']}!")

    if st.sidebar.button("Logout"):
        st.session_state.pop('user')
        st.experimental_rerun()

    st.write("### Trending KDramas")
    trending_kdramas = kdrama_data.sort_values(by="Year of release", ascending=False).head(10)
    for index, row in trending_kdramas.iterrows():
        st.write(f"**{row['Name']}** ({row['Year of release']}) - {row['Genre']}")

    kdrama_list = kdrama_data['Name'].tolist()
    kdrama_liked_by_user = st.selectbox("Enter a KDrama you like:", options=kdrama_list, help="Start typing to see suggestions")

    genre_filter = st.selectbox("Filter by Genre:", options=["All"] + sorted(kdrama_data['Genre'].unique().tolist()))

    if kdrama_liked_by_user:
        try:
            liked_kdrama_indices = get_index_from_title(kdrama_liked_by_user)
            if liked_kdrama_indices:
                liked_kdrama_index = liked_kdrama_indices[0]  # Choose the first index if multiple are found
                similar_kdramas = list(enumerate(cosine_sim[liked_kdrama_index]))
                similar_kdramas.sort(key=lambda row: row[1], reverse=True)

                st.write("### Top 10 recommended KDramas for you:")
                count = 0
                for i in range(1, len(similar_kdramas)):
                    index = similar_kdramas[i][0]
                    name = get_title_from_index(index)
                    details = kdrama_data.iloc[index]
                    if genre_filter == "All" or genre_filter in details['Genre']:
                        count += 1
                        st.write(f"**{count}. {name}**")
                        st.write(f"   - Year of Release: {details['Year of release']}")
                        st.write(f"   - Original Network: {details['Original Network']}")
                        st.write(f"   - Aired On: {details['Aired On']}")
                        st.write(f"   - Duration: {details['Duration']}")
                        st.write(f"   - Content Rating: {details['Content Rating']}")
                        st.write(f"   - Genre: {details['Genre']}")
                        st.write(f"   - Rating: {details['Rating']}")

                        # Collect rating and feedback
                        st.write(f"### Feedback for {name}:")
                        rating = st.slider(f"Rate {name} (1-5)", 1, 5)
                        feedback = st.text_area(f"Provide feedback for {name}")

                        if st.button(f"Submit Feedback for {name}"):
                            # Update kdrama_reviews.csv
                            new_review = pd.DataFrame({
                                'kdrama_name': [name],
                                'username': [user['username']],
                                'rating': [rating],
                                'feedback': [feedback]
                            })
                            kdrama_reviews_df = pd.read_csv('data/kdrama_reviews.csv')  # Load existing reviews
                            kdrama_reviews_df = pd.concat([kdrama_reviews_df, new_review], ignore_index=True)
                            kdrama_reviews_df.to_csv('data/kdrama_reviews.csv', index=False)  # Save updated reviews
                            st.success(f"Feedback submitted for {name}!")

                        if st.button(f"Add {name} to Watchlist"):
                            user_watchlist = ast.literal_eval(user['watchlist'])
                            if name not in user_watchlist:
                                user_watchlist.append(name)
                                user['watchlist'] = str(user_watchlist)  # Update session state user watchlist
                                users_df.loc[users_df['username'] == user['username'], 'watchlist'] = str(user_watchlist)
                                save_users(users_df)
                                st.success(f"{name} added to your watchlist!")
                            else:
                                st.warning(f"{name} is already in your watchlist!")

                        if count >= 10:
                            break
        except IndexError:
            st.warning("KDrama not found. Please check the name.")

    st.write("### Your Watchlist")
    user_watchlist = ast.literal_eval(user['watchlist'])  # Convert watchlist string to list
    if user_watchlist:
        for drama in user_watchlist:
            st.write(f"**{drama}**")
            imdb_id = get_imdb_id(drama)
            if imdb_id:
                imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
                st.write(f"[IMDb Link]({imdb_url})")
    else:
        st.write("Your watchlist is empty.")

    st.write("### Your Average Ratings")
    user_reviews = pd.read_csv('data/kdrama_reviews.csv')
    user_ratings = user_reviews[user_reviews['username'] == user['username']]
    if not user_ratings.empty:
        avg_rating = user_ratings['rating'].mean()
        st.write(f"Your average rating for KDramas is {avg_rating:.2f}")
    else:
        st.write("You have not rated any KDramas yet.")
