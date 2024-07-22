import streamlit as st
import pandas as pd

USER_DATA_FILE = 'data/users.csv'

def load_user_data():
    try:
        return pd.read_csv(USER_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['username', 'password', 'age', 'gender', 'preferences'])

def save_user_data(users):
    users.to_csv(USER_DATA_FILE, index=False)

def create_user_profile(existing_profiles):
    st.sidebar.write("## User Profile")
    name = st.sidebar.text_input("Name", key="name_input_profile")
    age = st.sidebar.number_input("Age", 10, 100, key="age_input_profile")
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"], key="gender_input_profile")
    preferences = st.sidebar.multiselect("Preferred Genres", ["Romance", "Action", "Comedy", "Drama", "Thriller", "Fantasy"], key="preferences_input_profile")
    
    if st.sidebar.button("Save Profile", key="save_profile_button"):
        if name in existing_profiles:
            st.sidebar.warning(f"Profile for {name} already exists!")
        else:
            existing_profiles.add(name)
            st.session_state.user_profiles[name] = {"Name": name, "Age": age, "Gender": gender, "Preferences": preferences}
            st.sidebar.success("Profile saved!")
