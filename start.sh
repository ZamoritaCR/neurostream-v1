#!/bin/bash
mkdir -p .streamlit

cat > .streamlit/secrets.toml << EOF
[tmdb]
api_key = "$TMDB_API_KEY"

[openai]
api_key = "$OPENAI_API_KEY"
EOF

echo "secrets.toml created"
echo "TMDB key length: ${#TMDB_API_KEY}"
echo "OpenAI key length: ${#OPENAI_API_KEY}"

python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
