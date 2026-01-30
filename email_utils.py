# email_utils.py
# --------------------------------------------------
# DOPAMINE.WATCH - EMAIL AUTOMATION WITH RESEND
# --------------------------------------------------

import os
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, List

# Initialize Resend
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    resend = None

# Get Resend API key
def get_resend_api_key():
    """Get Resend API key from secrets or environment"""
    return st.secrets.get("resend", {}).get("api_key", "") or os.environ.get("RESEND_API_KEY", "")

def init_resend():
    """Initialize Resend with API key"""
    if not RESEND_AVAILABLE:
        return False
    api_key = get_resend_api_key()
    if api_key:
        resend.api_key = api_key
        return True
    return False

# Email sender configuration
FROM_EMAIL = os.environ.get("FROM_EMAIL", "Mr.DP <mrdb@dopamine.watch>")
REPLY_TO = os.environ.get("REPLY_TO_EMAIL", "support@dopamine.watch")

# --------------------------------------------------
# EMAIL TEMPLATES
# --------------------------------------------------

def get_welcome_email_html(user_name: str) -> str:
    """Welcome email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Dopamine.watch!</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #181825;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #181825; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.1), rgba(0, 201, 167, 0.1)); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <h1 style="color: #8A56E2; font-size: 32px; margin: 0;">Welcome to Dopamine.watch!</h1>
                            </td>
                        </tr>

                        <!-- Greeting -->
                        <tr>
                            <td style="color: #ffffff; font-size: 18px; padding-bottom: 20px;">
                                Hey {user_name}! 👋
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding-bottom: 20px;">
                                I'm <strong style="color: #8A56E2;">Mr.DP</strong>, your personal dopamine curator! I'm so excited you're here.
                            </td>
                        </tr>

                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding-bottom: 20px;">
                                Dopamine.watch is the first streaming guide designed specifically for <strong>ADHD & neurodivergent brains</strong>. No more endless scrolling - just tell me how you feel, and I'll find the perfect content for you.
                            </td>
                        </tr>

                        <!-- Features Box -->
                        <tr>
                            <td style="padding: 20px; background: rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 20px;">
                                <p style="color: #00C9A7; font-weight: bold; margin: 0 0 15px 0;">Here's what you can do:</p>
                                <ul style="color: rgba(255,255,255,0.8); margin: 0; padding-left: 20px; line-height: 2;">
                                    <li>🎯 Select your mood and get personalized recommendations</li>
                                    <li>⚡ Use <strong>Quick Dope Hit</strong> for instant picks</li>
                                    <li>💬 Chat with me anytime for suggestions</li>
                                    <li>🏆 Earn Dopamine Points and climb the leaderboard</li>
                                    <li>🔥 Build your streak for bonus rewards</li>
                                </ul>
                            </td>
                        </tr>

                        <!-- CTA Button -->
                        <tr>
                            <td align="center" style="padding: 30px 0;">
                                <a href="https://app.dopamine.watch" style="display: inline-block; background: linear-gradient(135deg, #8A56E2, #00C9A7); color: white; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-weight: bold; font-size: 16px;">Start Watching</a>
                            </td>
                        </tr>

                        <!-- Sign off -->
                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; padding-top: 20px;">
                                Ready when you are,<br>
                                <strong style="color: #8A56E2;">Mr.DP</strong> 🧠
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px;">
                                <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin: 0;">
                                    Dopamine.watch - Feel Better, Watch Better<br>
                                    <a href="https://dopamine.watch/unsubscribe" style="color: rgba(255,255,255,0.4);">Unsubscribe</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_streak_reminder_html(user_name: str, streak_days: int) -> str:
    """Streak reminder email template"""
    emoji = "🔥" if streak_days > 7 else "⚡"
    urgency = "Don't break it now!" if streak_days > 3 else "Keep it going!"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Streak is Waiting!</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #181825;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #181825; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 215, 0, 0.1)); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding-bottom: 20px;">
                                <span style="font-size: 64px;">{emoji}</span>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <h1 style="color: #FFD700; font-size: 28px; margin: 0;">Your {streak_days}-Day Streak!</h1>
                            </td>
                        </tr>

                        <tr>
                            <td style="color: #ffffff; font-size: 18px; padding-bottom: 20px;">
                                Hey {user_name}!
                            </td>
                        </tr>

                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding-bottom: 20px;">
                                You're on a <strong style="color: #FFD700;">{streak_days}-day streak</strong>! {urgency}
                            </td>
                        </tr>

                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding-bottom: 20px;">
                                Log in today to keep your streak alive and earn bonus Dopamine Points!
                            </td>
                        </tr>

                        <!-- CTA Button -->
                        <tr>
                            <td align="center" style="padding: 30px 0;">
                                <a href="https://app.dopamine.watch" style="display: inline-block; background: linear-gradient(135deg, #FFD700, #FF6B6B); color: #181825; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-weight: bold; font-size: 16px;">Keep My Streak!</a>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
                                <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin: 0;">
                                    Dopamine.watch - Feel Better, Watch Better<br>
                                    <a href="https://dopamine.watch/unsubscribe" style="color: rgba(255,255,255,0.4);">Unsubscribe</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_milestone_email_html(user_name: str, milestone: str, reward: str) -> str:
    """Milestone celebration email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Congratulations! 🎉</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #181825;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #181825; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.2), rgba(236, 72, 153, 0.2)); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding-bottom: 20px;">
                                <span style="font-size: 64px;">🎉</span>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <h1 style="color: #ec4899; font-size: 28px; margin: 0;">Milestone Unlocked!</h1>
                            </td>
                        </tr>

                        <tr>
                            <td style="color: #ffffff; font-size: 18px; padding-bottom: 20px;">
                                Hey {user_name}! 🌟
                            </td>
                        </tr>

                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding-bottom: 20px;">
                                You just hit an amazing milestone: <strong style="color: #ec4899;">{milestone}</strong>!
                            </td>
                        </tr>

                        <!-- Reward Box -->
                        <tr>
                            <td style="padding: 20px; background: rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 20px; text-align: center;">
                                <p style="color: #00C9A7; font-weight: bold; margin: 0 0 10px 0;">Your Reward:</p>
                                <p style="color: #FFD700; font-size: 24px; font-weight: bold; margin: 0;">{reward}</p>
                            </td>
                        </tr>

                        <tr>
                            <td style="color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6; padding: 20px 0;">
                                Keep up the amazing work! Every milestone brings you closer to becoming a Dopamine Master.
                            </td>
                        </tr>

                        <!-- CTA Button -->
                        <tr>
                            <td align="center" style="padding: 30px 0;">
                                <a href="https://app.dopamine.watch" style="display: inline-block; background: linear-gradient(135deg, #8A56E2, #ec4899); color: white; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-weight: bold; font-size: 16px;">Claim My Reward</a>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
                                <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin: 0;">
                                    Dopamine.watch - Feel Better, Watch Better<br>
                                    <a href="https://dopamine.watch/unsubscribe" style="color: rgba(255,255,255,0.4);">Unsubscribe</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_daily_digest_html(user_name: str, recommendations: List[Dict], mood_summary: Dict) -> str:
    """Daily digest email template"""
    # Build recommendations HTML
    recs_html = ""
    for rec in recommendations[:3]:
        recs_html += f"""
        <div style="padding: 15px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 10px;">
            <strong style="color: #ffffff;">{rec.get('title', 'Unknown')}</strong>
            <p style="color: rgba(255,255,255,0.6); margin: 5px 0 0 0; font-size: 14px;">{rec.get('reason', 'Perfect for your mood')}</p>
        </div>
        """

    top_mood = mood_summary.get("top_mood", "Bored")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Daily Dopamine Digest</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #181825;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #181825; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.1), rgba(0, 201, 167, 0.1)); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <h1 style="color: #8A56E2; font-size: 28px; margin: 0;">Your Daily Digest 📬</h1>
                                <p style="color: rgba(255,255,255,0.6); margin: 10px 0 0 0;">{datetime.now().strftime('%B %d, %Y')}</p>
                            </td>
                        </tr>

                        <tr>
                            <td style="color: #ffffff; font-size: 18px; padding-bottom: 20px;">
                                Good morning, {user_name}! ☀️
                            </td>
                        </tr>

                        <!-- Mood Summary -->
                        <tr>
                            <td style="padding: 20px; background: rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 20px;">
                                <p style="color: #00C9A7; font-weight: bold; margin: 0 0 10px 0;">Your Mood Yesterday:</p>
                                <p style="color: rgba(255,255,255,0.8); margin: 0;">You felt mostly <strong style="color: #8A56E2;">{top_mood}</strong> and we hope today brings even better vibes!</p>
                            </td>
                        </tr>

                        <!-- Recommendations -->
                        <tr>
                            <td style="padding-top: 20px;">
                                <p style="color: #FFD700; font-weight: bold; margin: 0 0 15px 0;">Today's Picks for You:</p>
                                {recs_html if recs_html else '<p style="color: rgba(255,255,255,0.6);">Log in to get personalized picks!</p>'}
                            </td>
                        </tr>

                        <!-- CTA Button -->
                        <tr>
                            <td align="center" style="padding: 30px 0;">
                                <a href="https://app.dopamine.watch" style="display: inline-block; background: linear-gradient(135deg, #8A56E2, #00C9A7); color: white; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-weight: bold; font-size: 16px;">See All Recommendations</a>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
                                <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin: 0;">
                                    Dopamine.watch - Feel Better, Watch Better<br>
                                    <a href="https://dopamine.watch/unsubscribe" style="color: rgba(255,255,255,0.4);">Unsubscribe from digest</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

