"""
Content Bot for dopamine.watch
Main orchestrator for content generation and publishing
"""

import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

from generator import ContentGenerator
from publisher import ContentPublisher
from social_media import SocialMediaManager

load_dotenv()


class ContentBot:
    """Orchestrates content generation and publishing"""

    def __init__(self):
        self.generator = ContentGenerator()
        self.publisher = ContentPublisher()
        self.social = SocialMediaManager()
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "posts"), exist_ok=True)

    def generate_and_publish(self, count: int = 1, pillar: str = None,
                              publish: bool = True, dry_run: bool = False) -> list:
        """Generate articles and optionally publish them"""

        print(f"\n{'='*60}")
        print(f"Content Bot - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")

        # Step 1: Generate topic ideas
        print(f"\n📝 Generating {count} topic ideas...")
        topics = self.generator.generate_topic_ideas(pillar=pillar, count=count)

        if not topics:
            print("❌ Failed to generate topics")
            return []

        print(f"✅ Generated {len(topics)} topics:")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic['title']}")

        # Step 2: Generate full articles
        published_posts = []
        for i, topic in enumerate(topics, 1):
            print(f"\n📄 Generating article {i}/{len(topics)}: {topic['title']}")

            article = self.generator.generate_article(topic)
            if not article:
                print(f"   ❌ Failed to generate article")
                continue

            print(f"   ✅ Article generated ({article.get('reading_time', '?')} min read)")

            # Step 3: Generate HTML
            html_content = self.generator.generate_html_page(article)

            if dry_run:
                # Save locally only
                self.publisher.save_locally(f"{article['slug']}.html", html_content, "posts")
                print(f"   💾 Saved locally (dry run)")
            elif publish:
                # Publish to FTP
                success = self.publisher.publish_article(html_content, article['slug'])
                if success:
                    print(f"   🚀 Published to dopamine.watch/blog/posts/{article['slug']}.html")
                    published_posts.append(article)

                    # Post to social media
                    post_url = f"https://dopamine.watch/blog/posts/{article['slug']}.html"
                    post_data = {
                        "title": article['title'],
                        "excerpt": article.get('excerpt', article.get('meta_description', '')),
                        "url": post_url
                    }
                    self.social.post_to_all_platforms(post_data)
                else:
                    print(f"   ❌ Failed to publish")
            else:
                # Save locally
                self.publisher.save_locally(f"{article['slug']}.html", html_content, "posts")
                print(f"   💾 Saved locally")
                published_posts.append(article)

            # Save article JSON for reference
            json_path = os.path.join(self.output_dir, "posts", f"{article['slug']}.json")
            with open(json_path, 'w') as f:
                json.dump(article, f, indent=2)

        # Step 4: Update sitemap and index
        if published_posts and publish and not dry_run:
            print(f"\n📊 Updating sitemap and blog homepage...")
            self.publisher.update_posts_index(published_posts)
            self.publisher.update_sitemap(published_posts)

            # Get all posts for homepage update
            index_path = os.path.join(self.output_dir, "posts_index.json")
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    all_posts = json.load(f)
                self.publisher.update_blog_homepage(all_posts)

        print(f"\n{'='*60}")
        print(f"✨ Complete! Generated {len(published_posts)} articles")
        print(f"{'='*60}\n")

        return published_posts

    def list_topics(self, pillar: str = None, count: int = 10) -> list:
        """Generate and display topic ideas without creating articles"""
        print(f"\n📝 Generating {count} topic ideas...")
        if pillar:
            print(f"   Pillar: {pillar}")

        topics = self.generator.generate_topic_ideas(pillar=pillar, count=count)

        print(f"\n{'='*60}")
        print("TOPIC IDEAS")
        print(f"{'='*60}")

        for i, topic in enumerate(topics, 1):
            print(f"\n{i}. {topic['title']}")
            print(f"   Slug: {topic.get('slug', 'n/a')}")
            print(f"   Keyword: {topic.get('primary_keyword', 'n/a')}")
            print(f"   Type: {topic.get('content_type', 'guide')}")
            print(f"   Audience: {topic.get('target_audience', 'n/a')}")

        return topics


def main():
    parser = argparse.ArgumentParser(description="Content Bot for dopamine.watch")
    parser.add_argument("command", choices=["generate", "topics", "test", "schedule"],
                        help="Command to run")
    parser.add_argument("--count", "-n", type=int, default=1,
                        help="Number of articles/topics to generate")
    parser.add_argument("--pillar", "-p", type=str, default=None,
                        help="Content pillar to focus on")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate but don't publish")
    parser.add_argument("--no-publish", action="store_true",
                        help="Save locally without publishing")

    args = parser.parse_args()

    bot = ContentBot()

    if args.command == "generate":
        bot.generate_and_publish(
            count=args.count,
            pillar=args.pillar,
            publish=not args.no_publish,
            dry_run=args.dry_run
        )
    elif args.command == "topics":
        bot.list_topics(pillar=args.pillar, count=args.count)
    elif args.command == "test":
        print("Testing content bot...")
        print(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
        print(f"FTP Password: {'✅ Set' if os.getenv('FTP_PASSWORD') else '❌ Missing'}")
        print(f"Twitter API Key: {'✅ Set' if os.getenv('TWITTER_API_KEY') else '⚪ Not set (will log only)'}")
        print(f"LinkedIn Token: {'✅ Set' if os.getenv('LINKEDIN_TOKEN') else '⚪ Not set (will log only)'}")
        print(f"Facebook Token: {'✅ Set' if os.getenv('FACEBOOK_PAGE_TOKEN') else '⚪ Not set (will log only)'}")
        print(f"Output directory: {bot.output_dir}")

    elif args.command == "schedule":
        import time
        try:
            import schedule
        except ImportError:
            print("❌ schedule package not installed. Run: pip install schedule")
            return

        print("\n📅 Content Bot Scheduler Started!")
        print("   Will publish Mondays & Thursdays at 9am")
        print("   Press Ctrl+C to stop\n")

        # Schedule for Monday and Thursday at 9am
        schedule.every().monday.at("09:00").do(
            lambda: bot.generate_and_publish(count=1, publish=True)
        )
        schedule.every().thursday.at("09:00").do(
            lambda: bot.generate_and_publish(count=1, publish=True)
        )

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
