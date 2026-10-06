import pandas as pd
import requests
import time
import sqlite3

# 1. Load and clean data
print("Loading CSV...")
df = pd.read_csv('netflix_viewing_history_sample.csv')
unique_titles = df[['Title']].drop_duplicates().reset_index(drop=True)

def extract_base_title(raw_title):
    parts = raw_title.split(':')
    base_title = parts[0].strip()
    media_type_guess = 'tv' if len(parts) > 1 else 'movie'
    return pd.Series([base_title, media_type_guess])

unique_titles[['base_title', 'type_guess']] = unique_titles['Title'].apply(extract_base_title)

# 2. Fetch TMDB data
TMDB_API_KEY = "1b7634ff8cae1ad79f997310a27e783e"
BASE_URL = "https://api.themoviedb.org/3/search/multi"
enriched_data = []

print("Querying TMDB API... (This may take a few minutes)")
for index, row in unique_titles.iterrows():
    try:
        response = requests.get(BASE_URL, params={
            'api_key': TMDB_API_KEY, 
            'query': row['base_title'], 
            'include_adult': 'false'
        })
        results = response.json().get('results', [])
        
        if results:
            top_match = results[0]
            # Verify the media type matches our guess
            if top_match.get('media_type') == row['type_guess']:
                enriched_data.append({
                    'original_title': row['Title'],
                    'tmdb_id': top_match.get('id'),
                    'media_type': top_match.get('media_type'),
                    'title': top_match.get('name') if row['type_guess'] == 'tv' else top_match.get('title')
                })
    except Exception as e:
        pass
    
    time.sleep(0.1) # Respect API rate limits

# 3. Store in SQLite
print(f"Matched {len(enriched_data)} titles. Saving to database...")
final_df = pd.DataFrame(enriched_data)

conn = sqlite3.connect('watch_history.db')
final_df.to_sql('history', conn, if_exists='replace', index=False)
conn.close()

print("Done! Database created as watch_history.db")