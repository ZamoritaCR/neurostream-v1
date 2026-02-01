"""
Analytics Dashboard for dopamine.watch
Custom analytics tracking and reporting
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsDashboard:
    """Custom analytics tracking"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.log_dir = os.path.join(self.base_dir, "logs", "analytics")
        os.makedirs(self.log_dir, exist_ok=True)

    def track_post_performance(self, post_slug: str, metrics: dict = None):
        """Track post metrics"""

        default_metrics = {
            "slug": post_slug,
            "published_date": datetime.now().isoformat(),
            "views": 0,
            "clicks": 0,
            "social_shares": 0,
            "time_on_page_avg": 0,
            "bounce_rate": 0,
            "scroll_depth_avg": 0
        }

        if metrics:
            default_metrics.update(metrics)

        # Save metrics
        log_file = os.path.join(self.log_dir, f"{post_slug}_metrics.json")
        with open(log_file, 'w') as f:
            json.dump(default_metrics, f, indent=2)

        print(f"✅ Tracking initialized for: {post_slug}")

    def update_metrics(self, post_slug: str, updates: dict):
        """Update metrics for a post"""

        log_file = os.path.join(self.log_dir, f"{post_slug}_metrics.json")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = {"slug": post_slug}

        metrics.update(updates)
        metrics["last_updated"] = datetime.now().isoformat()

        with open(log_file, 'w') as f:
            json.dump(metrics, f, indent=2)

    def get_post_metrics(self, post_slug: str) -> dict:
        """Get metrics for a specific post"""

        log_file = os.path.join(self.log_dir, f"{post_slug}_metrics.json")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
        return None

    def get_all_metrics(self) -> list:
        """Get metrics for all posts"""

        all_metrics = []

        for filename in os.listdir(self.log_dir):
            if filename.endswith('_metrics.json'):
                with open(os.path.join(self.log_dir, filename), 'r') as f:
                    all_metrics.append(json.load(f))

        return all_metrics

    def generate_report(self, output_format: str = "console"):
        """Generate performance report"""

        print("\n" + "="*60)
        print("📊 CONTENT PERFORMANCE REPORT")
        print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60 + "\n")

        # Get all post metrics
        total_posts = 0
        total_views = 0
        total_clicks = 0
        total_shares = 0

        posts = []

        for filename in os.listdir(self.log_dir):
            if filename.endswith('_metrics.json'):
                with open(os.path.join(self.log_dir, filename), 'r') as f:
                    metrics = json.load(f)
                    total_posts += 1
                    total_views += metrics.get('views', 0)
                    total_clicks += metrics.get('clicks', 0)
                    total_shares += metrics.get('social_shares', 0)
                    posts.append(metrics)

        # Sort by views (highest first)
        posts.sort(key=lambda x: x.get('views', 0), reverse=True)

        # Display individual posts
        print("TOP PERFORMING POSTS:")
        print("-"*60)

        for i, metrics in enumerate(posts[:10], 1):
            print(f"\n{i}. {metrics['slug']}")
            print(f"   Views: {metrics.get('views', 0):,}")
            print(f"   Clicks: {metrics.get('clicks', 0):,}")
            print(f"   CTR: {self._calculate_ctr(metrics):.2f}%")
            print(f"   Social Shares: {metrics.get('social_shares', 0)}")
            pub_date = metrics.get('published_date', 'N/A')
            if pub_date != 'N/A':
                pub_date = pub_date[:10]
            print(f"   Published: {pub_date}")

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\n  Total Posts: {total_posts}")
        print(f"  Total Views: {total_views:,}")
        print(f"  Total Clicks: {total_clicks:,}")
        print(f"  Total Social Shares: {total_shares:,}")

        if total_posts > 0:
            print(f"\n  Avg Views/Post: {total_views/total_posts:.0f}")
            print(f"  Avg Clicks/Post: {total_clicks/total_posts:.0f}")

        if total_views > 0:
            print(f"  Overall CTR: {(total_clicks/total_views*100):.2f}%")

        print("\n" + "="*60 + "\n")

        # Save report to file
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_posts": total_posts,
                "total_views": total_views,
                "total_clicks": total_clicks,
                "total_shares": total_shares,
                "avg_views_per_post": total_views/total_posts if total_posts > 0 else 0,
                "overall_ctr": (total_clicks/total_views*100) if total_views > 0 else 0
            },
            "posts": posts
        }

        report_file = os.path.join(self.log_dir, f"report_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Report saved to: {report_file}")

        return report_data

    def _calculate_ctr(self, metrics: dict) -> float:
        """Calculate click-through rate"""
        views = metrics.get('views', 0)
        clicks = metrics.get('clicks', 0)
        return (clicks / views * 100) if views > 0 else 0

    def track_social_post(self, platform: str, post_data: dict):
        """Track social media post performance"""

        social_log_dir = os.path.join(self.base_dir, "logs", "social")
        os.makedirs(social_log_dir, exist_ok=True)

        log_file = os.path.join(social_log_dir, f"{platform}_{datetime.now().strftime('%Y%m%d')}.json")

        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)

        logs.append({
            "timestamp": datetime.now().isoformat(),
            **post_data
        })

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)


if __name__ == "__main__":
    dashboard = AnalyticsDashboard()

    # Create some sample data for testing
    sample_posts = [
        "adhd-decision-paralysis-science",
        "netflix-algorithm-not-built-for-adhd",
        "shows-that-help-anxiety"
    ]

    for slug in sample_posts:
        dashboard.track_post_performance(slug, {
            "views": 100 + hash(slug) % 500,
            "clicks": 10 + hash(slug) % 50,
            "social_shares": 5 + hash(slug) % 20
        })

    # Generate report
    dashboard.generate_report()
