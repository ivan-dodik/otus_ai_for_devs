"""
In-memory session store for Flask web UI.

Maps session IDs to message history and provides
session management for the web interface.

Includes PreferenceProfile for tracking user anime preferences within a session.
"""

import logging
import uuid
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PreferenceProfile:
    """Profile of user's anime preferences within a session.

    Tracks liked/disliked anime and maintains genre scores
    for better recommendation ranking.
    """

    def __init__(self):
        self.liked_anime: List[str] = []        # Titles user liked
        self.disliked_anime: List[str] = []      # Titles user disliked
        self.viewed_anime: List[str] = []        # All discussed/viewed titles
        self.genre_scores: Dict[str, int] = {}   # Genre slug -> score

    def add_like(self, anime_title: str, genres: List[str] | None = None):
        """Add an anime to liked list and update genre scores.

        Args:
            anime_title: Title of the anime.
            genres: Optional list of genre slugs for this anime.
        """
        if anime_title not in self.liked_anime:
            self.liked_anime.append(anime_title)

        # Boost genre scores for liked anime
        if genres:
            for genre in genres:
                self.genre_scores[genre] = self.genre_scores.get(genre, 0) + 2

        if anime_title not in self.viewed_anime:
            self.viewed_anime.append(anime_title)

        logger.debug(f"[DEBUG] PreferenceProfile: added like for '{anime_title}', genres={genres}")

    def add_dislike(self, anime_title: str):
        """Add an anime to disliked list.

        Args:
            anime_title: Title of the anime.
        """
        if anime_title not in self.disliked_anime:
            self.disliked_anime.append(anime_title)

        if anime_title not in self.viewed_anime:
            self.viewed_anime.append(anime_title)

        logger.debug(f"[DEBUG] PreferenceProfile: added dislike for '{anime_title}'")

    def add_viewed(self, anime_title: str):
        """Add an anime to viewed list (discussed in conversation).

        Args:
            anime_title: Title of the anime.
        """
        if anime_title not in self.viewed_anime:
            self.viewed_anime.append(anime_title)

    def get_excluded_titles(self) -> List[str]:
        """Get list of titles to exclude from recommendations.

        Returns:
            Combined list of disliked and viewed anime titles.
        """
        return self.disliked_anime + self.viewed_anime

    def get_top_genres(self, n: int = 5) -> List[str]:
        """Get top N genres by score.

        Args:
            n: Number of top genres to return.

        Returns:
            List of genre slugs sorted by score descending.
        """
        sorted_genres = sorted(self.genre_scores.items(), key=lambda x: x[1], reverse=True)
        return [g[0] for g in sorted_genres[:n]]

    def reset(self):
        """Clear all preferences."""
        self.liked_anime.clear()
        self.disliked_anime.clear()
        self.viewed_anime.clear()
        self.genre_scores.clear()
        logger.debug("[DEBUG] PreferenceProfile: all preferences cleared")

    def to_dict(self) -> dict:
        """Convert profile to dictionary for serialization.

        Returns:
            Dictionary with all profile data.
        """
        return {
            "liked": list(self.liked_anime),
            "disliked": list(self.disliked_anime),
            "viewed": list(self.viewed_anime),
            "genre_scores": dict(self.genre_scores),
        }


class SessionStore:
    """Simple in-memory session store with preference tracking."""

    def __init__(self):
        self._sessions: Dict[str, List[dict]] = {}
        self._preferences: Dict[str, PreferenceProfile] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())[:8]
        self._sessions[session_id] = []
        self._preferences[session_id] = PreferenceProfile()
        logger.debug(f"[DEBUG] SessionStore: created session {session_id}")
        return session_id

    def get_history(self, session_id: str) -> List[dict]:
        """Get message history for a session."""
        return self._sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})

    def get_preferences(self, session_id: str) -> PreferenceProfile:
        """Get or create preference profile for a session.

        Args:
            session_id: Session identifier.

        Returns:
            PreferenceProfile instance.
        """
        if session_id not in self._preferences:
            self._preferences[session_id] = PreferenceProfile()
        return self._preferences[session_id]

    def clear_session(self, session_id: str):
        """Clear all messages and preferences for a session."""
        if session_id in self._sessions:
            self._sessions[session_id] = []
        if session_id in self._preferences:
            self._preferences[session_id].reset()
        logger.debug(f"[DEBUG] SessionStore: cleared session {session_id}")

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in self._sessions

    def get_session_summary(self, session_id: str) -> dict:
        """Get a summary of session state.

        Args:
            session_id: Session identifier.

        Returns:
            Dictionary with message count and preference summary.
        """
        history = self.get_history(session_id)
        prefs = self.get_preferences(session_id)

        return {
            "message_count": len(history),
            "liked_count": len(prefs.liked_anime),
            "disliked_count": len(prefs.disliked_anime),
            "viewed_count": len(prefs.viewed_anime),
            "top_genres": prefs.get_top_genres(3),
        }


# Global session store instance
session_store = SessionStore()