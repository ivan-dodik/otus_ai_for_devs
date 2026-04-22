#!/usr/bin/env python3
"""
Скрипт запуска Mini-Questionnaire

Кроссплатформенная альтернатива start.sh для запуска приложения.
Автоматически устанавливает зависимости и запускает backend и frontend серверы.

Использование: python start.py
"""

import subprocess
import sys
import time
import os
import signal
import socket

# Цвета для вывода
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """Печать заголовка"""
    print(f"{Colors.BLUE}{'='*40}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*40}{Colors.NC}")

def print_success(text):
    """Печать успеха"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text):
    """Печать ошибки"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_warning(text):
    """Печать предупреждения"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_info(text):
    """Печать информации"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")

def is_port_in_use(port):
    """Проверка, занят ли порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_python():
    """Проверка наличия Python"""
    try:
        version = subprocess.check_output([sys.executable, '--version'], 
                                        stderr=subprocess.STDOUT)
        version_str = version.decode().strip()
        print_success(f"Python найден: {version_str}")
        
        # Проверка версии
        if sys.version_info < (3, 8):
            print_error(f"Требуется Python 3.8 или выше. Найдено: {version_str}")
            return False
        
        return True
    except:
        print_error("Python не найден. Пожалуйста, установите Python 3.8+.")
        return False

def install_dependencies():
    """Установка зависимостей"""
    print_info("Установка зависимостей...")
    
    # Пробуем uv sync
    try:
        print_info("Синхронизация зависимостей через uv sync...")
        subprocess.run([sys.executable, '-m', 'uv', 'sync'], 
                      check=True, capture_output=True, cwd='backend')
        print_success("Зависимости установлены через uv sync")
        return True
    except:
        pass
    
    # Падаем back на pip
    try:
        print_warning("uv не найден, используем pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', 'backend/'], 
                      check=True, capture_output=True)
        print_success("Зависимости установлены через pip")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Не удалось установить зависимости: {e}")
        return False

def start_backend():
    """Запуск backend"""
    print_info("Запуск backend...")
    
    # Проверка порта
    if is_port_in_use(5000):
        print_warning("Port 5000 уже используется. Возможно, backend уже запущен.")
        print_info("Завершите существующий процесс или используйте другой порт.")
        return None
    
    try:
        backend_process = subprocess.Popen(
            [sys.executable, 'backend/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Ожидание запуска
        time.sleep(3)
        
        # Проверка, запущен ли процесс
        if backend_process.poll() is not None:
            print_error("Не удалось запустить backend.")
            print_error("Вывод ошибки:")
            print(backend_process.stderr.read())
            return None
        
        print_success(f"Backend запущен (PID: {backend_process.pid})")
        return backend_process
    
    except Exception as e:
        print_error(f"Ошибка при запуске backend: {e}")
        return None

def start_frontend():
    """Запуск frontend"""
    print_info("Запуск frontend...")
    
    # Проверка порта
    if is_port_in_use(8080):
        print_warning("Port 8080 уже используется. Возможно, frontend уже запущен.")
        print_info("Завершите существующий процесс или используйте другой порт.")
        return None
    
    try:
        # Меняем рабочую директорию на frontend
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
        frontend_process = subprocess.Popen(
            [sys.executable, '-m', 'http.server', '8080'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Ожидание запуска
        time.sleep(2)
        
        # Проверка, запущен ли процесс
        if frontend_process.poll() is not None:
            print_error("Не удалось запустить frontend.")
            print_error("Вывод ошибки:")
            print(frontend_process.stderr.read())
            return None
        
        print_success(f"Frontend запущен (PID: {frontend_process.pid})")
        return frontend_process
    
    except Exception as e:
        print_error(f"Ошибка при запуске frontend: {e}")
        return None

def cleanup(backend_process, frontend_process):
    """Остановка процессов"""
    print_info("Остановка приложения...")
    
    if backend_process:
        print_info(f"Остановка backend (PID: {backend_process.pid})...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print_success("Backend остановлен")
    
    if frontend_process:
        print_info(f"Остановка frontend (PID: {frontend_process.pid})...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
        print_success("Frontend остановлен")
    
    print_success("Все процессы остановлены")

def main():
    """Основная функция"""
    print_header("🚀 Запуск Mini-Questionnaire")
    
    # Проверка Python
    if not check_python():
        sys.exit(1)
    
    # Установка зависимостей
    if not install_dependencies():
        sys.exit(1)
    
    backend_process = None
    frontend_process = None
    
    try:
        # Запуск backend
        backend_process = start_backend()
        if not backend_process:
            sys.exit(1)
        
        # Запуск frontend
        frontend_process = start_frontend()
        if not frontend_process:
            sys.exit(1)
        
        # Финальное сообщение
        print("")
        print_header("🎉 Приложение успешно запущено!")
        
        print("")
        print(f"{Colors.GREEN}📱 Frontend:{Colors.NC}       http://localhost:8080")
        print(f"{Colors.GREEN}🔧 Backend:{Colors.NC}         http://localhost:5000")
        print(f"{Colors.GREEN}📊 Swagger UI:{Colors.NC}      http://localhost:5000/apidocs")
        print(f"{Colors.GREEN}📝 Answers page:{Colors.NC}    http://localhost:8080/answers.html")
        print(f"{Colors.GREEN}🧪 Test API:{Colors.NC}        ./test_api.sh or uv run python test_api.py")
        print("")
        print(f"{Colors.YELLOW}Для остановки нажмите Ctrl+C{Colors.NC}")
        print("")
        
        # Ожидание прерывания
        backend_process.wait()
    
    except KeyboardInterrupt:
        print("\n")
        print_info("Получен сигнал прерывания (Ctrl+C)")
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
    finally:
        cleanup(backend_process, frontend_process)

if __name__ == "__main__":
    main()
