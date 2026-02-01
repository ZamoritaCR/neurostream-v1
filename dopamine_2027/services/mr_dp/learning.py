"""
═══════════════════════════════════════════════════════════════════════════════
USER LEARNING SERVICE
Learns from user behavior to improve recommendations and Mr.DP responses.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of user events to track."""
    # Content interactions
    CONTENT_VIEW = "content_view"
    CONTENT_COMPLETE = "content_complete"
    CONTENT_SKIP = "content_skip"
    CONTENT_SAVE = "content_save"
    CONTENT_SHARE = "content_share"
    CONTENT_RATE = "content_rate"

    # Search behavior
    SEARCH_QUERY = "search_query"
    SEARCH_CLICK = "search_click"

    # Mood tracking
    MOOD_SELECT = "mood_select"
    MOOD_TRANSITION = "mood_transition"

    # Session behavior
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # Mr.DP interactions
    MRDP_CHAT = "mrdp_chat"
    MRDP_SUGGESTION_ACCEPT = "mrdp_suggestion_accept"
    MRDP_SUGGESTION_REJECT = "mrdp_suggestion_reject"


@dataclass
class UserEvent:
    """A tracked user event."""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentInteraction:
    """Aggregated interaction data for a piece of content."""
    content_id: str
    content_type: str  # movie, tv, music, etc.
    title: str
    view_count: int = 0
    completion_count: int = 0
    skip_count: int = 0
    total_watch_time: float = 0  # minutes
    ratings: List[int] = field(default_factory=list)
    last_interacted: datetime = field(default_factory=datetime.utcnow)
    genres: List[str] = field(default_factory=list)
    mood_when_watched: List[str] = field(default_factory=list)


@dataclass
class UserPattern:
    """Detected patterns in user behavior."""
    pattern_type: str
    confidence: float  # 0-1
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserProfile:
    """Learned user profile and preferences."""
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Content preferences
    favorite_genres: Dict[str, float] = field(default_factory=dict)  # genre -> score
    favorite_content_types: Dict[str, float] = field(default_factory=dict)  # type -> score
    preferred_duration: Tuple[int, int] = (30, 120)  # min, max minutes
    content_interactions: Dict[str, ContentInteraction] = field(default_factory=dict)

    # Mood patterns
    common_moods: Dict[str, float] = field(default_factory=dict)  # mood -> frequency
    mood_to_content: Dict[str, Dict[str, float]] = field(default_factory=dict)  # mood -> {genre: score}
    mood_transitions: Dict[str, Dict[str, int]] = field(default_factory=dict)  # from_mood -> {to_mood: count}

    # Time patterns
    active_hours: Dict[int, float] = field(default_factory=dict)  # hour -> activity score
    active_days: Dict[int, float] = field(default_factory=dict)  # day_of_week -> activity score
    avg_session_duration: float = 30  # minutes

    # ADHD-specific patterns
    attention_span_estimate: float = 45  # minutes
    preferred_content_length: str = "medium"  # short, medium, long
    needs_variety: bool = True
    hyperfocus_content: List[str] = field(default_factory=list)  # content_ids user binges

    # Detected patterns
    patterns: List[UserPattern] = field(default_factory=list)

    # Event history (last 1000 events)
    events: List[UserEvent] = field(default_factory=list)


