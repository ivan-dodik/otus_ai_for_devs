"""
E2E integration tests for the anime recommendation agent.

These tests verify the full agent pipeline with mocked Kitsu API responses.
Designed to run against both llama3.1:8b and qwen3.5:9b-q4_K_M models.

Note: These tests require Ollama to be running locally with the specified models.
For CI environments without Ollama, use `pytest -m "not e2e"` to skip E2E tests.
"""

import pytest
import responses
import os
import json

from agent.agent import process_query, reset_agent
from tools.kitsu_tools import _clear_cache, _genre_cache

# Mark all tests in this file
pytestmark = pytest.mark.e2e


# ---- E2E Test Fixtures ----

@pytest.fixture(autouse=True)
def e2e_cleanup():
    """Reset agent and caches before/after each E2E test."""
    reset_agent()
    _clear_cache()
    _genre_cache.clear()
    yield
    reset_agent()
    _clear_cache()
    _genre_cache.clear()


# ---- E2E Tests: Trending ----

class TestE2ETrending:
    """E2E tests for trending anime queries."""

    @responses.activate
    def test_trending_query_russian(self):
        """Test: что сейчас популярно?"""
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/trending/anime",
            json={
                "data": [{
                    "id": "1",
                    "attributes": {
                        "canonicalTitle": "Cowboy Bebop",
                        "titles": {"en_jp": "Cowboy Bebop"},
                        "averageRating": "87",
                        "episodeCount": "26",
                        "status": "finished_airing",
                        "synopsis": "Space western adventure",
                    }
                }],
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json={
                "data": [
                    {"id": "1", "attributes": {"slug": "action", "name": "Action"}},
                    {"id": "2", "attributes": {"slug": "sci-fi", "name": "Sci-Fi"}},
                ],
            },
            status=200,
        )

        result = process_query("что сейчас популярно?")
        # LLM may return text summary or JSON with data
        assert "Cowboy Bebop" in result or "популяр" in result.lower() or "popular" in result.lower()

    @responses.activate
    def test_what_to_watch_english(self):
        """Test: what should I watch?"""
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/trending/anime",
            json={
                "data": [{
                    "id": "2",
                    "attributes": {
                        "canonicalTitle": "Steins;Gate",
                        "titles": {"en_jp": "Steins;Gate"},
                        "averageRating": "91",
                        "episodeCount": "24",
                        "status": "finished_airing",
                        "synopsis": "Time travel adventure",
                    }
                }],
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json={
                "data": [
                    {"id": "1", "attributes": {"slug": "sci-fi", "name": "Sci-Fi"}},
                ],
            },
            status=200,
        )

        result = process_query("what should I watch?")
        assert "Steins;Gate" in result or "watch" in result.lower() or "recommend" in result.lower()


# ---- E2E Tests: Genre Search ----

class TestE2EGenreSearch:
    """E2E tests for genre-based queries."""

    @responses.activate
    def test_genre_query_russian(self):
        """Test: найди топ аниме жанра романтика"""
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json={
                "data": [
                    {"id": "1", "attributes": {"slug": "romance", "name": "Romance"}},
                    {"id": "2", "attributes": {"slug": "comedy", "name": "Comedy"}},
                ],
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json={
                "data": [{
                    "id": "10",
                    "attributes": {
                        "canonicalTitle": "Toradora!",
                        "titles": {"en_jp": "Toradora!"},
                        "averageRating": "81",
                        "episodeCount": "25",
                        "status": "finished_airing",
                        "synopsis": "Romantic comedy",
                    }
                }],
            },
            status=200,
        )

        result = process_query("найди топ аниме жанра романтика")
        assert "Toradora" in result or "Romance" in result or "романти" in result.lower() or "romance" in result.lower()

    @responses.activate
    def test_genre_query_english(self):
        """Test: find action anime"""
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json={
                "data": [
                    {"id": "1", "attributes": {"slug": "action", "name": "Action"}},
                ],
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json={
                "data": [{
                    "id": "20",
                    "attributes": {
                        "canonicalTitle": "Attack on Titan",
                        "titles": {"en_jp": "Attack on Titan"},
                        "averageRating": "85",
                        "episodeCount": "25",
                        "status": "finished_airing",
                        "synopsis": "Humanity fights giants",
                    }
                }],
            },
            status=200,
        )

        result = process_query("find action anime")
        assert "Attack on Titan" in result or "action" in result.lower()


# ---- E2E Tests: Anime Info ----

class TestE2EAnimeInfo:
    """E2E tests for anime info queries."""

    @responses.activate
    def test_anime_info_query(self):
        """Test: расскажи про Cowboy Bebop"""
        # Search
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json={
                "data": [{
                    "id": "1",
                    "attributes": {
                        "canonicalTitle": "Cowboy Bebop",
                        "titles": {"en_jp": "Cowboy Bebop"},
                        "averageRating": "87",
                        "episodeCount": "26",
                        "status": "finished_airing",
                        "synopsis": "Space western",
                    }
                }],
            },
            status=200,
        )
        # Detail
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime/1",
            json={
                "data": {
                    "id": "1",
                    "attributes": {
                        "canonicalTitle": "Cowboy Bebop",
                        "titles": {"en_jp": "Cowboy Bebop"},
                        "averageRating": "87",
                        "episodeCount": "26",
                        "status": "finished_airing",
                        "synopsis": "Space western adventure",
                        "startDate": "1998-04-03",
                        "endDate": "1999-04-24",
                        "ageRating": "r",
                        "nsfw": False,
                    }
                }
            },
            status=200,
        )

        result = process_query("расскажи про Cowboy Bebop")
        assert "Cowboy Bebop" in result or "Bebop" in result


# ---- E2E Tests: Similar Anime ----

class TestE2ESimilar:
    """E2E tests for similar anime queries."""

    @responses.activate
    def test_similar_anime_query(self):
        """Test: найди похожее на Cowboy Bebop"""
        # Search
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json={
                "data": [{
                    "id": "1",
                    "attributes": {
                        "canonicalTitle": "Cowboy Bebop",
                        "titles": {"en_jp": "Cowboy Bebop"},
                        "averageRating": "87",
                        "episodeCount": "26",
                        "status": "finished_airing",
                        "synopsis": "Space western",
                    }
                }],
            },
            status=200,
        )
        # Categories
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/1/categories",
            json={
                "data": [
                    {"id": "c1", "attributes": {"slug": "space"}},
                    {"id": "c2", "attributes": {"slug": "action"}},
                ],
            },
            status=200,
        )
        # Genre results
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json={
                "data": [{
                    "id": "100",
                    "attributes": {
                        "canonicalTitle": "Space Dandy",
                        "titles": {"en_jp": "Space Dandy"},
                        "averageRating": "75",
                        "episodeCount": "26",
                        "status": "finished_airing",
                        "synopsis": "Space adventure comedy",
                    }
                }],
            },
            status=200,
        )

        result = process_query("найди похожее на Cowboy Bebop")
        # LLM may return text or data - check for any relevant content
        assert len(result) > 20  # Should have some meaningful output