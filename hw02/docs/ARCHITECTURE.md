# Архитектура приложения "Мини-анкета"

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектурные компоненты](#архитектурные-компоненты)
3. [Взаимодействие компонентов](#взаимодействие-компонентов)
4. [Поток данных](#поток-данных)
5. [Технологические решения](#технологические-решения)
6. [Безопасность](#безопасность)
7. [Масштабируемость и ограничения](#масштабируемость-и-ограничения)

## 🎯 Обзор системы

Приложение "Мини-анкета" - это **full-stack веб-приложение**, состоящее из двух основных компонентов:

- **Backend (серверная часть)** - обрабатывает данные, хранит ответы, предоставляет API
- **Frontend (клиентская часть)** - отображает интерфейс, собирает ответы пользователя

```
┌─────────────────┐         HTTP/JSON         ┌─────────────────┐
│                 │  ←────────────────────→   │                 │
│    Frontend     │                           │     Backend     │
│  (HTML/CSS/JS)  │                           │   (Flask API)   │
│                 │                           │                 │
└─────────────────┘                           └─────────────────┘
      │                                                 │
      │                                                 │
      ▼                                                 ▼
┌─────────────────┐                           ┌─────────────────┐
│   Браузер       │                           │   Память        │
│   пользователя  │                           │   сервера       │
└─────────────────┘                           └─────────────────┘
```

**Ключевые характеристики:**
- **Одностраничное приложение (SPA)** - frontend загружается один раз, далее взаимодействует с API
- **RESTful API** - backend предоставляет стандартные HTTP endpoint'ы
- **CORS-enabled** - разрешены跨доменные запросы с localhost
- **Stateless** - каждый запрос независим, состояние хранится на сервере

## 🏗️ Архитектурные компоненты

### 1. Backend (Flask API)

**Файл:** `backend/app.py`

**Назначение:** Серверная часть приложения, которая:
- Предоставляет API для работы с вопросами и ответами
- Хранит данные в памяти сервера
- Обрабатывает CORS запросы
- Обеспечивает базовую безопасность

**Компоненты backend:**

```python
# Структура приложения
Flask App
├── Маршруты (Routes)
│   ├── GET /questions      # Получить список вопросов
│   ├── POST /answers       # Отправить ответы
│   ├── GET /answers        # Получить все ответы
│   └── GET /health         # Проверка работоспособности
├── middlewares
│   ├── CORS middleware     # Обработка跨доменных запросов
│   ├── Rate limiter        # Ограничение частоты запросов
│   └── Валидация данных    # Проверка входящих данных
└── Хранилище
    └── answers_store[]     # Список для хранения ответов
```

**Пример структуры данных:**

```python
# Вопрос
{
    "id": 1,
    "question": "Как вас зовут?",
    "type": "text"
}

# Ответ
{
    "timestamp": "2024-04-22T10:30:00",
    "answers": {
        "question-1": "Иван",
        "question-2": 25,
        "question-3": "Python",
        "question-4": 5,
        "question-5": "VS Code"
    }
}
```

### 2. Frontend (HTML/CSS/JavaScript)

**Файлы:** 
- `frontend/index.html` - основная страница с формой
- `frontend/script.js` - логика взаимодействия с API
- `frontend/answers.html` - страница просмотра ответов
- `frontend/answers.js` - логика страницы ответов

**Назначение:** Клиентская часть, которая:
- Отображает пользовательский интерфейс
- Загружает вопросы с сервера
- Отправляет ответы пользователя
- Отображает сохраненные ответы

**Архитектура frontend:**

```
HTML Structure
├── Header (заголовок, статус подключения)
├── Form Container
│   ├── Loading indicator
│   ├── Questions (динамически загружаемые)
│   └── Submit button
├── Thank you message (после отправки)
└── Footer (ссылка на страницу ответов)

JavaScript Logic
├── API Client
│   ├── fetchQuestions()
│   ├── submitAnswers()
│   └── checkConnection()
├── UI Controller
│   ├── renderQuestions()
│   ├── showLoading()
│   ├── showError()
│   └── showThankYou()
└── Event Handlers
    ├── form submission
    └── connection status
```

### 3. Система управления зависимостями

**Файл:** `backend/pyproject.toml`

**Назначение:** Определение зависимостей Python проекта

**Ключевые зависимости:**
- `Flask` - веб-фреймворк
- `flask-cors` - обработка CORS запросов
- `flasgger` - Swagger/OpenAPI документация
- `flask-limiter` - ограничение частоты запросов

## 🔄 Взаимодействие компонентов

### Последовательность действий при загрузке страницы

```
1. Пользователь открывает frontend/index.html
   ↓
2. Браузер загружает HTML и JavaScript
   ↓
3. script.js выполняет checkConnection()
   ↓
4. Делает GET запрос на /health
   ↓
5. Backend возвращает {"status": "ok"}
   ↓
6. Frontend показывает "Подключено к серверу"
   ↓
7. script.js вызывает fetchQuestions()
   ↓
8. Делает GET запрос на /questions
   ↓
9. Backend возвращает список вопросов
   ↓
10. Frontend рендерит форму с вопросами
```

### Последовательность отправки ответов

```
1. Пользователь заполняет форму
   ↓
2. Нажимает "Отправить ответы"
   ↓
3. script.js собирает данные формы
   ↓
4. Делает POST запрос на /answers с JSON
   ↓
5. Backend валидирует данные
   ↓
6. Сохраняет ответы в answers_store
   ↓
7. Возвращает {"message": "Ответы сохранены"}
   ↓
8. Frontend показывает "Спасибо!"
```

## 📊 Поток данных

### Структура запроса/ответа

**GET /questions:**
```http
Запрос:
GET /questions HTTP/1.1
Host: localhost:5000

Ответ:
HTTP/1.1 200 OK
Content-Type: application/json

[
    {"id": 1, "question": "Как вас зовут?", "type": "text"},
    {"id": 2, "question": "Сколько вам лет?", "type": "number"},
    ...
]
```

**POST /answers:**
```http
Запрос:
POST /answers HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
    "question-1": "Иван",
    "question-2": 25,
    "question-3": "Python",
    "question-4": 5,
    "question-5": "VS Code"
}

Ответ:
HTTP/1.1 201 Created
Content-Type: application/json

{
    "message": "Ответы успешно сохранены",
    "id": 1
}
```

### Хранение данных

**На сервере:**
```python
# В памяти Flask приложения
answers_store = []

# При получении POST /answers
def save_answer(answers_data):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "answers": answers_data
    }
    answers_store.append(entry)
    return entry
```

**На клиенте:**
- Данные не хранятся постоянно
- Только во время сессии браузера
- После перезагрузки страницы данные теряются

## 🔧 Технологические решения

### Почему Flask?

**Преимущества для учебного проекта:**
1. **Простота** - минимальный код для создания API
2. **Легковесность** - не требует сложной настройки
3. **Гибкость** - можно добавлять расширения (CORS, Swagger)
4. **Документация** - отличная документация и сообщество

**Альтернативы:**
- Django - слишком тяжелый for простого API
- FastAPI - современнее, но требует Python 3.6+
- Express.js - требует знания JavaScript на сервере

### Почему ванильный JavaScript?

**Преимущества:**
1. **Нет сборщиков** - не нужен Webpack, Vite
2. **Прозрачность** - весь код виден в браузере
3. **Минимум зависимостей** - только браузер
4. **Обучение** - понимание основ JavaScript

**Альтернативы:**
- React/Vue - избыточны для простой формы
- jQuery - устарел, современный JS не нужен

### Почему CORS?

**Проблема:** 
- Frontend загружается с `file://` или `localhost:8080`
- Backend на `localhost:5000`
- Браузеры блокируют跨доменные запросы по умолчанию

**Решение:**
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ]
    }
})
```

### Почему хранение в памяти?

**Преимущества для учебного проекта:**
1. **Простота** - не нужно настраивать БД
2. **Скорость** - мгновенный доступ к данным
3. **Переносимость** - работает везде, где есть Python

**Недостатки:**
1. **Данные теряются** при перезапуске сервера
2. **Нет постоянства** - нельзя перезагрузить сервер
3. **Масштабируемость** - не подходит for production

**Для production нужно:**
- База данных (PostgreSQL, MySQL, MongoDB)
- ORM (SQLAlchemy, Django ORM)
- Миграции схемы
- Резервное копирование

## 🔒 Безопасность

### CORS ограничения

**Что защищает:**
- Предотвращает доступ с чужих доменов
- Только localhost разрешен

**Ограничения:**
- Не защищает от атак с того же компьютера
- Не заменяет настоящую аутентификацию

### Валидация данных

**На сервере:**
```python
def validate_answers(data):
    # Проверка типа
    if not isinstance(data, dict):
        return False, "Данные должны быть словарем"
    
    # Проверка обязательных полей
    required_fields = ["question-1", "question-2", "question-3", "question-4", "question-5"]
    for field in required_fields:
        if field not in data:
            return False, f"Отсутствует поле {field}"
    
    # Проверка длины строк
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 500:
            return False, f"Поле {key} слишком длинное"
    
    # Проверка диапазонов
    if not (1 <= data.get("question-2", 0) <= 150):
        return False, "Возраст должен быть от 1 до 150"
    
    return True, "OK"
```

**На клиенте:**
```javascript
// Проверка перед отправкой
function validateForm(formData) {
    if (!formData["question-1"].trim()) {
        alert("Пожалуйста, введите имя");
        return false;
    }
    
    const age = parseInt(formData["question-2"]);
    if (isNaN(age) || age < 1 || age > 150) {
        alert("Пожалуйста, введите корректный возраст");
        return false;
    }
    
    return true;
}
```

### Rate Limiting

**Защита от злоупотреблений:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/answers", methods=["POST"])
@limiter.limit("10 per minute")
def submit_answers():
    # Обработка ответов
```

**Что защищает:**
- От спама ответами
- От DoS атак
- От случайных множественных отправок

## 📈 Масштабируемость и ограничения

### Текущие ограничения

1. **Хранение в памяти**
   - Данные теряются при перезапуске
   - Нет резервного копирования
   - Ограничено памятью сервера

2. **Однопоточность**
   - Flask development server однопоточный
   - Не подходит для высоких нагрузок
   - Блокирующие операции замедляют ответ

3. **Отсутствие аутентификации**
   - Любой может отправить ответы
   - Нет разделения пользователей
   - Нет прав доступа

4. **Нет кэширования**
   - Каждый запрос обрабатывается заново
   - Вопросы загружаются каждый раз
   - Нет оптимизации

### Как масштабировать

**1. Добавить базу данных:**
```python
# Вместо хранения в памяти
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///answers.db'
db = SQLAlchemy(app)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON)
```

**2. Использовать production сервер:**
```bash
# Вместо flask run
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**3. Добавить аутентификацию:**
```python
from flask_jwt_extended import JWTManager, create_access_token

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)
```

**4. Разделить frontend и backend:**
```
frontend/  →  хостинг статических файлов (Netlify, Vercel)
backend/   →  облачный сервер (Heroku, AWS, DigitalOcean)
```

**5. Добавить кэширование:**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'memory'})

@app.route('/questions')
@cache.cached(timeout=300)  # Кэшировать на 5 минут
def get_questions():
    return QUESTIONS
```

## 🎓 Ключевые концепции

### RESTful API

**Принципы:**
1. **Клиент-сервер** - разделение интерфейса и данных
2. **Stateless** - каждый запрос содержит всю информацию
3. **Кэширование** - ответы могут кэшироваться
4. **Единый интерфейс** - стандартные HTTP методы

**HTTP методы:**
- `GET` - получение данных
- `POST` - создание данных
- `PUT` - обновление данных
- `DELETE` - удаление данных

### JSON формат

**Почему JSON:**
1. **Читаемость** - понятен людям и машинам
2. **Универсальность** - поддерживается всеми языками
3. **Легковесность** - меньше overhead чем XML
4. **Стандартизация** - есть спецификация

**Пример:**
```json
{
    "id": 1,
    "question": "Как вас зовут?",
    "type": "text",
    "required": true
}
```

### CORS (Cross-Origin Resource Sharing)

**Проблема:**
- Браузеры блокируют запросы на другие домены
- Защита от CSRF атак
- Same-origin policy

**Решение:**
- Сервер отправляет заголовки `Access-Control-Allow-*`
- Браузер проверяет заголовки
- Разрешает или блокирует запрос

**Заголовки:**
```http
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
```

## 📚 Дополнительные ресурсы

### Для изучения Flask:
- [Официальная документация Flask](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello)

### Для изучения JavaScript:
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/ru/docs/Web/JavaScript)
- [learn.javascript.ru](https://learn.javascript.ru/)

### Для изучения REST API:
- [REST API Tutorial](https://restfulapi.net/)
- [HTTP Basics](https://developer.mozilla.org/ru/docs/Web/HTTP)

### Для изучения безопасности:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)

---

**Документ создан:** 22 апреля 2024  
**Целевая аудитория:** Разработчики с базовыми знаниями Python и HTML  
**Уровень сложности:** Начальный-средний
