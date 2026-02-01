"""
Social Media Manager for dopamine.watch
Auto-posts to Twitter, LinkedIn, Facebook
"""

import os
import json
from datetime import datetime
from openai import OpenAI


class SocialMediaManager:
    """Manages posting to all social media platforms"""

    def __init__(self):
        self.twitter_enabled = bool(os.getenv('TWITTER_API_KEY'))
        self.facebook_enabled = bool(os.getenv('FACEBOOK_PAGE_TOKEN'))
        self.linkedin_enabled = bool(os.getenv('LINKEDIN_TOKEN'))
        self.logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

    def post_to_all_platforms(self, post_data: dict) -> dict:
        """Post to all enabled platforms"""

        results = {}

        print("\n📱 POSTING TO SOCIAL MEDIA...")

        # Generate platform-specific content
        twitter_content = self._generate_twitter_thread(post_data)
        linkedin_content = self._generate_linkedin_post(post_data)
        facebook_content = self._generate_facebook_post(post_data)

        # Post to each platform
        if self.twitter_enabled:
            results['twitter'] = self.post_to_twitter(twitter_content)
        else:
            results['twitter'] = self._log_twitter(twitter_content)

        if self.linkedin_enabled:
            results['linkedin'] = self.post_to_linkedin(linkedin_content)
        else:
            results['linkedin'] = self._log_linkedin(linkedin_content)

        if self.facebook_enabled:
            results['facebook'] = self.post_to_facebook(facebook_content)
        else:
            results['facebook'] = self._log_facebook(facebook_content)

        # Log results
        self._log_social_posts(post_data, results)

        return results

    def _generate_twitter_thread(self, post_data: dict) -> list:
        """Generate Twitter/X thread from blog post"""

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Fallback if no OpenAI key
            return [
                f"🧠 New on the blog: {post_data['title']}\n\nThread 🧵👇",
                post_data.get('excerpt', '')[:250],
                f"Read the full article: {post_data['url']}\n\n#ADHD #Streaming #Neurodivergent"
            ]

        client = OpenAI(api_key=api_key)

        prompt = f"""Create a Twitter/X thread about this blog post:

TITLE: {post_data['title']}
EXCERPT: {post_data.get('excerpt', '')}
URL: {post_data['url']}

REQUIREMENTS:
- 3-5 tweets total
- First tweet: Hook (grab attention)
- Middle tweets: Key insights from post
- Last tweet: CTA + link
- Use simple language
- Include relevant hashtags (#ADHD #Streaming)
- Engaging and conversational
- Each tweet under 280 characters

OUTPUT AS JSON:
{{
  "tweets": [
    "Tweet 1 text...",
    "Tweet 2 text...",
    "Tweet 3 text..."
  ]
}}"""

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )

            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            thread = json.loads(content)
            return thread['tweets']
        except Exception as e:
            print(f"   ⚠️ OpenAI error: {e}")
            return [
                f"🧠 New: {post_data['title']}\n\nThread 🧵👇",
                post_data.get('excerpt', '')[:250],
                f"Read more: {post_data['url']}\n\n#ADHD #Streaming"
            ]

    def _generate_linkedin_post(self, post_data: dict) -> str:
        """Generate LinkedIn post"""

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return f"""📚 New on the Dopamine.watch blog:

{post_data['title']}

{post_data.get('excerpt', '')}

As someone building tools for neurodivergent minds, this topic is close to my heart. Would love to hear your thoughts!

Read the full article: {post_data['url']}

#ADHD #Neurodiversity #Streaming #MentalHealth #ProductDevelopment"""

        client = OpenAI(api_key=api_key)

        prompt = f"""Write a LinkedIn post about this article:

TITLE: {post_data['title']}
EXCERPT: {post_data.get('excerpt', '')}
URL: {post_data['url']}

STYLE:
- Professional but personal
- Share insights/learning
- 3-5 paragraphs
- Include hook
- End with question for engagement
- Add relevant hashtags

Write as a LinkedIn post:"""

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"   ⚠️ OpenAI error: {e}")
            return f"""📚 New on the blog: {post_data['title']}

{post_data.get('excerpt', '')}

Read more: {post_data['url']}

#ADHD #Neurodivergent #Streaming #MentalHealth"""

    def _generate_facebook_post(self, post_data: dict) -> str:
        """Generate Facebook post"""

        return f"""📚 New on the blog: {post_data['title']}

{post_data.get('excerpt', '')}

Read more: {post_data['url']}

#ADHD #Neurodivergent #Streaming #MentalHealth"""

    def _log_twitter(self, tweets: list) -> dict:
        """Log Twitter content (when API not connected)"""
        print("🐦 Twitter thread (logged - API not connected):")
        for i, tweet in enumerate(tweets, 1):
            print(f"   {i}. {tweet[:80]}...")
        return {"status": "logged", "tweets": len(tweets), "content": tweets}

    def _log_linkedin(self, content: str) -> dict:
        """Log LinkedIn content (when API not connected)"""
        print("💼 LinkedIn post (logged - API not connected):")
        print(f"   {content[:100]}...")
        return {"status": "logged", "content": content}

    def _log_facebook(self, content: str) -> dict:
        """Log Facebook content (when API not connected)"""
        print("📘 Facebook post (logged - API not connected):")
        print(f"   {content[:100]}...")
        return {"status": "logged", "content": content}

    def post_to_twitter(self, tweets: list) -> dict:
        """Post thread to Twitter/X using API"""

        # Using Twitter API v2
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')

        print("🐦 Twitter thread:")
        for i, tweet in enumerate(tweets, 1):
            print(f"   {i}. {tweet[:80]}...")

        # TODO: Implement actual Twitter API posting with tweepy
        # For now, just log the content

        return {"status": "logged", "tweets": len(tweets)}

    def post_to_linkedin(self, content: str) -> dict:
        """Post to LinkedIn"""

        print("💼 LinkedIn post:")
        print(f"   {content[:100]}...")

        # TODO: Implement LinkedIn API

        return {"status": "logged"}

    def post_to_facebook(self, content: str) -> dict:
        """Post to Facebook page"""

        print("📘 Facebook post:")
        print(f"   {content[:100]}...")

        # TODO: Implement Facebook Graph API

        return {"status": "logged"}

    def _log_social_posts(self, post_data: dict, results: dict):
        """Log all social media posts"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "post_title": post_data['title'],
            "post_url": post_data['url'],
            "platforms": results
        }

        log_file = os.path.join(self.logs_dir, f"social_posts_{datetime.now().strftime('%Y%m%d')}.json")

        # Append to log
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"\n✅ Social posts logged to {log_file}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Test with sample post
    test_post = {
        "title": "Why ADHD Makes Choosing Content Impossible",
        "excerpt": "Decision paralysis isn't laziness - it's neuroscience. Here's what actually happens in your ADHD brain.",
        "url": "https://dopamine.watch/blog/posts/adhd-decision-paralysis-science.html"
    }

    social = SocialMediaManager()
    results = social.post_to_all_platforms(test_post)

    print("\n✅ Social media posting complete!")
