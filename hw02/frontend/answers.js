// URL API backend
const API_URL = 'http://localhost:5000';

// DOM элементы
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const noDataDiv = document.getElementById('no-data');
const answersContainer = document.getElementById('answers-container');
const answersBody = document.getElementById('answers-body');
const statsDiv = document.getElementById('stats');
const totalAnswersSpan = document.getElementById('total-answers');
const lastAnswerTimeSpan = document.getElementById('last-answer-time');
const todayAnswersSpan = document.getElementById('today-answers');
const actionsDiv = document.getElementById('actions');

// Хранилище ответов
let answersData = [];

// Загрузка ответов
async function loadAnswers() {
    showLoading();
    
    try {
        const response = await fetch(`${API_URL}/answers`);
        
        if (!response.ok) {
            throw new Error(`HTTP ошибка! статус: ${response.status}`);
        }
        
        answersData = await response.json();
        
        if (answersData.length === 0) {
            showNoData();
            return;
        }
        
        renderAnswers();
        updateStats();
        showStats();
        showActions();
        
    } catch (error) {
        console.error('Ошибка при загрузке ответов:', error);
        showError('Не удалось загрузить ответы. Убедитесь, что backend запущен на порту 5000.');
    }
}

// Отображение ответов
function renderAnswers() {
    answersBody.innerHTML = '';
    
    answersData.forEach((response, index) => {
        const row = document.createElement('tr');
        
        const answers = response.answers;
        const timestamp = formatTimestamp(response.timestamp);
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td class="timestamp">${timestamp}</td>
            <td>${escapeHtml(answers['question-1'] || 'N/A')}</td>
            <td>${answers['question-2'] || 'N/A'}</td>
            <td>${escapeHtml(answers['question-3'] || 'N/A')}</td>
            <td>${answers['question-4'] || 'N/A'}</td>
            <td>${escapeHtml(answers['question-5'] || 'N/A')}</td>
        `;
        
        answersBody.appendChild(row);
    });
    
    loadingDiv.style.display = 'none';
    noDataDiv.style.display = 'none';
    answersContainer.style.display = 'block';
}

// Форматирование временной метки
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    return date.toLocaleString('ru-RU', options);
}

// Обновление статистики
function updateStats() {
    totalAnswersSpan.textContent = answersData.length;
    
    // Последний ответ
    if (answersData.length > 0) {
        const lastAnswer = answersData[answersData.length - 1];
        const lastTime = formatTimestamp(lastAnswer.timestamp);
        lastAnswerTimeSpan.textContent = lastTime.split(', ')[1] || '-';
    } else {
        lastAnswerTimeSpan.textContent = '-';
    }
    
    // Ответы сегодня
    const today = new Date().toISOString().split('T')[0];
    const todayCount = answersData.filter(answer => {
        const answerDate = new Date(answer.timestamp).toISOString().split('T')[0];
        return answerDate === today;
    }).length;
    todayAnswersSpan.textContent = todayCount;
}

// Показ статистики
function showStats() {
    statsDiv.style.display = 'flex';
}

// Показ действий
function showActions() {
    actionsDiv.style.display = 'flex';
}

// Показ загрузки
function showLoading() {
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    noDataDiv.style.display = 'none';
    answersContainer.style.display = 'none';
    statsDiv.style.display = 'none';
    actionsDiv.style.display = 'none';
}

// Показ отсутствия данных
function showNoData() {
    loadingDiv.style.display = 'none';
    noDataDiv.style.display = 'block';
    answersContainer.style.display = 'none';
    statsDiv.style.display = 'none';
    actionsDiv.style.display = 'none';
}

// Показ ошибки
function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    loadingDiv.style.display = 'none';
    noDataDiv.style.display = 'none';
    answersContainer.style.display = 'none';
    statsDiv.style.display = 'none';
    actionsDiv.style.display = 'none';
}

// Экспорт в JSON
function exportToJSON() {
    if (answersData.length === 0) {
        alert('Нет данных для экспорта.');
        return;
    }
    
    const dataStr = JSON.stringify(answersData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `answers-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    // Показываем уведомление
    showNotification('Файл JSON успешно экспортирован!', 'success');
}

// Экспорт в CSV
function exportToCSV() {
    if (answersData.length === 0) {
        alert('Нет данных для экспорта.');
        return;
    }
    
    // Заголовки
    const headers = ['№', 'Время отправки', 'Имя', 'Возраст', 'Язык программирования', 'Опыт (лет)', 'Среда разработки'];
    
    // Данные
    const rows = answersData.map((response, index) => {
        const answers = response.answers;
        const timestamp = formatTimestamp(response.timestamp);
        return [
            index + 1,
            timestamp,
            answers['question-1'] || '',
            answers['question-2'] || '',
            answers['question-3'] || '',
            answers['question-4'] || '',
            answers['question-5'] || ''
        ];
    });
    
    // Создаем CSV
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const dataBlob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `answers-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    // Показываем уведомление
    showNotification('Файл CSV успешно экспортирован!', 'success');
}

// Очистка всех ответов
async function clearAllAnswers() {
    if (answersData.length === 0) {
        alert('Нет данных для очистки.');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите удалить все ответы? Это действие нельзя отменить.')) {
        return;
    }
    
    try {
        // В текущей реализации нет эндпоинта DELETE, поэтому просто очищаем локальные данные
        // и показываем сообщение
        
        // В будущем можно добавить DELETE /answers endpoint
        answersData = [];
        showNoData();
        hideStats();
        hideActions();
        
        showNotification('Все ответы очищены. Для полного удаления данных перезапустите backend.', 'info');
        
    } catch (error) {
        console.error('Ошибка при очистке ответов:', error);
        showError('Не удалось очистить ответы.');
    }
}

// Скрытие статистики
function hideStats() {
    statsDiv.style.display = 'none';
}

// Скрытие действий
function hideActions() {
    actionsDiv.style.display = 'none';
}

// Показ уведомления
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Добавляем стили для анимации
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(-100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Экранирование HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Автоматическое обновление каждые 30 секунд
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        loadAnswers();
    }, 30000); // 30 секунд
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadAnswers();
    startAutoRefresh();
    
    // Очистка при закрытии страницы
    window.addEventListener('beforeunload', stopAutoRefresh);
});
