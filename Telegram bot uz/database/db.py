import sqlite3

def init_db():
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()

    # Filmlar jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            download_link TEXT,
            code TEXT UNIQUE,
            imdb_rating REAL DEFAULT 0.0,
            search_count INTEGER DEFAULT 0,
            category TEXT DEFAULT 'movies'
        )
        ''')

    # Foydalanuvchilar jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    # Chat tarixi jadvali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    conn.commit()
    conn.close()

def add_movie(title, description, image_url, download_link, code, imdb_rating=0.0, category='movies'):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        try:
                    cursor.execute('''
                                INSERT INTO movies (title, description, image_url, download_link, code, imdb_rating, category) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?)
                                                    ''', (title, description, image_url, download_link, code, imdb_rating, category))
                    conn.commit()
                    return True
except sqlite3.IntegrityError:
        return False
finally:
        conn.close()

def get_movie_by_code(code):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        # Increment search count
        cursor.execute('UPDATE movies SET search_count = search_count + 1 WHERE code = ?', (code,))
        cursor.execute('SELECT * FROM movies WHERE code = ?', (code,))
        movie = cursor.fetchone()
        conn.commit()
        conn.close()
        return movie

def get_movies_by_title(title):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE title LIKE ?', (f'%{title}%',))
        movies = cursor.fetchall()
        conn.close()
        return movies

def get_stats():
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM movies")
        movies_count = cursor.fetchone()[0]
        conn.close()
        return users_count, movies_count

def get_all_movies():
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT title, code, description, imdb_rating, category FROM movies")
        movies = cursor.fetchall()
        conn.close()
        return movies

def get_movies_by_category(category):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE category = ?', (category,))
        movies = cursor.fetchall()
        conn.close()
        return movies

def add_user(user_id, username, full_name):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                       (user_id, username, full_name))
        conn.commit()
        conn.close()

def set_user_lang(user_id, lang):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
        conn.commit()
        conn.close()

def get_user_lang(user_id):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else 'uz'

def get_top_imdb(limit=10):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies ORDER BY imdb_rating DESC LIMIT ?', (limit,))
        movies = cursor.fetchall()
        conn.close()
        return movies

def update_movie(code, title=None, description=None, image_url=None, download_link=None, imdb_rating=None, category=None):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()

    updates = []
    params = []

    if title is not None:
                updates.append("title = ?")
                params.append(title)
            if description is not None:
                        updates.append("description = ?")
                        params.append(description)
                    if image_url is not None:
                                updates.append("image_url = ?")
                                params.append(image_url)
                            if download_link is not None:
                                        updates.append("download_link = ?")
                                        params.append(download_link)
                                    if imdb_rating is not None:
                                                updates.append("imdb_rating = ?")
                                                params.append(imdb_rating)
                                            if category is not None:
                                                        updates.append("category = ?")
                                                        params.append(category)

    if not updates:
                conn.close()
                return False

    params.append(code)
    query = f"UPDATE movies SET {', '.join(updates)} WHERE code = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return True

def get_most_searched(limit=10):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies ORDER BY search_count DESC LIMIT ?', (limit,))
        movies = cursor.fetchall()
        conn.close()
        return movies

def add_chat_msg(user_id, role, content):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)',
                       (user_id, role, content))
        conn.commit()
        conn.close()

def get_chat_history(user_id, limit=10):
        conn = sqlite3.connect('database/bot_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
                       (user_id, limit))
        history = cursor.fetchall()
        conn.close()
        return history[::-1]  # Oldindan yangiga tartibbda qaytaramiz

if __name__ == "__main__":
        init_db()
    