# --------------------------------------------------
# EMAIL SENDING FUNCTIONS
# --------------------------------------------------

def send_email(to_email: str, subject: str, html_content: str) -> Dict:
    """Send an email via Resend"""
    if not RESEND_AVAILABLE or not init_resend():
        return {"success": False, "error": "Resend not configured"}

    try:
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "reply_to": REPLY_TO
        })
        return {"success": True, "id": response.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_welcome_email(to_email: str, user_name: str) -> Dict:
    """Send welcome email to new user"""
    html = get_welcome_email_html(user_name)
    return send_email(
        to_email=to_email,
        subject="Welcome to Dopamine.watch! 🧠",
        html_content=html
    )

def send_streak_reminder(to_email: str, user_name: str, streak_days: int) -> Dict:
    """Send streak reminder email"""
    html = get_streak_reminder_html(user_name, streak_days)
    return send_email(
        to_email=to_email,
        subject=f"🔥 Your {streak_days}-Day Streak is Waiting!",
        html_content=html
    )

def send_milestone_email(to_email: str, user_name: str, milestone: str, reward: str) -> Dict:
    """Send milestone celebration email"""
    html = get_milestone_email_html(user_name, milestone, reward)
    return send_email(
        to_email=to_email,
        subject=f"🎉 Milestone Unlocked: {milestone}!",
        html_content=html
    )

def send_daily_digest(to_email: str, user_name: str, recommendations: List[Dict], mood_summary: Dict) -> Dict:
    """Send daily digest email"""
    html = get_daily_digest_html(user_name, recommendations, mood_summary)
    return send_email(
        to_email=to_email,
        subject="📬 Your Daily Dopamine Digest",
        html_content=html
    )

# --------------------------------------------------
# BATCH EMAIL FUNCTIONS (for scheduled tasks)
# --------------------------------------------------

def get_users_for_streak_reminder(supabase_client, hours_inactive: int = 20) -> List[Dict]:
    """Get users who haven't logged in today but have an active streak"""
    if not supabase_client:
        return []

    try:
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=hours_inactive)).isoformat()

        # Get users with streaks who haven't been active recently
        users = supabase_client.table("profiles")\
            .select("id, email, name, streak_days, last_visit")\
            .gt("streak_days", 0)\
            .lt("last_visit", cutoff)\
            .execute()

        return users.data if users.data else []
    except Exception as e:
        print(f"Error getting streak users: {e}")
        return []

