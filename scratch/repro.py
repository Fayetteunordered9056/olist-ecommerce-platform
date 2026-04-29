from app.config import Config
from sqlalchemy import create_engine, text

url = str(Config.DATABASE_URL)
print(f"Is password in string? {Config.DB_PASSWORD in url}")
print(f"URL string length: {len(url)}")

print("Testing with URL object:")
try:
    engine = create_engine(Config.DATABASE_URL)
    with engine.connect() as conn:
        print("  Success (Object)!")
except Exception as e:
    print(f"  Failure (Object): {e}")

print("\nTesting with string URL:")
url = str(Config.DATABASE_URL)
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print("  Success (String)!")
except Exception as e:
    print(f"  Failure (String): {e}")
