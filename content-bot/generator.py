"""
Content Generator for dopamine.watch blog
Uses GPT-4 to generate ADHD-focused blog content
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    """Generates SEO-optimized, ADHD-focused blog content using GPT-4"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"

        # Content pillars for dopamine.watch
        self.content_pillars = [
            "ADHD and content consumption",
            "Streaming platform psychology",
            "Mood-based entertainment",
            "Neurodivergent-friendly media",
            "Decision fatigue and choice overload",
            "Dopamine and entertainment",
            "Anxiety-reducing content",
            "Focus and background media",
            "Binge-watching psychology",
            "ADHD productivity and rest"
        ]

        # SEO keyword clusters
        self.keyword_clusters = {
            "adhd": [
                "ADHD streaming", "ADHD Netflix", "ADHD TV shows",
                "ADHD decision paralysis", "ADHD content recommendations",
                "neurodivergent streaming", "ADHD entertainment"
            ],
            "mood": [
                "mood-based recommendations", "shows for anxiety",
                "calming TV shows", "feel-good content", "comfort shows",
                "shows for depression", "uplifting movies"
            ],
            "streaming": [
                "Netflix algorithm", "streaming recommendations",
                "what to watch", "best shows for", "streaming fatigue",
                "content discovery", "recommendation engine"
            ],
            "psychology": [
                "dopamine and TV", "binge watching psychology",
                "entertainment psychology", "media and mental health",
                "screen time ADHD", "parasocial relationships"
            ]
        }

    def generate_topic_ideas(self, pillar: str = None, count: int = 5) -> list:
        """Generate blog topic ideas based on content pillars"""

        selected_pillar = pillar or self.content_pillars[
            datetime.now().day % len(self.content_pillars)
        ]

        prompt = f"""Generate {count} blog post topic ideas for dopamine.watch,
an ADHD-friendly streaming recommendation app.

Content pillar: {selected_pillar}

Requirements:
- Each topic should be specific and searchable
- Include long-tail keyword potential
- Focus on problems ADHD/neurodivergent people face with streaming
- Make titles compelling and click-worthy (not clickbait)
- Topics should position dopamine.watch as the solution

Return as JSON array with objects containing:
- title: The blog post title
- slug: URL-friendly slug
- primary_keyword: Main SEO keyword
- secondary_keywords: List of 3-5 related keywords
- target_audience: Who this is for
- estimated_word_count: 1500-2500 words
- content_type: "guide" | "listicle" | "explainer" | "comparison" | "how-to"

Return ONLY valid JSON, no other text."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO content strategist specializing in ADHD and mental health content. You create engaging, research-backed content ideas."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        try:
            topics = json.loads(response.choices[0].message.content)
            return topics
        except json.JSONDecodeError:
            # Try to extract JSON from response
            content = response.choices[0].message.content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            return []

    def generate_article(self, topic: dict) -> dict:
        """Generate a full blog article from a topic"""

        prompt = f"""Write a comprehensive blog post for dopamine.watch.

Title: {topic['title']}
Primary Keyword: {topic['primary_keyword']}
Secondary Keywords: {', '.join(topic.get('secondary_keywords', []))}
Content Type: {topic.get('content_type', 'guide')}
Target Word Count: {topic.get('estimated_word_count', 2000)}

CRITICAL REQUIREMENTS:

1. ADHD-FRIENDLY WRITING:
   - Short paragraphs (2-3 sentences max)
   - Use bullet points and lists frequently
   - Bold important phrases for scanning
   - Clear, simple language
   - No fluff or filler content

2. SEO OPTIMIZATION:
   - Include primary keyword in first 100 words
   - Use H2 and H3 headings with keywords
   - Include a FAQ section with 4-5 questions
   - Natural keyword placement throughout

3. STRUCTURE:
   - Hook opening that identifies the problem
   - Research-backed claims where possible
   - Practical, actionable advice
   - Subtle mention of dopamine.watch as a solution (not salesy)
   - Strong conclusion with CTA

4. TONE:
   - Empathetic and understanding
   - "We get it" energy
   - Not condescending or overly clinical
   - Conversational but authoritative

Return as JSON with:
- title: Final title
- meta_description: 155 characters max for SEO
- content: Full HTML article content (use h2, h3, p, ul, li, strong tags)
- excerpt: 2-3 sentence preview
- reading_time: Estimated minutes
- faq: Array of {{question, answer}} objects

Return ONLY valid JSON."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert content writer for dopamine.watch, an ADHD-friendly streaming recommendation app.

You write engaging, research-backed content that:
- Helps neurodivergent people understand their relationship with media
- Provides practical advice for better content consumption
- Positions dopamine.watch as a helpful tool (subtly, not salesy)
- Uses ADHD-friendly formatting (short paragraphs, lists, bold text)

