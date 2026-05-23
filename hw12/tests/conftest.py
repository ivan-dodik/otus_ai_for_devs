"""
Shared test fixtures for the anime recommendation agent tests.

Provides mock Kitsu API responses using the `responses` library.
"""

import json
from typing import Any, Dict

import pytest
import responses

# ---- Mock Kitsu API responses ----

MOCK_TRENDING_RESPONSE = {
    "data": [
        {
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
        },
        {
            "id": "2",
            "attributes": {
                "canonicalTitle": "Samurai Champloo",
                "titles": {"en_jp": "Samurai Champloo"},
                "averageRating": "83",
                "episodeCount": "26",
                "status": "finished_airing",
                "synopsis": "Historical hip-hop adventure",
                "startDate": "2004-05-20",
                "endDate": "2005-03-19",
                "ageRating": "r",
                "nsfw": False,
            }
        },
    ],
    "meta": {},
    "links": {}
}

MOCK_SEARCH_RESPONSE = {
    "data": [
        {
            "id": "10",
            "attributes": {
                "canonicalTitle": "Naruto",
                "titles": {"en_jp": "Naruto"},
                "averageRating": "76",
                "episodeCount": "220",
                "status": "finished_airing",
                "synopsis": "A young ninja seeks recognition",
                "startDate": "2002-10-03",
                "endDate": "2007-02-08",
                "ageRating": "pg-13",
                "nsfw": False,
            }
        },
        {
            "id": "11",
            "attributes": {
                "canonicalTitle": "Naruto Shippuden",
                "titles": {"en_jp": "Naruto Shippuden"},
                "averageRating": "80",
                "episodeCount": "500",
                "status": "finished_airing",
                "synopsis": "Naruto returns after training",
                "startDate": "2007-02-15",
                "endDate": "2017-03-23",
                "ageRating": "pg-13",
                "nsfw": False,
            }
        },
    ],
    "meta": {},
    "links": {}
}

MOCK_ANIME_DETAIL_RESPONSE = {
    "data": {
        "id": "10",
        "attributes": {
            "canonicalTitle": "Naruto",
            "titles": {"en_jp": "Naruto"},
            "averageRating": "76",
            "episodeCount": "220",
            "status": "finished_airing",
            "synopsis": "A young ninja seeks recognition",
            "startDate": "2002-10-03",
            "endDate": "2007-02-08",
            "ageRating": "pg-13",
            "nsfw": False,
        }
    }
}

MOCK_GENRES_RESPONSE = {
    "data": [
        {"id": "1", "attributes": {"slug": "action", "name": "Action"}},
        {"id": "2", "attributes": {"slug": "romance", "name": "Romance"}},
        {"id": "3", "attributes": {"slug": "sci-fi", "name": "Sci-Fi"}},
        {"id": "4", "attributes": {"slug": "comedy", "name": "Comedy"}},
        {"id": "5", "attributes": {"slug": "drama", "name": "Drama"}},
        {"id": "6", "attributes": {"slug": "slice-of-life", "name": "Slice of Life"}},
        {"id": "7", "attributes": {"slug": "supernatural", "name": "Supernatural"}},
        {"id": "8", "attributes": {"slug": "adventure", "name": "Adventure"}},
        {"id": "9", "attributes": {"slug": "fantasy", "name": "Fantasy"}},
        {"id": "10", "attributes": {"slug": "mystery", "name": "Mystery"}},
    ],
    "meta": {},
    "links": {}
}

MOCK_CATEGORIES_RESPONSE = {
    "data": [
        {"id": "c1", "attributes": {"slug": "action"}},
        {"id": "c2", "attributes": {"slug": "sci-fi"}},
        {"id": "c3", "attributes": {"slug": "adventure"}},
    ],
    "meta": {},
    "links": {}
}

MOCK_GENRE_ANIME_RESPONSE = {
    "data": [
        {
            "id": "100",
            "attributes": {
                "canonicalTitle": "Space Dandy",
                "titles": {"en_jp": "Space Dandy"},
                "averageRating": "75",
                "episodeCount": "26",
                "status": "finished_airing",
                "synopsis": "A dandy in space",
            }
        },
        {
            "id": "101",
            "attributes": {
                "canonicalTitle": "Trigun",
                "titles": {"en_jp": "Trigun"},
                "averageRating": "82",
                "episodeCount": "26",
                "status": "finished_airing",
                "synopsis": "A gunfighter on a desert planet",
            }
        },
    ],
    "meta": {},
    "links": {}
}


@pytest.fixture
def mock_api():
    """Fixture that sets up all mock Kitsu API endpoints.

    Uses responses.start()/stop()/reset() pattern to avoid
    'Not all requests have been executed' errors when tests
    only use a subset of the registered mocks.
    """
    with responses.RequestsMock() as mock:
        # Trending
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/trending/anime",
            json=MOCK_TRENDING_RESPONSE,
            status=200,
        )
        # Search by text (match any request to /anime path)
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json=MOCK_SEARCH_RESPONSE,
            status=200,
        )
        # Genres
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json=MOCK_GENRES_RESPONSE,
            status=200,
        )
        # Categories
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/10/categories",
            json=MOCK_CATEGORIES_RESPONSE,
            status=200,
        )
        # Genre anime list
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime",
            json=MOCK_GENRE_ANIME_RESPONSE,
            status=200,
        )
        # Anime detail
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime/10",
            json=MOCK_ANIME_DETAIL_RESPONSE,
            status=200,
        )
        yield mock


def setup_search_mock(mock: responses.RequestsMock, anime_id: str, title: str, **kwargs):
    """Set up a mock for searching a specific anime by name.

    Args:
        mock: responses.RequestsMock instance.
        anime_id: The anime ID to return.
        title: The canonical title to return.
        **kwargs: Additional attributes to include.
    """
    default_attrs = {
        "averageRating": "80",
        "episodeCount": "24",
        "status": "finished_airing",
        "synopsis": "Test anime synopsis",
        "startDate": "2020-01-01",
        "endDate": "2020-06-30",
        "ageRating": "pg-13",
        "nsfw": False,
    }
    default_attrs.update(kwargs)

    response_data = {
        "data": [
            {
                "id": anime_id,
                "attributes": default_attrs,
            }
        ],
        "meta": {},
        "links": {}
    }
    mock.add(
        responses.GET,
        "https://kitsu.io/api/edge/anime",
        json=response_data,
        status=200,
    )


def setup_genre_anime_mock(mock: responses.RequestsMock, anime_id: str, title: str, rating: str = "85", **kwargs):
    """Set up a mock for genre-based anime list results.

    Args:
        mock: responses.RequestsMock instance.
        anime_id: The anime ID to return in the list.
        title: The canonical title to return.
        rating: The average rating.
        **kwargs: Additional attributes.
    """
    default_attrs = {
        "averageRating": rating,
        "episodeCount": "12",
        "status": "finished_airing",
        "synopsis": "Recommendation test anime",
    }
    default_attrs.update(kwargs)

    response_data = {
        "data": [
            {
                "id": anime_id,
                "attributes": default_attrs,
            }
        ],
        "meta": {},
        "links": {}
    }
    mock.add(
        responses.GET,
        "https://kitsu.io/api/edge/anime",
        json=response_data,
        status=200,
    )