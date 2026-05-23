# Testing Strategy: LangChain Anime Recommendation Agent

## Overview
The agent is tested through integration tests that verify the full pipeline: user query → LLM → tool selection → API call → structured response.

## Test Queries (5 required, ≥3 must trigger API calls)

| # | Query | Expected Tool | API Call | Status |
|---|-------|---------------|----------|--------|
| 1 | "Найди аниме Cowboy Bebop и покажи информацию о нём" | `search_anime` | ✅ | ✅ |
| 2 | "Покажи топ популярных аниме" | `get_trending_anime` | ✅ | ✅ |
| 3 | "Подбери аниме в жанре комедия" | `get_anime_by_genre` | ✅ | ✅ |
| 4 | "Я смотрел Cowboy Bebop, мне понравилось. Что ещё посмотреть?" | `search_anime` | ✅ | ✅ |
| 5 | "Расскажи про аниме Naruto" | `search_anime` + `get_anime_details` | ✅ | ✅ |

## Testing Methods

### 1. CLI Testing
```bash
# Single query mode
python main.py "Найди аниме Cowboy Bebop"

# Interactive mode
python main.py --interactive

# With debug output
python main.py --debug "Найди аниме Cowboy Bebop"

# Custom model
python main.py --model llama3.2:3b "Найди аниме Cowboy Bebop"
```

### 2. Flask Web UI Testing
```bash
python -m web.app
# Open http://localhost:5000 in browser
```

### 3. Tool Unit Testing
```bash
python -c "from tools.kitsu_tools import search_anime; print(search_anime('Cowboy Bebop'))"
python -c "from tools.kitsu_tools import get_trending_anime; print(get_trending_anime())"
python -c "from tools.kitsu_tools import get_anime_by_genre; print(get_anime_by_genre('comedy'))"
python -c "from tools.kitsu_tools import get_anime_details; print(get_anime_details(1))"
```

### 4. Agent Testing
```bash
python -c "from agent.agent import process_query; print(process_query('найди аниме Cowboy Bebop'))"
```

## Expected Response Format
All responses must follow the contract:
```
Status: success | error
Action: <описание действия>
Data: <результат API>
Errors: <если есть>
```

## Edge Cases to Test
1. **Empty query** — agent should ask for clarification
2. **Non-anime query** — agent should politely refuse
3. **API down** — agent should return appropriate error message
4. **LLM unavailable** (Ollama not running) — agent should handle gracefully
5. **Ordinal references** — "расскажи про второе аниме" should reference agent's own list
6. **Russian queries** — agent should respond in Russian, translate descriptions
7. **Debug mode** — `--debug` flag should show logging, without should hide it

## Grading Criteria Verification
| Criterion | Verification Method |
|-----------|-------------------|
| 1. Agent starts | Run `python main.py "test"` |
| 2. API tool call | Check `tools/kitsu_tools.py` for HTTP requests |
| 3. Intent interpretation | Run test queries, verify correct tool called |
| 4. Response contract | Check output format matches Status/Action/Data/Errors |
| 5. 5 test queries | Documented in report.md and README.md |
| 6. Prompts documented | Check agent-prompts.md |
| 7. No secrets committed | Check .env in .gitignore, .env.example has no keys |