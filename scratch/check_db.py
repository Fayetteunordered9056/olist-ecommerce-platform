import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("Successfully connected to the database!")
        
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        if tables:
            print(f"Found {len(tables)} tables: {[t[0] for t in tables]}")
        else:
            print("No tables found in the public schema.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    check_db_connection()
