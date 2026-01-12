import streamlit as st
from openai import OpenAI
import json

def get_client():
    return OpenAI(api_key=st.secrets["openai"]["api_key"])

@st.cache_data(show_spinner=False)
def get_mood_suggestions(mood, intensity, genres):
    """
    Translates 'Anxious' -> 'Calming search terms' using ChatGPT.
    Returns a list of 3 specific search queries for TMDB.
    """
    client = get_client()
    
    # 1. Construct the Neuro-Aware Prompt
    system_prompt = """
    You are a cognitive regulation assistant for a user with ADHD.
    Based on their current mood, suggest 3 specific, distinct search queries 
    for a Movie/TV database (TMDB).
    
    Rules:
    - If 'Anxious/Over-stimulated': Suggest low-sensory, familiar, calming content.
    - If 'Bored/Under-stimulated': Suggest high-novelty, gripping, complex content.
    - Output must be valid JSON: {"queries": ["term1", "term2", "term3"], "reason": "brief explanation"}
    """
    
    user_prompt = f"""
    User State: {mood}
    Intensity: {intensity}/100
    Preferred Genres: {', '.join(genres)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"AI Error: {e}")
        return {"queries": ["Planet Earth", "Comfort Movie", "Animation"], "reason": "Fallback due to connection error."}