import streamlit as st

def collect_feedback():
    st.write("### Rate the recommended KDramas")
    for i in range(1, 11):
        st.write(f"**{i}.**")
        rating = st.slider(f"Rate KDrama {i}", 1, 5, key=f"rating_{i}")
        feedback = st.text_area(f"Feedback for KDrama {i}", key=f"feedback_{i}")

# In app.py, import and use this function after displaying recommendations