Your writing is empathetic, clear, and backed by psychology research when relevant."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        try:
            article = json.loads(response.choices[0].message.content)
            article['slug'] = topic.get('slug', '')
            article['primary_keyword'] = topic.get('primary_keyword', '')
            article['secondary_keywords'] = topic.get('secondary_keywords', [])
            article['generated_at'] = datetime.now().isoformat()
            return article
        except json.JSONDecodeError:
            # Try to extract JSON
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                article = json.loads(content[start:end])
                article['slug'] = topic.get('slug', '')
                article['generated_at'] = datetime.now().isoformat()
                return article
            return None

    def generate_html_page(self, article: dict) -> str:
        """Convert article JSON to full HTML page"""

        # Build FAQ schema
        faq_schema = []
        faq_html = ""
        if article.get('faq'):
            faq_html = "<h2>Frequently Asked Questions</h2>\n"
            for qa in article['faq']:
                faq_html += f"<h3>{qa['question']}</h3>\n<p>{qa['answer']}</p>\n"
                faq_schema.append({
                    "@type": "Question",
                    "name": qa['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": qa['answer']
                    }
                })

        schema_json = json.dumps({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article['title'],
            "description": article.get('meta_description', ''),
            "author": {
                "@type": "Organization",
                "name": "Dopamine.watch"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Dopamine.watch",
                "url": "https://dopamine.watch"
            },
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "mainEntityOfPage": f"https://dopamine.watch/blog/posts/{article['slug']}.html"
        }, indent=2)

        faq_schema_json = ""
        if faq_schema:
            faq_schema_json = f"""
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": {json.dumps(faq_schema, indent=2)}
    }}
    </script>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | Dopamine.watch Blog</title>

    <meta name="description" content="{article.get('meta_description', '')}">
    <meta name="keywords" content="{article.get('primary_keyword', '')}, {', '.join(article.get('secondary_keywords', []))}">

    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article.get('meta_description', '')}">
    <meta property="og:url" content="https://dopamine.watch/blog/posts/{article['slug']}.html">
    <meta property="og:type" content="article">

    <link rel="canonical" href="https://dopamine.watch/blog/posts/{article['slug']}.html">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../assets/css/blog.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">

    <script type="application/ld+json">
    {schema_json}
    </script>
    {faq_schema_json}
</head>
<body>
    <header class="blog-header">
        <div class="container">
            <div class="blog-header-inner">
                <a href="https://dopamine.watch" class="blog-logo">🧠 Dopamine.watch</a>
                <nav class="blog-nav">
                    <a href="/blog/">Blog</a>
                    <a href="/blog/categories/adhd.html">ADHD</a>
                    <a href="/blog/categories/streaming.html">Streaming</a>
                    <a href="/blog/categories/psychology.html">Psychology</a>
                    <a href="https://app.dopamine.watch" class="btn-app">Try App →</a>
                </nav>
            </div>
        </div>
    </header>

    <article>
        <div style="text-align: center; margin-bottom: 2rem;">
            <div class="post-meta" style="justify-content: center; margin-bottom: 1rem;">
                <span class="post-category">ADHD</span>
                <span>{datetime.now().strftime("%B %d, %Y")}</span>
                <span>{article.get('reading_time', 7)} min read</span>
            </div>

            <h1>{article['title']}</h1>
        </div>

        {article.get('content', '')}

        {faq_html}

        <div class="share-section">
            <p>Share this with someone who needs it.</p>
            <div class="share-buttons">
                <a href="https://twitter.com/intent/tweet?url=https://dopamine.watch/blog/posts/{article['slug']}.html&text={article['title'].replace(' ', '%20')}" target="_blank" class="share-btn twitter">Twitter</a>
                <a href="https://www.facebook.com/sharer/sharer.php?u=https://dopamine.watch/blog/posts/{article['slug']}.html" target="_blank" class="share-btn facebook">Facebook</a>
                <a href="https://www.linkedin.com/shareArticle?mini=true&url=https://dopamine.watch/blog/posts/{article['slug']}.html" target="_blank" class="share-btn linkedin">LinkedIn</a>
            </div>
        </div>
    </article>

    <div class="container">
        <div class="cta-box">
            <h3>Find What You Actually Want to Watch</h3>
            <p>No more endless scrolling. Get recommendations based on your mood, not engagement metrics.</p>
            <a href="https://app.dopamine.watch" class="btn-primary">Try Dopamine.watch Free →</a>
        </div>
    </div>

    <footer class="blog-footer">
        <div class="container">
            <p>&copy; 2026 Dopamine.watch. Built with 💜 for neurodivergent brains.</p>
            <p style="margin-top: 1rem;">
                <a href="/blog/">← Back to Blog</a>
            </p>
        </div>
    </footer>
</body>
</html>
"""
        return html


if __name__ == "__main__":
    # Test the generator
    generator = ContentGenerator()

    print("Generating topic ideas...")
    topics = generator.generate_topic_ideas(count=3)

    for i, topic in enumerate(topics, 1):
        print(f"\n{i}. {topic['title']}")
        print(f"   Keyword: {topic['primary_keyword']}")
        print(f"   Type: {topic.get('content_type', 'guide')}")
