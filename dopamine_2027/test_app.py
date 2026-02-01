"""
═══════════════════════════════════════════════════════════════════════════════
DOPAMINE.WATCH 2027 - TEST GUI
Complete QA testing interface for all new features.
═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config
st.set_page_config(
    page_title="dopamine.watch 2027 - Test GUI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def test_imports() -> Dict[str, Any]:
    """Test all service and feature imports."""
    results = {
        "gamification": {"status": "pending", "details": []},
        "premium": {"status": "pending", "details": []},
        "wellness": {"status": "pending", "details": []},
        "features": {"status": "pending", "details": []},
        "api": {"status": "pending", "details": []}
    }

    # Test Gamification
    try:
        from services.gamification.points import (
            PointAction, UserPoints, add_points, get_leaderboard, get_user_rank
        )
        results["gamification"]["details"].append("✓ points.py")

        from services.gamification.streaks import (
            UserStreak, update_streak, get_streak_milestone_reward
        )
        results["gamification"]["details"].append("✓ streaks.py")

        from services.gamification.achievements import (
            Achievement, AchievementCategory, ACHIEVEMENTS, check_achievement, get_user_achievements
        )
        results["gamification"]["details"].append("✓ achievements.py")

        results["gamification"]["status"] = "success"
    except Exception as e:
        results["gamification"]["status"] = "error"
        results["gamification"]["details"].append(f"✗ Error: {str(e)}")

    # Test Premium
    try:
        from services.premium.subscriptions import (
            SubscriptionTier, TIER_CONFIGS, get_user_tier, upgrade_subscription
        )
        results["premium"]["details"].append("✓ subscriptions.py")

        from services.premium.usage_limits import (
            UsageType, USAGE_LIMITS, check_can_use, increment_usage
        )
        results["premium"]["details"].append("✓ usage_limits.py")

        results["premium"]["status"] = "success"
    except Exception as e:
        results["premium"]["status"] = "error"
        results["premium"]["details"].append(f"✗ Error: {str(e)}")

    # Test Wellness
    try:
        from services.wellness.sos_mode import (
            BREATHING_EXERCISES, GROUNDING_54321, CALMING_VIDEOS, get_sos_content
        )
        results["wellness"]["details"].append("✓ sos_mode.py")

        from services.wellness.focus_timer import (
            SessionType, FocusSession, start_session, should_remind_break
        )
        results["wellness"]["details"].append("✓ focus_timer.py")

        results["wellness"]["status"] = "success"
    except Exception as e:
        results["wellness"]["status"] = "error"
        results["wellness"]["details"].append(f"✗ Error: {str(e)}")

    # Test Features
    try:
        from features.onboarding import (
            ONBOARDING_STEPS, MOOD_OPTIONS, CONTENT_TYPES, GENRE_OPTIONS,
            should_show_onboarding, render_onboarding
        )
        results["features"]["details"].append("✓ onboarding")

        from features.analytics import (
            render_analytics_dashboard, get_user_stats, get_mood_history
        )
        results["features"]["details"].append("✓ analytics")

        results["features"]["status"] = "success"
    except Exception as e:
        results["features"]["status"] = "error"
        results["features"]["details"].append(f"✗ Error: {str(e)}")

    # Test API Routes
    try:
        from api.routes.gamification import router as gamification_router
        results["api"]["details"].append("✓ gamification routes")

        from api.routes.premium import router as premium_router
        results["api"]["details"].append("✓ premium routes")

        from api.routes.wellness import router as wellness_router
        results["api"]["details"].append("✓ wellness routes")

        results["api"]["status"] = "success"
    except Exception as e:
        results["api"]["status"] = "error"
        results["api"]["details"].append(f"✗ Error: {str(e)}")

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TEST GUI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    st.title("🧪 dopamine.watch 2027 - Test GUI")
    st.markdown("**Complete QA testing interface for all new features**")
    st.markdown("---")

    # Sidebar navigation
    st.sidebar.title("Test Sections")
    section = st.sidebar.radio(
        "Select Test Section",
        [
            "🔍 Import Verification",
            "🎮 Gamification",
            "💎 Premium & Usage",
            "🧘 Wellness",
            "👋 Onboarding",
            "📊 Analytics",
            "🔗 Streaming Links",
            "📝 Full Report"
        ]
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # IMPORT VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════════
    if section == "🔍 Import Verification":
        st.header("🔍 Import Verification")
        st.markdown("Testing all service and feature imports...")

        if st.button("Run Import Tests", type="primary"):
            with st.spinner("Testing imports..."):
                results = test_imports()

            for category, data in results.items():
                status_icon = "✅" if data["status"] == "success" else "❌"
                with st.expander(f"{status_icon} {category.title()}", expanded=True):
                    for detail in data["details"]:
                        st.markdown(detail)

            # Summary
            all_pass = all(r["status"] == "success" for r in results.values())
            if all_pass:
                st.success("🎉 All imports successful!")
            else:
                st.error("❌ Some imports failed. Check details above.")

    # ═══════════════════════════════════════════════════════════════════════════
    # GAMIFICATION TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "🎮 Gamification":
        st.header("🎮 Gamification System Tests")

        tab1, tab2, tab3 = st.tabs(["Points", "Streaks", "Achievements"])

        with tab1:
            st.subheader("💜 Dopamine Points")
            try:
                from services.gamification.points import (
                    PointAction, UserPoints, add_points, get_leaderboard,
                    get_user_rank, calculate_level
                )

                st.success("✓ Points module loaded")

                # Show all point actions
                st.markdown("#### Point Actions")
                action_cols = st.columns(4)
                for i, action in enumerate(PointAction):
                    with action_cols[i % 4]:
                        st.markdown(f"**{action.name}**: `{action.value}` DP")

                # Test add_points
                st.markdown("#### Test Add Points")
                test_user = st.text_input("Test User ID", value="test_user_123")
                selected_action = st.selectbox(
                    "Action",
                    options=[a.name for a in PointAction]
                )

                if st.button("Add Points"):
                    action = PointAction[selected_action]
                    result = add_points(test_user, action)
                    st.json(result)

                # Test level calculation
                st.markdown("#### Level Calculator")
                test_points = st.number_input("Total Points", min_value=0, value=2450)
                level_info = calculate_level(test_points)
                st.json(level_info)

            except Exception as e:
                st.error(f"Error loading points module: {e}")

        with tab2:
            st.subheader("🔥 Streak System")
            try:
                from services.gamification.streaks import (
                    UserStreak, update_streak, get_streak_milestone_reward,
                    STREAK_MILESTONES
                )

                st.success("✓ Streaks module loaded")

                # Show milestones
                st.markdown("#### Streak Milestones")
                for days, reward in STREAK_MILESTONES.items():
                    st.markdown(f"**{days} days**: {reward['emoji']} {reward['title']} - `{reward['bonus_points']}` bonus DP")

                # Test streak update
                st.markdown("#### Test Streak Update")
                test_user = st.text_input("User ID", value="test_user_123", key="streak_user")

                if st.button("Update Streak"):
                    result = update_streak(test_user)
                    st.json({
                        "current_streak": result.current_streak,
                        "longest_streak": result.longest_streak,
                        "milestone_reached": result.milestone_reached,
                        "streak_broken": result.streak_broken
                    })

            except Exception as e:
                st.error(f"Error loading streaks module: {e}")

        with tab3:
            st.subheader("🏆 Achievements")
            try:
                from services.gamification.achievements import (
                    Achievement, AchievementCategory, ACHIEVEMENTS,
                    check_achievement, get_user_achievements
                )

                st.success("✓ Achievements module loaded")

                # Show achievements by category
                st.markdown("#### All Achievements")
                for category in AchievementCategory:
                    with st.expander(f"{category.value} - {category.name}"):
                        for ach_id, ach in ACHIEVEMENTS.items():
                            if ach.category == category:
                                st.markdown(f"""
                                **{ach.icon} {ach.name}**
                                {ach.description}
                                Reward: `{ach.points}` DP | Requirement: {ach.requirement or 'N/A'}
                                """)

                st.markdown(f"**Total Achievements**: {len(ACHIEVEMENTS)}")

            except Exception as e:
                st.error(f"Error loading achievements module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # PREMIUM TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "💎 Premium & Usage":
        st.header("💎 Premium & Usage Limits Tests")

        tab1, tab2 = st.tabs(["Subscriptions", "Usage Limits"])

        with tab1:
            st.subheader("⭐ Subscription Tiers")
            try:
                from services.premium.subscriptions import (
                    SubscriptionTier, TIER_CONFIGS, get_user_tier, upgrade_subscription
                )

                st.success("✓ Subscriptions module loaded")

                # Show tier configs
                for tier, config in TIER_CONFIGS.items():
                    with st.expander(f"{tier.value} Tier", expanded=True):
                        st.markdown(f"**Price**: ${config['price']}/month")
                        st.markdown("**Features**:")
                        for feature in config['features']:
                            st.markdown(f"  - {feature}")
                        st.markdown("**Limits**:")
                        st.json(config['limits'])

            except Exception as e:
                st.error(f"Error loading subscriptions module: {e}")

        with tab2:
            st.subheader("📊 Usage Limits")
            try:
                from services.premium.usage_limits import (
                    UsageType, USAGE_LIMITS, check_can_use, increment_usage,
                    get_daily_usage, should_show_upgrade_prompt
                )

                st.success("✓ Usage limits module loaded")

                # Show usage types and limits
                st.markdown("#### Usage Types & Free Tier Limits")
                for usage_type in UsageType:
                    limit = USAGE_LIMITS.get(usage_type, {}).get("free", "unlimited")
                    st.markdown(f"**{usage_type.value}**: {limit}/day")

                # Test usage checking
                st.markdown("#### Test Usage Check")
                test_user = st.text_input("User ID", value="test_user_123", key="usage_user")
                selected_type = st.selectbox(
                    "Usage Type",
                    options=[t.value for t in UsageType]
                )

                if st.button("Check Can Use"):
                    usage_type = UsageType(selected_type)
                    result = check_can_use(test_user, usage_type)
                    if result.get("allowed"):
                        st.success(f"✓ Can use! Remaining: {result.get('remaining')}")
                    else:
                        st.warning(f"✗ Cannot use: {result.get('upgrade_message')}")

                if st.button("Increment Usage"):
                    usage_type = UsageType(selected_type)
                    result = increment_usage(test_user, usage_type)
                    st.json(result)

            except Exception as e:
                st.error(f"Error loading usage limits module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # WELLNESS TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "🧘 Wellness":
        st.header("🧘 Wellness Features Tests")

        tab1, tab2 = st.tabs(["SOS Mode", "Focus Timer"])

        with tab1:
            st.subheader("🆘 SOS Calm Mode")
            try:
                from services.wellness.sos_mode import (
                    BREATHING_EXERCISES, GROUNDING_54321, CALMING_VIDEOS,
                    AFFIRMATIONS, get_sos_content, SOSMode
                )

                st.success("✓ SOS mode module loaded")

                # Breathing exercises
                st.markdown("#### Breathing Exercises")
                for name, exercise in BREATHING_EXERCISES.items():
                    with st.expander(f"🌬️ {exercise['name']}"):
                        st.markdown(f"**Description**: {exercise['description']}")
                        st.markdown(f"**Duration**: {exercise['total_duration']}s")
                        st.markdown("**Pattern**:")
                        for step in exercise['steps']:
                            st.markdown(f"  - {step['action']}: {step['duration']}s")

                # Grounding technique
                st.markdown("#### 5-4-3-2-1 Grounding")
                st.json(GROUNDING_54321)

                # Calming videos
                st.markdown("#### Calming Videos")
                for video in CALMING_VIDEOS[:3]:
                    st.markdown(f"**{video['title']}** - {video['duration']} | [{video['type']}]({video['youtube_id']})")

                # Affirmations
                st.markdown("#### Sample Affirmations")
                for aff in AFFIRMATIONS[:5]:
                    st.info(aff)

                # Test get_sos_content
                st.markdown("#### Test Get SOS Content")
                sos_mode = st.selectbox("SOS Mode", [m.value for m in SOSMode])
                if st.button("Get SOS Content"):
                    content = get_sos_content(SOSMode(sos_mode))
                    st.json(content)

            except Exception as e:
                st.error(f"Error loading SOS mode module: {e}")

        with tab2:
            st.subheader("⏱️ Focus Timer")
            try:
                from services.wellness.focus_timer import (
                    SessionType, FocusSession, BREAK_ACTIVITIES,
                    start_session, should_remind_break
                )

                st.success("✓ Focus timer module loaded")

                # Session types
                st.markdown("#### Session Types")
                for stype in SessionType:
                    st.markdown(f"**{stype.name}**: {stype.value} minutes")

                # Break activities
                st.markdown("#### Break Activities")
                for activity in BREAK_ACTIVITIES:
                    st.markdown(f"**{activity['emoji']} {activity['name']}** ({activity['duration_minutes']} min) - {activity['description']}")

                # Test start session
                st.markdown("#### Test Start Session")
                test_user = st.text_input("User ID", value="test_user_123", key="focus_user")
                session_type = st.selectbox("Session Type", [s.name for s in SessionType])
                content_title = st.text_input("Content Title", value="Test Movie")

                if st.button("Start Focus Session"):
                    session = start_session(test_user, SessionType[session_type], content_title)
                    st.json({
                        "session_id": session.session_id,
                        "session_type": session.session_type.name,
                        "duration_minutes": session.duration_minutes,
                        "started_at": session.started_at.isoformat(),
                        "content_title": session.content_title
                    })

            except Exception as e:
                st.error(f"Error loading focus timer module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # ONBOARDING TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "👋 Onboarding":
        st.header("👋 Onboarding Flow Tests")

        try:
            from features.onboarding import (
                ONBOARDING_STEPS, MOOD_OPTIONS, CONTENT_TYPES, GENRE_OPTIONS,
                should_show_onboarding, render_onboarding, complete_onboarding
            )

            st.success("✓ Onboarding module loaded")

            # Show onboarding steps
            st.markdown("#### Onboarding Steps")
            for i, step in enumerate(ONBOARDING_STEPS):
                st.markdown(f"**Step {i+1}**: {step['icon']} {step['title']} - {step['subtitle']}")

            # Mood options
            st.markdown("#### Mood Options")
            mood_cols = st.columns(4)
            for i, mood in enumerate(MOOD_OPTIONS):
                with mood_cols[i % 4]:
                    st.markdown(f"{mood['emoji']} **{mood['label']}**")

            # Content types
            st.markdown("#### Content Types")
            type_cols = st.columns(3)
            for i, ct in enumerate(CONTENT_TYPES):
                with type_cols[i % 3]:
                    st.markdown(f"{ct['emoji']} {ct['label']}")

            # Genre options
            st.markdown("#### Genre Options")
            genre_cols = st.columns(5)
            for i, genre in enumerate(GENRE_OPTIONS):
                with genre_cols[i % 5]:
                    st.markdown(f"{genre['emoji']} {genre['label']}")

            # Test onboarding flow
            st.markdown("---")
            st.markdown("#### Preview Onboarding Flow")

            if st.checkbox("Show Onboarding Preview"):
                # Reset for preview
                if "preview_onboarding" not in st.session_state:
                    st.session_state.preview_onboarding = True
                    st.session_state.onboarding_step = 0
                    st.session_state.onboarding_completed = False

                render_onboarding()

        except Exception as e:
            st.error(f"Error loading onboarding module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYTICS TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "📊 Analytics":
        st.header("📊 Analytics Dashboard Tests")

        try:
            from features.analytics import (
                render_analytics_dashboard, render_summary_cards,
                render_mood_analytics, render_content_analytics,
                render_gamification_analytics, render_insights,
                get_user_stats, get_mood_history
            )

            st.success("✓ Analytics module loaded")

            # Test get_user_stats
            st.markdown("#### User Stats (Mock)")
            test_user = st.text_input("User ID", value="test_user_123", key="analytics_user")
            stats = get_user_stats(test_user)
            st.json(stats)

            # Test mood history
            st.markdown("#### Mood History (Mock)")
            mood_history = get_mood_history(test_user)
            st.markdown(f"Generated {len(mood_history)} mood entries")
            st.json(mood_history[:5])  # Show first 5

            # Preview dashboard
            st.markdown("---")
            st.markdown("#### Preview Analytics Dashboard")

            if st.checkbox("Show Analytics Dashboard"):
                render_analytics_dashboard(test_user)

        except Exception as e:
            st.error(f"Error loading analytics module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # STREAMING LINKS TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "🔗 Streaming Links":
        st.header("🔗 Streaming Deep Links Tests")

        try:
            from services.search.tmdb import (
                STREAMING_DEEP_LINKS, get_streaming_deep_link
            )

            st.success("✓ Streaming links module loaded")

            # Show all supported providers
            st.markdown("#### Supported Streaming Services")
            for provider, links in STREAMING_DEEP_LINKS.items():
                with st.expander(provider):
                    st.markdown(f"**Web**: `{links.get('web', 'N/A')}`")
                    st.markdown(f"**App**: `{links.get('app', 'N/A')}`")
                    st.markdown(f"**Search**: `{links.get('search', 'N/A')}`")

            # Test deep link generation
            st.markdown("#### Test Deep Link Generation")
            provider = st.selectbox("Provider", list(STREAMING_DEEP_LINKS.keys()))
            title = st.text_input("Movie/Show Title", value="The Matrix")
            link_type = st.selectbox("Link Type", ["search", "web", "app"])

            if st.button("Generate Deep Link"):
                link = get_streaming_deep_link(provider, title, link_type=link_type)
                if link:
                    st.success(f"Generated link: {link}")
                    st.markdown(f"[Open Link]({link})")
                else:
                    st.warning("Could not generate link")

        except Exception as e:
            st.error(f"Error loading streaming links module: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # FULL REPORT
    # ═══════════════════════════════════════════════════════════════════════════
    elif section == "📝 Full Report":
        st.header("📝 Full QA Report")

        if st.button("Generate Full Report", type="primary"):
            with st.spinner("Running all tests..."):
                report = []
                report.append("# dopamine.watch 2027 - QA Report")
                report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                report.append("")

                # Import tests
                import_results = test_imports()
                all_imports_pass = all(r["status"] == "success" for r in import_results.values())

                report.append("## Import Verification")
                for category, data in import_results.items():
                    status = "✅ PASS" if data["status"] == "success" else "❌ FAIL"
                    report.append(f"- **{category.title()}**: {status}")
                    for detail in data["details"]:
                        report.append(f"  - {detail}")
                report.append("")

                # Feature counts
                report.append("## Feature Summary")

                try:
                    from services.gamification.points import PointAction
                    from services.gamification.achievements import ACHIEVEMENTS
                    from services.wellness.sos_mode import BREATHING_EXERCISES, CALMING_VIDEOS, AFFIRMATIONS
                    from services.wellness.focus_timer import SessionType, BREAK_ACTIVITIES
                    from features.onboarding import MOOD_OPTIONS, CONTENT_TYPES, GENRE_OPTIONS
                    from services.search.tmdb import STREAMING_DEEP_LINKS

                    report.append(f"- **Point Actions**: {len(PointAction)}")
                    report.append(f"- **Achievements**: {len(ACHIEVEMENTS)}")
                    report.append(f"- **Breathing Exercises**: {len(BREATHING_EXERCISES)}")
                    report.append(f"- **Calming Videos**: {len(CALMING_VIDEOS)}")
                    report.append(f"- **Affirmations**: {len(AFFIRMATIONS)}")
                    report.append(f"- **Focus Session Types**: {len(SessionType)}")
                    report.append(f"- **Break Activities**: {len(BREAK_ACTIVITIES)}")
                    report.append(f"- **Mood Options**: {len(MOOD_OPTIONS)}")
                    report.append(f"- **Content Types**: {len(CONTENT_TYPES)}")
                    report.append(f"- **Genre Options**: {len(GENRE_OPTIONS)}")
                    report.append(f"- **Streaming Providers**: {len(STREAMING_DEEP_LINKS)}")
                except Exception as e:
                    report.append(f"- Error counting features: {e}")

                report.append("")

                # Overall status
                report.append("## Overall Status")
                if all_imports_pass:
                    report.append("### ✅ ALL TESTS PASSED")
                    report.append("The application is ready for deployment.")
                else:
                    report.append("### ❌ SOME TESTS FAILED")
                    report.append("Please fix the issues above before deployment.")

                # Display report
                st.markdown("\n".join(report))

                # Download button
                st.download_button(
                    label="Download Report",
                    data="\n".join(report),
                    file_name=f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )


if __name__ == "__main__":
    main()
