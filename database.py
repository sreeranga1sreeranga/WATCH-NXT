import sqlite3
import pandas as pd
from config import DB_FILE, GENRE_COLORS

FALLBACK_POSTERS = {
    "interstellar": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&auto=format&fit=crop",
    "the matrix": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop",
    "matrix": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop",
    "parasite": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop",
    "drishyam": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop",
    "jumanji": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop",
    "toy story": "https://images.unsplash.com/photo-1534809027769-62174de05553?w=500&auto=format&fit=crop",
    "oppenheimer": "https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=500&auto=format&fit=crop",
    "the dark knight": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&auto=format&fit=crop",
    "batman": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&auto=format&fit=crop",
    "joker": "https://images.unsplash.com/photo-1571401834311-b0e6df2e6840?w=500&auto=format&fit=crop",
    "dune": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=500&auto=format&fit=crop"
}

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_title TEXT,
            tmdb_id INTEGER,
            media_type TEXT,
            title TEXT,
            platform TEXT DEFAULT 'Netflix',
            genres TEXT DEFAULT 'Action, Sci-Fi',
            poster TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def resolve_poster(title, existing_poster=""):
    if existing_poster and len(existing_poster) > 10:
        return existing_poster
    title_lower = str(title).lower()
    for key, url in FALLBACK_POSTERS.items():
        if key in title_lower:
            return url
    return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop"

def get_all_history():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM history ORDER BY rowid DESC", conn)
    conn.close()
    if not df.empty:
        df['poster'] = df.apply(lambda r: resolve_poster(r['title'], r.get('poster', '')), axis=1)
    return df

def log_movie_watch(tmdb_id, title, media_type, platform, genres_str, poster=""):
    resolved = resolve_poster(title, poster)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (original_title, tmdb_id, media_type, title, platform, genres, poster) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, tmdb_id, media_type, title, platform, genres_str, resolved)
    )
    conn.commit()
    conn.close()

def log_bulk_movies(records):
    conn = get_db()
    cursor = conn.cursor()
    enhanced_records = [
        (r[0], r[1], r[2], r[3], r[4], r[5], resolve_poster(r[3], r[6] if len(r) > 6 else ""))
        for r in records
    ]
    cursor.executemany(
        "INSERT INTO history (original_title, tmdb_id, media_type, title, platform, genres, poster) VALUES (?, ?, ?, ?, ?, ?, ?)",
        enhanced_records
    )
    conn.commit()
    conn.close()

def compute_dynamic_genre_distribution():
    df = get_all_history()
    if df.empty or 'genres' not in df.columns:
        return [
            {"name": "Action", "value": 35, "color": GENRE_COLORS["Action"]},
            {"name": "Sci-Fi", "value": 30, "color": GENRE_COLORS["Sci-Fi"]},
            {"name": "Drama", "value": 20, "color": GENRE_COLORS["Drama"]},
            {"name": "Thriller", "value": 15, "color": GENRE_COLORS["Thriller"]}
        ]
    all_genres = []
    for g_entry in df['genres'].dropna():
        tags = [t.strip() for t in str(g_entry).split(',') if t.strip()]
        all_genres.extend(tags)
    if not all_genres:
        return [{"name": "Action", "value": 100, "color": GENRE_COLORS["Action"]}]

    genre_series = pd.Series(all_genres).value_counts()
    top_5 = genre_series.head(5)
    other_sum = genre_series.iloc[5:].sum() if len(genre_series) > 5 else 0
    total = top_5.sum() + other_sum
    distribution = []

    for name, count in top_5.items():
        distribution.append({
            "name": name, 
            "value": round((count / total) * 100, 1), 
            "color": GENRE_COLORS.get(name, "#8E8E93")
        })
    if other_sum > 0:
        distribution.append({"name": "Other", "value": round((other_sum / total) * 100, 1), "color": GENRE_COLORS["Other"]})
    return distribution