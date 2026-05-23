# Kitsu API Reference

## Overview
Kitsu is a public REST API for anime and manga data. No authentication required for read operations.
Base URL: `https://kitsu.io/api/edge`

## Rate Limits
- Public API: no API key needed
- Rate-limited per IP address
- Typical limit: ~120 requests per minute

## Endpoints Used

### Search Anime
```
GET /api/edge/anime?filter[text]={query}
```
- **Description:** Search anime by title or keywords
- **Params:** `filter[text]` — search query string
- **Response:** JSON:API collection of anime objects
- **Example:** `GET /api/edge/anime?filter[text]=Cowboy%20Bebop`

### Anime Details by ID
```
GET /api/edge/anime/{id}
```
- **Description:** Get detailed information about a specific anime
- **Params:** `id` — numeric anime ID (e.g., 1, 4224, 1535)
- **Response:** JSON:API single resource object
- **Example:** `GET /api/edge/anime/1`

### Anime by Genre
```
GET /api/edge/anime?filter[genres]={genre}
```
- **Description:** Filter anime by genre name
- **Params:** `filter[genres]` — genre name (English)
- **Response:** JSON:API collection of anime objects
- **Example:** `GET /api/edge/anime?filter[genres]=action`

### Trending Anime
```
GET /api/edge/trending/anime
```
- **Description:** Get currently trending/popular anime
- **Params:** None
- **Response:** JSON:API collection of trending anime objects
- **Example:** `GET /api/edge/trending/anime`

## Response Format (JSON:API)
All endpoints return data in JSON:API format:
```json
{
  "data": [
    {
      "id": "1",
      "type": "anime",
      "attributes": {
        "slug": "cowboy-bebop",
        "canonicalTitle": "Cowboy Bebop",
        "synopsis": "...",
        "averageRating": "82.26",
        "episodeCount": 26,
        "status": "finished",
        "startDate": "1998-04-03",
        "endDate": "1999-04-24",
        "ageRatingGuide": "PG-13",
        "nsfw": false,
        "genres": ["action", "adventure", "comedy", "drama", "sci-fi"]
      }
    }
  ],
  "meta": {
    "count": 1
  }
}
```

## Error Handling
- **404 Not Found:** Resource doesn't exist
- **429 Too Many Requests:** Rate limit exceeded
- **503 Service Unavailable:** API temporarily unavailable

## Endpoints for People (Staff)

### Search Person by Name (Pagination)
```
GET /api/edge/people?page[limit]=20&page[offset]=0
```
- **Description:** Kitsu API does NOT support `filter[name]` for people endpoint. Must use pagination and client-side filtering.
- **Params:** `page[limit]` (max 20), `page[offset]` for pagination
- **Response:** JSON:API collection of people objects
- **Implementation:** `_search_person_by_name()` iterates through pages and matches by name

### Get Staff Roles for Person
```
GET /api/edge/people/{id}/staff
```
- **Description:** Get all staff roles (Music, Director, etc.) for a specific person
- **Params:** `id` — numeric person ID
- **Response:** JSON:API collection of mediaStaff objects with `role` attribute
- **Example:** `GET /api/edge/people/15/staff` (Yoko Kanno)

### Get Anime for Staff Entry
```
GET /api/edge/media-staff/{id}/media
```
- **Description:** Get the anime associated with a specific staff entry
- **Params:** `id` — numeric mediaStaff ID
- **Response:** JSON:API single anime object
- **Implementation:** `_get_anime_by_person_id()` uses this to get anime list

## Implemented Tools
| Tool | Endpoint | Python Method |
|------|----------|---------------|
| `search_anime` | `GET /anime?filter[text]={query}` | `tools/kitsu_tools.py:search_anime()` |
| `get_anime_details` | `GET /anime/{id}` | `tools/kitsu_tools.py:get_anime_details()` |
| `get_anime_by_genre` | `GET /anime?filter[genres]={genre}` | `tools/kitsu_tools.py:get_anime_by_genre()` |
| `get_trending_anime` | `GET /trending/anime` | `tools/kitsu_tools.py:get_trending_anime()` |
| `get_tags` | `GET /genres` | `tools/kitsu_tools.py:get_tags()` |
| `find_similar_anime` | `GET /anime/{id}/categories` + search | `tools/kitsu_tools.py:find_similar_anime()` |
| `recommend_anime` | Multiple endpoints | `tools/kitsu_tools.py:recommend_anime()` |
| `search_anime_by_filter` | Various (genre, person, studio) | `tools/kitsu_tools.py:search_anime_by_filter()` |

## API Limitations

### People Search
- **`filter[name]` NOT supported** — Returns 400 error: "name is not allowed"
- **Workaround:** Use pagination (`page[limit]=20&page[offset]=N`) and client-side name matching
- **Implementation:** `_search_person_by_name()` iterates up to 10 pages (200 people)

### Anime by Person Filter
- **`filter[person]={id}` NOT supported** for anime endpoint
- **Workaround:** Use `/people/{id}/staff` → `/media-staff/{id}/media` chain
- **Implementation:** `_get_anime_by_person_id()` fetches staff entries, then anime for each
