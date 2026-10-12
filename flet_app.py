import flet as ft
import flet_charts as fch
import sqlite3
import pandas as pd
import requests
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()

TMDB_API_KEY = "1b7634ff8cae1ad79f997310a27e783e"
DB_FILE = "watch_history.db"

# --- HELPER DATABASE & API FUNCTIONS ---

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            original_title TEXT,
            tmdb_id INTEGER,
            media_type TEXT,
            title TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_to_history(tmdb_id, title, media_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (original_title, tmdb_id, media_type, title) VALUES (?, ?, ?, ?)",
        (title, tmdb_id, media_type, title)
    )
    conn.commit()
    conn.close()

def fetch_recent_history():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()
    return df

def get_recommendations_for_genre(genre_name):
    # Mapping genre names to TMDB Genre IDs
    genre_map = {
        "Sci-Fi": 878,
        "Action": 28,
        "Comedy": 35,
        "Drama": 18,
        "Thriller": 53,
        "Adventure": 12
    }
    genre_id = genre_map.get(genre_name, 28)
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": str(genre_id),
        "sort_by": "popularity.desc"
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            results = res.json().get("results", [])
            return results[:6]
    except Exception:
        pass
    return []

def search_tmdb_movies(query):
    if not query.strip():
        return []
    url = "https://api.themoviedb.org/3/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": "false"
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("results", [])[:8]
    except Exception:
        pass
    return []


# --- MAIN FLET APPLICATION ---

