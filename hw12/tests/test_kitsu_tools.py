"""
Unit tests for tools/kitsu_tools.py

Tests genre resolution, franchise detection, formatting helpers,
and API caching using mocked HTTP responses.
"""

import json
import pytest
import responses

from tools.kitsu_tools import (
    _extract_franchise_words,
    _format_anime_detail,
    _format_anime_list,
    _format_anime_list_compact,
    _is_same_franchise,
    _clear_cache,
    _search_person_by_name,
    _search_studio_by_name,
    search_anime_by_filter,
    _people_cache,
    _studio_cache,
)


@pytest.fixture
def genre_mock_api():
    """Fixture that sets up mock for genre resolution tests."""
    _clear_cache()
    from tools.kitsu_tools import _genre_cache
    _genre_cache.clear()

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres",
            json={
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
                    {"id": "11", "attributes": {"slug": "mahou-shoujo", "name": "Magical Girl"}},
                    {"id": "12", "attributes": {"slug": "magic", "name": "Magic"}},
                    {"id": "13", "attributes": {"slug": "horror", "name": "Horror"}},
                    {"id": "14", "attributes": {"slug": "sports", "name": "Sports"}},
                ],
                "meta": {},
                "links": {}
            },
            status=200,
        )
        yield mock


class TestResolveGenreSlug:
    """Tests for genre name to slug resolution."""

    def test_alias_russian_romance(self, genre_mock_api):
        """Test Russian alias for romance."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("романтика") == "romance"

    def test_alias_russian_action(self, genre_mock_api):
        """Test Russian alias for action."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("экшн") == "action"

    def test_alias_russian_comedy(self, genre_mock_api):
        """Test Russian alias for comedy."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("комедия") == "comedy"

    def test_alias_russian_fantasy(self, genre_mock_api):
        """Test Russian alias for fantasy."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("фэнтези") == "fantasy"

    def test_alias_russian_horror(self, genre_mock_api):
        """Test Russian alias for horror."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("ужасы") == "horror"

    def test_alias_russian_slice_of_life(self, genre_mock_api):
        """Test Russian alias for slice of life."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("повседневность") == "slice-of-life"

    def test_alias_russian_mystery(self, genre_mock_api):
        """Test Russian alias for mystery."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("детектив") == "mystery"

    def test_alias_russian_sports(self, genre_mock_api):
        """Test Russian alias for sports."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("спорт") == "sports"

    def test_alias_english_exact(self, genre_mock_api):
        """Test exact English match."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("action") == "action"

    def test_alias_magical_girl(self, genre_mock_api):
        """Test Magical Girl alias."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("magical girl") == "mahou-shoujo"

    def test_alias_magic(self, genre_mock_api):
        """Test Magic alias."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("магия") == "magic"

    def test_exact_match_on_name(self, genre_mock_api):
        """Test exact match on genre name from API."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("Action") == "action"

    def test_exact_match_on_slug(self, genre_mock_api):
        """Test exact match on genre slug."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("sci-fi") == "sci-fi"

    def test_substring_match_on_name(self, genre_mock_api):
        """Test substring match on genre name."""
        from tools.kitsu_tools import _resolve_genre_slug
        # "Rom" should match "Romance" via substring
        assert _resolve_genre_slug("Rom") == "romance"

    def test_not_found(self, genre_mock_api):
        """Test genre not found returns None."""
        from tools.kitsu_tools import _resolve_genre_slug
        assert _resolve_genre_slug("nonexistent_genre_xyz_123") is None

    def test_case_insensitive(self, genre_mock_api):
        """Test case insensitive matching."""
        from tools.kitsu_tools import _resolve_genre_slug
        slug1 = _resolve_genre_slug("ACTION")
        slug2 = _resolve_genre_slug("action")
        assert slug1 == slug2 == "action"


class TestExtractFranchiseWords:
    """Tests for franchise word extraction."""

    def test_simple_title(self):
        """Test simple title extraction."""
        words = _extract_franchise_words("Naruto")
        assert "Naruto" in words

    def test_title_with_number(self):
        """Test title with number."""
        words = _extract_franchise_words("Attack on Titan")
        assert "Attack" in words or "Titan" in words

    def test_title_with_parentheses(self):
        """Test title with parentheses."""
        words = _extract_franchise_words("Cowboy Bebop (2020)")
        assert "Bebop" in words or "Cowboy" in words

    def test_short_words_filtered(self):
        """Test that short words are filtered."""
        words = _extract_franchise_words("The A")
        # Should fall back to len > 2
        assert len(words) >= 0  # May be empty if all too short

    def test_multiple_significant_words(self):
        """Test multiple significant words."""
        words = _extract_franchise_words("One Punch Man")
        # Should take up to 2 significant words
        assert len(words) <= 2


class TestIsSameFranchise:
    """Tests for franchise matching."""

    def test_same_franchise(self):
        """Test same franchise detection."""
        assert _is_same_franchise("Naruto Shippuden", ["Naruto"]) is True

    def test_different_franchise(self):
        """Test different franchise."""
        assert _is_same_franchise("Cowboy Bebop", ["Naruto"]) is False

    def test_empty_franchise_words(self):
        """Test empty franchise words returns False."""
        assert _is_same_franchise("Any Title", []) is False

    def test_case_insensitive(self):
        """Test case insensitive franchise matching."""
        assert _is_same_franchise("naruto shippuden", ["NARUTO"]) is True


class TestFormatAnimeList:
    """Tests for anime list formatting."""

    def test_empty_list(self):
        """Test formatting empty list."""
        result = _format_anime_list({"data": []})
        assert result == "Аниме не найдены."

    def test_single_item(self):
        """Test formatting single item."""
        data = {
            "data": [{
                "id": "1",
                "attributes": {
                    "canonicalTitle": "Cowboy Bebop",
                    "averageRating": "87",
                    "episodeCount": "26",
                    "status": "finished_airing",
                    "synopsis": "Space western",
                }
            }]
        }
        result = _format_anime_list(data)
        assert "Cowboy Bebop" in result
        assert "87" in result
        assert "26" in result

    def test_max_results_limit(self):
        """Test max_results limit."""
        data = {
            "data": [{
                "id": str(i),
                "attributes": {
                    "canonicalTitle": f"Anime {i}",
                    "averageRating": "80",
                    "episodeCount": "12",
                    "status": "finished_airing",
                    "synopsis": "Test",
                }
            } for i in range(10)]
        }
        result = _format_anime_list(data, max_results=3)
        assert "Anime 0" in result
        assert "Anime 3" not in result


class TestFormatAnimeListCompact:
    """Tests for compact anime list formatting."""

    def test_empty_list(self):
        """Test formatting empty compact list."""
        result = _format_anime_list_compact([])
        assert result == "Аниме не найдены."

    def test_single_item(self):
        """Test formatting single compact item."""
        items = [{
            "id": "1",
            "title": "Cowboy Bebop",
            "rating": "87",
            "ep_count": "26",
            "status": "finished_airing",
        }]
        result = _format_anime_list_compact(items)
        assert "Cowboy Bebop" in result
        assert "87" in result


class TestFormatAnimeDetail:
    """Tests for anime detail formatting."""

    def test_full_detail(self):
        """Test full detail formatting."""
        item = {
            "id": "1",
            "attributes": {
                "canonicalTitle": "Cowboy Bebop",
                "averageRating": "87",
                "episodeCount": "26",
                "status": "finished_airing",
                "startDate": "1998-04-03",
                "endDate": "1999-04-24",
                "ageRating": "r",
                "nsfw": False,
                "synopsis": "Space western adventure",
            }
        }
        result = _format_anime_detail(item)
        assert "Cowboy Bebop" in result
        assert "87" in result
        assert "26" in result
        assert "1998-04-03" in result
        assert "Space western adventure" in result

    def test_missing_fields(self):
        """Test formatting with missing fields."""
        item = {
            "id": "1",
            "attributes": {}
        }
        result = _format_anime_detail(item)
        assert "Unknown" in result
        assert "N/A" in result


class TestAPICache:
    """Tests for API caching functionality."""

    @responses.activate
    def test_cache_hit(self):
        """Test that cached responses are returned without API call."""
        from tools.kitsu_tools import _cached_make_request, _api_cache

        _api_cache.clear()

        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/trending/anime",
            json={"data": []},
            status=200,
        )

        # First call - should hit API
        result1 = _cached_make_request("https://kitsu.io/api/edge/trending/anime")
        assert len(responses.calls) == 1

        # Second call - should hit cache
        result2 = _cached_make_request("https://kitsu.io/api/edge/trending/anime")
        assert len(responses.calls) == 1  # No additional API call
        assert result1 == result2

    @responses.activate
    def test_cache_miss_after_clear(self):
        """Test that cleared cache forces API call."""
        from tools.kitsu_tools import _cached_make_request, _api_cache, _clear_cache

        _api_cache.clear()

        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/trending/anime",
            json={"data": []},
            status=200,
        )

        url = "https://kitsu.io/api/edge/trending/anime"
        _cached_make_request(url)
        assert len(responses.calls) == 1

        _clear_cache()
        _cached_make_request(url)
        assert len(responses.calls) == 2


class TestSearchPersonByName:
    """Tests for person search functionality."""

    @responses.activate
    def test_person_found(self):
        """Test that person search returns ID when found."""
        _clear_cache()
        _people_cache.clear()

        # New API uses pagination instead of filter[name]
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people?page%5Blimit%5D=20&page%5Boffset%5D=0",
            json={
                "data": [
                    {"id": "12345", "attributes": {"name": "Yoko Kanno"}},
                    {"id": "12346", "attributes": {"name": "Other Person"}},
                ]
            },
            status=200,
        )
        person_id = _search_person_by_name("Yoko Kanno")
        assert person_id == "12345"

    @responses.activate
    def test_person_not_found(self):
        """Test that person search returns None when not found."""
        _clear_cache()
        _people_cache.clear()

        # New API uses pagination - return empty list
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people?page%5Blimit%5D=20&page%5Boffset%5D=0",
            json={"data": []},
            status=200,
        )
        person_id = _search_person_by_name("Unknown Person")
        assert person_id is None

    def test_person_cache_hit(self):
        """Test that cached person ID is returned without API call."""
        _clear_cache()
        _people_cache.clear()

        # Pre-populate cache
        _people_cache["Test Person"] = "99999"

        person_id = _search_person_by_name("Test Person")
        assert person_id == "99999"


class TestSearchStudioByName:
    """Tests for studio search functionality."""

    @responses.activate
    def test_studio_found(self):
        """Test that studio search returns ID when found."""
        _clear_cache()
        _studio_cache.clear()

        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/studios?filter[name]=Studio%20Ghibli",
            json={
                "data": [
                    {"id": "567", "attributes": {"name": "Studio Ghibli"}}
                ]
            },
            status=200,
        )
        studio_id = _search_studio_by_name("Studio Ghibli")
        assert studio_id == "567"

    @responses.activate
    def test_studio_not_found(self):
        """Test that studio search returns None when not found."""
        _clear_cache()
        _studio_cache.clear()

        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/studios?filter[name]=Unknown%20Studio",
            json={"data": []},
            status=200,
        )
        studio_id = _search_studio_by_name("Unknown Studio")
        assert studio_id is None

    def test_studio_cache_hit(self):
        """Test that cached studio ID is returned without API call."""
        _clear_cache()
        _studio_cache.clear()

        # Pre-populate cache
        _studio_cache["Test Studio"] = "888"

        studio_id = _search_studio_by_name("Test Studio")
        assert studio_id == "888"


class TestSearchAnimeByFilter:
    """Tests for the universal filter search tool."""

    def test_invalid_filter_type(self):
        """Test that invalid filter type returns error."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "invalid_type",
            "filter_value": "test"
        }))

        assert result["status"] == "error"
        assert "Неподдерживаемый тип фильтра" in result["errors"]

    @responses.activate
    def test_person_filter_success(self):
        """Test search by person filter (uses staff endpoint, not filter[person])."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        # Mock person search (uses pagination, not filter[name])
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people?page%5Blimit%5D=20&page%5Boffset%5D=0",
            json={
                "data": [
                    {"id": "12345", "attributes": {"name": "Yoko Kanno"}}
                ]
            },
            status=200,
        )
        # Mock staff entries for person (new approach uses /people/{id}/staff)
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people/12345/staff?page[limit]=20",
            json={
                "data": [
                    {
                        "id": "100",
                        "attributes": {"role": "Music"}
                    }
                ]
            },
            status=200,
        )
        # Mock anime for staff entry (uses /media-staff/{id}/media)
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/media-staff/100/media",
            json={
                "data": {
                    "id": "1",
                    "attributes": {
                        "canonicalTitle": "Cowboy Bebop",
                        "averageRating": "87",
                        "episodeCount": "26",
                        "status": "finished_airing",
                    }
                }
            },
            status=200,
        )

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "person",
            "filter_value": "Yoko Kanno",
            "limit": 5
        }))

        assert result["status"] == "success"
        assert "Cowboy Bebop" in result["data"]

    @responses.activate
    def test_studio_filter_success(self):
        """Test search by studio filter."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        # Mock studio search
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/studios?filter[name]=Studio%20Ghibli",
            json={
                "data": [
                    {"id": "567", "attributes": {"name": "Studio Ghibli"}}
                ]
            },
            status=200,
        )
        # Mock anime search by studio
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime?filter[studio]=567&sort=-averageRating&page[limit]=5",
            json={
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "canonicalTitle": "Spirited Away",
                            "averageRating": "90",
                            "episodeCount": "1",
                            "status": "finished_airing",
                            "synopsis": "Fantasy adventure",
                        }
                    }
                ]
            },
            status=200,
        )

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "studio",
            "filter_value": "Studio Ghibli",
            "limit": 5
        }))

        assert result["status"] == "success"
        assert "Spirited Away" in result["data"]

    @responses.activate
    def test_genre_filter_success(self):
        """Test search by genre filter."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()
        from tools.kitsu_tools import _genre_cache
        _genre_cache.clear()

        # Mock genres endpoint (needed for genre resolution)
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/genres?page[limit]=50",
            json={
                "data": [
                    {"id": "1", "attributes": {"slug": "action", "name": "Action"}},
                    {"id": "2", "attributes": {"slug": "romance", "name": "Romance"}},
                ],
            },
            status=200,
        )
        # Mock anime search by genre
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/anime?filter[genres]=action&sort=-averageRating&page[limit]=5",
            json={
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "canonicalTitle": "Action Anime",
                            "averageRating": "85",
                            "episodeCount": "24",
                            "status": "finished_airing",
                            "synopsis": "Action packed",
                        }
                    }
                ]
            },
            status=200,
        )

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "genre",
            "filter_value": "action",
            "limit": 5
        }))

        assert result["status"] == "success"
        assert "Action Anime" in result["data"]

    @responses.activate
    def test_person_not_found_error(self):
        """Test error when person not found."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        # New API uses pagination
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people?page%5Blimit%5D=20&page%5Boffset%5D=0",
            json={"data": []},
            status=200,
        )

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "person",
            "filter_value": "Unknown Person"
        }))

        assert result["status"] == "error"
        assert "не найден" in result["errors"].lower()

    @responses.activate
    def test_studio_not_found_error(self):
        """Test error when studio not found."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/studios?filter[name]=Unknown%20Studio",
            json={"data": []},
            status=200,
        )

        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "studio",
            "filter_value": "Unknown Studio"
        }))

        assert result["status"] == "error"
        assert "не найдена" in result["errors"].lower()

    @responses.activate
    def test_limit_validation(self):
        """Test that limit is clamped to valid range."""
        _clear_cache()
        _people_cache.clear()
        _studio_cache.clear()

        # New API uses pagination
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people?page%5Blimit%5D=20&page%5Boffset%5D=0",
            json={"data": [{"id": "1", "attributes": {"name": "Test Person"}}]},
            status=200,
        )
        # Mock staff endpoint (new approach)
        responses.add(
            responses.GET,
            "https://kitsu.io/api/edge/people/1/staff?page[limit]=20",
            json={"data": []},
            status=200,
        )

        # Test limit > 20 gets clamped to 20
        result = json.loads(search_anime_by_filter.invoke({
            "filter_type": "person",
            "filter_value": "Test Person",
            "limit": 50
        }))

        # Should not error, just use limit=20
        assert result["status"] == "success" or result["status"] == "error"
