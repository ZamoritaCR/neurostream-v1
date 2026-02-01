"""
RSS Feed Generator for dopamine.watch
Generates and uploads RSS feed for blog
"""

import os
import json
from datetime import datetime
from ftplib import FTP


def generate_rss_feed(posts: list = None) -> str:
    """Generate RSS feed for blog"""

    # Default posts if none provided
    if not posts:
        posts = [
            {
                "title": "Why ADHD Makes Choosing Content Impossible (The Science)",
                "slug": "adhd-decision-paralysis-science",
                "description": "Decision paralysis isn't laziness - it's neuroscience. Here's what actually happens in your ADHD brain when you open Netflix.",
                "date": "2026-01-31"
            },
            {
                "title": "The Netflix Algorithm Wasn't Built for Your Brain",
                "slug": "netflix-algorithm-not-built-for-adhd",
                "description": "Streaming algorithms optimize for engagement, not wellbeing - here's why that's a problem for neurodivergent users.",
                "date": "2026-01-31"
            },
            {
                "title": "10 Shows That Actually Help With Anxiety (Research-Backed)",
                "slug": "shows-that-help-anxiety",
                "description": "Not all content is created equal - these shows have been shown to actually reduce anxiety symptoms.",
                "date": "2026-01-31"
            }
        ]

    # Build RSS items
    items_xml = ""
    for post in posts:
        pub_date = datetime.strptime(post.get('date', '2026-01-31'), '%Y-%m-%d')
        pub_date_str = pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

        items_xml += f'''    <item>
        <title>{post['title']}</title>
        <link>https://dopamine.watch/blog/posts/{post['slug']}.html</link>
        <description><![CDATA[{post.get('description', post.get('excerpt', ''))}]]></description>
        <pubDate>{pub_date_str}</pubDate>
        <guid>https://dopamine.watch/blog/posts/{post['slug']}.html</guid>
    </item>
'''

    rss = f'''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>Dopamine.watch Blog</title>
    <link>https://dopamine.watch/blog/</link>
    <description>Science-backed insights on ADHD, neurodivergent content consumption, and mood-based entertainment</description>
    <language>en-us</language>
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    <atom:link href="https://dopamine.watch/blog/feed.xml" rel="self" type="application/rss+xml" />
    <image>
        <url>https://dopamine.watch/logo.png</url>
        <title>Dopamine.watch Blog</title>
        <link>https://dopamine.watch/blog/</link>
    </image>
{items_xml}
</channel>
</rss>'''

    return rss


def save_and_upload_rss(rss_content: str = None, upload: bool = True):
    """Save RSS feed locally and upload to FTP"""

    if not rss_content:
        rss_content = generate_rss_feed()

    # Save locally
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    local_file = os.path.join(output_dir, "feed.xml")
    with open(local_file, 'w', encoding='utf-8') as f:
        f.write(rss_content)

    print(f"✅ RSS feed saved locally: {local_file}")

    if not upload:
        return local_file

    # Upload to server
    ftp_host = os.getenv('FTP_HOST', 'ftp.pcmodderscr.com')
    ftp_user = os.getenv('FTP_USER', 'MrRobotto2@dopamine.watch')
    ftp_password = os.getenv('FTP_PASSWORD')

    if not ftp_password:
        print("⚠️ FTP_PASSWORD not set - skipping upload")
        return local_file

    try:
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_password)

        # Navigate to blog directory
        try:
            ftp.cwd('/blog')
        except:
            ftp.cwd('/')
            try:
                ftp.mkd('blog')
            except:
                pass
            ftp.cwd('/blog')

        # Upload RSS feed
        with open(local_file, 'rb') as f:
            ftp.storbinary('STOR feed.xml', f)

        ftp.quit()

        print("✅ RSS feed uploaded to server!")
        print("   URL: https://dopamine.watch/blog/feed.xml")

        return "https://dopamine.watch/blog/feed.xml"

    except Exception as e:
        print(f"❌ FTP upload failed: {e}")
        return local_file


def load_posts_from_index() -> list:
    """Load posts from posts_index.json"""

    index_path = os.path.join(os.path.dirname(__file__), "output", "posts_index.json")

    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    return []


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("\n" + "="*60)
    print("📡 RSS FEED GENERATOR")
    print("="*60 + "\n")

    # Try to load posts from index, fallback to defaults
    posts = load_posts_from_index()
    if posts:
        print(f"Found {len(posts)} posts in index")
    else:
        print("Using default posts")

    # Generate and upload
    rss_content = generate_rss_feed(posts if posts else None)
    result = save_and_upload_rss(rss_content)

    print(f"\n✅ Complete! RSS feed available at: {result}")
