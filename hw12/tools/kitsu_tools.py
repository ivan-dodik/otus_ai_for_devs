"""
Kitsu API tools for LangChain agent.

Provides 9 tools:
1. search_anime — search anime by title/keywords
2. get_anime_details — get detailed info about a specific anime by ID
3. get_anime_info — get detailed info about an anime by name (search + details in one tool)
4. get_anime_by_genre — find anime by genre (auto-resolves genre names to Kitsu slugs)
5. get_trending_anime — get currently trending anime
6. get_tags — get available genres from Kitsu
7. find_similar_anime — find anime similar to a given one, filtering out same-franchise titles
8. recommend_anime — comprehensive personalized recommendation based on liked/disliked anime
9. search_anime_by_filter — universal search by genre, category, person (composer/director), or studio

Debug output is controlled via config.DEBUG flag (--debug CLI argument or DEBUG env var).
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

import requests
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

KITSU_API_BASE = "https://kitsu.io/api/edge"
REQUEST_TIMEOUT = 30  # seconds
_API_CACHE_TTL = 300  # 5 minutes


# ---- API Cache ----

# In-memory cache for API responses: url -> (timestamp, data)
_api_cache: Dict[str, tuple[float, Dict[str, Any]]] = {}


def _cached_make_request(url: str) -> Dict[str, Any]:
    """Make a GET request to Kitsu API with in-memory caching (TTL=5 min).

    Args:
        url: API endpoint URL.

    Returns:
        Parsed JSON response.
    """
    now = time.time()
    if url in _api_cache and now - _api_cache[url][0] < _API_CACHE_TTL:
        logger.debug(f"[DEBUG] _cached_make_request: cache hit for {url[:80]}")
        return _api_cache[url][1]

    logger.debug(f"[DEBUG] _cached_make_request: cache miss for {url[:80]}")
    data = _make_request(url)
    _api_cache[url] = (now, data)
    return data


def _make_request(url: str) -> Dict[str, Any]:
    """Make a GET request to Kitsu API and return parsed JSON.

    Args:
        url: API endpoint URL.

    Returns:
        Parsed JSON response.
    """
    logger.debug(f"[DEBUG] _make_request URL: {url}")
    response = requests.get(url, headers={"Accept": "application/vnd.api+json"}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _clear_cache():
    """Clear the API cache (useful for testing)."""
    _api_cache.clear()
    logger.debug("[DEBUG] API cache cleared")


# ---- Genre Resolution ----

# Cache for genres to avoid repeated API calls
_genre_cache: List[Dict[str, Any]] = []


def _fetch_genres() -> List[Dict[str, Any]]:
    """
    Fetch genres from Kitsu API, with caching.

    Returns:
        List of genre dicts with "slug", "name" keys.
    """
    if _genre_cache:
        logger.debug(f"[DEBUG] _fetch_genres: using cached genres")
        return _genre_cache

    logger.debug(f"[DEBUG] _fetch_genres: fetching from API")
    try:
        url = f"{KITSU_API_BASE}/genres?page[limit]=50"
        data = _cached_make_request(url)
        items = data.get("data", [])

        genres = []
        for item in items:
            attrs = item.get("attributes", {})
            genres.append({
                "slug": attrs.get("slug", ""),
                "name": attrs.get("name", ""),
            })

        _genre_cache.extend(genres)
        logger.debug(f"[DEBUG] _fetch_genres: cached {len(genres)} genres")
        return genres
    except Exception as e:
        logger.error(f"[DEBUG] _fetch_genres error: {e}")
        return []


# Mapping of common user-facing genre names to Kitsu slugs
# Covers English, Russian, Japanese and common variations
GENRE_ALIAS_MAP = {
    # Magical Girl -> Mahou Shoujo
    "magical girl": "mahou-shoujo",
    "махоу сёжо": "mahou-shoujo",
    "махоу шоjo": "mahou-shoujo",
    "магическая девочка": "mahou-shoujo",
    "magical girl anime": "mahou-shoujo",
    "mahou shoujo": "mahou-shoujo",
    "махоу": "mahou-shoujo",
    "магия": "magic",
    "магика": "magic",
    "magic": "magic",
    # Romance
    "романтик": "romance",
    "романтика": "romance",
    "love": "romance",
    # Action
    "экшн": "action",
    "боевик": "action",
    "action": "action",
    # Comedy
    "комедия": "comedy",
    "comedy": "comedy",
    # Drama
    "драма": "drama",
    "drama": "drama",
    # Fantasy
    "фэнтези": "fantasy",
    "fantasy": "fantasy",
    # Sci-Fi
    "научная фантастика": "sci-fi",
    "science fiction": "sci-fi",
    "sci-fi": "sci-fi",
    "скай-фай": "sci-fi",
    # Horror
    "ужасы": "horror",
    "horror": "horror",
    # Slice of Life
    "повседневность": "slice-of-life",
    "slice of life": "slice-of-life",
    "повседневная": "slice-of-life",
    # Mecha
    "меха": "mecha",
    "mecha": "mecha",
    # School
    "школа": "school",
    "school": "school",
    # Super Power
    "суперсила": "super-power",
    "super power": "super-power",
    "супер силы": "super-power",
    # Adventure
    "приключения": "adventure",
    "adventure": "adventure",
    # Mystery
    "детектив": "mystery",
    "mystery": "mystery",
    # Supernatural
    "сверхъестественное": "supernatural",
    "supernatural": "supernatural",
    # Sports
    "спорт": "sports",
    "sports": "sports",
    # Military
    "военное": "military",
    "military": "military",
    # Psychological
    "психологическое": "psychological",
    "psychological": "psychological",
    # Thriller
    "триллер": "thriller",
    "thriller": "thriller",
    # Music
    "музыка": "music",
    "music": "music",
    # Historical
    "историческое": "historical",
    "historical": "historical",
}


def _resolve_genre_slug(genre: str) -> Optional[str]:
    """
    Resolve a genre name (user-provided) to a Kitsu genre slug.

    Tries:
    1. Alias map (covers Russian, English, Japanese variations)
    2. Exact match (case-insensitive) on name
    3. Exact match on slug
    4. Substring match on name
    5. Substring match on slug

    Args:
        genre: Genre name provided by user (e.g., "Magical Girl", "action", "романтика")

    Returns:
        Slug string if found, None otherwise.
    """
    genres = _fetch_genres()
    if not genres:
        logger.warning("[DEBUG] _resolve_genre_slug: no genres cached")
        return None

    genre_lower = genre.lower().strip()

    # 1. Check alias map first (covers Russian, Japanese, common variations)
    if genre_lower in GENRE_ALIAS_MAP:
        slug = GENRE_ALIAS_MAP[genre_lower]
        logger.debug(f"[DEBUG] _resolve_genre_slug: alias match '{genre}' -> '{slug}'")
        return slug

    # 2. Exact match (case-insensitive) on name
    for g in genres:
        if g["name"].lower() == genre_lower:
            logger.debug(f"[DEBUG] _resolve_genre_slug: exact match '{genre}' -> '{g['slug']}'")
            return g["slug"]

    # 3. Exact match on slug
    for g in genres:
        if g["slug"].lower() == genre_lower:
            logger.debug(f"[DEBUG] _resolve_genre_slug: slug match '{genre}' -> '{g['slug']}'")
            return g["slug"]

    # 4. Substring match on name (e.g., "Magical" matches "Magical Girl")
    for g in genres:
        if genre_lower in g["name"].lower():
            logger.debug(f"[DEBUG] _resolve_genre_slug: substring match '{genre}' -> '{g['slug']}'")
            return g["slug"]

    # 5. Substring match on slug
    for g in genres:
        if genre_lower in g["slug"].lower():
            logger.debug(f"[DEBUG] _resolve_genre_slug: slug substring match '{genre}' -> '{g['slug']}'")
            return g["slug"]

    logger.debug(f"[DEBUG] _resolve_genre_slug: no match for '{genre}'")
    return None


# ---- Franchise Detection ----

def _extract_franchise_words(title: str) -> List[str]:
    """
    Extract key franchise words from an anime title for exclusion filtering.

    Takes the first 1-2 significant words (ignoring short/common words).

    Args:
        title: Anime title string.

    Returns:
        List of words to exclude.
    """
    # Remove parenthetical text and special characters
    cleaned = re.sub(r'\([^)]*\)', '', title)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    words = cleaned.split()

    # Filter out short/common words
    significant = [w for w in words if len(w) > 3]
    if not significant:
        significant = [w for w in words if len(w) > 2]

    # Take up to 2 significant words
    return significant[:2]


def _is_same_franchise(title: str, franchise_words: List[str]) -> bool:
    """
    Check if an anime title belongs to the same franchise.

    Args:
        title: Anime title to check.
        franchise_words: List of words identifying the franchise.

    Returns:
        True if the title contains any franchise word.
    """
    if not franchise_words:
        return False
    title_lower = title.lower()
    return any(word.lower() in title_lower for word in franchise_words)


# ---- Formatting Helpers ----

def _format_anime_list(data: Dict[str, Any], max_results: int = 10) -> str:
    """
    Format a list of anime from Kitsu API response into readable string.

    Args:
        data: Kitsu API response data.
        max_results: Maximum number of results to include.

    Returns:
        Formatted string.
    """
    items = data.get("data", [])
    if not items:
        return "Аниме не найдены."

    result_lines = []
    for item in items[:max_results]:
        attrs = item.get("attributes", {})
        title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en_jp", "Unknown")
        anime_id = item.get("id", "?")
        avg_rating = attrs.get("averageRating") or "N/A"
        ep_count = attrs.get("episodeCount") or "N/A"
        status = attrs.get("status") or "N/A"
        synopsis = attrs.get("synopsis", "") or ""
        result_lines.append(
            f"- [{anime_id}] {title} (рейтинг: {avg_rating}, "
            f"серий: {ep_count}, статус: {status})\n"
            f"  {synopsis[:150].strip()}..."
        )
    return "\n\n".join(result_lines)


def _format_anime_list_compact(data: List[Dict[str, Any]], max_results: int = 10) -> str:
    """
    Format a list of anime items (raw dicts) into compact readable string.
    Used by find_similar_anime which works with pre-processed items.

    Args:
        data: List of anime item dicts with 'title', 'id', 'rating', 'ep_count', 'status' keys.
        max_results: Maximum number of results to include.

    Returns:
        Formatted string.
    """
    if not data:
        return "Аниме не найдены."

    result_lines = []
    for item in data[:max_results]:
        result_lines.append(
            f"- [{item['id']}] {item['title']} "
            f"(рейтинг: {item['rating']}, серий: {item['ep_count']}, статус: {item['status']})"
        )
    return "\n".join(result_lines)


def _format_anime_detail(item: Dict[str, Any]) -> str:
    """Format a single anime detail into readable string."""
    attrs = item.get("attributes", {})
    title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en_jp", "Unknown")
    synopsis = attrs.get("synopsis", "") or "Нет описания"
    avg_rating = attrs.get("averageRating") or "N/A"
    ep_count = attrs.get("episodeCount") or "N/A"
    status = attrs.get("status") or "N/A"
    start_date = attrs.get("startDate") or "N/A"
    end_date = attrs.get("endDate") or "N/A"
    age_rating = attrs.get("ageRating") or "N/A"
    nsfw = attrs.get("nsfw", False)

    return (
        f"Название: {title}\n"
        f"Рейтинг: {avg_rating}\n"
        f"Серий: {ep_count}\n"
        f"Статус: {status}\n"
        f"Даты: {start_date} — {end_date}\n"
        f"Возрастной рейтинг: {age_rating}\n"
        f"NSFW: {nsfw}\n\n"
        f"Описание:\n{synopsis.strip()}"
    )


def _get_anime_genres(anime_id: str) -> List[str]:
    """
    Get genre/category slugs for an anime by ID.

    Args:
        anime_id: Kitsu anime ID.

    Returns:
        List of genre/category slugs.
    """
    try:
        url = f"{KITSU_API_BASE}/anime/{anime_id}/categories"
        data = _cached_make_request(url)
        category_items = data.get("data", [])

        slugs = []
        for cat_item in category_items:
            cat_attrs = cat_item.get("attributes", {})
            slug = cat_attrs.get("slug", "")
            if slug:
                slugs.append(slug)
            if len(slugs) >= 5:
                break
        return slugs
    except Exception as e:
        logger.error(f"[DEBUG] _get_anime_genres error for {anime_id}: {e}")
        return []


def _search_anime_by_id(anime_id: str) -> Dict[str, Any]:
    """
    Get full anime data by ID.

    Args:
        anime_id: Kitsu anime ID.

    Returns:
        Full anime item dict, or empty dict if not found.
    """
    try:
        url = f"{KITSU_API_BASE}/anime/{anime_id}"
        data = _cached_make_request(url)
        return data.get("data", {})
    except Exception as e:
        logger.error(f"[DEBUG] _search_anime_by_id error for {anime_id}: {e}")
        return {}


def _search_anime_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Search for anime by name and return the first result.

    Args:
        name: Anime title to search for.

    Returns:
        First matching anime item dict, or None if not found.
    """
    try:
        url = f"{KITSU_API_BASE}/anime?filter[text]={requests.utils.quote(name)}"
        data = _cached_make_request(url)
        items = data.get("data", [])
        if items:
            return items[0]
        return None
    except Exception as e:
        logger.error(f"[DEBUG] _search_anime_by_name error for '{name}': {e}")
        return None


