from database.db import get_movie_by_code
import sqlite3

def test_search():
    conn = sqlite3.connect('database/bot_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT code, title FROM movies LIMIT 5")
    res = cursor.fetchall()
    conn.close()
    
    if res:
        for code, title in res:
            print(f"Testing with code: {code} (Title: {title})")
            movie = get_movie_by_code(code)
            if movie:
                print(f"  SUCCESS: Found movie {movie[1]}")
            else:
                print(f"  FAILED: Movie {title} NOT found by code {code}.")
    else:
        print("No movies in database.")

if __name__ == "__main__":
    test_search()
