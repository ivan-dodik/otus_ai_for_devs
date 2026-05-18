# План выполнения ДЗ "Дополнение проекта инструкциями для ИИ"

## Прогресс

- [x] Шаг 1: Создать `docs/ai/TASKS.md`
- [x] Шаг 2: Создать `docs/ai/DEFINITION_OF_DONE.md`
- [x] Шаг 3: Создать `docs/ai/PLAN.md` (текущий файл)
- [x] Шаг 4: Создать `.clinerules/project-guide.md`
- [x] Шаг 5: Выполнить проверку инструкций через AI-агента (задача Debounce для DISARM)
- [x] Шаг 6: Оформить отчёт, обновить `PROMPTS.md` и `CHANGES.md`

### Задача №3: Рефакторинг blackbox (выделение инициализации)

- [x] Создан `docs/ai/task3-blackbox-refactor-plan.md` — план выполнения
- [x] Создан `src/main/blackbox/blackbox_init.h` — заголовочный файл с extern declarations
- [x] Создан `src/main/blackbox/blackbox_init.c` — функции инициализации
- [x] Добавлен `#include "blackbox_init.h"` в `blackbox.c`
- [x] Удалены дублирующиеся функции из `blackbox.c`
- [x] Исправлены static/extern конфликты (переменные iteration)
- [x] Добавлен `blackbox_init.c` в `mk/source.mk` (COMMON_SRC)
- [x] Добавлена `blackboxFinish()` в `blackbox_init.c` (lost during refactor)
- [x] Проверка компиляции (STM32F405) — успешно
- [x] Обновлены `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`

### Задача №4: Unit-тесты для модуля RX (RC каналы)

- [x] Создан `docs/ai/task4-unit-tests-plan.md` — план выполнения
- [x] Изучена существующая тестовая инфраструктура
- [x] Обновлён `src/test/unit/rx_rx_unittest.cc` — добавлены тесты для 4 функций
- [x] Тесты собраны и выполнены (13/13 PASS)
- [x] Обновлены `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`, `memory-bank/activeContext.md`

## Файлы для создания

| Файл | Назначение |
|------|-----------|
| `.clinerules/project-guide.md` | Главный файл инструкций для агента |
| `docs/ai/TASKS.md` | 4 сценария задач |
| `docs/ai/DEFINITION_OF_DONE.md` | Чеклист готовности |
| `docs/ai/PLAN.md` | План с прогрессом |

## Описание шагов

### Шаг 4: `.clinerules/project-guide.md`

Главный файл инструкций. Содержит:
1. **Контекст и границы** — кратко + ссылки на `memory-bank/` и `docs/`
2. **Требования к результату** — формат ответа, стиль кода, Definition of Done
3. **Примеры задач** — ссылка на `docs/ai/TASKS.md`
4. **Проверочные требования** — преамбула, обновление CHANGES/PROMPTS/PLAN

### Шаг 5: Проверка инструкций через AI-агента

1. Выбрать задачу: **Сценарий 2 (debounce)**
2. Дать промпт с указанием следовать `project-guide.md`
3. Проверить:
   - Формат ответа (план → изменения → пояснение → проверка)
   - Соблюдение coding-style
   - Обновление `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`
   - Преамбула в новых файлах
   - Использование Definition of Done
4. Зафиксировать результат
5. При необходимости доработать инструкции

### Шаг 8: Создан краткий общий отчёт HW10 (2026-05-18)

1. Создан `docs/hw10/README.md` с кратким отчётом о ДЗ
2. Описание AI-инструмента, что сделано, результаты 3 проверок, трудности, таблица промптов
3. Обновлены `CHANGES.md`, `docs/ai/PLAN.md`

### Шаг 7: Редактирование отчётов HW10 (2026-05-18)

1. Удалены промпты 1–5 (11-12 мая) из `docs/hw10/prompts.md`
2. Удалены секции "Документация проекта (дополнительная)" и "Документация (история и мета)" из `docs/hw10/created_files.md`
3. Удалено упоминание `docs/architecture-overview.md` из `docs/hw10/difficulties_report.md`
4. Обновлены `CHANGES.md`, `docs/ai/PLAN.md`

### Шаг 6: Оформление отчёта

- Инструмент: Cline (VS Code extension), использует `.clinerules/` для правил
- Что создано: перечень файлов
- Результат проверки
- Трудности
- Все промпты