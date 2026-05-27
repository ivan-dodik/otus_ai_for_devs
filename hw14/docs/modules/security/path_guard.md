# `path_guard.py` — PathGuard sandbox

## Назначение

Sandbox для защиты от path traversal при доступе к файлам SDK. Все пути проверяются на принадлежность SDK_ROOT. Запрещены: path traversal (`..`), симлинки наружу, абсолютные пути вне SDK_ROOT.

## Класс `PathGuard`

### Конструктор

```python
def __init__(self, sdk_root: Path) -> None
```

**Параметры:**
- `sdk_root` — корневая директория SDK (разрешённая зона). Автоматически резолвится через `.resolve()`.

### Исключение `SecurityError`

```python
class SecurityError(Exception):
    """Ошибка безопасности при попытке доступа вне sandbox."""
```

### Методы

#### `validate()`

```python
def validate(self, path: str) -> Path
```

Проверка относительного пути. Аргумент `path` интерпретируется как относительный от `sdk_root`.

**Проверки:**
1. Резолвит путь: `(sdk_root / path).resolve()`
2. Проверяет, что результат начинается с `sdk_root`
3. Проверяет, что путь не является симлинком
4. Проверяет, что файл существует

**Возвращает:** `Resolved path` внутри `sdk_root`.

**Исключения:**
- `SecurityError` — path traversal или симлинк
- `FileNotFoundError` — файл не существует

#### `validate_absolute()`

```python
def validate_absolute(self, path: str) -> Path
```

Проверка абсолютного пути. Путь уже должен быть внутри `sdk_root` (не конкатенируется).

**Проверки:**
1. Резолвит путь: `Path(path).resolve()`
2. Проверяет, что результат начинается с `sdk_root`

**Возвращает:** `Resolved path`.

## Примеры

```python
guard = PathGuard(Path("/opt/bcm-sdk"))

# Успешно
guard.validate("include/bcm/vlan.h")
# → /opt/bcm-sdk/include/bcm/vlan.h

# Path traversal
guard.validate("../../etc/passwd")
# → SecurityError: Path traversal detected

# Симлинк наружу
guard.validate("link_to_outside")
# → SecurityError: Symlinks are not allowed

# Абсолютный путь вне sandbox
guard.validate_absolute("/etc/passwd")
# → SecurityError: Path outside sandbox
```

## Тестирование

Модуль покрыт 8 unit-тестами в `tests/test_security.py`:
- Успешная валидация
- Path traversal
- Симлинки
- Абсолютные пути вне sandbox
- Несуществующие файлы
- Пути с `..`