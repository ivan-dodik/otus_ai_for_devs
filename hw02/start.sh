#!/bin/bash

################################################################################
# Скрипт запуска Mini-Questionnaire
# 
# Этот скрипт автоматически устанавливает зависимости и запускает
# backend и frontend серверы приложения "Мини-анкета".
#
# Использование: ./start.sh
################################################################################

set -e  # Выход при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для печати заголовка
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

# Функция для печати успеха
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для печати ошибки
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для печати предупреждения
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для печати информации
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Обработчик прерывания
cleanup() {
    echo ""
    print_info "Остановка приложения..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_info "Остановка backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
        print_success "Backend остановлен"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_info "Остановка frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend остановлен"
    fi
    
    print_success "Все процессы остановлены"
    exit 0
}

# Регистрируем обработчик прерывания
trap cleanup EXIT INT TERM

# Начало
print_header "🚀 Запуск Mini-Questionnaire"

# Проверка Python
print_info "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 не найден. Пожалуйста, установите Python 3.8+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python найден: $PYTHON_VERSION"

# Проверка версии Python
if ! python3 -c "import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)"; then
    print_error "Требуется Python 3.8 или выше. Найдено: $PYTHON_VERSION"
    exit 1
fi

# Проверка и установка uv
if ! command -v uv &> /dev/null; then
    print_warning "uv не найден. Будет использован pip для установки зависимостей."
    USE_UV=false
else
    print_success "uv найден"
    USE_UV=true
fi

# Установка зависимостей
print_info "Установка зависимостей..."
cd "$(dirname "$0")"  # Переход в директорию скрипта

if [ "$USE_UV" = true ]; then
    print_info "Синхронизация зависимостей через uv sync..."
    (cd backend && uv sync 2>&1 | grep -v "^warning:") || true
else
    print_info "Установка зависимостей через pip..."
    pip3 install -e backend/ 2>&1 | grep -v "^warning:" || true
fi

print_success "Зависимости установлены"

# Проверка, не запущен ли уже backend
if lsof -i :5000 &> /dev/null; then
    print_warning "Port 5000 уже используется. Возможно, backend уже запущен."
    print_info "Завершите существующий процесс или используйте другой порт."
    exit 1
fi

# Запуск backend
print_info "Запуск backend..."
cd backend
uv run python3 app.py &
BACKEND_PID=$!
cd ..

# Ожидание запуска backend
print_info "Ожидание запуска backend..."
sleep 3

# Проверка, запущен ли backend
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Не удалось запустить backend. Проверьте логи выше."
    exit 1
fi

print_success "Backend запущен (PID: $BACKEND_PID)"

# Проверка, не запущен ли уже frontend
if lsof -i :8080 &> /dev/null; then
    print_warning "Port 8080 уже используется. Возможно, frontend уже запущен."
    print_info "Завершите существующий процесс или используйте другой порт."
    exit 1
fi

# Запуск frontend
print_info "Запуск frontend..."
cd frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

# Ожидание запуска frontend
sleep 2

# Проверка, запущен ли frontend
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Не удалось запустить frontend. Проверьте логи выше."
    exit 1
fi

print_success "Frontend запущен (PID: $FRONTEND_PID)"

# Финальное сообщение
echo ""
print_header "🎉 Приложение успешно запущено!"

echo ""
echo -e "${GREEN}📱 Frontend:${NC}       http://localhost:8080"
echo -e "${GREEN}🔧 Backend:${NC}         http://localhost:5000"
echo -e "${GREEN}📊 Swagger UI:${NC}      http://localhost:5000/apidocs"
echo -e "${GREEN}📝 Answers page:${NC}    http://localhost:8080/answers.html"
echo -e "${GREEN}🧪 Test API:${NC}        ./test_api.sh or uv run python test_api.py"
echo ""
echo -e "${YELLOW}Для остановки нажмите Ctrl+C${NC}"
echo ""

# Ожидание прерывания пользователем
wait $BACKEND_PID
