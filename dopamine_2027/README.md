# dopamine.watch 2027

ADHD-friendly streaming recommendation platform with AI-powered curation.

## Quick Start

### Option 1: One-liner (Recommended)
```bash
cd /Users/zamorita/Desktop/Neuronav/dopamine_2027 && ./start.sh
```

### Option 2: Manual
```bash
cd /Users/zamorita/Desktop/Neuronav/dopamine_2027
pip install -r requirements.txt
python server.py
```

Then open: **http://localhost:8000**

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Main App (Frontend) |
| http://localhost:8000/api/docs | Interactive API Documentation |
| http://localhost:8000/api/health | Health Check |
| http://localhost:8000/api/status | Full Status |

## Test GUI (Optional)

For testing individual features:
```bash
streamlit run test_app.py
```

## API Endpoints

### Mr.DP AI
- `POST /api/mr-dp/chat` - Chat with Mr.DP
- `GET /api/mr-dp/quick-dope-hit` - Quick recommendation
- `GET /api/mr-dp/marathon-mode` - Marathon session

### Gamification
- `GET /api/gamification/points/{user_id}` - Get points
- `POST /api/gamification/points` - Add points
- `GET /api/gamification/achievements/{user_id}` - Get achievements
- `GET /api/gamification/streak/{user_id}` - Get streak

### Premium
- `GET /api/premium/subscription/{user_id}` - Subscription info
- `GET /api/premium/usage/{user_id}` - Usage limits
- `POST /api/premium/usage/increment` - Use a feature

### Wellness
- `GET /api/wellness/sos` - SOS calm mode content
- `GET /api/wellness/sos/breathing` - Breathing exercises
- `POST /api/wellness/focus/start` - Start focus session
- `GET /api/wellness/focus/{user_id}/status` - Session status

### Search
- `GET /api/search/multi?query=...` - Multi-platform search
- `GET /api/search/movies?query=...` - Movie search
- `GET /api/search/music?query=...` - Music search

## Environment Variables (Optional)

Create a `.env` file or set these in your environment:

```env
OPENAI_API_KEY=sk-...          # For AI chat (optional - has fallback)
TMDB_API_KEY=...               # For movie search
SPOTIFY_CLIENT_ID=...          # For music search
SPOTIFY_CLIENT_SECRET=...
SUPABASE_URL=...               # For user data persistence
SUPABASE_ANON_KEY=...
```

## Features

- **Mr.DP AI Chat** - ADHD-aware recommendation assistant
- **Gamification** - Points, streaks, 25+ achievements
- **Premium Tiers** - Free/Plus/Pro with usage limits
- **Wellness** - SOS calm mode, focus timer, breathing exercises
- **Multi-Platform Search** - Movies, TV, Music, Podcasts
- **Real-time** - WebSocket support for watch parties

## Architecture

```
dopamine_2027/
├── server.py          # Main entry point
├── api/               # FastAPI routes
├── services/          # Business logic
│   ├── mr_dp/         # AI chatbot
│   ├── gamification/  # Points, streaks, achievements
│   ├── premium/       # Subscriptions, usage limits
│   ├── wellness/      # SOS mode, focus timer
│   └── search/        # Multi-platform search
├── features/          # UI features (Streamlit)
└── config/            # Settings
```

## Support

Built for ADHD brains, by ADHD brains. 💜