# ---- Tool definitions ----


@tool
def search_anime(query: str) -> str:
    """Поиск аниме по названию или ключевым словам."""
    logger.debug(f"[DEBUG] search_anime called with query='{query}'")

    try:
        url = f"{KITSU_API_BASE}/anime?filter[text]={requests.utils.quote(query)}"
        data = _cached_make_request(url)

        result = {
            "status": "success",
            "action": f"Поиск аниме по запросу: {query}",
            "data": _format_anime_list(data),
            "errors": None,
        }

        logger.debug(f"[DEBUG] search_anime result: {json.dumps(result, ensure_ascii=False)[:300]}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Поиск аниме по запросу: {query}",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] search_anime error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def get_anime_details(anime_id: int) -> str:
    """Получение детальной информации об аниме по его ID."""
    logger.debug(f"[DEBUG] get_anime_details called with id={anime_id}")

    try:
        url = f"{KITSU_API_BASE}/anime/{anime_id}"
        data = _cached_make_request(url)

        item = data.get("data", {})
        if not item:
            result = {
                "status": "error",
                "action": f"Получение информации об аниме ID {anime_id}",
                "data": None,
                "errors": f"Аниме с ID {anime_id} не найдено",
            }
        else:
            result = {
                "status": "success",
                "action": f"Получение информации об аниме ID {anime_id}",
                "data": _format_anime_detail(item),
                "errors": None,
            }

        logger.debug(f"[DEBUG] get_anime_details result: {json.dumps(result, ensure_ascii=False)[:300]}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Получение информации об аниме ID {anime_id}",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] get_anime_details error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def get_anime_by_genre(genre: str) -> str:
    """
    Поиск аниме по жанру. Автоматически определяет правильный идентификатор жанра.
    Если жанр не найден — используй get_tags() чтобы увидеть список доступных жанров.
    """
    logger.debug(f"[DEBUG] get_anime_by_genre called with genre='{genre}'")

    try:
        # Resolve genre name to slug
        slug = _resolve_genre_slug(genre)

        if slug is None:
            # Could not resolve — return available genres as hint
            genres = _fetch_genres()
            genre_names = [g["name"] for g in genres]
            result = {
                "status": "error",
                "action": f"Поиск аниме в жанре: {genre}",
                "data": None,
                "errors": f"Жанр '{genre}' не найден. Доступные жанры: {', '.join(genre_names)}",
            }
            logger.debug(f"[DEBUG] get_anime_by_genre: genre '{genre}' not resolved")
            return json.dumps(result, ensure_ascii=False)

        # Fetch anime by genre slug, sorted by rating
        url = f"{KITSU_API_BASE}/anime?filter[genres]={slug}&sort=-averageRating&page[limit]=10"
        data = _cached_make_request(url)

        formatted_data = _format_anime_list(data, max_results=10)

        result = {
            "status": "success",
            "action": f"Выведен топ аниме в жанре: {genre}",
            "data": formatted_data,
            "errors": None,
        }

        logger.debug(f"[DEBUG] get_anime_by_genre result: {json.dumps(result, ensure_ascii=False)[:300]}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Поиск аниме в жанре: {genre}",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] get_anime_by_genre error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def get_trending_anime() -> str:
    """Получение списка популярных/трендовых аниме."""
    logger.debug("[DEBUG] get_trending_anime called")

    try:
        url = f"{KITSU_API_BASE}/trending/anime"
        data = _cached_make_request(url)

        result = {
            "status": "success",
            "action": "Получение списка популярных аниме",
            "data": _format_anime_list(data),
            "errors": None,
        }

        logger.debug(f"[DEBUG] get_trending_anime result: {json.dumps(result, ensure_ascii=False)[:300]}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": "Получение списка популярных аниме",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] get_trending_anime error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def get_anime_info(name: str) -> str:
    """
    Получение полной информации об аниме по названию.
    Сам находит ID аниме и возвращает полную информацию.
    """
    logger.debug(f"[DEBUG] get_anime_info called with name='{name}'")

    try:
        # Step 1: Search for the anime
        search_url = f"{KITSU_API_BASE}/anime?filter[text]={requests.utils.quote(name)}"
        logger.debug(f"[DEBUG] get_anime_info search URL: {search_url}")
        search_data = _cached_make_request(search_url)

        items = search_data.get("data", [])
        if not items:
            result = {
                "status": "error",
                "action": f"Поиск информации об аниме: {name}",
                "data": None,
                "errors": f"Аниме с названием '{name}' не найдено",
            }
            logger.debug(f"[DEBUG] get_anime_info: no results found")
            return json.dumps(result, ensure_ascii=False)

        # Take the first result and get its ID
        first_item = items[0]
        anime_id = first_item.get("id")
        attrs = first_item.get("attributes", {})
        search_title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en_jp", "Unknown")
        logger.debug(f"[DEBUG] get_anime_info: found '{search_title}' with ID={anime_id}")

        # Step 2: Get full details by ID
        detail_url = f"{KITSU_API_BASE}/anime/{anime_id}"
        logger.debug(f"[DEBUG] get_anime_info detail URL: {detail_url}")
        detail_data = _cached_make_request(detail_url)

        detail_item = detail_data.get("data", {})
        if not detail_item:
            # Fallback: return search result only
            result = {
                "status": "success",
                "action": f"Поиск информации об аниме: {name}",
                "data": _format_anime_list(search_data),
                "errors": None,
            }
            logger.debug(f"[DEBUG] get_anime_info: details not found, returning search results")
            return json.dumps(result, ensure_ascii=False)

        full_info = _format_anime_detail(detail_item)

        result = {
            "status": "success",
            "action": f"Получение информации об аниме: {name}",
            "data": full_info,
            "errors": None,
        }

        logger.debug(f"[DEBUG] get_anime_info result: {json.dumps(result, ensure_ascii=False)[:300]}")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Поиск информации об аниме: {name}",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] get_anime_info error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def get_tags() -> str:
    """
    Получение списка доступных жанров из Kitsu API.
    Используй, когда get_anime_by_genre не нашёл нужный жанр.
    """
    logger.debug("[DEBUG] get_tags called")

    try:
        genres = _fetch_genres()
        if not genres:
            result = {
                "status": "error",
                "action": "Получение списка жанров",
                "data": None,
                "errors": "Жанры не найдены.",
            }
            return json.dumps(result, ensure_ascii=False)

        lines = ["Доступные жанры (genre):"]
        for g in genres:
            lines.append(f"- {g['name']} (slug: {g['slug']})")

        result = {
            "status": "success",
            "action": "Получен список жанров",
            "data": "\n".join(lines),
            "errors": None,
        }

        logger.debug(f"[DEBUG] get_tags result: {len(genres)} items")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": "Получение списка жанров",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] get_tags error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def find_similar_anime(name: str) -> str:
    """
    Поиск аниме, похожего на указанное, НО исключая тайтлы из той же франшизы.
    Находит жанры указанного аниме, ищет другие аниме с теми же жанрами,
    и исключает те, что содержат в названии ключевые слова франшизы.
    """
    logger.debug(f"[DEBUG] find_similar_anime called with name='{name}'")

    try:
        # Step 1: Search for the anime
        search_url = f"{KITSU_API_BASE}/anime?filter[text]={requests.utils.quote(name)}"
        logger.debug(f"[DEBUG] find_similar_anime search URL: {search_url}")
        search_data = _cached_make_request(search_url)

        items = search_data.get("data", [])
        if not items:
            result = {
                "status": "error",
                "action": f"Поиск аниме, похожих на: {name}",
                "data": None,
                "errors": f"Аниме с названием '{name}' не найдено",
            }
            return json.dumps(result, ensure_ascii=False)

        # Take the first result
        first_item = items[0]
        anime_id = first_item.get("id")
        attrs = first_item.get("attributes", {})
        search_title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en_jp", "Unknown")
        logger.debug(f"[DEBUG] find_similar_anime: found '{search_title}' with ID={anime_id}")

        # Determine words to exclude
        franchise_words = _extract_franchise_words(search_title)
        logger.debug(f"[DEBUG] find_similar_anime: franchise_words={franchise_words}")

        # Step 2: Get categories/genres for this anime
        category_slugs = _get_anime_genres(anime_id)

        if not category_slugs:
            result = {
                "status": "error",
                "action": f"Поиск аниме, похожих на: {name}",
                "data": None,
                "errors": f"Не удалось определить категории для аниме '{search_title}'",
            }
            return json.dumps(result, ensure_ascii=False)

        logger.debug(f"[DEBUG] find_similar_anime: using category slugs: {category_slugs}")

        # Step 3: Fetch anime for each category
        seen_ids: set = set()
        similar_items: List[Dict[str, Any]] = []

        for slug in category_slugs:
            # Use filter[categories] instead of filter[genres] for category slugs
            # Categories are more specific tags (bounty-hunter, space, etc.)
            # while genres are broader (action, comedy, etc.)
            url = f"{KITSU_API_BASE}/anime?filter[categories]={slug}&sort=-averageRating&page[limit]=10"
            genre_data = _cached_make_request(url)
            genre_items = genre_data.get("data", [])

            for item in genre_items:
                item_id = item.get("id")
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)

                item_attrs = item.get("attributes", {})
                item_title = item_attrs.get("canonicalTitle") or item_attrs.get("titles", {}).get("en_jp", "Unknown")

                # Skip if same franchise
                if _is_same_franchise(item_title, franchise_words):
                    logger.debug(f"[DEBUG] find_similar_anime: skipping same-franchise: '{item_title}'")
                    continue

                # Skip the original anime itself
                if str(item_id) == str(anime_id):
                    continue

                similar_items.append({
                    "id": item_id,
                    "title": item_title,
                    "rating": item_attrs.get("averageRating") or "N/A",
                    "ep_count": item_attrs.get("episodeCount") or "N/A",
                    "status": item_attrs.get("status") or "N/A",
                })

            # Stop if we have enough results
            if len(similar_items) >= 15:
                break

        if not similar_items:
            result = {
                "status": "success",
                "action": f"Поиск аниме, похожих на: {name}",
                "data": f"Аниме, похожие на '{search_title}' не найдены среди других франшиз.",
                "errors": None,
            }
            return json.dumps(result, ensure_ascii=False)

        # Sort by rating descending
        similar_items.sort(key=lambda x: (
            0 if x["rating"] == "N/A" else -float(x["rating"])
        ))

        # Format the result
        formatted = _format_anime_list_compact(similar_items, max_results=10)
        genre_names = ", ".join(category_slugs)

        result = {
            "status": "success",
            "action": f"Поиск аниме, похожих на: {name} (категории: {genre_names})",
            "data": formatted,
            "errors": None,
        }

        logger.debug(f"[DEBUG] find_similar_anime result: {len(similar_items)} items found")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Поиск аниме, похожих на: {name}",
            "data": None,
            "errors": str(e),
        }
        logger.debug(f"[DEBUG] find_similar_anime error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


@tool
def recommend_anime(
    liked_anime: str,
    disliked_anime: str = "",
    exclude_franchise: str = "",
    limit: int = 8
) -> str:
    """
    Персональная рекомендация аниме на основе предпочтений пользователя.

    Выполняет комплексный пайплайн:
    1. Находит жанры/теги понравившегося аниме
    2. Ищет топ аниме по этим жанрам
    3. Исключает франшизы и не понравившиеся тайтлы
    4. Агрегирует и ранжирует результаты

    Args:
        liked_anime: Название аниме, которое понравилось (одно или несколько через запятую)
        disliked_anime: Название аниме, которое не понравилось (опционально, через запятую)
        exclude_franchise: Исключить тайтлы, содержащие эти слова в названии (опционально)
        limit: Максимальное количество рекомендаций (по умолчанию 8)

    Returns:
        JSON с агрегированными персональными рекомендациями.

    Example:
        recommend_anime(liked_anime="Cowboy Bebop, Evangelion", disliked_anime="Naruto", exclude_franchise="Bebop")
    """
    logger.debug(f"[DEBUG] recommend_anime called: liked='{liked_anime}', disliked='{disliked_anime}', "
                 f"exclude='{exclude_franchise}', limit={limit}")

    try:
        # Parse input lists
        liked_titles = [t.strip() for t in liked_anime.split(",") if t.strip()]
        disliked_titles = [t.strip() for t in disliked_anime.split(",") if t.strip()] if disliked_anime else []
        exclude_words = [w.strip() for w in exclude_franchise.split(",") if w.strip()] if exclude_franchise else []

        if not liked_titles:
            result = {
                "status": "error",
                "action": "Персональная рекомендация",
                "data": None,
                "errors": "Укажите хотя бы одно аниме, которое вам понравилось.",
            }
            return json.dumps(result, ensure_ascii=False)

        # Collect all genre slugs from liked anime
        all_genre_slugs: List[str] = []
        seen_slugs: set = set()
        anime_details: Dict[str, Dict] = {}

        for title in liked_titles:
            search_result = _search_anime_by_name(title)
            if not search_result:
                logger.warning(f"[DEBUG] recommend_anime: liked anime '{title}' not found")
                continue

            item_id = search_result.get("id")
            item_attrs = search_result.get("attributes", {})
            item_title = item_attrs.get("canonicalTitle") or item_attrs.get("titles", {}).get("en_jp", title)

            # Store anime info
            anime_details[item_title] = {
                "id": item_id,
                "title": item_title,
            }

            # Get genres
            slugs = _get_anime_genres(item_id)
            for slug in slugs:
                if slug not in seen_slugs:
                    all_genre_slugs.append(slug)
                    seen_slugs.add(slug)

        if not all_genre_slugs:
            result = {
                "status": "error",
                "action": "Персональная рекомендация",
                "data": None,
                "errors": f"Не удалось найти жанры для указанных аниме: {', '.join(liked_titles)}",
            }
            return json.dumps(result, ensure_ascii=False)

        logger.debug(f"[DEBUG] recommend_anime: collected {len(all_genre_slugs)} unique genre slugs: {all_genre_slugs}")

        # Build exclusion word list
        all_exclude_words = list(exclude_words)
        for disliked_title in disliked_titles:
            all_exclude_words.extend(_extract_franchise_words(disliked_title))
        for liked_title in liked_titles:
            all_exclude_words.extend(_extract_franchise_words(liked_title))

        # Fetch anime for each genre and aggregate
        seen_ids: set = set()
        scored_items: Dict[str, Dict[str, Any]] = {}

        for slug in all_genre_slugs:
            try:
                url = f"{KITSU_API_BASE}/anime?filter[genres]={slug}&sort=-averageRating&page[limit]=15"
                genre_data = _cached_make_request(url)
                genre_items = genre_data.get("data", [])

                for item in genre_items:
                    item_id = item.get("id")
                    if item_id in seen_ids:
                        continue

                    item_attrs = item.get("attributes", {})
                    item_title = item_attrs.get("canonicalTitle") or item_attrs.get("titles", {}).get("en_jp", "Unknown")

                    # Skip already seen
                    if item_id in seen_ids:
                        continue

                    # Skip excluded franchises
                    if _is_same_franchise(item_title, all_exclude_words):
                        logger.debug(f"[DEBUG] recommend_anime: skipping excluded franchise: '{item_title}'")
                        continue

                    # Skip disliked anime
                    if any(dt.lower() in item_title.lower() for dt in disliked_titles):
                        logger.debug(f"[DEBUG] recommend_anime: skipping disliked: '{item_title}'")
                        continue

                    # Skip liked anime themselves
                    if any(lt.lower() in item_title.lower() for lt in liked_titles):
                        logger.debug(f"[DEBUG] recommend_anime: skipping liked: '{item_title}'")
                        continue

                    # Score: higher rating = higher score, bonus for multiple genre matches
                    rating = item_attrs.get("averageRating")
                    if rating and rating != "N/A":
                        score = float(rating)
                    else:
                        score = 0

                    if item_title not in scored_items:
                        scored_items[item_title] = {
                            "id": item_id,
                            "title": item_title,
                            "rating": rating or "N/A",
                            "ep_count": item_attrs.get("episodeCount") or "N/A",
                            "status": item_attrs.get("status") or "N/A",
                            "synopsis": item_attrs.get("synopsis", "") or "",
                            "score": score,
                            "genre_count": 0,
                            "matched_genres": [],
                        }
                    scored_items[item_title]["genre_count"] += 1
                    scored_items[item_title]["matched_genres"].append(slug)

                    seen_ids.add(item_id)

            except Exception as e:
                logger.error(f"[DEBUG] recommend_anime: error fetching genre '{slug}': {e}")
                continue

        if not scored_items:
            result = {
                "status": "success",
                "action": f"Персональная рекомендация (понравилось: {', '.join(liked_titles)})",
                "data": "К сожалению, не удалось найти подходящих рекомендаций. Попробуйте указать другие аниме.",
                "errors": None,
            }
            return json.dumps(result, ensure_ascii=False)

        # Sort: first by genre_count (more matches = better), then by score
        sorted_items = sorted(
            scored_items.values(),
            key=lambda x: (x["genre_count"], x["score"]),
            reverse=True
        )

        # Take top N
        recommendations = sorted_items[:limit]

        # Format output with genre match explanations
        genre_name_map = {}
        for g in _fetch_genres():
            genre_name_map[g["slug"]] = g["name"]

        result_lines = []
        for i, item in enumerate(recommendations, 1):
            matched_genres = []
            for slug in item["matched_genres"]:
                name = genre_name_map.get(slug, slug)
                if name not in matched_genres:
                    matched_genres.append(name)

            genres_str = ", ".join(matched_genres) if matched_genres else "не определено"
            synopsis = (item["synopsis"] or "")[:200].strip()

            result_lines.append(
                f"{i}. **{item['title']}** (рейтинг: {item['rating']}, серий: {item['ep_count']})\n"
                f"   Совпадения: {genres_str}\n"
                f"   {synopsis}..."
            )

        formatted = "\n\n".join(result_lines)
        action_str = f"Персональная рекомендация (понравилось: {', '.join(liked_titles)})"

        result = {
            "status": "success",
            "action": action_str,
            "data": formatted,
            "errors": None,
        }

        logger.debug(f"[DEBUG] recommend_anime result: {len(recommendations)} recommendations")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": "Персональная рекомендация",
            "data": None,
            "errors": str(e),
        }
        logger.error(f"[DEBUG] recommend_anime error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


# ---- Staff/Studio Resolution ----

# Cache for people (composers, directors, voice actors)
_people_cache: Dict[str, int] = {}


def _search_person_by_name(name: str, max_pages: int = 10) -> Optional[int]:
    """
    Search for a person by name and return their Kitsu ID.

    Kitsu API does not support filter[name] for people endpoint, so we
    iterate through pages and match by name client-side.

    Args:
        name: Person's name (e.g., "Yoko Kanno", "Hayao Miyazaki")
        max_pages: Maximum number of pages to search (default 10, 200 people)

    Returns:
        Person ID if found, None otherwise.
    """
    if name in _people_cache:
        logger.debug(f"[DEBUG] _search_person_by_name: cache hit for '{name}'")
        return _people_cache[name]

    logger.debug(f"[DEBUG] _search_person_by_name: searching for '{name}'")
    try:
        name_lower = name.lower().strip()
        limit = 20  # Max page size for Kitsu API
        offset = 0

        for page in range(max_pages):
            url = f"{KITSU_API_BASE}/people?page[limit]={limit}&page[offset]={offset}"
            logger.debug(f"[DEBUG] _search_person_by_name: fetching page {page + 1}, offset={offset}")
            data = _cached_make_request(url)
            items = data.get("data", [])

            if not items:
                logger.debug(f"[DEBUG] _search_person_by_name: no more results at page {page + 1}")
                break

            # Search for exact or partial match
            for item in items:
                person_name = item.get("attributes", {}).get("name", "")
                if name_lower in person_name.lower() or person_name.lower() in name_lower:
                    person_id = item.get("id")
                    _people_cache[name] = person_id
                    logger.debug(f"[DEBUG] _search_person_by_name: found '{name}' -> '{person_name}' with ID={person_id}")
                    return person_id

            offset += limit

        logger.debug(f"[DEBUG] _search_person_by_name: no results for '{name}' after {max_pages} pages")
        return None
    except Exception as e:
        logger.error(f"[DEBUG] _search_person_by_name error for '{name}': {e}")
        return None


def _get_anime_by_person_id(
    person_id: int,
    role_filter: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get anime list for a person by their Kitsu ID.

    Uses the /people/{id}/staff endpoint to get staff roles, then fetches
    anime details for each role. Optionally filters by role (e.g., "Music").

    Args:
        person_id: Kitsu person ID.
        role_filter: Optional role filter (e.g., "Music", "Director").
                     If None, returns all anime regardless of role.
        limit: Maximum number of anime to return.

    Returns:
        List of anime dicts with 'id', 'title', 'rating', 'role' keys.
    """
    logger.debug(f"[DEBUG] _get_anime_by_person_id: person_id={person_id}, role_filter={role_filter}")
    try:
        # Step 1: Get staff entries for this person
        url = f"{KITSU_API_BASE}/people/{person_id}/staff?page[limit]=20"
        data = _cached_make_request(url)
        staff_entries = data.get("data", [])

        if not staff_entries:
            logger.debug(f"[DEBUG] _get_anime_by_person_id: no staff entries for person {person_id}")
            return []

        anime_list: List[Dict[str, Any]] = []
        seen_ids: set = set()

        for entry in staff_entries:
            if len(anime_list) >= limit:
                break

            entry_id = entry.get("id")
            attrs = entry.get("attributes", {})
            role = attrs.get("role", "")

            # Filter by role if specified
            if role_filter and role_filter.lower() not in role.lower():
                continue

            # Step 2: Get anime for this staff entry
            media_url = f"{KITSU_API_BASE}/media-staff/{entry_id}/media"
            media_data = _cached_make_request(media_url)
            media_item = media_data.get("data", {})

            if not media_item:
                continue

            anime_id = media_item.get("id")
            if anime_id in seen_ids:
                continue
            seen_ids.add(anime_id)

            media_attrs = media_item.get("attributes", {})
            anime_list.append({
                "id": anime_id,
                "title": media_attrs.get("canonicalTitle", "Unknown"),
                "rating": media_attrs.get("averageRating", "N/A"),
                "ep_count": media_attrs.get("episodeCount", "N/A"),
                "status": media_attrs.get("status", "N/A"),
                "role": role,
            })

        logger.debug(f"[DEBUG] _get_anime_by_person_id: found {len(anime_list)} anime")
        return anime_list

    except Exception as e:
        logger.error(f"[DEBUG] _get_anime_by_person_id error for person {person_id}: {e}")
        return []


# Cache for studios
_studio_cache: Dict[str, int] = {}


def _search_studio_by_name(name: str) -> Optional[int]:
    """
    Search for a studio by name and return their Kitsu ID.

    Args:
        name: Studio name (e.g., "Studio Ghibli", "Madhouse")

    Returns:
        Studio ID if found, None otherwise.
    """
    if name in _studio_cache:
        logger.debug(f"[DEBUG] _search_studio_by_name: cache hit for '{name}'")
        return _studio_cache[name]

    logger.debug(f"[DEBUG] _search_studio_by_name: searching for '{name}'")
    try:
        url = f"{KITSU_API_BASE}/studios?filter[name]={requests.utils.quote(name)}"
        data = _cached_make_request(url)
        items = data.get("data", [])
        if items:
            studio_id = items[0].get("id")
            _studio_cache[name] = studio_id
            logger.debug(f"[DEBUG] _search_studio_by_name: found '{name}' with ID={studio_id}")
            return studio_id
        logger.debug(f"[DEBUG] _search_studio_by_name: no results for '{name}'")
        return None
    except Exception as e:
        logger.error(f"[DEBUG] _search_studio_by_name error for '{name}': {e}")
        return None


# ---- Universal Filter Tool ----

# Mapping of filter types to Kitsu API parameter names
_FILTER_TYPE_MAP = {
    "genre": "genres",
    "category": "categories",
    "person": "person",
    "studio": "studio",
}

# Supported sort options
_SORT_OPTIONS = {
    "rating": "-averageRating",
    "popularity": "-subscriberCount",
    "newest": "-startDate",
    "oldest": "startDate",
    "episodes": "-episodeCount",
}


@tool
def search_anime_by_filter(
    filter_type: str,
    filter_value: str,
    sort: str = "rating",
    limit: int = 10
) -> str:
    """
    Универсальный поиск аниме по различным фильтрам.

    Поддерживаемые типы фильтров:
    - "genre" — поиск по жанру (action, comedy, romance, etc.)
    - "category" — поиск по категории/тегу (space, ninja, magical-girl, etc.)
    - "person" — поиск по человеку (композитор, режиссёр, сэйю)
    - "studio" — поиск по студии-производителю

    Args:
        filter_type: Тип фильтра (genre, category, person, studio)
        filter_value: Значение фильтра (название жанра, имя человека, название студии)
        sort: Сортировка результатов (rating, popularity, newest, oldest, episodes)
        limit: Максимальное количество результатов (1-20)

    Returns:
        JSON с результатами поиска.
    """
    logger.debug(f"[DEBUG] search_anime_by_filter: type={filter_type}, value={filter_value}, sort={sort}")

    # Validate filter_type
    filter_type_lower = filter_type.lower().strip()
    if filter_type_lower not in _FILTER_TYPE_MAP:
        result = {
            "status": "error",
            "action": f"Поиск аниме по фильтру: {filter_type}={filter_value}",
            "data": None,
            "errors": f"Неподдерживаемый тип фильтра '{filter_type}'. Доступные: {', '.join(_FILTER_TYPE_MAP.keys())}",
        }
        return json.dumps(result, ensure_ascii=False)

    # Validate sort
    sort_lower = sort.lower().strip()
    if sort_lower not in _SORT_OPTIONS:
        sort_lower = "rating"

    # Validate limit
    limit = max(1, min(20, limit))

    api_filter_key = _FILTER_TYPE_MAP[filter_type_lower]
    sort_value = _SORT_OPTIONS[sort_lower]

    try:
        # Resolve filter value based on type
        if filter_type_lower in ("genre", "category"):
            # Use existing genre resolution (supports aliases, slugs, etc.)
            resolved_value = _resolve_genre_slug(filter_value)
            if resolved_value is None:
                result = {
                    "status": "error",
                    "action": f"Поиск аниме по фильтру: {filter_type}={filter_value}",
                    "data": None,
                    "errors": f"Не удалось найти {filter_type} '{filter_value}'. Используй get_tags() для просмотра доступных жанров.",
                }
                return json.dumps(result, ensure_ascii=False)
            api_filter_value = resolved_value

        elif filter_type_lower == "person":
            # Search for person by name and get their anime
            person_id = _search_person_by_name(filter_value)
            if person_id is None:
                result = {
                    "status": "error",
                    "action": f"Поиск аниме по человеку: {filter_value}",
                    "data": None,
                    "errors": f"Человек '{filter_value}' не найден в базе Kitsu",
                }
                return json.dumps(result, ensure_ascii=False)

            # Use _get_anime_by_person_id to get anime list
            # Kitsu API doesn't support filter[person]=ID, so we use staff endpoint
            anime_list = _get_anime_by_person_id(person_id, limit=limit)

            if not anime_list:
                result = {
                    "status": "success",
                    "action": f"Поиск аниме по человеку: {filter_value}",
                    "data": f"Аниме с участием '{filter_value}' не найдены.",
                    "errors": None,
                }
                return json.dumps(result, ensure_ascii=False)

            # Format the result
            result_lines = []
            for anime in anime_list:
                result_lines.append(
                    f"- [{anime['id']}] {anime['title']} (рейтинг: {anime['rating']}, "
                    f"серий: {anime['ep_count']}, статус: {anime['status']})\n"
                    f"  Роль: {anime['role']}"
                )

            result = {
                "status": "success",
                "action": f"Поиск аниме: {filter_type}={filter_value}",
                "data": "\n\n".join(result_lines),
                "errors": None,
            }
            logger.debug(f"[DEBUG] search_anime_by_filter: found {len(anime_list)} anime for person")
            return json.dumps(result, ensure_ascii=False)

        elif filter_type_lower == "studio":
            # Search for studio by name
            studio_id = _search_studio_by_name(filter_value)
            if studio_id is None:
                result = {
                    "status": "error",
                    "action": f"Поиск аниме по студии: {filter_value}",
                    "data": None,
                    "errors": f"Студия '{filter_value}' не найдена в базе Kitsu",
                }
                return json.dumps(result, ensure_ascii=False)
            api_filter_value = str(studio_id)

        else:
            # Should not reach here due to validation above
            api_filter_value = filter_value

        # Build API URL
        url = f"{KITSU_API_BASE}/anime?filter[{api_filter_key}]={requests.utils.quote(api_filter_value)}&sort={sort_value}&page[limit]={limit}"
        logger.debug(f"[DEBUG] search_anime_by_filter: URL={url}")

        data = _cached_make_request(url)

        result = {
            "status": "success",
            "action": f"Поиск аниме: {filter_type}={filter_value} (сортировка: {sort})",
            "data": _format_anime_list(data, max_results=limit),
            "errors": None,
        }

        logger.debug(f"[DEBUG] search_anime_by_filter: found results")
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "action": f"Поиск аниме по фильтру: {filter_type}={filter_value}",
            "data": None,
            "errors": str(e),
        }
        logger.error(f"[DEBUG] search_anime_by_filter error: {e}")
        return json.dumps(error_result, ensure_ascii=False)


# Export all tools as a list
KITSU_TOOLS = [
    search_anime,
    get_anime_details,
    get_anime_info,
    get_anime_by_genre,
    get_trending_anime,
    get_tags,
    find_similar_anime,
    recommend_anime,
    search_anime_by_filter,
]
