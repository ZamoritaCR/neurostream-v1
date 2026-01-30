#!/bin/bash
mkdir -p .streamlit

cat > .streamlit/secrets.toml << EOF
[tmdb]
api_key = "$TMDB_API_KEY"

[openai]
api_key = "$OPENAI_API_KEY"

[supabase]
url = "$SUPABASE_URL"
anon_key = "$SUPABASE_ANON_KEY"

[stripe]
publishable_key = "$STRIPE_PUBLISHABLE_KEY"
secret_key = "$STRIPE_SECRET_KEY"
webhook_secret = "$STRIPE_WEBHOOK_SECRET"
EOF

echo "=== Railway Startup ==="
echo "secrets.toml created"
echo "PORT: $PORT"
echo "TMDB key length: ${#TMDB_API_KEY}"
echo "OpenAI key length: ${#OPENAI_API_KEY}"
echo "Supabase URL: ${SUPABASE_URL:0:30}..."
echo "Supabase key length: ${#SUPABASE_ANON_KEY}"
echo "Starting Streamlit..."

python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
