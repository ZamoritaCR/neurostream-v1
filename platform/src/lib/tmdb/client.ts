const TMDB_API_KEY = process.env.NEXT_PUBLIC_TMDB_API_KEY;
const TMDB_BASE_URL = "https://api.themoviedb.org/3";

export interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  vote_average: number;
  release_date: string;
  genre_ids: number[];
}

export interface TVShow {
  id: number;
  name: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  vote_average: number;
  first_air_date: string;
  genre_ids: number[];
}

export const tmdb = {
  async searchMovies(query: string): Promise<Movie[]> {
    const response = await fetch(
      `${TMDB_BASE_URL}/search/movie?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(query)}`
    );
    const data = await response.json();
    return data.results || [];
  },

  async searchTV(query: string): Promise<TVShow[]> {
    const response = await fetch(
      `${TMDB_BASE_URL}/search/tv?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(query)}`
    );
    const data = await response.json();
    return data.results || [];
  },

  async getPopularMovies(): Promise<Movie[]> {
    const response = await fetch(
      `${TMDB_BASE_URL}/movie/popular?api_key=${TMDB_API_KEY}`
    );
    const data = await response.json();
    return data.results || [];
  },

  async getPopularTV(): Promise<TVShow[]> {
    const response = await fetch(
      `${TMDB_BASE_URL}/tv/popular?api_key=${TMDB_API_KEY}`
    );
    const data = await response.json();
    return data.results || [];
  },

  async discoverByMood(mood: string): Promise<(Movie | TVShow)[]> {
    const moodGenres: Record<string, number[]> = {
      anxious: [18, 10749],
      happy: [35, 10751],
      sad: [35, 10402],
      bored: [28, 12, 878],
      energized: [28, 53],
      tired: [16, 10751],
      stressed: [35, 10770],
      calm: [99, 10751],
    };

    const genres = moodGenres[mood.toLowerCase()] || [18];
    const genreParam = genres.join(",");

    const [movies, tv] = await Promise.all([
      fetch(
        `${TMDB_BASE_URL}/discover/movie?api_key=${TMDB_API_KEY}&with_genres=${genreParam}&sort_by=vote_average.desc&vote_count.gte=100`
      ).then((r) => r.json()),
      fetch(
        `${TMDB_BASE_URL}/discover/tv?api_key=${TMDB_API_KEY}&with_genres=${genreParam}&sort_by=vote_average.desc&vote_count.gte=50`
      ).then((r) => r.json()),
    ]);

    return [...(movies.results || []), ...(tv.results || [])];
  },

  getPosterUrl(
    path: string | null,
    size: "w185" | "w342" | "w500" = "w342"
  ): string {
    if (!path) return "";
    return `https://image.tmdb.org/t/p/${size}${path}`;
  },
};
