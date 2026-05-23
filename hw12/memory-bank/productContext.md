# Product Context: LangChain Anime Recommendation Agent

## Why This Project Exists
This is a homework assignment for the course "AI for Developers". The goal is to build a minimal AI agent using LangChain that demonstrates:
- Natural language interface over a real API
- Tool-based agent architecture
- Local LLM integration with Ollama

## Problems It Solves
- Users can discover anime recommendations through natural conversation instead of manual API queries
- Eliminates the need to know Kitsu API endpoints or query syntax
- Provides personalized recommendations based on user's viewing history and preferences
- Session memory allows contextual follow-up questions without repeating context

## How It Should Work
1. User describes anime they've watched and their preferences (liked/disliked)
2. Agent interprets the intent and queries Kitsu API via tools
3. Agent analyzes results and provides structured recommendations
4. User can refine, ask for details, or request different recommendations
5. Session memory maintains conversation context

## User Experience Goals
- CLI-based interaction: `python main.py "запрос пользователя"`
- Natural Russian language queries supported
- Structured response format: Status, Action, Data, Errors
- Fast responses using local LLM (no cloud dependency)
- Clear error messages when API or LLM fails