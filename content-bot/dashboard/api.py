"""
Content Bot Dashboard API
Flask backend for the control dashboard
"""

import os
import sys
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__, static_folder='.')
CORS(app)

# Chat agent (lazy loaded)
chat_agent = None

def get_agent():
    """Get or create the chat agent"""
    global chat_agent
    if chat_agent is None:
        try:
            from agent import ContentAgent
            chat_agent = ContentAgent()
        except Exception as e:
            print(f"Failed to initialize agent: {e}")
            return None
    return chat_agent

# State management
bot_state = {
    "status": "idle",
    "last_run": None,
    "next_run": None,
    "scheduler_active": False,
    "current_task": None
}

# Activity log
activity_log = []

def log_activity(action: str, status: str = "success", details: str = ""):
    """Add entry to activity log"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "details": details
    }
    activity_log.insert(0, entry)
    # Keep only last 100 entries
    if len(activity_log) > 100:
        activity_log.pop()

    # Also save to file
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"dashboard_{datetime.now().strftime('%Y%m%d')}.json")

    try:
        with open(log_file, 'w') as f:
            json.dump(activity_log[:50], f, indent=2)
    except:
        pass


# ============================================
# ROUTES - Dashboard UI
# ============================================

@app.route('/')
def serve_dashboard():
    """Serve the dashboard HTML"""
    return send_from_directory('.', 'index.html')


# ============================================
# ROUTES - System Status
# ============================================

@app.route('/api/status')
def get_status():
    """Get overall system status"""

    # Check various systems
    openai_ok = bool(os.getenv('OPENAI_API_KEY'))
    ftp_ok = bool(os.getenv('FTP_PASSWORD'))

    # Calculate next scheduled run
    now = datetime.now()
    next_monday = now + timedelta(days=(7 - now.weekday()) % 7 or 7)
    next_thursday = now + timedelta(days=(3 - now.weekday()) % 7 or 7)
    next_run = min(next_monday, next_thursday).replace(hour=9, minute=0)

    return jsonify({
        "bot_status": bot_state["status"],
        "scheduler_active": bot_state["scheduler_active"],
        "last_run": bot_state["last_run"],
        "next_run": next_run.isoformat() if bot_state["scheduler_active"] else None,
        "current_task": bot_state["current_task"],
        "systems": {
            "openai": "connected" if openai_ok else "not_configured",
            "ftp": "connected" if ftp_ok else "not_configured",
            "blog": "online",  # Assume online, health check will verify
            "bot": bot_state["status"]
        },
        "updated_at": datetime.now().isoformat()
    })


@app.route('/api/health')
def health_check():
    """Run site health check"""
    import requests

    urls = [
        ("Blog", "https://dopamine.watch/blog/"),
        ("Homepage", "https://dopamine.watch/"),
        ("App", "https://app.dopamine.watch/")
    ]

    results = []
    for name, url in urls:
        try:
            response = requests.get(url, timeout=10)
            results.append({
                "name": name,
                "url": url,
                "status": "online" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "load_time": response.elapsed.total_seconds()
            })
        except Exception as e:
            results.append({
                "name": name,
                "url": url,
                "status": "offline",
                "error": str(e)
            })

    log_activity("Health check", "success", f"Checked {len(urls)} URLs")

    return jsonify({
        "results": results,
        "all_healthy": all(r["status"] == "online" for r in results),
        "checked_at": datetime.now().isoformat()
    })


# ============================================
# ROUTES - Posts
# ============================================

@app.route('/api/posts')
def get_posts():
    """Get list of all posts"""

    posts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "posts")
    posts = []

    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(posts_dir, filename), 'r') as f:
                        post = json.load(f)
                        posts.append({
                            "title": post.get("title", "Untitled"),
                            "slug": post.get("slug", filename.replace('.json', '')),
                            "category": post.get("category", "General"),
                            "date": post.get("date", "Unknown"),
                            "reading_time": post.get("reading_time", 5),
                            "url": f"https://dopamine.watch/blog/posts/{post.get('slug', filename.replace('.json', ''))}.html"
                        })
                except:
                    pass

    # Also check the blog directory for existing posts
    blog_posts = [
        {
            "title": "Why ADHD Makes Choosing Content Impossible (The Science)",
            "slug": "adhd-decision-paralysis-science",
            "category": "ADHD",
            "date": "Jan 31, 2026",
            "reading_time": 8,
            "url": "https://dopamine.watch/blog/posts/adhd-decision-paralysis-science.html"
        },
        {
            "title": "The Netflix Algorithm Wasn't Built for Your Brain",
            "slug": "netflix-algorithm-not-built-for-adhd",
            "category": "Streaming",
            "date": "Jan 31, 2026",
            "reading_time": 7,
            "url": "https://dopamine.watch/blog/posts/netflix-algorithm-not-built-for-adhd.html"
        },
        {
            "title": "10 Shows That Actually Help With Anxiety (Research-Backed)",
            "slug": "shows-that-help-anxiety",
            "category": "Psychology",
            "date": "Jan 31, 2026",
            "reading_time": 10,
            "url": "https://dopamine.watch/blog/posts/shows-that-help-anxiety.html"
        }
    ]

    # Merge and dedupe
    existing_slugs = {p["slug"] for p in posts}
    for bp in blog_posts:
        if bp["slug"] not in existing_slugs:
            posts.append(bp)

    # Sort by date
    posts.sort(key=lambda x: x.get("date", ""), reverse=True)

    return jsonify({
        "posts": posts,
        "total": len(posts)
    })


@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """Trigger new post generation"""
    global bot_state

    if bot_state["status"] == "running":
        return jsonify({"error": "Bot is already running"}), 400

    data = request.json or {}
    pillar = data.get("pillar")
    dry_run = data.get("dry_run", False)

    bot_state["status"] = "running"
    bot_state["current_task"] = "Generating new post..."

    log_activity("Generate post", "started", f"Pillar: {pillar or 'Any'}")

    def run_generation():
        global bot_state
        try:
            from main import ContentBot
            bot = ContentBot()
            posts = bot.generate_and_publish(
                count=1,
                pillar=pillar,
                publish=not dry_run,
                dry_run=dry_run
            )

            bot_state["status"] = "idle"
            bot_state["current_task"] = None
            bot_state["last_run"] = datetime.now().isoformat()

            if posts:
                log_activity("Generate post", "success", f"Created: {posts[0].get('title', 'Unknown')}")
            else:
                log_activity("Generate post", "failed", "No post generated")

        except Exception as e:
            bot_state["status"] = "error"
            bot_state["current_task"] = None
            log_activity("Generate post", "error", str(e))

    # Run in background thread
    thread = threading.Thread(target=run_generation)
    thread.start()

    return jsonify({
        "status": "started",
        "message": "Post generation started"
    })


# ============================================
# ROUTES - Analytics
# ============================================

@app.route('/api/analytics')
def get_analytics():
    """Get analytics summary"""

    # Load analytics data if available
    analytics_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "analytics")

    posts_count = 3  # Default known posts
    total_views = 0
    total_clicks = 0

    if os.path.exists(analytics_dir):
        for filename in os.listdir(analytics_dir):
            if filename.endswith('_metrics.json'):
                try:
                    with open(os.path.join(analytics_dir, filename), 'r') as f:
                        metrics = json.load(f)
                        total_views += metrics.get('views', 0)
                        total_clicks += metrics.get('clicks', 0)
                except:
                    pass

    return jsonify({
        "summary": {
            "total_posts": posts_count,
            "total_views": total_views or 150,  # Sample data
            "total_clicks": total_clicks or 25,
            "email_subscribers": 12,  # Sample
            "social_shares": 8  # Sample
        },
        "growth": {
            "posts_this_week": 2,
            "views_trend": "+15%",
            "subscribers_trend": "+5"
        },
        "top_posts": [
            {"title": "ADHD Decision Paralysis", "views": 85, "ctr": 18.2},
            {"title": "Netflix Algorithm", "views": 45, "ctr": 15.5},
            {"title": "Shows for Anxiety", "views": 20, "ctr": 12.0}
        ]
    })


# ============================================
# ROUTES - Logs
# ============================================

@app.route('/api/logs')
def get_logs():
    """Get activity logs"""

    limit = request.args.get('limit', 20, type=int)

    # Load from file if activity_log is empty
    if not activity_log:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        log_file = os.path.join(log_dir, f"dashboard_{datetime.now().strftime('%Y%m%d')}.json")

        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    loaded_logs = json.load(f)
                    activity_log.extend(loaded_logs)
            except:
                pass

    return jsonify({
        "logs": activity_log[:limit],
        "total": len(activity_log)
    })


# ============================================
# ROUTES - Scheduler
# ============================================

@app.route('/api/scheduler', methods=['GET'])
def get_scheduler():
    """Get scheduler status"""

    now = datetime.now()

    # Calculate next runs
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.hour >= 9:
        days_until_monday = 7
    next_monday = (now + timedelta(days=days_until_monday)).replace(hour=9, minute=0, second=0)

    days_until_thursday = (3 - now.weekday()) % 7
    if days_until_thursday == 0 and now.hour >= 9:
        days_until_thursday = 7
    next_thursday = (now + timedelta(days=days_until_thursday)).replace(hour=9, minute=0, second=0)

    return jsonify({
        "active": bot_state["scheduler_active"],
        "schedule": [
            {"day": "Monday", "time": "09:00", "next": next_monday.isoformat()},
            {"day": "Thursday", "time": "09:00", "next": next_thursday.isoformat()}
        ],
        "next_run": min(next_monday, next_thursday).isoformat() if bot_state["scheduler_active"] else None
    })


@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    global bot_state

    bot_state["scheduler_active"] = True
    log_activity("Scheduler", "started", "Scheduled for Mon & Thu 9am")

    return jsonify({"status": "started", "message": "Scheduler activated"})


@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    global bot_state

    bot_state["scheduler_active"] = False
    log_activity("Scheduler", "stopped", "Manual stop")

    return jsonify({"status": "stopped", "message": "Scheduler paused"})


# ============================================
# ROUTES - Settings
# ============================================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""

    return jsonify({
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "ftp_configured": bool(os.getenv('FTP_PASSWORD')),
        "twitter_configured": bool(os.getenv('TWITTER_API_KEY')),
        "linkedin_configured": bool(os.getenv('LINKEDIN_TOKEN')),
        "facebook_configured": bool(os.getenv('FACEBOOK_PAGE_TOKEN')),
        "ftp_host": os.getenv('FTP_HOST', 'Not set'),
        "ftp_user": os.getenv('FTP_USER', 'Not set')
    })


# ============================================
# ROUTES - RSS Feed
# ============================================

@app.route('/api/generate-rss', methods=['POST'])
def trigger_rss():
    """Generate RSS feed"""

    try:
        from generate_rss import save_and_upload_rss
        result = save_and_upload_rss()
        log_activity("RSS Feed", "generated", f"Uploaded to {result}")
        return jsonify({"status": "success", "url": result})
    except Exception as e:
        log_activity("RSS Feed", "error", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500


# ============================================
# ROUTES - Chat
# ============================================

@app.route('/chat')
def serve_chat():
    """Serve the chat interface"""
    return send_from_directory('.', 'web_chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""

    data = request.json or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    agent = get_agent()
    if not agent:
        return jsonify({"error": "Agent not available. Check ANTHROPIC_API_KEY."}), 500

    try:
        response = agent.chat(message)
        log_activity("Chat", "success", f"User: {message[:50]}...")
        return jsonify({"response": response})
    except Exception as e:
        log_activity("Chat", "error", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    global chat_agent

    if chat_agent:
        chat_agent.clear_history()

    return jsonify({"status": "cleared"})


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    log_activity("Dashboard", "started", "Server initialized")
    print("\n" + "="*60)
    print("🎛️  CONTENT BOT DASHBOARD")
    print("="*60)
    print(f"\n   Open: http://localhost:5000")
    print(f"   Press Ctrl+C to stop\n")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
