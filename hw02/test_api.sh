#!/bin/bash

# Скрипт тестирования API для Мини-анкеты
# Убедитесь, что backend запущен перед выполнением этого скрипта

API_URL="http://localhost:5000"

echo "🧪 Тестирование API Мини-анкеты"
echo "=================================="
echo ""

# Проверяем, запущен ли backend
echo "1. Проверка работоспособности backend..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)

if [ "$HEALTH_RESPONSE" -eq 200 ]; then
    echo "   ✅ Backend запущен"
    echo ""
    echo "   Ответ проверки работоспособности:"
    curl -s $API_URL/health | python -m json.tool
else
    echo "   ❌ Backend не запущен или недоступен"
    echo "   Пожалуйста, запустите backend командой: uv run python backend/app.py"
    exit 1
fi

echo ""
echo "2. Получение вопросов..."
QUESTIONS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/questions)

if [ "$QUESTIONS_RESPONSE" -eq 200 ]; then
    echo "   ✅ Вопросы успешно получены"
    echo ""
    echo "   Вопросы:"
    curl -s $API_URL/questions | python -m json.tool
else
    echo "   ❌ Не удалось получить вопросы"
    exit 1
fi

echo ""
echo "3. Отправка тестовых ответов..."
# Отправляем тестовые ответы
TEST_DATA='{
    "question-1": "Иван Иванов",
    "question-2": "25",
    "question-3": "Python",
    "question-4": "5",
    "question-5": "VS Code"
}'

SUBMIT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $API_URL/answers \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA")

if [ "$SUBMIT_RESPONSE" -eq 201 ]; then
    echo "   ✅ Ответы успешно отправлены"
    echo ""
    echo "   Ответ сервера:"
    curl -s -X POST $API_URL/answers \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" | python -m json.tool
else
    echo "   ❌ Не удалось отправить ответы (HTTP $SUBMIT_RESPONSE)"
    exit 1
fi

echo ""
echo "4. Получение сохраненных ответов..."
ANSWERS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/answers)

if [ "$ANSWERS_RESPONSE" -eq 200 ]; then
    echo "   ✅ Ответы успешно получены"
    echo ""
    echo "   Сохраненные ответы:"
    curl -s $API_URL/answers | python -m json.tool
else
    echo "   ❌ Не удалось получить ответы"
fi

echo ""
echo "=================================="
echo "✅ Все тесты пройдены!"
echo "API Мини-анкеты работает корректно."
