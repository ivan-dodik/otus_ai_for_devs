# Как работает Backend: подробное руководство

## 📋 Содержание

1. [Структура приложения](#структура-приложения)
2. [Инициализация Flask приложения](#инициализация-flask-приложения)
3. [Настройка CORS](#настройка-cors)
4. [Создание API endpoint'ов](#создание-api-endpoint'ов)
5. [Валидация данных](#валидация-данных)
6. [Rate Limiting](#rate-limiting)
7. [Хранение данных](#хранение-данных)
8. [Обработка ошибок](#обработка-ошибок)
9. [Логирование](#логирование)
10. [Запуск и отладка](#запуск-и-отладка)

## 🏗️ Структура приложения

### Файловая структура

```
backend/
├── app.py                 # Основной файл приложения
├── pyproject.toml         # Зависимости и конфигурация
└── __pycache__/           # Скомпилированные файлы (автоматически)
```

### Структура кода app.py

```python
# 1. Импорты библиотек
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
# ...

# 2. Инициализация приложения
app = Flask(__name__)

# 3. Настройка расширений
CORS(app, ...)
limiter = Limiter(...)

# 4. Глобальные переменные
QUESTIONS = [...]
answers_store = []

# 5. Декораторы и middleware
@app.before_request
def log_request():
    ...

# 6. Маршруты (endpoint'ы)
@app.route('/health', methods=['GET'])
def health_check():
    ...

# 7. Точка входа
if __name__ == '__main__':
    app.run(...)
```

## 🚀 Инициализация Flask приложения

### Базовая инициализация

```python
from flask import Flask

# Создание экземпляра приложения
app = Flask(__name__)

# Конфигурация приложения
app.config.update(
    DEBUG=True,  # Режим отладки
    SECRET_KEY='dev-secret-key',  # Секретный ключ для сессий
    JSON_AS_ASCII=False  # Поддержка Unicode в JSON
)
```

**Что происходит:**
1. `Flask(__name__)` создает новое приложение
2. `__name__` используется для определения пути к ресурсам
3. `app.config` хранит настройки приложения

### Конфигурационные параметры

**Важные настройки:**
```python
app.config.update(
    # Режим отладки (включает автоперезагрузку)
    DEBUG=True,
    
    # Секретный ключ для шифрования сессий
    SECRET_KEY='ваш-секретный-ключ',
    
    # Настройки JSON
    JSON_SORT_KEYS=False,  # Не сортировать ключи
    JSON_AS_ASCII=False,   # Поддержка кириллицы
    
    # Настройки сервера
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # Макс. размер запроса (16MB)
)
```

## 🌐 Настройка CORS

### Проблема跨доменных запросов

**Ситуация:**
- Frontend загружается с `http://localhost:8080`
- Backend работает на `http://localhost:5000`
- Браузер блокирует запросы между разными доменами

**Решение:**
```python
from flask_cors import CORS

# Простая настройка (разрешить все)
CORS(app)

# Настройка с ограничениями
CORS(app, resources={
    r"/api/*": {  # Применяется только к /api/*
        "origins": [  # Разрешенные источники
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Как работает CORS

**1. Pre-flight запрос (OPTIONS):**
```http
OPTIONS /answers HTTP/1.1
Host: localhost:5000
Origin: http://localhost:8080
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

**2. Ответ сервера:**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 3600
```

**3. Основной запрос:**
```http
POST /answers HTTP/1.1
Host: localhost:5000
Origin: http://localhost:8080
Content-Type: application/json

{"question-1": "Иван", ...}
```

## 🎯 Создание API endpoint'ов

### Декоратор @app.route

```python
@app.route('/path', methods=['GET', 'POST'])
def function_name():
    # Логика endpoint'а
    return response
```

**Параметры:**
- `'/path'` - URL путь
- `methods` - разрешенные HTTP методы
- `endpoint` - имя endpoint'а (по умолчанию имя функции)

### Endpoint проверки работоспособности

```python
@app.route('/health', methods=['GET'])
def health_check():
    """
    Проверка работоспособности сервера.
    
    Returns:
        JSON с статусом сервера
    """
    return jsonify({
        'status': 'ok',
        'message': 'Сервер работает',
        'timestamp': datetime.now().isoformat()
    }), 200
```

**Использование:**
```bash
curl http://localhost:5000/health
# {"status": "ok", "message": "Сервер работает", "timestamp": "2024-04-22T10:30:00"}
```

### Endpoint получения вопросов

```python
@app.route('/questions', methods=['GET'])
def get_questions():
    """
    Получить список всех вопросов.
    
    Returns:
        JSON массив с вопросами
    """
    return jsonify(QUESTIONS), 200
```

**Структура вопроса:**
```python
QUESTIONS = [
    {
        "id": 1,
        "question": "Как вас зовут?",
        "type": "text",
        "required": True
    },
    {
        "id": 2,
        "question": "Сколько вам лет?",
        "type": "number",
        "required": True,
        "min": 1,
        "max": 150
    }
]
```

### Endpoint отправки ответов

```python
@app.route('/answers', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def submit_answers():
    """
    Принять и сохранить ответы пользователя.
    
    Request Body:
        JSON с ответами на вопросы
        
    Returns:
        JSON с подтверждением и ID ответа
    """
    
    # 1. Получение данных из запроса
    data = request.get_json()
    
    # 2. Проверка наличия данных
    if not data:
        return jsonify({
            'error': 'Тело запроса должно быть в формате JSON'
        }), 400
    
    # 3. Валидация данных
    is_valid, error_message = validate_answers(data)
    if not is_valid:
        return jsonify({
            'error': error_message
        }), 400
    
    # 4. Создание записи об ответе
    answer_entry = {
        'id': len(answers_store) + 1,
        'timestamp': datetime.now().isoformat(),
        'answers': data
    }
    
    # 5. Сохранение в хранилище
    answers_store.append(answer_entry)
    
    # 6. Логирование
    app.logger.info(f"Получен ответ #{answer_entry['id']}")
    
    # 7. Возврат ответа
    return jsonify({
        'message': 'Ответы успешно сохранены',
        'id': answer_entry['id']
    }), 201  # 201 = Created
```

### Endpoint получения всех ответов

```python
@app.route('/answers', methods=['GET'])
def get_answers():
    """
    Получить все сохраненные ответы.
    
    Returns:
        JSON массив со всеми ответами
    """
    return jsonify(answers_store), 200
```

## ✅ Валидация данных

### Функция валидации

```python
def validate_answers(data):
    """
    Валидация входящих данных.
    
    Args:
        data: Словарь с ответами
        
    Returns:
        (bool, str): (успех, сообщение об ошибке)
    """
    
    # 1. Проверка типа данных
    if not isinstance(data, dict):
        return False, "Данные должны быть словарем"
    
    # 2. Проверка обязательных полей
    required_fields = [
        "question-1", "question-2", "question-3", 
        "question-4", "question-5"
    ]
    
    for field in required_fields:
        if field not in data:
            return False, f"Отсутствует обязательное поле: {field}"
    
    # 3. Проверка типов значений
    if not isinstance(data["question-1"], str):
        return False, "Поле 'question-1' должно быть строкой"
    
    if not isinstance(data["question-2"], (int, float)):
        return False, "Поле 'question-2' должно быть числом"
    
    # 4. Проверка длины строк
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 500:
            return False, f"Поле '{key}' слишком длинное (макс. 500 символов)"
    
    # 5. Проверка диапазонов чисел
    age = data.get("question-2")
    if age is not None and (age < 1 or age > 150):
        return False, "Возраст должен быть от 1 до 150"
    
    experience = data.get("question-4")
    if experience is not None and (experience < 0 or experience > 80):
        return False, "Опыт работы должен быть от 0 до 80 лет"
    
    # 6. Если все проверки пройдены
    return True, "Данные валидны"
```

### Почему важна валидация?

**Без валидации:**
```python
# Плохой пример
@app.route('/answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers_store.append(data)  # ОПАСНО!
    return jsonify({'ok': True})
```

**Проблемы:**
1. **Неверные типы данных** - строка вместо числа
2. **Отсутствие обязательных полей** - нет имени
3. **Некорректные значения** - возраст -5 лет
4. **Слишком длинные строки** - переполнение памяти
5. **SQL инъекции** (если используется БД)

**С валидацией:**
```python
# Хороший пример
@app.route('/answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    
    is_valid, error = validate_answers(data)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    answers_store.append(data)
    return jsonify({'ok': True}), 201
```

## 🛡️ Rate Limiting

### Настройка ограничителя

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Инициализация
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Ключ - IP адрес клиента
    default_limits=[
        "200 per day",    # 200 запросов в день
        "50 per hour"     # 50 запросов в час
    ],
    storage_uri="memory://"  # Хранение счетчиков в памяти
)
```

### Применение к endpoint'ам

```python
# Ограничение для конкретного endpoint'а
@app.route('/answers', methods=['POST'])
@limiter.limit("10 per minute")  # 10 запросов в минуту
def submit_answers():
    ...

# Несколько ограничений
@app.route('/answers', methods=['POST'])
@limiter.limit("10 per minute")
@limiter.limit("100 per hour")
def submit_answers():
    ...
```

### Ответ при превышении лимита

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
    "error": "Превышен лимит запросов",
    "message": "Пожалуйста, подождите 60 секунд"
}
```

## 💾 Хранение данных

### Глобальное хранилище

```python
# Глобальная переменная для хранения ответов
answers_store = []

def add_answer(answer_data):
    """Добавить ответ в хранилище"""
    answer_entry = {
        'id': len(answers_store) + 1,
        'timestamp': datetime.now().isoformat(),
        'answers': answer_data
    }
    answers_store.append(answer_entry)
    return answer_entry

def get_all_answers():
    """Получить все ответы"""
    return answers_store

def clear_answers():
    """Очистить хранилище"""
    answers_store.clear()
```

### Проблемы хранения в памяти

**1. Потеря данных при перезапуске:**
```python
# Сервер перезапускается
# answers_store = []  # ПУСТО!
```

**2. Отсутствие постоянства:**
```python
# Нет возможности восстановить данные
# Нет истории изменений
# Нет резервных копий
```

**3. Ограничения масштабируемости:**
```python
# Все данные в одном экземпляре приложения
# При запуске нескольких экземпляров - разные данные
# Нет синхронизации между процессами
```

### Решения для production

**1. База данных SQLite:**
```python
import sqlite3

def init_db():
    conn = sqlite3.connect('answers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
```

**2. SQLAlchemy ORM:**
```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///answers.db'
db = SQLAlchemy(app)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
```

## 🚨 Обработка ошибок

### Глобальные обработчики ошибок

```python
@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return jsonify({
        'error': 'Не найдено',
        'message': str(error)
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    return jsonify({
        'error': 'Внутренняя ошибка сервера',
        'message': str(error)
    }), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Обработчик ошибки 429 (превышение лимита)"""
    return jsonify({
        'error': 'Превышен лимит запросов',
        'message': 'Пожалуйста, попробуйте позже'
    }), 429
```

### Обработка исключений в endpoint'ах

```python
@app.route('/answers', methods=['POST'])
def submit_answers():
    try:
        data = request.get_json()
        
        if not data:
            raise ValueError("Пустое тело запроса")
        
        # Валидация и сохранение
        is_valid, error = validate_answers(data)
        if not is_valid:
            raise ValueError(error)
        
        answer_entry = add_answer(data)
        
        return jsonify({
            'message': 'Ответы сохранены',
            'id': answer_entry['id']
        }), 201
        
    except ValueError as e:
        app.logger.error(f"Ошибка валидации: {e}")
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        app.logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        return jsonify({
            'error': 'Внутренняя ошибка сервера'
        }), 500
```

## 📝 Логирование

### Настройка логирования

```python
import logging

# Настройка уровня логирования
app.logger.setLevel(logging.INFO)

# Создание обработчика для консоли
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Добавление обработчика
app.logger.addHandler(handler)
```

### Использование логирования

```python
@app.route('/answers', methods=['POST'])
def submit_answers():
    app.logger.info("Получен запрос на отправку ответов")
    
    data = request.get_json()
    app.logger.debug(f"Данные запроса: {data}")
    
    is_valid, error = validate_answers(data)
    if not is_valid:
        app.logger.warning(f"Ошибка валидации: {error}")
        return jsonify({'error': error}), 400
    
    answer_entry = add_answer(data)
    app.logger.info(f"Ответ #{answer_entry['id']} сохранен")
    
    return jsonify({'message': 'Ответы сохранены'}), 201
```

### Уровни логирования

```python
app.logger.debug("Детальная информация для отладки")
app.logger.info("Общая информация о событии")
app.logger.warning("Предупреждение о потенциальной проблеме")
app.logger.error("Ошибка в работе приложения")
app.logger.critical("Критическая ошибка, требующая немедленного вмешательства")
```

## 🏃 Запуск и отладка

### Запуск приложения

```python
if __name__ == '__main__':
    # Запуск в режиме отладки
    app.run(
        host='0.0.0.0',      # Слушать все интерфейсы
        port=5000,           # Порт 5000
        debug=True,          # Режим отладки (автоперезагрузка)
        threaded=True        # Многопоточность
    )
```

### Режим отладки

**Преимущества:**
- Автоматическая перезагрузка при изменении кода
- Интерактивный отладчик в браузере
- Подробные сообщения об ошибках

**Недостатки:**
- Не подходит для production
- Медленнее работает
- Показывает внутреннюю информацию

### Отладка с помощью print

```python
@app.route('/answers', methods=['POST'])
def submit_answers():
    print("=== ЗАПРОС ===")
    print(f"Метод: {request.method}")
    print(f"Заголовки: {dict(request.headers)}")
    print(f"Данные: {request.get_json()}")
    print("==============")
    
    # Логика...
```

### Отладка с помощью pdb

```python
import pdb

@app.route('/answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    
    pdb.set_trace()  # Точка останова
    
    is_valid, error = validate_answers(data)
    # ...
```

### Тестирование с curl

```bash
# Проверка работоспособности
curl http://localhost:5000/health

# Получение вопросов
curl http://localhost:5000/questions

# Отправка ответов
curl -X POST http://localhost:5000/answers \
  -H "Content-Type: application/json" \
  -d '{"question-1": "Иван", "question-2": 25, "question-3": "Python", "question-4": 5, "question-5": "VS Code"}'

# Получение всех ответов
curl http://localhost:5000/answers
```

### Тестирование с Python

```python
import requests

# Проверка работоспособности
response = requests.get('http://localhost:5000/health')
print(response.json())

# Отправка ответов
data = {
    'question-1': 'Иван',
    'question-2': 25,
    'question-3': 'Python',
    'question-4': 5,
    'question-5': 'VS Code'
}
response = requests.post('http://localhost:5000/answers', json=data)
print(response.status_code, response.json())
```

---

**Документ создан:** 22 апреля 2024  
**Сложность:** Начальный-средний  
**Время изучения:** 1-2 часа
