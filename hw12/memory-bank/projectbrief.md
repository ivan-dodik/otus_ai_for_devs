# Project Brief: LangChain Anime Recommendation Agent

## Core Requirements
- Build a minimal AI agent using LangChain that acts as a natural language wrapper over the Kitsu API
- Agent runs locally with Ollama (llama3.1:8b, configurable)
- No persistent database — session data stored in memory
- Agent answers in a fixed structured format

## Key Goals
1. Accept natural language queries about anime preferences
2. Interpret user intent (recommendations, search, info lookup)
3. Call Kitsu API methods via LangChain tools
4. Return structured results with status

## Scope
- Kitsu API domain: anime search, details, genre filtering, recommendations based on preferences
- Local LLM: Ollama with llama3.1:8b
- Session memory: conversation history kept during session (MemorySaver)
- CLI-based interaction (single-shot and interactive modes with `--interactive` flag)
- Flask Web UI for browser-based interaction

## Constraints
- No API keys committed to repository
- `.env.example` provided for configuration
- Minimum 5 test queries, 3 must trigger actual API calls
- All prompts documented in Markdown