class UserLearningService:
    """
    Learns from user behavior to personalize recommendations.

    Features:
    - Content preference tracking
    - Mood pattern analysis
    - Time-based behavior patterns
    - ADHD-specific optimizations
    - Mr.DP personality adaptation
    """

    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}
        self._max_events = 1000

        # Learning parameters
        self._decay_rate = 0.95  # Score decay for older interactions
        self._min_interactions_for_pattern = 5

    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT TRACKING
    # ═══════════════════════════════════════════════════════════════════════════

    async def track_event(
        self,
        user_id: str,
        event_type: EventType,
        data: Dict[str, Any] = None
    ) -> None:
        """
        Track a user event for learning.

        Args:
            user_id: User's ID
            event_type: Type of event
            data: Event-specific data
        """
        profile = self._get_or_create_profile(user_id)

        event = UserEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data or {}
        )

        profile.events.append(event)

        # Trim old events
        if len(profile.events) > self._max_events:
            profile.events = profile.events[-self._max_events:]

        # Process event
        await self._process_event(profile, event)

        profile.updated_at = datetime.utcnow()

    async def _process_event(self, profile: UserProfile, event: UserEvent) -> None:
        """Process an event and update learned data."""
        if event.event_type == EventType.CONTENT_VIEW:
            await self._process_content_view(profile, event)
        elif event.event_type == EventType.CONTENT_COMPLETE:
            await self._process_content_complete(profile, event)
        elif event.event_type == EventType.CONTENT_SKIP:
            await self._process_content_skip(profile, event)
        elif event.event_type == EventType.CONTENT_RATE:
            await self._process_content_rate(profile, event)
        elif event.event_type == EventType.MOOD_SELECT:
            await self._process_mood_select(profile, event)
        elif event.event_type == EventType.MOOD_TRANSITION:
            await self._process_mood_transition(profile, event)
        elif event.event_type == EventType.SESSION_START:
            await self._process_session_start(profile, event)
        elif event.event_type == EventType.SESSION_END:
            await self._process_session_end(profile, event)
        elif event.event_type == EventType.MRDP_SUGGESTION_ACCEPT:
            await self._process_suggestion_response(profile, event, accepted=True)
        elif event.event_type == EventType.MRDP_SUGGESTION_REJECT:
            await self._process_suggestion_response(profile, event, accepted=False)

    async def _process_content_view(self, profile: UserProfile, event: UserEvent) -> None:
        """Process content view event."""
        content_id = event.data.get("content_id")
        content_type = event.data.get("content_type", "unknown")
        title = event.data.get("title", "Unknown")
        genres = event.data.get("genres", [])
        current_mood = event.data.get("mood")

        if not content_id:
            return

        # Get or create interaction record
        if content_id not in profile.content_interactions:
            profile.content_interactions[content_id] = ContentInteraction(
                content_id=content_id,
                content_type=content_type,
                title=title,
                genres=genres
            )

        interaction = profile.content_interactions[content_id]
        interaction.view_count += 1
        interaction.last_interacted = datetime.utcnow()

        if current_mood:
            interaction.mood_when_watched.append(current_mood)

        # Update content type preference
        profile.favorite_content_types[content_type] = (
            profile.favorite_content_types.get(content_type, 0) + 1
        )

        # Update genre preferences
        for genre in genres:
            profile.favorite_genres[genre] = (
                profile.favorite_genres.get(genre, 0) + 1
            )

            # Track mood -> genre correlation
            if current_mood:
                if current_mood not in profile.mood_to_content:
                    profile.mood_to_content[current_mood] = {}
                profile.mood_to_content[current_mood][genre] = (
                    profile.mood_to_content[current_mood].get(genre, 0) + 1
                )

        # Update activity patterns
        hour = event.timestamp.hour
        day = event.timestamp.weekday()
        profile.active_hours[hour] = profile.active_hours.get(hour, 0) + 1
        profile.active_days[day] = profile.active_days.get(day, 0) + 1

    async def _process_content_complete(self, profile: UserProfile, event: UserEvent) -> None:
        """Process content completion event."""
        content_id = event.data.get("content_id")
        watch_time = event.data.get("watch_time_minutes", 0)
        content_duration = event.data.get("duration_minutes", 0)

        if not content_id or content_id not in profile.content_interactions:
            return

        interaction = profile.content_interactions[content_id]
        interaction.completion_count += 1
        interaction.total_watch_time += watch_time

        # Detect hyperfocus (completed multiple times)
        if interaction.completion_count >= 3:
            if content_id not in profile.hyperfocus_content:
                profile.hyperfocus_content.append(content_id)

        # Update preferred duration estimate
        if content_duration > 0:
            self._update_duration_preference(profile, content_duration, completed=True)

    async def _process_content_skip(self, profile: UserProfile, event: UserEvent) -> None:
        """Process content skip event."""
        content_id = event.data.get("content_id")
        skip_time = event.data.get("skip_at_minutes", 0)
        content_duration = event.data.get("duration_minutes", 0)

        if not content_id:
            return

        if content_id in profile.content_interactions:
            profile.content_interactions[content_id].skip_count += 1

        # Learn from skip point
        if skip_time > 0 and content_duration > 0:
            skip_percentage = skip_time / content_duration
            if skip_percentage < 0.25:
                # Skipped very early - content not engaging
                self._update_attention_estimate(profile, skip_time)

    async def _process_content_rate(self, profile: UserProfile, event: UserEvent) -> None:
        """Process content rating event."""
        content_id = event.data.get("content_id")
        rating = event.data.get("rating", 0)  # 1-5 or 1-10

        if not content_id or content_id not in profile.content_interactions:
            return

        profile.content_interactions[content_id].ratings.append(rating)

        # Boost genre preferences for highly rated content
        if rating >= 4:  # Assuming 1-5 scale
            interaction = profile.content_interactions[content_id]
            for genre in interaction.genres:
                profile.favorite_genres[genre] = (
                    profile.favorite_genres.get(genre, 0) + 2  # Double boost for high rating
                )

    async def _process_mood_select(self, profile: UserProfile, event: UserEvent) -> None:
        """Process mood selection event."""
        mood = event.data.get("mood")
        if not mood:
            return

        profile.common_moods[mood] = profile.common_moods.get(mood, 0) + 1

    async def _process_mood_transition(self, profile: UserProfile, event: UserEvent) -> None:
        """Process mood transition event (before -> after content)."""
        from_mood = event.data.get("from_mood")
        to_mood = event.data.get("to_mood")
        content_id = event.data.get("content_id")

        if not from_mood or not to_mood:
            return

        if from_mood not in profile.mood_transitions:
            profile.mood_transitions[from_mood] = {}

        profile.mood_transitions[from_mood][to_mood] = (
            profile.mood_transitions[from_mood].get(to_mood, 0) + 1
        )

        # Track which content helps with mood transitions
        if content_id and from_mood != to_mood:
            positive_transitions = {"sad": "happy", "stressed": "calm", "bored": "energetic"}
            if positive_transitions.get(from_mood) == to_mood:
                # This content helped improve mood
                if content_id in profile.content_interactions:
                    interaction = profile.content_interactions[content_id]
                    for genre in interaction.genres:
                        if from_mood not in profile.mood_to_content:
                            profile.mood_to_content[from_mood] = {}
                        profile.mood_to_content[from_mood][genre] = (
                            profile.mood_to_content[from_mood].get(genre, 0) + 3  # Triple boost
                        )

    async def _process_session_start(self, profile: UserProfile, event: UserEvent) -> None:
        """Process session start."""
        hour = event.timestamp.hour
        profile.active_hours[hour] = profile.active_hours.get(hour, 0) + 1

    async def _process_session_end(self, profile: UserProfile, event: UserEvent) -> None:
        """Process session end."""
        duration = event.data.get("duration_minutes", 0)
        if duration > 0:
            # Update average session duration
            current_avg = profile.avg_session_duration
            profile.avg_session_duration = (current_avg * 0.9) + (duration * 0.1)

    async def _process_suggestion_response(
        self,
        profile: UserProfile,
        event: UserEvent,
        accepted: bool
    ) -> None:
        """Process Mr.DP suggestion acceptance/rejection."""
        content_id = event.data.get("content_id")
        genres = event.data.get("genres", [])

        if accepted:
            # Boost preferences for accepted suggestions
            for genre in genres:
                profile.favorite_genres[genre] = (
                    profile.favorite_genres.get(genre, 0) + 1.5
                )
        else:
            # Slightly decrease preferences for rejected suggestions
            for genre in genres:
                profile.favorite_genres[genre] = max(
                    0,
                    profile.favorite_genres.get(genre, 0) - 0.5
                )

    def _update_duration_preference(
        self,
        profile: UserProfile,
        duration: float,
        completed: bool
    ) -> None:
        """Update preferred content duration based on completion."""
        min_pref, max_pref = profile.preferred_duration

        if completed:
            # Completed - this duration works
            if duration < min_pref:
                min_pref = int(duration * 0.9)
            elif duration > max_pref:
                max_pref = int(duration * 1.1)
        else:
            # Not completed - this duration might be too long
            if duration > max_pref:
                max_pref = int(max_pref * 0.95)

        profile.preferred_duration = (max(10, min_pref), max(30, max_pref))

        # Update attention span estimate
        if completed and duration > profile.attention_span_estimate:
            profile.attention_span_estimate = (
                profile.attention_span_estimate * 0.9 + duration * 0.1
            )

    def _update_attention_estimate(self, profile: UserProfile, skip_time: float) -> None:
        """Update attention span estimate from early skips."""
        if skip_time < profile.attention_span_estimate:
            # Gradually decrease estimate
            profile.attention_span_estimate = (
                profile.attention_span_estimate * 0.95 + skip_time * 0.05
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # PATTERN DETECTION
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_patterns(self, user_id: str) -> List[UserPattern]:
        """
        Analyze user behavior and detect patterns.

        Returns:
            List of detected patterns
        """
        profile = self._profiles.get(user_id)
        if not profile:
            return []

        patterns = []

        # Check for binge-watching pattern
        binge_pattern = self._detect_binge_pattern(profile)
        if binge_pattern:
            patterns.append(binge_pattern)

        # Check for mood-based viewing pattern
        mood_pattern = self._detect_mood_pattern(profile)
        if mood_pattern:
            patterns.append(mood_pattern)

        # Check for time-based pattern
        time_pattern = self._detect_time_pattern(profile)
        if time_pattern:
            patterns.append(time_pattern)

        # Check for genre fatigue
        fatigue_pattern = self._detect_genre_fatigue(profile)
        if fatigue_pattern:
            patterns.append(fatigue_pattern)

        # Check attention span pattern
        attention_pattern = self._detect_attention_pattern(profile)
        if attention_pattern:
            patterns.append(attention_pattern)

        profile.patterns = patterns
        return patterns

    def _detect_binge_pattern(self, profile: UserProfile) -> Optional[UserPattern]:
        """Detect binge-watching behavior."""
        # Look for content watched multiple times in short period
        recent_events = [
            e for e in profile.events
            if e.event_type == EventType.CONTENT_COMPLETE
            and (datetime.utcnow() - e.timestamp) < timedelta(days=7)
        ]

        if len(recent_events) < self._min_interactions_for_pattern:
            return None

        # Count content types
        type_counts = defaultdict(int)
        for event in recent_events:
            content_type = event.data.get("content_type", "unknown")
            type_counts[content_type] += 1

        # Check for binge (more than 5 of same type in a week)
        for content_type, count in type_counts.items():
            if count >= 5:
                return UserPattern(
                    pattern_type="binge_watching",
                    confidence=min(1.0, count / 10),
                    description=f"User tends to binge {content_type} content",
                    data={"content_type": content_type, "weekly_count": count}
                )

        return None

    def _detect_mood_pattern(self, profile: UserProfile) -> Optional[UserPattern]:
        """Detect mood-based content selection pattern."""
        if not profile.mood_to_content:
            return None

        # Find strongest mood -> genre correlation
        strongest_correlation = None
        max_strength = 0

        for mood, genres in profile.mood_to_content.items():
            total = sum(genres.values())
            if total < self._min_interactions_for_pattern:
                continue

            for genre, count in genres.items():
                strength = count / total
                if strength > max_strength and strength > 0.3:  # At least 30% correlation
                    max_strength = strength
                    strongest_correlation = (mood, genre, strength)

        if strongest_correlation:
            mood, genre, strength = strongest_correlation
            return UserPattern(
                pattern_type="mood_genre_correlation",
                confidence=strength,
                description=f"When feeling {mood}, user prefers {genre} content",
                data={"mood": mood, "genre": genre, "strength": strength}
            )

        return None

    def _detect_time_pattern(self, profile: UserProfile) -> Optional[UserPattern]:
        """Detect time-based usage pattern."""
        if not profile.active_hours:
            return None

        total_activity = sum(profile.active_hours.values())
        if total_activity < self._min_interactions_for_pattern:
            return None

        # Find peak hours
        sorted_hours = sorted(
            profile.active_hours.items(),
            key=lambda x: x[1],
            reverse=True
        )

        peak_hour = sorted_hours[0][0]
        peak_activity = sorted_hours[0][1] / total_activity

        if peak_activity > 0.2:  # At least 20% of activity in one hour
            time_label = self._hour_to_label(peak_hour)
            return UserPattern(
                pattern_type="peak_usage_time",
                confidence=peak_activity,
                description=f"User is most active during {time_label}",
                data={"peak_hour": peak_hour, "time_label": time_label}
            )

        return None

    def _detect_genre_fatigue(self, profile: UserProfile) -> Optional[UserPattern]:
        """Detect if user is showing fatigue with a genre."""
        recent_skips = [
            e for e in profile.events
            if e.event_type == EventType.CONTENT_SKIP
            and (datetime.utcnow() - e.timestamp) < timedelta(days=7)
        ]

        if len(recent_skips) < 3:
            return None

        # Count skipped genres
        skip_genres = defaultdict(int)
        for event in recent_skips:
            for genre in event.data.get("genres", []):
                skip_genres[genre] += 1

        # Find genre with most skips
        if skip_genres:
            most_skipped = max(skip_genres.items(), key=lambda x: x[1])
            if most_skipped[1] >= 3:
                return UserPattern(
                    pattern_type="genre_fatigue",
                    confidence=min(1.0, most_skipped[1] / 5),
                    description=f"User may be experiencing {most_skipped[0]} fatigue",
                    data={"genre": most_skipped[0], "skip_count": most_skipped[1]}
                )

        return None

    def _detect_attention_pattern(self, profile: UserProfile) -> Optional[UserPattern]:
        """Detect attention span patterns for ADHD optimization."""
        attention_span = profile.attention_span_estimate

        if attention_span < 20:
            return UserPattern(
                pattern_type="short_attention_span",
                confidence=0.8,
                description="User prefers shorter content (under 20 min)",
                data={
                    "estimated_span": attention_span,
                    "recommendation": "short"
                }
            )
        elif attention_span > 90:
            return UserPattern(
                pattern_type="long_attention_span",
                confidence=0.8,
                description="User can engage with longer content (90+ min)",
                data={
                    "estimated_span": attention_span,
                    "recommendation": "long"
                }
            )

        return None

    def _hour_to_label(self, hour: int) -> str:
        """Convert hour to human-readable label."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "late night"

    # ═══════════════════════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_genre_preferences(self, user_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get user's top genre preferences."""
        profile = self._profiles.get(user_id)
        if not profile or not profile.favorite_genres:
            return []

        # Apply decay to older preferences
        total = sum(profile.favorite_genres.values())
        if total == 0:
            return []

        normalized = {
            genre: score / total
            for genre, score in profile.favorite_genres.items()
        }

        sorted_genres = sorted(
            normalized.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_genres[:top_n]

    def get_mood_recommendations(
        self,
        user_id: str,
        current_mood: str
    ) -> Dict[str, float]:
        """Get genre recommendations based on current mood."""
        profile = self._profiles.get(user_id)
        if not profile:
            return {}

        mood_genres = profile.mood_to_content.get(current_mood, {})
        if not mood_genres:
            # Fall back to general preferences
            return dict(self.get_genre_preferences(user_id, top_n=5))

        total = sum(mood_genres.values())
        if total == 0:
            return {}

        return {
            genre: score / total
            for genre, score in sorted(
                mood_genres.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    def get_duration_recommendation(self, user_id: str) -> Dict[str, Any]:
        """Get content duration recommendation for user."""
        profile = self._profiles.get(user_id)
        if not profile:
            return {"min": 30, "max": 120, "ideal": 60}

        min_dur, max_dur = profile.preferred_duration
        attention = profile.attention_span_estimate

        return {
            "min": min_dur,
            "max": max_dur,
            "ideal": int(attention),
            "attention_span": attention
        }

    def get_optimal_time(self, user_id: str) -> Optional[int]:
        """Get user's optimal viewing time (hour of day)."""
        profile = self._profiles.get(user_id)
        if not profile or not profile.active_hours:
            return None

        return max(profile.active_hours.items(), key=lambda x: x[1])[0]

    def should_suggest_variety(self, user_id: str) -> bool:
        """Check if user needs content variety suggestion."""
        profile = self._profiles.get(user_id)
        if not profile:
            return False

        # Check for genre fatigue pattern
        for pattern in profile.patterns:
            if pattern.pattern_type == "genre_fatigue":
                return True

        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # MR.DP PERSONALIZATION
    # ═══════════════════════════════════════════════════════════════════════════

    def get_mrdp_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context for Mr.DP to personalize responses.

        Returns personality adjustments and user-specific info.
        """
        profile = self._profiles.get(user_id)
        if not profile:
            return {}

        # Analyze patterns
        asyncio.create_task(self.analyze_patterns(user_id))

        context = {
            "user_profile": {
                "top_genres": self.get_genre_preferences(user_id, top_n=3),
                "preferred_duration": profile.preferred_duration,
                "attention_span": profile.attention_span_estimate,
                "common_moods": list(profile.common_moods.keys())[:3],
                "total_interactions": len(profile.events)
            },
            "patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.description,
                    "confidence": p.confidence
                }
                for p in profile.patterns[:5]
            ],
            "suggestions": []
        }

        # Add personalized suggestions
        if self.should_suggest_variety(user_id):
            context["suggestions"].append({
                "type": "variety",
                "message": "User may benefit from trying different genres"
            })

        if profile.attention_span_estimate < 30:
            context["suggestions"].append({
                "type": "short_content",
                "message": "Prefer shorter content recommendations"
            })

        return context

    # ═══════════════════════════════════════════════════════════════════════════
    # PROFILE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create new one."""
        if user_id not in self._profiles:
            self._profiles[user_id] = UserProfile(user_id=user_id)
        return self._profiles[user_id]

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile."""
        return self._profiles.get(user_id)

    def export_profile(self, user_id: str) -> Optional[Dict]:
        """Export user profile as dictionary (for storage/backup)."""
        profile = self._profiles.get(user_id)
        if not profile:
            return None

        return {
            "user_id": profile.user_id,
            "favorite_genres": profile.favorite_genres,
            "favorite_content_types": profile.favorite_content_types,
            "preferred_duration": profile.preferred_duration,
            "common_moods": profile.common_moods,
            "attention_span_estimate": profile.attention_span_estimate,
            "avg_session_duration": profile.avg_session_duration,
            "active_hours": profile.active_hours,
            "active_days": profile.active_days,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat()
        }

    def import_profile(self, user_id: str, data: Dict) -> UserProfile:
        """Import user profile from dictionary."""
        profile = self._get_or_create_profile(user_id)

        profile.favorite_genres = data.get("favorite_genres", {})
        profile.favorite_content_types = data.get("favorite_content_types", {})
        profile.preferred_duration = tuple(data.get("preferred_duration", (30, 120)))
        profile.common_moods = data.get("common_moods", {})
        profile.attention_span_estimate = data.get("attention_span_estimate", 45)
        profile.avg_session_duration = data.get("avg_session_duration", 30)
        profile.active_hours = data.get("active_hours", {})
        profile.active_days = data.get("active_days", {})

        return profile


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_service: Optional[UserLearningService] = None


def get_learning_service() -> UserLearningService:
    """Get or create the global learning service instance."""
    global _service
    if _service is None:
        _service = UserLearningService()
    return _service
