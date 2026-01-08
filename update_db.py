import requests
import pandas as pd

# --- CONFIGURATION ---
API_KEY = "ee628f8efc90ab11dffc948c4fd2f29e"

def get_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    response = requests.get(url)
    return response.json().get('results', [])

def get_sensory_details(movie):
    genre_ids = movie.get('genre_ids', [])
    if any(g in [27, 28, 53] for g in genre_ids):
        return "High", "Loud noises, Fast Paced", "🔴"
    elif any(g in [10751, 10749] for g in genre_ids):
        return "Low", "Calming, Predictable", "🟢"
    else:
        return "Medium", "Balanced", "🟡"

# --- MAIN RUN ---
print("🚀 Fetching Trending Movies with Backdrops...")
trending_movies = get_trending_movies()
clean_data = []

for movie in trending_movies:
    load, triggers, emoji = get_sensory_details(movie)
    title = movie.get('title')
    
    clean_data.append({
        "Title": title,
        "Overview": movie.get('overview'),
        "Poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
        "Backdrop": f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}", # <--- THIS IS THE KEY LINE
        "Rating": movie.get('vote_average'),
        "Sensory Load": load,
        "Triggers": triggers,
        "Emoji": emoji,
        "Link": f"https://www.justwatch.com/us/search?q={title.replace(' ', '%20')}"
    })

df = pd.DataFrame(clean_data)
df.to_csv("movies.csv", sep="|", index=False)
print("✅ DONE! Created new database with Backdrops.")