import sqlite3
import pandas as pd
import requests

TMDB_API_KEY = "1b7634ff8cae1ad79f997310a27e783e"

# 1. Connect to your database and load your watch history
conn = sqlite3.connect('watch_history.db')
history_df = pd.read_sql('SELECT * FROM history', conn)
conn.close()

# Create a list of IDs you've already watched so we don't recommend them
watched_tmdb_ids = history_df['tmdb_id'].dropna().astype(int).tolist()

# 2. Select recent watches to base recommendations on
# Grabbing the last 5 entries from your dataset
recent_watches = history_df.tail(5)

recommendations = []

print("Analyzing recent watch history and fetching recommendations...")

# 3. Ask TMDB for recommendations based on these recent IDs
for index, row in recent_watches.iterrows():
    # Skip rows where TMDB couldn't find a match in the previous script
    if pd.isna(row['tmdb_id']):
        continue
        
    tmdb_id = int(row['tmdb_id'])
    media_type = row['media_type'] # 'movie' or 'tv'
    
    # Hit the specific TMDB recommendation endpoint
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/recommendations"
    response = requests.get(url, params={'api_key': TMDB_API_KEY})
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        
        # Take the top 5 recommendations for each watched show
        for res in results[:5]:  
            # CRITICAL: Only add to the list if you haven't watched it yet
            if res['id'] not in watched_tmdb_ids:
                recommendations.append({
                    'Watch Next': res.get('title') or res.get('name'),
                    'Because you watched': row['title'],
                    'Rating': res.get('vote_average')
                })

# 4. Sort and display the best matches
rec_df = pd.DataFrame(recommendations)

if not rec_df.empty:
    # Remove duplicates in case multiple shows recommended the same exact thing
    rec_df = rec_df.drop_duplicates(subset=['Watch Next'])
    # Sort by the highest user rating on TMDB
    rec_df = rec_df.sort_values(by='Rating', ascending=False).head(10)
    
    print("\n--- TOP 10 WATCH NEXT RECOMMENDATIONS ---")
    print(rec_df.to_string(index=False))
else:
    print("Not enough data to generate recommendations yet.")