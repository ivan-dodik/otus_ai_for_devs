# План рефакторинга blackbox (Задача №3)

## Цель
Выделить логику инициализации из `src/main/blackbox/blackbox.c` в отдельный файл `blackbox_init.c`.

## Требования
- Сигнатуры функций не менять.
- `blackbox.c` должен только объявлять `extern`-функции инициализации (через `#include`).
- Все функции инициализации переместить в `blackbox_init.c`.
- Нет дублирования кода.
- Код соответствует `.clinerules/coding-style.md`.

## Файлы для создания
1. `docs/ai/task3-blackbox-refactor-plan.md` — данный план
2. `src/main/blackbox/blackbox_init.h` — заголовок с объявлениями extern-функций инициализации
3. `src/main/blackbox/blackbox_init.c` — реализация функций инициализации

## Файлы для изменения
4. `src/main/blackbox/blackbox.c` — удалить функции инициализации, добавить `#include "blackbox_init.h"`
5. Система сборки — добавить `blackbox_init.c` в список исходников
6. `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md` — обновить документацию

## Перемещаемые функции

| Функция | Описание | Статус |
|---------|----------|--------|
| `blackboxInit()` | Основная инициализация | non-static, публичная |
| `blackboxValidateConfig()` | Валидация конфигурации | non-static, публичная |
| `blackboxResetIterationTimers()` | Сброс таймеров | static → extern |
| `blackboxStart()` | Запуск логирования | static → extern |
| `blackboxFinish()` | Завершение логирования | non-static, публичная |
| `blackboxSetState()` | Управление состояниями | static → extern (нужна и init, и runtime) |
| `blackboxMayEditConfig()` | Проверка возможности редактирования | non-static, публичная |
| `startInTestMode()` | Старт тестового режима | static → extern |
| `stopInTestMode()` | Стоп тестового режима | static → extern |
| `inMotorTestMode()` | Проверка тестового режима | static → extern |

## Разделяемые переменные (снять `static`, объявить `extern`)

| Переменная | Используется в |
|------------|---------------|
| `blackboxState` | init + runtime |
| `blackboxPInterval` | init + runtime |
| `blackboxIInterval` | init + runtime |
| `blackboxHighResolutionScale` | init + runtime |
| `blackboxLoggedAnyFrames` | init (finish) + runtime |
| `startedLoggingInTestMode` | init + runtime |

## Шаги проверки
1. `make` компилируется без ошибок
2. Все функции инициализации находятся в `blackbox_init.c`
3. Нет дублирования кода
4. Код соответствует coding-style
5. `CHANGES.md` и `PROMPTS.md` обновлены