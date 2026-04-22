// URL API backend - измените, если backend запущен на другом хосте/порту
const API_URL = 'http://localhost:5000';

// DOM элементы
const loadingDiv = document.getElementById('loading');
const form = document.getElementById('questionnaire-form');
const questionsContainer = document.getElementById('questions-container');
const submitBtn = document.getElementById('submit-btn');
const thankYouDiv = document.getElementById('thank-you');
const errorMessage = document.getElementById('error-message');
const connectionStatus = document.getElementById('connection-status');

// Проверка подключения к backend при загрузке страницы
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            connectionStatus.innerHTML = '✓ Подключено к backend';
            connectionStatus.className = 'connection-status status-connected';
            return true;
        }
    } catch (error) {
        console.error('Проверка подключения не удалась:', error);
    }
    
    connectionStatus.innerHTML = '✗ Не удалось подключиться к backend. Убедитесь, что он запущен на порту 5000.';
    connectionStatus.className = 'connection-status status-disconnected';
    showError('Не удалось подключиться к серверу backend. Пожалуйста, убедитесь, что backend запущен.');
    return false;
}

// Загрузка вопросов из backend
async function loadQuestions() {
    try {
        const response = await fetch(`${API_URL}/questions`);
        
        if (!response.ok) {
            throw new Error(`HTTP ошибка! статус: ${response.status}`);
        }
        
        const questions = await response.json();
        renderQuestions(questions);
        
    } catch (error) {
        console.error('Ошибка при загрузке вопросов:', error);
        showError('Не удалось загрузить вопросы. Пожалуйста, попробуйте позже.');
        loadingDiv.innerHTML = 'Не удалось загрузить вопросы. Пожалуйста, обновите страницу.';
    }
}

// Отображение вопросов в виде полей формы
function renderQuestions(questions) {
    loadingDiv.style.display = 'none';
    form.style.display = 'block';
    
    questionsContainer.innerHTML = '';
    
    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        
        const label = document.createElement('label');
        label.className = 'question-label';
        label.textContent = `${index + 1}. ${q.question}`;
        label.htmlFor = `question-${q.id}`;
        
        let input;
        if (q.type === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.className = 'question-input';
            input.id = `question-${q.id}`;
            input.name = `question-${q.id}`;
            input.required = true;
            input.min = '0';
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'question-input';
            input.id = `question-${q.id}`;
            input.name = `question-${q.id}`;
            input.required = true;
            input.placeholder = 'Ваш ответ...';
        }
        
        questionDiv.appendChild(label);
        questionDiv.appendChild(input);
        questionsContainer.appendChild(questionDiv);
    });
}

// Отправка ответов в backend
async function submitAnswers(event) {
    event.preventDefault();
    
    // Сбор ответов
    const formData = new FormData(form);
    const answers = {};
    let allFilled = true;
    
    formData.forEach((value, key) => {
        if (!value.trim()) {
            allFilled = false;
        }
        answers[key] = value;
    });
    
    if (!allFilled) {
        showError('Пожалуйста, заполните все вопросы перед отправкой.');
        return;
    }
    
    // Отключение кнопки отправки
    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка...';
    
    try {
        const response = await fetch(`${API_URL}/answers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(answers)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ошибка! статус: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Показ сообщения "Спасибо"
        form.style.display = 'none';
        thankYouDiv.style.display = 'block';
        hideError();
        
        console.log('Ответы успешно отправлены:', result);
        
    } catch (error) {
        console.error('Ошибка при отправке ответов:', error);
        showError('Не удалось отправить ответы. Пожалуйста, попробуйте снова.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Отправить ответы';
    }
}

// Показать сообщение об ошибке
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Скрыть сообщение об ошибке
function hideError() {
    errorMessage.style.display = 'none';
}

// Инициализация приложения
async function init() {
    const connected = await checkConnection();
    if (connected) {
        await loadQuestions();
    }
}

// Обработчики событий
form.addEventListener('submit', submitAnswers);

// Запуск приложения при готовности DOM
document.addEventListener('DOMContentLoaded', init);
