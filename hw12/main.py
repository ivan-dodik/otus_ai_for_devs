#!/usr/bin/env python3
"""
CLI entry point for the LangChain Anime Recommendation Agent.

Usage:
    python main.py "найди аниме Cowboy Bebop"
    python main.py --interactive
"""

import argparse
import sys

from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt

from agent.agent import process_query, clear_session
from config import config, setup_logging


def interactive_mode():
    """Run the agent in interactive mode with session memory."""
    print("=" * 60)
    print(" LangChain Anime Recommendation Agent")
    print("=" * 60)
    print("Введите ваш запрос об аниме.")
    print("Команды: /exit — выход, /clear — очистить историю")
    print("-" * 60)

    session_id = "cli_interactive"

    while True:
        try:
            user_input = prompt(
                "\nВы: ",
                history=InMemoryHistory()
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/exit":
            print("До свидания!")
            break

        if user_input.lower() == "/clear":
            clear_session(session_id)
            print("[История сессии очищена]")
            continue

        print("\nАгент обрабатывает запрос...")
        result = process_query(user_input, session_id=session_id)
        print(f"\n{result}")


def main():
    parser = argparse.ArgumentParser(
        description="LangChain Anime Recommendation Agent — подбор аниме через естественный язык"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help='Запрос на естественном языке (например: "найди аниме Cowboy Bebop")',
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Интерактивный режим с сохранением истории диалога",
    )
    parser.add_argument(
        "--model",
        "-m",
        help="Модель Ollama (например: llama3.1:8b, llama3.2:3b, mistral:7b). "
        "Переопределяет OLLAMA_MODEL из .env",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Включить DEBUG-вывод (лог вызовов инструментов)",
    )

    args = parser.parse_args()
    if args.model:
        config.OLLAMA_MODEL = args.model
    if args.debug:
        config.DEBUG = True

    # Настройка логирования после парсинга аргументов
    setup_logging()

    if args.interactive:
        interactive_mode()
    elif args.query:
        try:
            result = process_query(args.query)
            print(result)
        except KeyboardInterrupt:
            print("\n(прервано пользователем)")
            sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()