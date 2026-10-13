import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import flet as ft
import flet_charts as fch
import database as db
import api
import config as c
import pandas as pd
import os
from components import NetflixRedButton

def main(page: ft.Page):
    db.init_db()
    page.title = "WATCH NXT"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.window.width = 414
    page.window.height = 896
    page.padding = 0
    page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap"}
    page.theme = ft.Theme(font_family="Inter")

    # Global Session State
    user_state = {
        "name": "Sreeranga", 
        "email": "sreeranga@watchnxt.com", 
        "type": "Cinephile", 
        "emoji": "🖤", 
        "languages": ["English", "Hindi", "Kannada"]
    }
    
    # Cross-Platform OTT Subscriptions
    connected_otts = {
        "Netflix": True, 
        "Prime Video": True, 
        "JioHotstar": True, 
        "ZEE5": False, 
        "Apple TV+": False,
        "SonyLIV": True
    }

    master_container = ft.Container(expand=True, bgcolor="#000000")
    page.add(master_container)

    def PremiumPillButton(text, icon=None, on_click=None):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="black", size=18) if icon else ft.Container(),
                ft.Text(text, color="black", weight=ft.FontWeight.W_800, size=15)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="white", border_radius=30, padding=14, on_click=on_click
        )

    # =========================================================
    # AUTHENTICATION & SIGN UP FLOW
    # =========================================================
    def render_auth_view(is_signup_mode=False):
        name_input = ft.TextField(hint_text="Your Name", border_color=ft.Colors.TRANSPARENT, bgcolor=c.CARD_BG, border_radius=12, text_size=14, visible=is_signup_mode)
        email_input = ft.TextField(hint_text="Email Address", border_color=ft.Colors.TRANSPARENT, bgcolor=c.CARD_BG, border_radius=12, text_size=14)
        pass_input = ft.TextField(hint_text="Password", password=True, can_reveal_password=True, border_color=ft.Colors.TRANSPARENT, bgcolor=c.CARD_BG, border_radius=12, text_size=14)

        def handle_auth_action(e):
            if is_signup_mode:
                if name_input.value.strip():
                    user_state["name"] = name_input.value.strip()
                if email_input.value.strip():
                    user_state["email"] = email_input.value.strip()
                render_dna_onboarding_view()
            else:
                if email_input.value.strip():
                    user_state["email"] = email_input.value.strip()
                show_main_app()

        def toggle_mode(e):
            render_auth_view(is_signup_mode=not is_signup_mode)

        auth_card = ft.Container(
            padding=30,
            border_radius=25,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            blur=ft.Blur(25, 25, ft.BlurTileMode.MIRROR),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.25, ft.Colors.WHITE)),
            content=ft.Column([
                ft.Text("Create Account" if is_signup_mode else "Welcome Back", size=32, weight=ft.FontWeight.W_900, color="white"),
                ft.Text("Set up your cinematic DNA tracker" if is_signup_mode else "Sign in to access your universal stream watchlist", size=13, color=ft.Colors.WHITE_70),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                name_input,
                email_input,
                pass_input,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                PremiumPillButton("Continue to Watch DNA" if is_signup_mode else "Sign In", on_click=handle_auth_action),
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=10,
                    content=ft.TextButton(
                        "Already have an account? Sign In" if is_signup_mode else "New to WATCH NXT? Create an account",
                        on_click=toggle_mode
                    )
                )
            ], spacing=10)
        )

        master_container.content = ft.Stack(
            expand=True,
            controls=[
                ft.Image(src="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&fit=crop", fit=ft.BoxFit.COVER, expand=True),
                ft.Container(gradient=ft.LinearGradient(begin=ft.Alignment(0, -0.4), end=ft.Alignment(0, 1), colors=[ft.Colors.TRANSPARENT, "#000000"]), expand=True),
                ft.Container(
                    padding=25, alignment=ft.Alignment(0, 1),
                    content=ft.Column([
                        ft.Text("WATCH NXT", size=48, weight=ft.FontWeight.W_900, color="white"),
                        auth_card
                    ], alignment=ft.MainAxisAlignment.END, spacing=15)
                )
            ]
        )
        page.update()

    # =========================================================
    # WATCHER DNA & ONBOARDING SELECTION
    # =========================================================
    def render_dna_onboarding_view():
        selected_tribe = [user_state["type"]]
        selected_langs = set(user_state["languages"])
        tribes_grid = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        langs_row = ft.Row(wrap=True, spacing=8, alignment=ft.MainAxisAlignment.CENTER)

        def save_and_launch(e):
            user_state["type"] = selected_tribe[0]
            # Match emoji
            for wt in c.WATCHER_TYPES:
                if wt["title"] == selected_tribe[0]:
                    user_state["emoji"] = wt["emoji"]
            user_state["languages"] = list(selected_langs)
            show_main_app()

        def pick_tribe(name):
            selected_tribe[0] = name
            build_tribes()
            page.update()

        def toggle_lang(lang):
            if lang in selected_langs:
                if len(selected_langs) > 1:
                    selected_langs.remove(lang)
            else:
                selected_langs.add(lang)
            build_langs()
            page.update()

        def build_tribes():
            tribes_grid.controls.clear()
            for wt in c.WATCHER_TYPES:
                is_active = (wt["title"] == selected_tribe[0])
                tribes_grid.controls.append(
                    ft.Container(
                        width=165, height=140,
                        padding=15, border_radius=18,
                        bgcolor=ft.Colors.with_opacity(0.85, c.NETFLIX_RED) if is_active else c.CARD_BG,
                        border=ft.Border.all(2, c.NETFLIX_RED if is_active else ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
                        content=ft.Column([
                            ft.Text(wt["emoji"], size=30),
                            ft.Text(wt["title"], size=15, weight=ft.FontWeight.W_900, color="white"),
                            ft.Text(wt["desc"], size=10, color=ft.Colors.WHITE_70, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                        ], alignment=ft.MainAxisAlignment.END, spacing=3),
                        on_click=lambda ev, n=wt["title"]: pick_tribe(n)
                    )
                )

        def build_langs():
            langs_row.controls.clear()
            for l in c.LANGUAGES:
                is_sel = (l in selected_langs)
                langs_row.controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        border_radius=20,
                        bgcolor=c.NETFLIX_RED if is_sel else c.CARD_BG,
                        border=ft.Border.all(1, ft.Colors.TRANSPARENT if is_sel else ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        content=ft.Text(l, size=12, weight=ft.FontWeight.BOLD, color="white"),
                        on_click=lambda ev, lang=l: toggle_lang(lang)
                    )
                )

        build_tribes()
        build_langs()

        master_container.content = ft.Container(
            padding=25, expand=True, bgcolor="#000000",
            content=ft.ListView(
                spacing=15,
                controls=[
                    ft.Container(height=35),
                    ft.Text("Define Your DNA", size=32, weight=ft.FontWeight.W_900, color="white"),
                    ft.Text("Select your primary watch archetype for tuned recommendations:", size=13, color=ft.Colors.WHITE_54),
                    tribes_grid,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("Languages You Stream In:", size=16, weight=ft.FontWeight.W_800, color="white"),
                    langs_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    PremiumPillButton("Save DNA & Enter Hub", on_click=save_and_launch),
                    ft.Container(height=30)
                ]
            )
        )
        page.update()

    def do_logout(e):
        page.navigation_bar = None
        render_auth_view(is_signup_mode=False)

    # =========================================================
    # CORE APPLICATION VIEWS
    # =========================================================

    # 1. HOME VIEW (ABUNDANT COLLECTION & RECOMMENDATION SHELF)
    def render_horizontal_shelf(category_title, items):
        cards = []
        for m in items:
            ott_cfg = c.OTT_PLATFORMS.get(m.get("ott", "Netflix"), {"color": "#333333", "logo": ""})
            cards.append(
                ft.Container(
                    width=145,
                    content=ft.Column([
                        ft.Stack([
                            ft.Image(src=m["img"], width=145, height=210, fit=ft.BoxFit.COVER, border_radius=16),
                            ft.Container(
                                padding=6, alignment=ft.Alignment(1, -1),
                                content=ft.Container(
                                    content=ft.Image(src=ott_cfg["logo"], width=14, height=14, fit=ft.BoxFit.CONTAIN),
                                    bgcolor=ft.Colors.with_opacity(0.85, "#000000"),
                                    padding=4, border_radius=6
                                )
                            )
                        ]),
                        ft.Text(m["title"], size=13, weight=ft.FontWeight.W_800, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color="white"),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR_ROUNDED, color="#FFD60A", size=14),
                            ft.Text(m.get("rating", "8.0"), size=11, color=ft.Colors.WHITE_70, weight=ft.FontWeight.BOLD),
                            ft.Text("• " + m.get("year", "2023"), size=11, color=ft.Colors.WHITE_38)
                        ], spacing=3)
                    ], spacing=5)
                )
            )
        return ft.Column([
            ft.Row([
                ft.Text(category_title, size=18, weight=ft.FontWeight.W_800, color="white"),
                ft.Text("See all", size=12, color=c.NETFLIX_RED, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(controls=cards, scroll=ft.ScrollMode.HIDDEN, spacing=14)
        ], spacing=10)

    home_view = ft.Container(
        expand=True, visible=True,
        content=ft.ListView(
            padding=0, spacing=0,
            controls=[
                # Cinematic Hero Backdrop
                ft.Stack([
                    ft.Image(src="https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&fit=crop", height=540, width=500, fit=ft.BoxFit.COVER),
                    ft.Container(height=540, gradient=ft.LinearGradient(begin=ft.Alignment(0, 0), end=ft.Alignment(0, 1), colors=[ft.Colors.TRANSPARENT, "#000000"])),
                    ft.Container(
                        height=540, padding=20, alignment=ft.Alignment(0, 1),
                        content=ft.Column([
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                bgcolor=c.NETFLIX_RED, border_radius=6,
                                content=ft.Text("FEATURED PREMIERE", size=10, weight=ft.FontWeight.W_900, color="white")
                            ),
                            ft.Text("Blade Runner 2049", size=36, weight=ft.FontWeight.W_900, height=1.1, color="white"),
                            ft.Text("Sci-Fi, Thriller • 8.0 • SonyLIV", size=13, color=ft.Colors.WHITE_70, weight=ft.FontWeight.W_600),
                            ft.Text("A young blade runner unearths a long-buried secret that leads him to track down former officer Rick Deckard...", size=12, color=ft.Colors.WHITE_54, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            PremiumPillButton("Watch now", icon=ft.Icons.PLAY_ARROW_ROUNDED)
                        ], alignment=ft.MainAxisAlignment.END, spacing=6)
                    )
                ]),
                # 5 Abundant Shelves including personalized DNA recommendation
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        render_horizontal_shelf(f"Recommended For You ({user_state['type']})", c.CATALOG["Recommended For You"]),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        render_horizontal_shelf("Top Trending Right Now", c.CATALOG["Top Trending Right Now"]),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        render_horizontal_shelf("Indian Cinema & Mega Hits", c.CATALOG["Indian Cinema & Mega Hits"]),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        render_horizontal_shelf("Cinephile & Award Winners", c.CATALOG["Cinephile & Award Winners"]),
                        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                        render_horizontal_shelf("Sci-Fi & Action Spectacles", c.CATALOG["Sci-Fi & Action Spectacles"]),
                        ft.Divider(height=50, color=ft.Colors.TRANSPARENT)
                    ], spacing=15)
                )
            ]
        )
    )

    # 2. ANALYTICS VIEW
    pie_chart = fch.PieChart(sections=[], sections_space=2, center_space_radius=40, expand=True)
    legend_col = ft.Column(spacing=8)

    def refresh_analytics():
        dist = db.compute_dynamic_genre_distribution()
        pie_chart.sections = [
            fch.PieChartSection(
                value=item["value"], 
                title=f"{item['value']}%", 
                title_style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD), 
                color=c.GENRE_COLORS.get(item["name"], "#8E8E93"), 
                radius=25
            ) for item in dist
        ]
        legend_col.controls.clear()
        for item in dist:
            legend_col.controls.append(
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=c.GENRE_COLORS.get(item["name"], "#8E8E93"), border_radius=4),
                    ft.Text(item['name'], size=13, weight=ft.FontWeight.W_600, color="white")
                ], spacing=10)
            )

    analytics_view = ft.Container(
        padding=20, expand=True, visible=False,
        content=ft.ListView(
            spacing=18,
            controls=[
                ft.Container(height=35),
                ft.Text("Analytics", size=32, weight=ft.FontWeight.W_900, color="white"),
                ft.Container(
                    padding=22, border_radius=20, bgcolor=c.CARD_BG,
                    content=ft.Row([
                        ft.Text(user_state["emoji"], size=42),
                        ft.Column([
                            ft.Text("Current Watcher Archetype", size=12, color=ft.Colors.WHITE_54, weight=ft.FontWeight.BOLD),
                            ft.Text(user_state["type"], size=22, weight=ft.FontWeight.W_900, color="white"),
                            ft.Text("Languages: " + ", ".join(user_state["languages"]), size=11, color=c.NETFLIX_RED, weight=ft.FontWeight.BOLD)
                        ], spacing=2, expand=True)
                    ], spacing=15)
                ),
                ft.Container(
                    padding=22, border_radius=20, bgcolor=c.CARD_BG,
                    content=ft.Column([
                        ft.Text("Genre Footprint", size=18, weight=ft.FontWeight.W_800, color="white"),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        ft.Container(content=pie_chart, height=180),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        legend_col
                    ])
                ),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT)
            ]
        )
    )

    # 3. TRACKER VIEW (VERIFIED POSTER RETRIEVAL)
    tracker_input = ft.TextField(hint_text="Search movie or series to log...", prefix_icon=ft.Icons.SEARCH, bgcolor=c.CARD_BG, border_color=ft.Colors.TRANSPARENT, border_radius=15)
    tracker_results = ft.Column(spacing=12)
    tracker_recent_log = ft.Column(spacing=12)

    def search_submit(ev):
        results = api.tmdb_search_with_providers(tracker_input.value)
        tracker_results.controls.clear()
        if not results:
            tracker_results.controls.append(ft.Text("No content found on TMDB.", color=ft.Colors.WHITE_54))
        else:
            for item in results:
                t_id = item.get('id')
                t_name = item.get('title') or item.get('name') or "Unknown"
                providers = item.get('watch_providers', [])
                poster_path = item.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else ""
                
                tracker_results.controls.append(
                    ft.Container(
                        padding=12, border_radius=16, bgcolor=c.CARD_BG,
                        content=ft.Row([
                            ft.Image(src=db.resolve_poster(t_name, poster_url), width=50, height=75, fit=ft.BoxFit.COVER, border_radius=10),
                            ft.Column([
                                ft.Text(t_name, size=15, weight=ft.FontWeight.W_800, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color="white"),
                                ft.Text("Streams on: " + (providers[0] if providers else "Theater / On Demand"), size=12, color=ft.Colors.WHITE_54)
                            ], expand=True, spacing=4),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE, 
                                icon_color="white",
                                on_click=lambda e, tid=t_id, tit=t_name, p=providers, img=poster_url: log_and_refresh(tid, tit, p, img)
                            )
                        ], spacing=12)
                    )
                )
        page.update()

    def log_and_refresh(t_id, title, providers, poster):
        plat = providers[0] if providers else "Theater"
        db.log_movie_watch(t_id, title, "movie", plat, "Action", poster=poster)
        tracker_results.controls.clear()
        tracker_input.value = ""
        refresh_tracker_history()
        page.snack_bar = ft.SnackBar(ft.Text(f"Added '{title}' to your history!"), bgcolor="#34C759")
        page.snack_bar.open = True
        page.update()

    def refresh_tracker_history():
        tracker_recent_log.controls.clear()
        history_df = db.get_all_history()
        for _, r in history_df.iterrows():
            img_url = r.get('poster', '')
            plat = str(r.get('platform', 'Netflix'))
            ott_cfg = c.OTT_PLATFORMS.get(plat, {"color": "#333333", "logo": ""})

            tracker_recent_log.controls.append(
                ft.Container(
                    padding=10, border_radius=14, bgcolor=c.CARD_BG,
                    content=ft.Row([
                        ft.Image(src=img_url, width=48, height=72, fit=ft.BoxFit.COVER, border_radius=8),
                        ft.Column([
                            ft.Text(str(r['title']), weight=ft.FontWeight.W_800, size=14, color="white"),
                            ft.Row([
                                ft.Image(src=ott_cfg["logo"], width=12, height=12, fit=ft.BoxFit.CONTAIN) if ott_cfg["logo"] else ft.Container(),
                                ft.Text(plat, size=11, color=ft.Colors.WHITE_54, weight=ft.FontWeight.W_600)
                            ], spacing=4)
                        ], spacing=3, expand=True)
                    ], spacing=14)
                )
            )

    tracker_view = ft.Container(
        padding=20, expand=True, visible=False,
        content=ft.ListView(
            spacing=16,
            controls=[
                ft.Container(height=35),
                ft.Text("Streaming Tracker", size=32, weight=ft.FontWeight.W_900, color="white"),
                ft.Row([
                    ft.Container(content=tracker_input, expand=True),
                    ft.IconButton(icon=ft.Icons.SEARCH, on_click=search_submit)
                ]),
                tracker_results,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("Recently Logged", size=20, weight=ft.FontWeight.W_800, color="white"),
                tracker_recent_log,
                ft.Divider(height=50, color=ft.Colors.TRANSPARENT)
            ]
        )
    )

    # 4. PROFILE & CROSS-PLATFORM OTT HUB
    def toggle_ott(plat_name):
        connected_otts[plat_name] = not connected_otts[plat_name]
        build_ott_manager()
        page.update()

    ott_cards_column = ft.Column(spacing=10)

    def build_ott_manager():
        ott_cards_column.controls.clear()
        for name, cfg in c.OTT_PLATFORMS.items():
            is_active = connected_otts.get(name, False)
            ott_cards_column.controls.append(
                ft.Container(
                    padding=14, border_radius=14, bgcolor=c.CARD_BG,
                    content=ft.Row([
                        ft.Row([
                            ft.Image(src=cfg["logo"], width=24, height=24, fit=ft.BoxFit.CONTAIN),
                            ft.Text(name, size=15, weight=ft.FontWeight.BOLD, color="white")
                        ], spacing=12),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                            border_radius=20,
                            bgcolor=ft.Colors.with_opacity(0.2, "#34C759") if is_active else ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                            content=ft.Text("CONNECTED" if is_active else "CONNECT", size=11, weight=ft.FontWeight.W_900, color="#34C759" if is_active else ft.Colors.WHITE_70),
                            on_click=lambda e, n=name: toggle_ott(n)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            )

    profile_view = ft.Container(
        padding=20, expand=True, visible=False,
        content=ft.ListView(
            spacing=18,
            controls=[
                ft.Container(height=35),
                ft.Row([
                    ft.Text("Profile Hub", size=32, weight=ft.FontWeight.W_900, color="white"),
                    ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=c.NETFLIX_RED, on_click=do_logout)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # User Header Card
                ft.Container(
                    padding=22, border_radius=20, bgcolor=c.CARD_BG,
                    content=ft.Row([
                        ft.CircleAvatar(content=ft.Text(user_state["name"][0], size=24, weight=ft.FontWeight.BOLD), bgcolor=c.NETFLIX_RED, radius=32),
                        ft.Column([
                            ft.Text(user_state["name"], size=20, weight=ft.FontWeight.W_900, color="white"),
                            ft.Text(user_state["email"], size=12, color=ft.Colors.WHITE_54),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=ft.Colors.with_opacity(0.2, c.NETFLIX_RED), border_radius=6,
                                content=ft.Text("UNIVERSAL TIER", size=9, weight=ft.FontWeight.W_900, color=c.NETFLIX_RED)
                            )
                        ], spacing=3, expand=True)
                    ], spacing=14)
                ),

                # Watcher DNA Quick Tile
                ft.Container(
                    padding=16, border_radius=16, bgcolor=c.CARD_BG,
                    content=ft.Row([
                        ft.Row([
                            ft.Text(user_state["emoji"], size=28),
                            ft.Column([
                                ft.Text("Watcher Archetype", size=11, color=ft.Colors.WHITE_54, weight=ft.FontWeight.BOLD),
                                ft.Text(user_state["type"], size=16, weight=ft.FontWeight.W_800, color="white")
                            ], spacing=2)
                        ], spacing=10),
                        ft.TextButton("Change DNA", on_click=lambda e: render_dna_onboarding_view())
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),

                # Cross-Platform OTT Management
                ft.Text("Connected OTT Platforms", size=18, weight=ft.FontWeight.W_800, color="white"),
                ott_cards_column,

                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                PremiumPillButton("Re-Sync Netflix CSV", icon=ft.Icons.FILE_DOWNLOAD, on_click=lambda e: process_direct_sample_csv(e)),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT)
            ]
        )
    )

    def process_direct_sample_csv(e):
        file_path = "netflix_viewing_history_sample.csv"
        if not os.path.exists(file_path):
            page.snack_bar = ft.SnackBar(ft.Text(f"File '{file_path}' not found."), bgcolor=c.NETFLIX_RED)
            page.snack_bar.open = True
            page.update()
            return
        
        df = pd.read_csv(file_path)
        df['BaseTitle'] = df['Title'].apply(lambda x: str(x).split(':')[0].strip())
        unique_titles = df['BaseTitle'].drop_duplicates().head(12).tolist()
        bulk_records = [
            (t, 0, "movie", t, "Netflix", "Action, Sci-Fi", "")
            for t in unique_titles
        ]
        db.log_bulk_movies(bulk_records)
        refresh_tracker_history()
        refresh_analytics()
        page.snack_bar = ft.SnackBar(ft.Text("Successfully synced Netflix history!"), bgcolor="#34C759")
        page.snack_bar.open = True
        page.update()

    # =========================================================
    # APP NAVIGATION
    # =========================================================
    def on_nav_change(e):
        idx = e.control.selected_index
        home_view.visible = (idx == 0)
        analytics_view.visible = (idx == 1)
        tracker_view.visible = (idx == 2)
        profile_view.visible = (idx == 3)
        if idx == 1:
            refresh_analytics()
        elif idx == 2:
            refresh_tracker_history()
        elif idx == 3:
            build_ott_manager()
        page.update()

    def show_main_app():
        home_view.visible = True
        analytics_view.visible = False
        tracker_view.visible = False
        profile_view.visible = False
        refresh_analytics()
        refresh_tracker_history()
        build_ott_manager()

        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            bgcolor="#000000",
            indicator_color="#2C2C2E",
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_ROUNDED, label="Analytics"),
                ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_ROUNDED, label="Tracker"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_ROUNDED, label="Profile"),
            ],
            on_change=on_nav_change,
        )

        master_container.content = ft.Stack([
            ft.Column([home_view, analytics_view, tracker_view, profile_view], expand=True)
        ], expand=True)
        page.update()

    # Initial Boot on Auth Screen
    render_auth_view(is_signup_mode=False)

if __name__ == '__main__':
    ft.run(main)