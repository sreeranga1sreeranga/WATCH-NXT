import flet as ft

BG_COLOR = "#000000"
CARD_BG = "#1C1C1E"
NETFLIX_RED = "#E50914"
TEXT_COLOR = "#FFFFFF"
DB_FILE = "watch_history.db"
TMDB_API_KEY = "1b7634ff8cae1ad79f997310a27e783e"

GENRE_ID_TO_NAME = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 53: "Thriller", 878: "Sci-Fi"
}

GENRE_COLORS = {
    "Action": "#FF3B30", "Sci-Fi": "#5AC8FA", "Drama": "#AF52DE", 
    "Comedy": "#FFCC00", "Thriller": "#FF9500", "Adventure": "#34C759", "Other": "#8E8E93"
}

# Major OTT streaming platforms in India with live high-res logos
OTT_PLATFORMS = {
    "Netflix": {"color": "#E50914", "logo": "https://img.icons8.com/color/48/netflix.png"},
    "Prime Video": {"color": "#00A8E1", "logo": "https://img.icons8.com/color/48/amazon-prime-video.png"},
    "JioHotstar": {"color": "#030B74", "logo": "https://img.icons8.com/color/48/disney-plus.png"}, 
    "ZEE5": {"color": "#821F8C", "logo": "https://img.icons8.com/color/48/z-symbol.png"}, 
    "Apple TV+": {"color": "#2D2D2D", "logo": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png"},
    "SonyLIV": {"color": "#E56300", "logo": "https://img.icons8.com/color/48/play-button.png"}
}

WATCHER_TYPES = [
    {"title": "Cinephile", "emoji": "🖤", "desc": "Art-house, auteur directions & deeply immersive cinema."},
    {"title": "Heat Seeker", "emoji": "🔥", "desc": "High adrenaline, opening day blockbusters & early hype."},
    {"title": "Masala Men", "emoji": "⚡", "desc": "Mass action, high-octane blockbusters & star power."},
    {"title": "Event Chaser", "emoji": "✨", "desc": "Prestige cinematic experiences & massive visual spectacles."},
    {"title": "Browser", "emoji": "🍿", "desc": "Selectively exploring diverse stories across genres."}
]

LANGUAGES = ["English", "Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "Korean", "Spanish"]

# Abundant multi-category movie library with guaranteed high-res posters
CATALOG = {
    "Recommended For You": [
        {"title": "Oppenheimer", "rating": "8.9", "ott": "Prime Video", "year": "2023", "img": "https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=500&auto=format&fit=crop"},
        {"title": "Dune: Part Two", "rating": "8.8", "ott": "JioHotstar", "year": "2024", "img": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=500&auto=format&fit=crop"},
        {"title": "Interstellar", "rating": "8.7", "ott": "Netflix", "year": "2014", "img": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&auto=format&fit=crop"},
        {"title": "Kantara", "rating": "8.3", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop"},
        {"title": "Anatomy of a Fall", "rating": "7.9", "ott": "SonyLIV", "year": "2023", "img": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop"}
    ],
    "Top Trending Right Now": [
        {"title": "The Batman", "rating": "7.9", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&auto=format&fit=crop"},
        {"title": "Spider-Man: Across the Spider-Verse", "rating": "8.7", "ott": "Netflix", "year": "2023", "img": "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=500&auto=format&fit=crop"},
        {"title": "Avengers: Endgame", "rating": "8.4", "ott": "JioHotstar", "year": "2019", "img": "https://images.unsplash.com/photo-1608889175123-8ee362201f81?w=500&auto=format&fit=crop"},
        {"title": "Top Gun: Maverick", "rating": "8.3", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1560930950-5c20d812158a?w=500&auto=format&fit=crop"},
        {"title": "Blade Runner 2049", "rating": "8.0", "ott": "SonyLIV", "year": "2017", "img": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop"}
    ],
    "Indian Cinema & Mega Hits": [
        {"title": "KGF: Chapter 2", "rating": "8.2", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=500&auto=format&fit=crop"},
        {"title": "RRR", "rating": "7.8", "ott": "Netflix", "year": "2022", "img": "https://images.unsplash.com/photo-1571401834311-b0e6df2e6840?w=500&auto=format&fit=crop"},
        {"title": "Drishyam 2", "rating": "8.2", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop"},
        {"title": "Jawan", "rating": "7.0", "ott": "Netflix", "year": "2023", "img": "https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=500&auto=format&fit=crop"},
        {"title": "Kantara", "rating": "8.3", "ott": "Prime Video", "year": "2022", "img": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop"}
    ],
    "Cinephile & Award Winners": [
        {"title": "Parasite", "rating": "8.5", "ott": "SonyLIV", "year": "2019", "img": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop"},
        {"title": "Past Lives", "rating": "7.9", "ott": "Prime Video", "year": "2023", "img": "https://images.unsplash.com/photo-1534809027769-62174de05553?w=500&auto=format&fit=crop"},
        {"title": "The Zone of Interest", "rating": "7.5", "ott": "Prime Video", "year": "2023", "img": "https://images.unsplash.com/photo-1584985552391-7667a42ec35a?w=500&auto=format&fit=crop"},
        {"title": "Drive My Car", "rating": "7.6", "ott": "ZEE5", "year": "2021", "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop"}
    ],
    "Sci-Fi & Action Spectacles": [
        {"title": "Inception", "rating": "8.8", "ott": "Netflix", "year": "2010", "img": "https://images.unsplash.com/photo-1555448248-2571daf6344b?w=500&auto=format&fit=crop"},
        {"title": "The Matrix", "rating": "8.7", "ott": "Prime Video", "year": "1999", "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop"},
        {"title": "Avatar: The Way of Water", "rating": "7.6", "ott": "JioHotstar", "year": "2022", "img": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop"},
        {"title": "Mad Max: Fury Road", "rating": "8.1", "ott": "Prime Video", "year": "2015", "img": "https://images.unsplash.com/photo-1611604548018-d56bbd85d681?w=500&auto=format&fit=crop"}
    ]
}