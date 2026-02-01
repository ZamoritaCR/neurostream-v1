"""
Content Publisher for dopamine.watch blog
Handles FTP upload and sitemap updates
"""

import os
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ContentPublisher:
    """Publishes generated content to dopamine.watch via FTP"""

    def __init__(self):
        self.ftp_host = os.getenv("FTP_HOST", "ftp.pcmodderscr.com")
        self.ftp_user = os.getenv("FTP_USER", "MrRobotto2@dopamine.watch")
        self.ftp_password = os.getenv("FTP_PASSWORD")
        self.ftp_path = os.getenv("FTP_PATH", "/blog")
        self.local_output_dir = os.path.join(os.path.dirname(__file__), "output")

        # Ensure output directory exists
        os.makedirs(self.local_output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.local_output_dir, "posts"), exist_ok=True)

    def save_locally(self, filename: str, content: str, subdir: str = "") -> str:
        """Save content to local output directory"""
        if subdir:
            target_dir = os.path.join(self.local_output_dir, subdir)
            os.makedirs(target_dir, exist_ok=True)
            filepath = os.path.join(target_dir, filename)
        else:
            filepath = os.path.join(self.local_output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Saved locally: {filepath}")
        return filepath

    def upload_file(self, local_path: str, remote_subpath: str = "") -> bool:
        """Upload a single file via FTP using curl"""
        if not self.ftp_password:
            print("ERROR: FTP_PASSWORD not set in environment")
            return False

        remote_path = f"{self.ftp_path}/{remote_subpath}" if remote_subpath else self.ftp_path
        ftp_url = f"ftp://{self.ftp_host}{remote_path}/{os.path.basename(local_path)}"

        cmd = [
            "curl", "-T", local_path,
            "--user", f"{self.ftp_user}:{self.ftp_password}",
            "--ftp-create-dirs",
            ftp_url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"Uploaded: {ftp_url}")
                return True
            else:
                print(f"Upload failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"Upload timeout: {local_path}")
            return False
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def publish_article(self, html_content: str, slug: str) -> bool:
        """Save article locally and upload to FTP"""
        filename = f"{slug}.html"

        # Save locally first
        local_path = self.save_locally(filename, html_content, "posts")

        # Upload to FTP
        return self.upload_file(local_path, "posts")

    def update_sitemap(self, new_posts: list) -> bool:
        """Generate and upload updated sitemap.xml"""
        # Read existing sitemap or create new
        sitemap_entries = [
            {
                "loc": "https://dopamine.watch/blog/",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "daily",
                "priority": "1.0"
            },
            {
                "loc": "https://dopamine.watch/blog/categories/adhd.html",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "weekly",
                "priority": "0.8"
            },
            {
                "loc": "https://dopamine.watch/blog/categories/streaming.html",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "weekly",
                "priority": "0.8"
            },
            {
                "loc": "https://dopamine.watch/blog/categories/psychology.html",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "weekly",
                "priority": "0.8"
            }
        ]

        # Add existing posts (from posts_index.json if exists)
        index_path = os.path.join(self.local_output_dir, "posts_index.json")
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                existing_posts = json.load(f)
                for post in existing_posts:
                    sitemap_entries.append({
                        "loc": f"https://dopamine.watch/blog/posts/{post['slug']}.html",
                        "lastmod": post.get('published_date', datetime.now().strftime("%Y-%m-%d")),
                        "changefreq": "monthly",
                        "priority": "0.9"
                    })

        # Add new posts
        for post in new_posts:
            sitemap_entries.append({
                "loc": f"https://dopamine.watch/blog/posts/{post['slug']}.html",
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "changefreq": "monthly",
                "priority": "0.9"
            })

        # Generate sitemap XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for entry in sitemap_entries:
            sitemap_xml += "    <url>\n"
            sitemap_xml += f"        <loc>{entry['loc']}</loc>\n"
            sitemap_xml += f"        <lastmod>{entry['lastmod']}</lastmod>\n"
            sitemap_xml += f"        <changefreq>{entry['changefreq']}</changefreq>\n"
            sitemap_xml += f"        <priority>{entry['priority']}</priority>\n"
            sitemap_xml += "    </url>\n"

        sitemap_xml += "</urlset>\n"

        # Save and upload
        local_path = self.save_locally("sitemap.xml", sitemap_xml)
        return self.upload_file(local_path)

    def update_posts_index(self, new_posts: list) -> None:
        """Maintain a local index of all published posts"""
        index_path = os.path.join(self.local_output_dir, "posts_index.json")

        existing_posts = []
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                existing_posts = json.load(f)

        # Add new posts
        for post in new_posts:
            existing_posts.append({
                "slug": post['slug'],
                "title": post['title'],
                "published_date": datetime.now().strftime("%Y-%m-%d"),
                "primary_keyword": post.get('primary_keyword', ''),
                "category": post.get('category', 'adhd')
            })

        with open(index_path, 'w') as f:
            json.dump(existing_posts, f, indent=2)

        print(f"Updated posts index: {len(existing_posts)} total posts")

    def update_blog_homepage(self, all_posts: list) -> bool:
        """Regenerate blog homepage with all posts"""
        # Get most recent 6 posts for homepage
        recent_posts = sorted(
            all_posts,
            key=lambda x: x.get('published_date', ''),
            reverse=True
        )[:6]

        posts_html = ""
        for post in recent_posts:
            category = post.get('category', 'adhd')
            category_colors = {
                'adhd': ('#9B7EDB', '#7B5FB8'),
                'streaming': ('#F5C563', '#E8A23A'),
                'psychology': ('#5EBAAF', '#3D9E94')
            }
            colors = category_colors.get(category, category_colors['adhd'])

            posts_html += f"""
            <article class="post-card" onclick="window.location.href='posts/{post['slug']}.html'">
                <div class="post-card-image" style="background: linear-gradient(135deg, {colors[0]}, {colors[1]}); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 4rem;">🧠</span>
                </div>
                <div class="post-card-content">
                    <div class="post-meta">
                        <span class="post-category">{category.title()}</span>
                        <span>{post.get('published_date', '')}</span>
                    </div>
                    <h2>{post['title']}</h2>
                    <a href="posts/{post['slug']}.html" class="read-more">Read article →</a>
                </div>
            </article>
"""

        homepage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dopamine.watch Blog - ADHD-Friendly Content Recommendations</title>
    <meta name="description" content="Research-backed insights on ADHD, streaming, and finding content that actually helps your brain. From the makers of dopamine.watch.">

    <meta property="og:title" content="Dopamine.watch Blog">
    <meta property="og:description" content="ADHD-friendly insights on content consumption, streaming psychology, and mood-based entertainment.">
    <meta property="og:url" content="https://dopamine.watch/blog/">
    <meta property="og:type" content="website">

    <link rel="canonical" href="https://dopamine.watch/blog/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/blog.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
</head>
<body>
    <header class="blog-header">
        <div class="container">
            <div class="blog-header-inner">
                <a href="https://dopamine.watch" class="blog-logo">🧠 Dopamine.watch</a>
                <nav class="blog-nav">
                    <a href="/blog/" style="color: var(--primary);">Blog</a>
                    <a href="/blog/categories/adhd.html">ADHD</a>
                    <a href="/blog/categories/streaming.html">Streaming</a>
                    <a href="/blog/categories/psychology.html">Psychology</a>
                    <a href="https://app.dopamine.watch" class="btn-app">Try App →</a>
                </nav>
            </div>
        </div>
    </header>

    <div class="hero-section">
        <div class="container">
            <h1>The Dopamine.watch Blog</h1>
            <p class="hero-subtitle">Research-backed insights on ADHD, streaming psychology, and finding content that actually helps your brain.</p>
        </div>
    </div>

    <div class="wide-container">
        <div class="posts-grid" id="posts-grid">
            {posts_html}
        </div>
    </div>

    <div class="container">
        <div class="cta-box">
            <h3>Stop Scrolling. Start Watching.</h3>
            <p>Get personalized recommendations based on your mood, not engagement algorithms.</p>
            <a href="https://app.dopamine.watch" class="btn-primary">Try Dopamine.watch Free →</a>
        </div>
    </div>

    <footer class="blog-footer">
        <div class="container">
            <p>&copy; 2026 Dopamine.watch. Built with 💜 for neurodivergent brains.</p>
        </div>
    </footer>
</body>
</html>
"""

        local_path = self.save_locally("index.html", homepage_html)
        return self.upload_file(local_path)


if __name__ == "__main__":
    publisher = ContentPublisher()

    # Test saving locally
    test_content = "<html><body><h1>Test</h1></body></html>"
    publisher.save_locally("test.html", test_content, "posts")
    print("Publisher test complete")
