from fastapi import FastAPI
from sqlalchemy.orm import Session
from models import Users  # Assuming you have a Users model defined in models.py
# Assuming you have a function to create a database session in database.py
from database import SessionLocal
from passlib.hash import bcrypt  # For hashing passwords

app = FastAPI()


def seed_users():
    db = SessionLocal()
    try:
        # Check if users exist in the database
        if db.query(Users).count() == 0:
            # If no users exist, create some sample users
            users = [
                Users(username="user1", password=bcrypt.hash(
                    "password1"), email="user1@example.com"),
                Users(username="user2", password=bcrypt.hash(
                    "password2"), email="user2@example.com"),
                Users(username="user3", password=bcrypt.hash(
                    "password3"), email="user3@example.com")
            ]
            db.add_all(users)
            db.commit()
            print("Seed data added successfully.")
        else:
            print("Users already exist in the database. Skipping seed data.")
    except Exception as e:
        print(f"Error seeding users: {str(e)}")
    finally:
        db.close()


seed_users()  # Call the seed_users function when the application starts
