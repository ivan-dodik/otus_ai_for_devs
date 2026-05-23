"""
Agent setup for the anime recommendation agent.

Creates a LangChain ReAct agent with:
- Ollama LLM (llama3.1:8b, configurable)
- Kitsu API tools
- Session memory via MemorySaver (LangGraph checkpointing)
- System prompt enforcing response contract

Uses singleton pattern for agent reuse across requests.
"""

import logging
from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

from agent.prompts import SYSTEM_PROMPT
from config import config
from tools.kitsu_tools import KITSU_TOOLS

logger = logging.getLogger(__name__)

# Global agent instance (singleton pattern)
_agent_instance: tuple | None = None


def _create_llm() -> ChatOllama:
    """Create and configure the Ollama LLM instance."""
    return ChatOllama(
        base_url=config.OLLAMA_BASE_URL,
        model=config.OLLAMA_MODEL,
        temperature=config.effective_temperature,
        num_predict=config.effective_num_predict,
        top_p=config.effective_top_p,
        top_k=config.effective_top_k,
        request_timeout=config.OLLAMA_REQUEST_TIMEOUT,
    )


def get_agent(session_id: str | None = None):
    """
    Get (or create) the singleton LangChain ReAct agent with session memory.

    Uses singleton pattern to avoid recreating the LLM on every request.
    Each session gets its own checkpointer thread for memory isolation.

    Args:
        session_id: Optional session ID for memory isolation.

    Returns:
        Tuple of (agent, checkpointer).
    """
    global _agent_instance

    if _agent_instance is None:
        logger.info(
            f"Creating agent: model={config.OLLAMA_MODEL}, "
            f"temp={config.effective_temperature}, top_p={config.effective_top_p}, "
            f"top_k={config.effective_top_k}"
        )
        llm = _create_llm()
        checkpointer = MemorySaver()
        agent = create_agent(
            model=llm,
            tools=KITSU_TOOLS,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=checkpointer,
        )
        _agent_instance = (agent, checkpointer)

    return _agent_instance


def process_query(query: str, session_id: str | None = None) -> str:
    """
    Process a user query through the agent and return the response.

    Args:
        query: User's natural language query.
        session_id: Optional session ID for memory isolation.

    Returns:
        Agent's response as a string.
    """
    agent, checkpointer = get_agent()
    thread_id = session_id or "default"

    # Build messages from session history + new query
    history = _get_session_history(session_id)
    messages = list(history) + [{"role": "user", "content": query}]

    # Configure thread for checkpointing
    config_thread = {"configurable": {"thread_id": thread_id}}

    try:
        # Invoke the agent
        response = agent.invoke(
            {"messages": messages},
            config=config_thread,
        )

        # Extract the final message
        response_messages = response.get("messages", [])
        if response_messages:
            final_msg = response_messages[-1]
            result = final_msg.content if hasattr(final_msg, "content") else str(final_msg)
        else:
            result = "Agent returned no response."

        # Save to session history (user message + assistant response)
        _session_messages[thread_id].append({"role": "user", "content": query})
        _session_messages[thread_id].append({"role": "assistant", "content": result})

        logger.debug(f"process_query: session={thread_id}, query_len={len(query)}, response_len={len(result)}")
        return result

    except Exception as e:
        error_msg = f"Ошибка обработки запроса: {str(e)}"
        logger.error(f"process_query error: {e}")
        return error_msg


# Global session store: session_id -> list of messages
_session_messages: Dict[str, List[Dict[str, str]]] = {}


def _get_session_history(session_id: str | None = None) -> List[Dict[str, str]]:
    """Get or create message history for a session."""
    sid = session_id or "default"
    if sid not in _session_messages:
        _session_messages[sid] = []
    return _session_messages[sid]


def clear_session(session_id: str | None = None):
    """Clear session history for a given session ID."""
    sid = session_id or "default"
    if sid in _session_messages:
        del _session_messages[sid]
        logger.info(f"Session cleared: {sid}")


def reset_agent():
    """Reset the singleton agent instance (useful for testing)."""
    global _agent_instance
    _agent_instance = None
    logger.info("Agent singleton reset")