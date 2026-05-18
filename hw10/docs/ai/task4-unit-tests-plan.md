# План выполнения задачи №4: Unit-тесты для модуля RX (RC каналы)

## Цель
Покрыть unit-тестами функции обработки RC каналов из `src/main/rx/rx.c` с использованием Google Test.

## Целевые функции

| Функция | Строки | Описание | Чистая логика? |
|---------|--------|----------|----------------|
| `isPulseValid()` | 234–238 | Проверка длительности импульса | Да (зависит от rxConfig) |
| `applyRxChannelRangeConfiguraton()` | 706–716 | Масштабирование канала + обработка PPM_RCVR_TIMEOUT | Да |
| `updateLinkQualitySamples()` | 493–503 | Скользящее среднее качества связи | Да |
| `resetAllRxChannelRangeConfigurations()` | 165–173 | Сброс конфигурации каналов | Да |
| `nullReadRawRC()` | 175–181 | Функция-заглушка чтения | Да |
| `nullFrameStatus()` | 183–188 | Функция-заглушка статуса | Да |
| `nullProcessFrame()` | 190–195 | Функция-заглушка обработки | Да |

## Тестовые сценарии

### 1. `isPulseValid()`
- **Normal:** pulseDuration = 1000, 1500, 2000
- **Boundary:** 750 (PWM_PULSE_MIN), 2250 (PWM_PULSE_MAX)
- **Error:** 0, 3000, <750, >2250
- **Config-dependent:** с разными rx_min_usec/rx_max_usec

### 2. `applyRxChannelRangeConfiguraton()`
- **Normal:** sample=1500, range [1000,2000] → 1500
- **Boundary:** sample=1000 (min), 2000 (max)
- **PPM_RCVR_TIMEOUT:** возвращает PPM_RCVR_TIMEOUT
- **Scale:** sample=0, range [1000,2000] → -1000

### 3. `updateLinkQualitySamples()`
- **Normal:** 16 samples of 1023 → 1023
- **Mixed:** чередование 1023 и 0 → ~511
- **Boundary:** все 0 → 0

### 4. `resetAllRxChannelRangeConfigurations()`
- Проверка, что все NON_AUX_CHANNEL_COUNT каналов получили `min = PWM_RANGE_MIN`, `max = PWM_RANGE_MAX`

### 5. Null-функции
- `nullReadRawRC()` → PPM_RCVR_TIMEOUT
- `nullFrameStatus()` → RX_FRAME_PENDING
- `nullProcessFrame()` → true

## Файлы для создания
1. `docs/ai/task4-unit-tests-plan.md` — данный план
2. `src/test/unit/rx/rx_unittest.cc` — файл с тестами

## Файлы для модификации
3. `CHANGES.md` — добавить запись
4. `PROMPTS.md` — добавить запись
5. `docs/ai/PLAN.md` — отметить прогресс
6. `memory-bank/activeContext.md` — обновить при необходимости

## Шаги выполнения
1. Создать план
2. Изучить существующую тестовую инфраструктуру
3. Создать тестовый тестовый файл
4. Собрать тесты
5. Запустить тесты и убедиться, что проходят
6. Обновить документацию

## Критерии готовности
- [ ] Тесты компилируются и проходят
- [ ] Покрытие: минимум 3 тестовых случая на функцию (норма, граница, ошибка)
- [ ] Тесты используют Google Test
- [ ] Тесты не требуют железо (чистая логика)
- [ ] Код тестов соответствует `.clinerules/coding-style.md`
- [ ] CHANGES.md, PROMPTS.md, docs/ai/PLAN.md обновлены