import streamlit as st
from openai import OpenAI
import json

def get_client():
    return OpenAI(api_key=st.secrets["openai"]["api_key"])

@st.cache_data(show_spinner=False)
def get_mood_suggestions(mood, intensity, genres):
    """(Old Logic) Suggests search terms."""
    return {"queries": [], "reason": "Aggregator active"}

@st.cache_data(show_spinner=False)
def sort_feed_by_mood(titles, mood):
    """
    Takes a list of movie titles and re-orders them based on dopamine needs.
    """
    if not titles: return titles
    
    client = get_client()
    prompt = f"""
    Sort these movie titles based on dopamine preference.
    
    Focus = calm, slow, low stimulation
    Regulate = comforting, familiar, balanced
    Stimulate = energetic, fast, exciting
    
    User mood: {mood}
    Titles: {json.dumps(titles)}
    
    Return ONLY a valid JSON array of strings: ["Title A", "Title B"...]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception as e:
        print(f"Sort Error: {e}")
        return titles # Fallback to original order