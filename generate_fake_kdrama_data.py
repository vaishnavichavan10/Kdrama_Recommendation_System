from faker import Faker
import pandas as pd
import random

# Initialize Faker
fake = Faker()

# Function to generate fake users
def generate_fake_users(num_users):
    users = []
    for _ in range(num_users):
        username = fake.user_name()
        password = fake.password()
        age = random.randint(18, 60)
        gender = fake.random_element(elements=('Male', 'Female'))
        preferences = fake.random_elements(elements=('Romance', 'Action', 'Comedy', 'Thriller', 'Fantasy'), unique=True)
        
        users.append({
            'username': username,
            'password': password,
            'age': age,
            'gender': gender,
            'preferences': ','.join(preferences)
        })
    return users

# Generate 10 fake users
fake_users = generate_fake_users(10)

# Convert fake_users list to DataFrame
users_df = pd.DataFrame(fake_users)

# Function to save users to users.csv
def save_users(users_df):
    users_df.to_csv('data/users.csv', index=False)

# Save fake_users to users.csv
save_users(users_df)

# Read KDrama names from kdrama.csv
kdrama_df = pd.read_csv('data/kdrama.csv')
kdramas = kdrama_df['Name'].tolist()

# Generate fake ratings and reviews for KDramas
kdrama_reviews = []
for kdrama in kdramas:
    num_reviews = random.randint(5, 20)
    for _ in range(num_reviews):
        username = fake_users[random.randint(0, len(fake_users) - 1)]['username']  # Select a random fake user
        rating = random.randint(1, 5)
        feedback = fake.paragraph()
        
        kdrama_reviews.append({
            'username': username,
            'kdrama': kdrama,
            'rating': rating,
            'feedback': feedback
        })

# Convert kdrama_reviews list to DataFrame
reviews_df = pd.DataFrame(kdrama_reviews)

# Save ratings and reviews to kdrama_reviews.csv
reviews_df.to_csv('data/kdrama_reviews.csv', index=False)