def main(page: ft.Page):
    init_db()

    page.title = "Watch Next"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 460
    page.window.height = 780
    page.padding = 16

    # ---------------------------------------------------------
    # TAB 1: PROFILE
    # ---------------------------------------------------------
    history_count_text = ft.Text("0 Movies Logged", size=14, color=ft.Colors.WHITE_70)

    profile_view = ft.Container(
        content=ft.Column([
            ft.Text("User Profile", size=26, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.CircleAvatar(
                radius=45,
                content=ft.Icon(ft.Icons.PERSON, size=50, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.DEEP_ORANGE_ACCENT_400
            ),
            ft.Text("Sriranga V", size=20, weight=ft.FontWeight.W_600),
            history_count_text,
            ft.Divider(height=20),
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.AMBER), ft.Text("Recommendation Engine Active", weight=ft.FontWeight.BOLD)]),
                        ft.Text("Engine: TMDB Multi-Vector Filtering\nPlatform: Cross-Streaming Aggregator\nDatabase: Local SQLite", size=12, color=ft.Colors.WHITE_60)
                    ])
                )
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False
    )

    # ---------------------------------------------------------
    # TAB 2: WATCH HISTORY & CATALOGUE SEARCH
    # ---------------------------------------------------------
    search_input = ft.TextField(
        hint_text="Search movie or TV show to add...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )
    search_results_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, height=180)
    history_list_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, height=220)

    def refresh_history_ui():
        history_df = fetch_recent_history()
        history_count_text.value = f"{len(history_df)} Titles Logged"

        history_list_col.controls.clear()
        if history_df.empty:
            history_list_col.controls.append(ft.Text("No history recorded yet.", color=ft.Colors.WHITE_38))
        else:
            for _, row in history_df.iloc[::-1].iterrows():
                history_list_col.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                            title=ft.Text(str(row['title']), weight=ft.FontWeight.W_500),
                            subtitle=ft.Text(f"Type: {str(row['media_type']).upper()}", size=11, color=ft.Colors.WHITE_54),
                        )
                    )
                )
        page.update()

    def on_add_item(tmdb_id, title, media_type):
        add_to_history(tmdb_id, title, media_type)
        search_results_col.controls.clear()
        search_input.value = ""
        refresh_history_ui()
        page.snack_bar = ft.SnackBar(ft.Text(f"Added '{title}' to your history!"))
        page.snack_bar.open = True
        page.update()

    def run_search(e):
        query = search_input.value
        results = search_tmdb_movies(query)
        search_results_col.controls.clear()

        if not results:
            search_results_col.controls.append(ft.Text("No matches found in catalogue.", size=12, color=ft.Colors.WHITE_38))
        else:
            for item in results:
                title = item.get('title') or item.get('name') or "Unknown"
                m_type = item.get('media_type', 'movie')
                t_id = item.get('id')
                poster = item.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w92{poster}" if poster else "https://via.placeholder.com/92x138"

                btn_add = ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=ft.Colors.TEAL_ACCENT,
                    on_click=lambda ev, tid=t_id, tit=title, mt=m_type: on_add_item(tid, tit, mt)
                )

                search_results_col.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.Image(src=poster_url, width=35, height=50, fit=ft.BoxFit.COVER, border_radius=3),
                            title=ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"{m_type.upper()} • Rating: {item.get('vote_average', 'N/A')}", size=11),
                            trailing=btn_add
                        )
                    )
                )
        page.update()

    search_button = ft.Button("Search", icon=ft.Icons.SEARCH, on_click=run_search)

    history_view = ft.Container(
        content=ft.Column([
            ft.Text("Manual Catalog Entry", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_input, search_button]),
            ft.Text("Search Matches:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE_70),
            ft.Container(content=search_results_col, border=ft.Border.all(1, ft.Colors.WHITE_10), border_radius=8, padding=6),
            ft.Divider(height=10),
            ft.Text("Your Logged History:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE_70),
            ft.Container(content=history_list_col, border=ft.Border.all(1, ft.Colors.WHITE_10), border_radius=8, padding=6)
        ]),
        visible=False
    )

    # ---------------------------------------------------------
    # TAB 3: INFOGRAPHIC PIE CHART & GENRE RECOMMENDATIONS
    # ---------------------------------------------------------
    genre_data = [
        {"name": "Sci-Fi", "value": 30, "color": ft.Colors.DEEP_ORANGE},
        {"name": "Action", "value": 20, "color": ft.Colors.BLUE_GREY_700},
        {"name": "Comedy", "value": 18, "color": ft.Colors.ORANGE_500},
        {"name": "Drama", "value": 12, "color": ft.Colors.TEAL_400},
        {"name": "Thriller", "value": 10, "color": ft.Colors.AMBER},
        {"name": "Adventure", "value": 10, "color": ft.Colors.TEAL_200},
    ]

    normal_radius = 45
    hover_radius = 60
    active_slice_index = -1

    rec_title_header = ft.Text("Tap any genre slice to explore recommendations", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.AMBER)
    genre_recs_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, height=150)

    def build_chart_sections():
        sections = []
        for i, g in enumerate(genre_data):
            is_active = (i == active_slice_index)
            radius = hover_radius if is_active else normal_radius
            sections.append(
                fch.PieChartSection(
                    value=g["value"],
                    title=f"{g['value']}%",
                    title_style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    color=g["color"],
                    radius=radius,
                    border_side=ft.BorderSide(3, ft.Colors.WHITE if is_active else ft.Colors.TRANSPARENT)
                )
            )
        return sections

    def update_genre_recommendations(genre_name):
        rec_title_header.value = f"Top Recommendations for '{genre_name}':"
        movies = get_recommendations_for_genre(genre_name)
        genre_recs_row.controls.clear()

        for m in movies:
            poster = m.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w185{poster}" if poster else "https://via.placeholder.com/90x130"
            m_title = m.get('title', 'Unknown')
            rating = m.get('vote_average', 0)

            genre_recs_row.controls.append(
                ft.Container(
                    width=95,
                    content=ft.Column([
                        ft.Image(src=poster_url, width=95, height=105, fit=ft.BoxFit.COVER, border_radius=6),
                        ft.Text(m_title, size=10, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=11),
                            ft.Text(str(rating), size=10)
                        ], spacing=3)
                    ], spacing=2)
                )
            )
        page.update()

    def on_pie_chart_event(e: fch.PieChartEvent):
        nonlocal active_slice_index
        if e.section_index is not None and e.section_index >= 0:
            if active_slice_index != e.section_index:
                active_slice_index = e.section_index
                selected_genre = genre_data[active_slice_index]["name"]
                pie_chart.sections = build_chart_sections()
                update_genre_recommendations(selected_genre)

    pie_chart = fch.PieChart(
        sections=build_chart_sections(),
        sections_space=3,
        center_space_radius=25,
        on_event=on_pie_chart_event,
        expand=True
    )

    def build_legend_column():
        rows = []
        for g in genre_data:
            rows.append(
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=g["color"], border_radius=3),
                    ft.Text(f"{g['name']} ({g['value']}%)", size=11, color=ft.Colors.WHITE_70)
                ], spacing=6)
            )
        return ft.Column(rows, spacing=4)

    stats_view = ft.Container(
        content=ft.Column([
            ft.Text("Genre Footprint", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Visual distribution of themes across your viewing activity", size=11, color=ft.Colors.WHITE_38),
            ft.Divider(height=10),
            ft.Row([
                ft.Container(content=pie_chart, width=170, height=170),
                build_legend_column()
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Divider(height=10),
            rec_title_header,
            genre_recs_row
        ]),
        visible=True
    )

    # ---------------------------------------------------------
    # MAIN NAVIGATION CONTROLLER
    # ---------------------------------------------------------
    views = [stats_view, history_view, profile_view]

    def on_nav_change(e):
        idx = e.control.selected_index
        stats_view.visible = (idx == 0)
        history_view.visible = (idx == 1)
        profile_view.visible = (idx == 2)
        if idx == 1:
            refresh_history_ui()
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_OUTLINE, selected_icon=ft.Icons.PIE_CHART, label="Infographics"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, selected_icon=ft.Icons.MANAGE_HISTORY, label="History"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Profile"),
        ]
    )

    page.add(ft.Column([stats_view, history_view, profile_view], expand=True))
    refresh_history_ui()

ft.run(main)