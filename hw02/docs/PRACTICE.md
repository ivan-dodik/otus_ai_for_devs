# Практические примеры и упражнения

## 📋 Содержание

1. [Базовые примеры кода](#базовые-примеры-кода)
2. [Упражнения для практики](#упражнения-для-практики)
3. [Расширение функциональности](#расширение-функциональности)
4. [Частые ошибки и решения](#частые-ошибки-и-решения)
5. [Дополнительные ресурсы](#дополнительные-ресурсы)

## 🔤 Базовые примеры кода

### 1. Простой HTTP запрос

**Пример 1.1: GET запрос с fetch**

```javascript
// Синхронный стиль (async/await)
async function getData() {
    try {
        const response = await fetch('http://localhost:5000/questions');
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Асинхронный стиль (Promise)
function getData() {
    fetch('http://localhost:5000/questions')
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Ошибка:', error));
}
```

**Пример 1.2: POST запрос с данными**

```javascript
async function sendData() {
    const answers = {
        'question-1': 'Иван',
        'question-2': 25,
        'question-3': 'Python',
        'question-4': 5,
        'question-5': 'VS Code'
    };
    
    try {
        const response = await fetch('http://localhost:5000/answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(answers)
        });
        
        const result = await response.json();
        console.log('Ответ сервера:', result);
        return result;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
```

### 2. Создание DOM элементов

**Пример 2.1: Динамическое создание элементов**

```javascript
// Создание одного элемента
function createQuestionElement(question) {
    const div = document.createElement('div');
    div.className = 'question-item';
    
    const label = document.createElement('label');
    label.textContent = question.question;
    label.htmlFor = `question-${question.id}`;
    
    const input = document.createElement('input');
    input.type = 'text';
    input.id = `question-${question.id}`;
    input.name = `question-${question.id}`;
    
    div.appendChild(label);
    div.appendChild(input);
    
    return div;
}

// Использование
const question = { id: 1, question: 'Как вас зовут?' };
const element = createQuestionElement(question);
document.getElementById('container').appendChild(element);
```

**Пример 2.2: Массовое создание элементов**

```javascript
async function loadAndRenderQuestions() {
    const response = await fetch('http://localhost:5000/questions');
    const questions = await response.json();
    
    const container = document.getElementById('questions-container');
    container.innerHTML = ''; // Очистка
    
    questions.forEach(question => {
        const element = createQuestionElement(question);
        container.appendChild(element);
    });
}
```

### 3. Обработка событий

**Пример 3.1: Простая обработка клика**

```javascript
document.getElementById('submit-btn').addEventListener('click', () => {
    console.log('Кнопка нажата!');
});
```

**Пример 3.2: Обработка отправки формы**

```javascript
document.getElementById('questionnaire-form').addEventListener('submit', async (event) => {
    event.preventDefault(); // Предотвращаем стандартную отправку
    
    const formData = new FormData(event.target);
    const answers = Object.fromEntries(formData);
    
    try {
        await sendData(answers);
        alert('Ответы отправлены!');
    } catch (error) {
        alert('Ошибка при отправке');
    }
});
```

### 4. Работа с формами

**Пример 4.1: Сбор данных формы**

```javascript
function getFormData() {
    const form = document.getElementById('questionnaire-form');
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    return data;
}

// Использование
const answers = getFormData();
console.log(answers);
```

**Пример 4.2: Валидация формы**

```javascript
function validateForm(data) {
    const errors = [];
    
    // Проверка имени
    if (!data['question-1'] || data['question-1'].trim() === '') {
        errors.push('Имя обязательно для заполнения');
    }
    
    // Проверка возраста
    const age = parseInt(data['question-2']);
    if (isNaN(age) || age < 1 || age > 150) {
        errors.push('Возраст должен быть от 1 до 150');
    }
    
    return errors;
}

// Использование
const formData = getFormData();
const errors = validateForm(formData);

if (errors.length > 0) {
    alert('Ошибки:\n' + errors.join('\n'));
} else {
    sendData(formData);
}
```

## 🏋️ Упражнения для практики

### Упражнение 1: Добавление нового вопроса

**Задание:** Добавьте шестой вопрос "Ваш email" в анкету.

**Решение:**

1. Измените `backend/app.py`:

```python
QUESTIONS = [
    {"id": 1, "question": "Как вас зовут?", "type": "text"},
    {"id": 2, "question": "Сколько вам лет?", "type": "number"},
    {"id": 3, "question": "Какой ваш любимый язык программирования?", "type": "text"},
    {"id": 4, "question": "Сколько у вас лет опыта?", "type": "number"},
    {"id": 5, "question": "Какая ваша предпочтительная среда разработки?", "type": "text"},
    # Добавьте новый вопрос здесь
    {"id": 6, "question": "Ваш email", "type": "email", "required": True}
]
```

2. Обновите валидацию в `backend/app.py`:

```python
def validate_answers(data):
    required_fields = [
        "question-1", "question-2", "question-3", 
        "question-4", "question-5", "question-6"  # Добавьте это
    ]
    # ... остальной код
```

3. Обновите валидацию в `frontend/script.js`:

```javascript
function validateAnswers(answers) {
    // Проверка email
    const email = answers['question-6'];
    if (email && !isValidEmail(email)) {
        showError('Пожалуйста, введите корректный email');
        return false;
    }
    return true;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}
```

### Упражнение 2: Добавление выпадающего списка

**Задание:** Замените вопрос "Какой ваш любимый язык программирования?" на выпадающий список.

**Решение:**

1. Измените вопрос в `backend/app.py`:

```python
{
    "id": 3,
    "question": "Какой ваш любимый язык программирования?",
    "type": "select",
    "options": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Другой"],
    "required": True
}
```

2. Обновите `frontend/script.js`:

```javascript
function createQuestionElement(question, index) {
    const div = document.createElement('div');
    div.className = 'question-item';
    
    const label = document.createElement('label');
    label.className = 'question-label';
    label.textContent = `${question.id}. ${question.question}`;
    label.htmlFor = `question-${question.id}`;
    
    let input;
    
    if (question.type === 'select' && question.options) {
        // Создаем выпадающий список
        input = document.createElement('select');
        input.className = 'question-input';
        input.id = `question-${question.id}`;
        input.name = `question-${question.id}`;
        
        // Пустой вариант
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = 'Выберите вариант';
        input.appendChild(emptyOption);
        
        // Варианты из списка
        question.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            input.appendChild(optionElement);
        });
    } else {
        // Создаем обычный input
        input = document.createElement('input');
        input.type = getInputType(question.type);
        input.className = 'question-input';
        input.id = `question-${question.id}`;
        input.name = `question-${question.id}`;
        input.required = question.required || false;
    }
    
    div.appendChild(label);
    div.appendChild(input);
    return div;
}
```

### Упражнение 3: Добавление счетчика ответов

**Задание:** Добавьте на страницу отображение количества отправленных ответов.

**Решение:**

1. Добавьте HTML в `frontend/index.html`:

```html
<div id="answers-counter" style="text-align: center; margin-top: 20px; color: #666;">
    Всего ответов: <span id="counter-value">0</span>
</div>
```

2. Добавьте JavaScript в `frontend/script.js`:

```javascript
async function updateAnswersCounter() {
    try {
        const response = await fetch(`${API_URL}/answers`);
        const answers = await response.json();
        document.getElementById('counter-value').textContent = answers.length;
    } catch (error) {
        console.error('Ошибка получения счетчика:', error);
    }
}

// Вызывайте после успешной отправки ответа
async function handleSubmit(event) {
    // ... существующий код
    
    if (response.ok) {
        showThankYou();
        await updateAnswersCounter(); // Обновляем счетчик
    }
}

// Обновляем при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    // ... существующий код
    await updateAnswersCounter();
});
```

### Упражнение 4: Добавление таймера сессии

**Задание:** Добавьте таймер, показывающий время, прошедшее с начала сессии.

**Решение:**

1. Добавьте HTML:

```html
<div id="session-timer" style="text-align: center; margin-top: 10px; color: #666;">
    Время сессии: <span id="timer-value">00:00</span>
</div>
```

2. Добавьте JavaScript:

```javascript
let sessionStartTime = null;
let timerInterval = null;

function startSessionTimer() {
    sessionStartTime = Date.now();
    
    timerInterval = setInterval(() => {
        const elapsed = Date.now() - sessionStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        const formatted = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        document.getElementById('timer-value').textContent = formatted;
    }, 1000);
}

function stopSessionTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
}

// Запускаем при загрузке
document.addEventListener('DOMContentLoaded', () => {
    startSessionTimer();
});

// Останавливаем при отправке формы
async function handleSubmit(event) {
    // ... после успешной отправки
    stopSessionTimer();
    const finalTime = document.getElementById('timer-value').textContent;
    console.log(`Сессия завершена. Время: ${finalTime}`);
}
```

## 🚀 Расширение функциональности

### 1. Добавление экспорта в Excel

**Пример кода:**

```javascript
async function exportToExcel() {
    try {
        const response = await fetch(`${API_URL}/answers`);
        const answers = await response.json();
        
        // Создаем CSV контент
        let csv = '№,Время,Имя,Возраст,Язык,Опыт,Среда\n';
        
        answers.forEach((answer, index) => {
            const a = answer.answers;
            const time = new Date(answer.timestamp).toLocaleString();
            csv += `${index + 1},"${time}","${a['question-1']}","${a['question-2']}","${a['question-3']}","${a['question-4']}","${a['question-5']}"\n`;
        });
        
        // Создаем и скачиваем файл
        const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `answers_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        
    } catch (error) {
        console.error('Ошибка экспорта:', error);
    }
}

// Добавьте кнопку в answers.html
// <button onclick="exportToExcel()">Экспорт в Excel</button>
```

### 2. Добавление графика ответов

**Пример с Chart.js:**

```html
<!-- Добавьте в HTML -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="answersChart" width="400" height="200"></canvas>
```

```javascript
async function renderChart() {
    try {
        const response = await fetch(`${API_URL}/answers`);
        const answers = await response.json();
        
        // Подсчет языков программирования
        const languages = {};
        answers.forEach(answer => {
            const lang = answer.answers['question-3'];
            languages[lang] = (languages[lang] || 0) + 1;
        });
        
        // Создание графика
        const ctx = document.getElementById('answersChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(languages),
                datasets: [{
                    label: 'Количество ответов',
                    data: Object.values(languages),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', 
                        '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }]
            }
        });
        
    } catch (error) {
        console.error('Ошибка создания графика:', error);
    }
}
```

### 3. Добавление поиска по ответам

```javascript
function renderAnswersWithSearch(answers, searchTerm = '') {
    const filtered = answers.filter(answer => {
        const text = JSON.stringify(answer.answers).toLowerCase();
        return text.includes(searchTerm.toLowerCase());
    });
    
    renderAnswers(filtered);
}

// Добавьте поле поиска в answers.html
// <input type="text" id="search-input" placeholder="Поиск...">

document.getElementById('search-input').addEventListener('input', (e) => {
    const searchTerm = e.target.value;
    renderAnswersWithSearch(currentAnswers, searchTerm);
});
```

## 🐛 Частые ошибки и решения

### Ошибка 1: CORS ошибка

**Симптомы:**
```
Access to fetch at 'http://localhost:5000/questions' from origin 'http://localhost:8080' has been blocked by CORS policy.
```

**Решение:**
Убедитесь, что в `backend/app.py` правильно настроен CORS:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:3000"
        ]
    }
})
```

### Ошибка 2: Неверный Content-Type

**Симптомы:**
```
400 Bad Request: Request must be JSON
```

**Решение:**
Всегда устанавливайте заголовок Content-Type при POST запросе:

```javascript
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'  // Обязательно!
    },
    body: JSON.stringify(data)
});
```

### Ошибка 3: Форма не отправляется

**Симптомы:**
Кнопка "Отправить" не реагирует на нажатия.

**Решение:**
1. Проверьте, что форма имеет правильный ID
2. Убедитесь, что обработчик событий подключен после загрузки DOM
3. Проверьте консоль на ошибки JavaScript

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('questionnaire-form');
    if (!form) {
        console.error('Форма не найдена!');
        return;
    }
    
    form.addEventListener('submit', handleSubmit);
});
```

### Ошибка 4: Вопросы не загружаются

**Симптомы:**
На странице отображается "Загрузка вопросов..." бесконечно.

**Решение:**
1. Проверьте, запущен ли backend: `curl http://localhost:5000/health`
2. Проверьте правильность URL API
3. Проверьте консоль браузера на ошибки

```javascript
async function fetchQuestions() {
    try {
        console.log('Загрузка вопросов с:', `${API_URL}/questions`);
        const response = await fetch(`${API_URL}/questions`);
        console.log('Статус ответа:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Получены вопросы:', data);
        return data;
        
    } catch (error) {
        console.error('Ошибка загрузки вопросов:', error);
        throw error;
    }
}
```

### Ошибка 5: Данные не сохраняются

**Симптомы:**
Ответы отправляются успешно, но при перезагрузке страницы исчезают.

**Решение:**
Это нормальное поведение, так как данные хранятся в памяти. Для постоянного хранения используйте базу данных:

```python
# Вместо хранения в памяти
# answers_store = []

# Используйте базу данных
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///answers.db'
db = SQLAlchemy(app)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON, nullable=False)
```

## 📚 Дополнительные ресурсы

### Документация

1. **Flask**
   - [Официальная документация](https://flask.palletsprojects.com/)
   - [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello)

2. **JavaScript**
   - [MDN Web Docs](https://developer.mozilla.org/ru/docs/Web/JavaScript)
   - [learn.javascript.ru](https://learn.javascript.ru/)

3. **Fetch API**
   - [MDN: Using Fetch](https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch)

4. **DOM**
   - [MDN: Document Object Model](https://developer.mozilla.org/ru/docs/Web/API/Document_Object_Model)

### Инструменты

1. **Postman** - тестирование API
2. **Chrome DevTools** - отладка JavaScript
3. **VS Code** - редактор кода
4. **Git** - контроль версий

### Книги

1. "Flask Web Development" by Miguel Grinberg
2. "Eloquent JavaScript" by Marijn Haverbeke
3. "You Don't Know JS" series by Kyle Simpson

### Онлайн-курсы

1. [Coursera: Python for Everybody](https://www.coursera.org/specializations/python)
2. [freeCodeCamp: JavaScript Algorithms](https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/)
3. [Udemy: The Web Developer Bootcamp](https://www.udemy.com/course/the-web-developer-bootcamp/)

---

**Документ создан:** 22 апреля 2024  
**Сложность:** Начальный-средний  
**Время выполнения упражнений:** 2-4 часа
