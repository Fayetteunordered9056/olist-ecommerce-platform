from app.config import Config
import os
from sqlalchemy import create_engine

print(f"DB_HOST: {Config.DB_HOST}")
print(f"DB_PORT: {Config.DB_PORT}")
print(f"DB_NAME: {Config.DB_NAME}")
print(f"DB_USER: {Config.DB_USER}")
print(f"DB_PASSWORD: {Config.DB_PASSWORD}")
print(f"DATABASE_URL: {Config.DATABASE_URL}")

try:
    engine = create_engine(Config.DATABASE_URL)
    with engine.connect() as conn:
        print("SQLAlchemy connection successful!")
except Exception as e:
    print(f"SQLAlchemy connection failed: {e}")
