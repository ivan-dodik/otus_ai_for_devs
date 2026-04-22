from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
import datetime

app = Flask(__name__)

# Настройка CORS с ограниченным списком разрешенных доменов
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Настройка ограничения скорости запросов
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Конфигурация Swagger
app.config['SWAGGER'] = {
    'title': 'Mini-Questionnaire API',
    'uiversion': 3,
    'version': '1.0.0',
    'openapi': '3.0.0',
    'docs_url': '/apidocs',
    'swagger_ui': True,
    'specs': [
        {
            'version': '1.0.0',
            'title': 'Mini-Questionnaire API',
            'endpoint': 'specs',
            'route': '/specs',
        }
    ]
}

Swagger(app)

# Жестко заданные вопросы для опросника
QUESTIONS = [
    {"id": 1, "question": "Как вас зовут?", "type": "text"},
    {"id": 2, "question": "Сколько вам лет?", "type": "number"},
    {"id": 3, "question": "Какой ваш любимый язык программирования?", "type": "text"},
    {"id": 4, "question": "Сколько у вас лет опыта?", "type": "number"},
    {"id": 5, "question": "Какая ваша предпочтительная среда разработки?", "type": "text"}
]

# In-memory storage for answers
answers_store = []

@app.route('/questions', methods=['GET'])
def get_questions():
    """
    Получить список вопросов анкеты
    ---
    tags:
      - Анкета
    summary: Возвращает список вопросов
    description: Возвращает массив вопросов с их идентификаторами, текстом и типом
    responses:
      200:
        description: Успешный ответ со списком вопросов
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Уникальный идентификатор вопроса
                    example: 1
                  question:
                    type: string
                    description: Текст вопроса
                    example: "Как вас зовут?"
                  type:
                    type: string
                    description: Тип поля для ввода (text или number)
                    example: "text"
      500:
        description: Внутренняя ошибка сервера
    """
    return jsonify(QUESTIONS)

@app.route('/answers', methods=['POST'])
@limiter.limit("10 per minute")
def submit_answers():
    """
    Отправить ответы на анкету
    ---
    tags:
      - Анкета
    summary: Принимает и сохраняет ответы пользователя
    description: Принимает JSON с ответами на вопросы и сохраняет их в памяти
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              question-1:
                type: string
                description: Ответ на первый вопрос (имя)
                example: "Иван Иванов"
              question-2:
                type: integer
                description: Ответ на второй вопрос (возраст)
                example: 25
              question-3:
                type: string
                description: Ответ на третий вопрос (любимый язык программирования)
                example: "Python"
              question-4:
                type: integer
                description: Ответ на четвертый вопрос (лет опыта)
                example: 5
              question-5:
                type: string
                description: Ответ на пятый вопрос (среда разработки)
                example: "VS Code"
    responses:
      201:
        description: Ответы успешно сохранены
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Сообщение об успехе
                  example: "Спасибо! Ваши ответы записаны."
      400:
        description: Ошибка валидации - данные не предоставлены или некорректны
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Сообщение об ошибке
                  example: "Данные не предоставлены"
      500:
        description: Внутренняя ошибка сервера
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400
    
    # Валидация структуры данных
    expected_questions = ['question-1', 'question-2', 'question-3', 'question-4', 'question-5']
    for q in expected_questions:
        if q not in data:
            return jsonify({"error": f"Отсутствует ответ на вопрос {q}"}), 400
        
        # Валидация типа данных
        value = data[q]
        if not isinstance(value, (str, int, float)):
            return jsonify({"error": f"Неверный тип данных for {q}. Ожидается строка или число."}), 400
        
        # Валидация длины строки
        if isinstance(value, str):
            if len(value.strip()) == 0:
                return jsonify({"error": f"Ответ on {q} не может быть пустым"}), 400
            if len(value) > 500:
                return jsonify({"error": f"Ответ on {q} слишком длинный (максимум 500 символов)"}), 400
        
        # Валидация возраста (question-2)
        if q == 'question-2':
            try:
                age = int(value)
                if age < 0 or age > 150:
                    return jsonify({"error": "Возраст должен быть between 0 and 150"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Возраст должен быть числом"}), 400
        
        # Валидация опыта (question-4)
        if q == 'question-4':
            try:
                exp = int(value)
                if exp < 0 or exp > 100:
                    return jsonify({"error": "Опыт должен be between 0 and 100"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Опыт должен be a number"}), 400
    
    # Добавляем временную метку к записи ответа
    answer_record = {
        "answers": data,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Сохраняем в памяти
    answers_store.append(answer_record)
    
    print(f"Получены ответы: {data}")
    print(f"Всего сохранено ответов: {len(answers_store)}")
    
    return jsonify({"message": "Спасибо! Ваши ответы записаны."}), 201

@app.route('/answers', methods=['GET'])
def get_answers():
    """
    Получить все сохраненные ответы
    ---
    tags:
      - Отладка
    summary: Возвращает все сохраненные ответы (для отладки)
    description: Возвращает массив всех ответов с временными метками
    responses:
      200:
        description: Успешный ответ со списком всех ответов
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  answers:
                    type: object
                    description: Объект с ответами на вопросы
                  timestamp:
                    type: string
                    format: date-time
                    description: Временная метка отправки
                    example: "2026-04-22T12:34:56.789012"
      500:
        description: Внутренняя ошибка сервера
    """
    return jsonify(answers_store)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Проверка работоспособности
    ---
    tags:
      - Системные
    summary: Проверяет работоспособность backend
    description: Возвращает статус "ok" если backend работает
    responses:
      200:
        description: Backend работает нормально
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  description: Статус работоспособности
                  example: "ok"
                message:
                  type: string
                  description: Сообщение о состоянии
                  example: "Backend запущен"
      500:
        description: Внутренняя ошибка сервера
    """
    return jsonify({"status": "ok", "message": "Backend запущен"})

if __name__ == '__main__':
    print("Запуск Mini-Questionnaire Backend...")
    print("Доступные эндпоинты:")
    print("  GET  /questions - Получить список вопросов")
    print("  POST /answers   - Отправить ответы")
    print("  GET  /answers   - Просмотр сохраненных ответов (отладка)")
    print("  GET  /health    - Проверка работоспособности")
    print("  GET  /apidocs   - Swagger документация API")
    app.run(debug=True, host='0.0.0.0', port=5000)
