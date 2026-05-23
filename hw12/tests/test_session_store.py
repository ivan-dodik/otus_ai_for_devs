"""
Unit tests for web/session_store.py

Tests SessionStore and PreferenceProfile classes.
"""

import pytest
from web.session_store import SessionStore, PreferenceProfile


class TestPreferenceProfile:
    """Tests for PreferenceProfile class."""

    def test_initial_state(self):
        """Test initial state of PreferenceProfile."""
        profile = PreferenceProfile()
        assert profile.liked_anime == []
        assert profile.disliked_anime == []
        assert profile.viewed_anime == []
        assert profile.genre_scores == {}

    def test_add_like(self):
        """Test adding a liked anime."""
        profile = PreferenceProfile()
        profile.add_like("Cowboy Bebop")
        assert "Cowboy Bebop" in profile.liked_anime
        assert "Cowboy Bebop" in profile.viewed_anime

    def test_add_like_with_genres(self):
        """Test adding a liked anime with genres updates scores."""
        profile = PreferenceProfile()
        profile.add_like("Cowboy Bebop", ["sci-fi", "action"])
        assert profile.genre_scores["sci-fi"] == 2
        assert profile.genre_scores["action"] == 2

    def test_add_like_same_anime_twice(self):
        """Test adding the same anime twice doesn't duplicate."""
        profile = PreferenceProfile()
        profile.add_like("Cowboy Bebop")
        profile.add_like("Cowboy Bebop")
        assert profile.liked_anime.count("Cowboy Bebop") == 1

    def test_add_like_with_genres_twice(self):
        """Test adding genres twice increases score."""
        profile = PreferenceProfile()
        profile.add_like("Cowboy Bebop", ["sci-fi"])
        profile.add_like("Cowboy Bebop", ["sci-fi"])
        assert profile.genre_scores["sci-fi"] == 4

    def test_add_dislike(self):
        """Test adding a disliked anime."""
        profile = PreferenceProfile()
        profile.add_dislike("Bad Anime")
        assert "Bad Anime" in profile.disliked_anime
        assert "Bad Anime" in profile.viewed_anime

    def test_add_viewed(self):
        """Test adding a viewed anime."""
        profile = PreferenceProfile()
        profile.add_viewed("Just Watched")
        assert "Just Watched" in profile.viewed_anime
        assert "Just Watched" not in profile.liked_anime
        assert "Just Watched" not in profile.disliked_anime

    def test_get_excluded_titles(self):
        """Test getting excluded titles."""
        profile = PreferenceProfile()
        profile.add_dislike("Disliked 1")
        profile.add_viewed("Viewed 1")
        excluded = profile.get_excluded_titles()
        assert "Disliked 1" in excluded
        assert "Viewed 1" in excluded

    def test_get_top_genres(self):
        """Test getting top N genres."""
        profile = PreferenceProfile()
        profile.genre_scores = {"action": 5, "romance": 3, "sci-fi": 7}
        top = profile.get_top_genres(2)
        assert top == ["sci-fi", "action"]

    def test_get_top_genres_n_larger_than_available(self):
        """Test getting top N when N > available genres."""
        profile = PreferenceProfile()
        profile.genre_scores = {"action": 5, "romance": 3}
        top = profile.get_top_genres(10)
        assert top == ["action", "romance"]

    def test_reset(self):
        """Test resetting all preferences."""
        profile = PreferenceProfile()
        profile.add_like("Anime 1", ["action"])
        profile.add_dislike("Anime 2")
        profile.reset()
        assert profile.liked_anime == []
        assert profile.disliked_anime == []
        assert profile.viewed_anime == []
        assert profile.genre_scores == {}

    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = PreferenceProfile()
        profile.add_like("Anime 1", ["action"])
        profile.add_dislike("Anime 2")
        d = profile.to_dict()
        assert d["liked"] == ["Anime 1"]
        assert d["disliked"] == ["Anime 2"]
        assert d["viewed"] == ["Anime 1", "Anime 2"]
        assert d["genre_scores"] == {"action": 2}


class TestSessionStore:
    """Tests for SessionStore class."""

    def test_create_session(self):
        """Test creating a new session."""
        store = SessionStore()
        session_id = store.create_session()
        assert session_id is not None
        assert len(session_id) == 8
        assert store.session_exists(session_id)

    def test_create_session_independent(self):
        """Test that sessions are independent."""
        store = SessionStore()
        id1 = store.create_session()
        id2 = store.create_session()
        assert id1 != id2

    def test_add_message(self):
        """Test adding a message to a session."""
        store = SessionStore()
        session_id = store.create_session()
        store.add_message(session_id, "user", "Hello")
        history = store.get_history(session_id)
        assert len(history) == 1
        assert history[0] == {"role": "user", "content": "Hello"}

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        store = SessionStore()
        session_id = store.create_session()
        store.add_message(session_id, "user", "Hello")
        store.add_message(session_id, "assistant", "Hi there!")
        history = store.get_history(session_id)
        assert len(history) == 2

    def test_get_history_nonexistent_session(self):
        """Test getting history for non-existent session."""
        store = SessionStore()
        history = store.get_history("nonexistent")
        assert history == []

    def test_clear_session(self):
        """Test clearing a session."""
        store = SessionStore()
        session_id = store.create_session()
        store.add_message(session_id, "user", "Hello")
        store.clear_session(session_id)
        assert store.get_history(session_id) == []

    def test_clear_session_clears_preferences(self):
        """Test that clearing session also clears preferences."""
        store = SessionStore()
        session_id = store.create_session()
        prefs = store.get_preferences(session_id)
        prefs.add_like("Anime 1", ["action"])
        store.clear_session(session_id)
        prefs_after = store.get_preferences(session_id)
        assert prefs_after.liked_anime == []
        assert prefs_after.genre_scores == {}

    def test_get_preferences_creates_if_not_exists(self):
        """Test that get_preferences creates profile if needed."""
        store = SessionStore()
        # Don't create session, just get preferences
        prefs = store.get_preferences("new_session")
        assert isinstance(prefs, PreferenceProfile)

    def test_session_exists(self):
        """Test session_exists method."""
        store = SessionStore()
        assert store.session_exists("nonexistent") is False
        session_id = store.create_session()
        assert store.session_exists(session_id) is True

    def test_get_session_summary(self):
        """Test getting session summary."""
        store = SessionStore()
        session_id = store.create_session()
        store.add_message(session_id, "user", "Hello")
        store.add_message(session_id, "assistant", "Hi!")
        prefs = store.get_preferences(session_id)
        prefs.add_like("Anime 1", ["action", "sci-fi"])

        summary = store.get_session_summary(session_id)
        assert summary["message_count"] == 2
        assert summary["liked_count"] == 1
        assert summary["disliked_count"] == 0
        assert summary["viewed_count"] == 1
        assert "action" in summary["top_genres"] or "sci-fi" in summary["top_genres"]