def get_users_for_daily_digest(supabase_client) -> List[Dict]:
    """Get users who opted in for daily digest"""
    if not supabase_client:
        return []

    try:
        users = supabase_client.table("profiles")\
            .select("id, email, name")\
            .eq("daily_digest", True)\
            .execute()

        return users.data if users.data else []
    except Exception as e:
        print(f"Error getting digest users: {e}")
        return []

def send_batch_streak_reminders(supabase_client) -> Dict:
    """Send streak reminders to all eligible users"""
    users = get_users_for_streak_reminder(supabase_client)
    results = {"sent": 0, "failed": 0, "errors": []}

    for user in users:
        result = send_streak_reminder(
            to_email=user.get("email"),
            user_name=user.get("name", "Friend"),
            streak_days=user.get("streak_days", 1)
        )
        if result.get("success"):
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(result.get("error"))

    return results

# --------------------------------------------------
# MILESTONE DEFINITIONS
# --------------------------------------------------

MILESTONES = {
    "first_mood": {"title": "First Mood Log", "reward": "+50 DP"},
    "streak_3": {"title": "3-Day Streak", "reward": "+100 DP"},
    "streak_7": {"title": "7-Day Streak", "reward": "+250 DP"},
    "streak_30": {"title": "30-Day Streak", "reward": "+1000 DP"},
    "points_100": {"title": "100 Dopamine Points", "reward": "Bronze Badge"},
    "points_500": {"title": "500 Dopamine Points", "reward": "Silver Badge"},
    "points_1000": {"title": "1000 Dopamine Points", "reward": "Gold Badge"},
    "mr_dp_10": {"title": "10 Mr.DP Chats", "reward": "+100 DP"},
    "queue_10": {"title": "10 Items in Queue", "reward": "+75 DP"},
    "referral_1": {"title": "First Referral", "reward": "+200 DP + 1 Week Premium"}
}

def check_and_send_milestone_email(supabase_client, user_id: str, milestone_key: str):
    """Check if milestone email should be sent and send it"""
    if milestone_key not in MILESTONES:
        return

    milestone = MILESTONES[milestone_key]

    try:
        # Get user info
        user = supabase_client.table("profiles").select("email, name, achieved_milestones").eq("id", user_id).single().execute()
        if not user.data:
            return

        achieved = user.data.get("achieved_milestones", []) or []
        if milestone_key in achieved:
            return  # Already achieved

        # Send email
        send_milestone_email(
            to_email=user.data.get("email"),
            user_name=user.data.get("name", "Friend"),
            milestone=milestone["title"],
            reward=milestone["reward"]
        )

        # Update achieved milestones
        achieved.append(milestone_key)
        supabase_client.table("profiles").update({"achieved_milestones": achieved}).eq("id", user_id).execute()

    except Exception as e:
        print(f"Milestone email error: {e}")
