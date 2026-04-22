#!/usr/bin/env python3
"""
Скрипт тестирования API для Мини-анкеты
Альтернатива bash скрипту, работает на всех платформах
"""

import requests
import json
import sys

API_URL = "http://localhost:5000"

def test_health():
    """Тестирование эндпоинта проверки работоспособности"""
    print("🔍 Тестирование проверки работоспособности...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Backend запущен")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Проверка работоспособности не удалась (HTTP {response.status_code})")
            return False
    except requests.ConnectionError:
        print("❌ Не удалось подключиться к backend. Убедитесь, что он запущен на порту 5000.")
        return False

def test_get_questions():
    """Тестирование получения вопросов"""
    print("\n📋 Тестирование GET /questions...")
    try:
        response = requests.get(f"{API_URL}/questions")
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ Получено {len(questions)} вопросов")
            for q in questions:
                print(f"   - {q['question']} ({q['type']})")
            return True
        else:
            print(f"❌ Не удалось получить вопросы (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_post_answers():
    """Тестирование отправки ответов"""
    print("\n✍️  Тестирование POST /answers...")
    test_data = {
        "question-1": "Алиса Иванова",
        "question-2": 28,
        "question-3": "Python",
        "question-4": 5,
        "question-5": "VS Code"
    }
    
    try:
        response = requests.post(f"{API_URL}/answers", json=test_data)
        if response.status_code == 201:
            print("✅ Ответы успешно отправлены")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Не удалось отправить ответы (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_get_answers():
    """Тестирование получения сохраненных ответов"""
    print("\n💾 Тестирование GET /answers...")
    try:
        response = requests.get(f"{API_URL}/answers")
        if response.status_code == 200:
            answers = response.json()
            print(f"✅ Получено {len(answers)} сохраненных ответов")
            if answers:
                print("   Последний ответ:")
                latest = answers[-1]
                print(f"   Временная метка: {latest['timestamp']}")
                for key, value in latest['answers'].items():
                    print(f"     {key}: {value}")
            return True
        else:
            print(f"❌ Не удалось получить ответы (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🧪 Набор тестов API для Мини-анкеты")
    print("=" * 50)
    
    tests = [
        test_health,
        test_get_questions,
        test_post_answers,
        test_get_answers
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ Все {total} тестов пройдены!")
        print("API Мини-анкеты работает корректно.")
        return 0
    else:
        print(f"❌ {total - passed} из {total} тестов не пройдены.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
