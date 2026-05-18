# План выполнения задачи №2: Debounce для DISARM через переключатель

## Анализ проблемы

**Текущая ситуация:** В `src/main/fc/rc_controls.c`, функция `processRcStickPositions()` (строка 145), при использовании ARM-переключателя (`!isUsingSticksToArm`), DISARM срабатывает при `rcDisarmTicks > 3` (строки 195-199). Это означает, что достаточно 4 последовательных кадров (frames) с неактивным BOXARM, чтобы произошёл DISARM.

**Проблема:** При вибрациях дрона переключатель может генерировать кратковременные ложные переключения (bouncing). Даже с существующей защитой в 3 тика, при высокой частоте обновления RX (например, 250 Гц для CRSF — 4 мс на кадр), 3 тика = всего ~12 мс защиты, что недостаточно для подавления вибрационных дребезгов.

**Решение:** Добавить временной debounce — состояние переключателя должно быть стабильным минимум 50 мс перед DISARM.

## Шаги выполнения

### Шаг 0: Сохранить план в отдельный файл
- Создать файл `docs/ai/task2-debounce-plan.md` с полным описанием плана.

### Шаг 1: Внести изменения в `src/main/fc/rc_controls.c`
1.1. Добавить константу `ARM_DEBOUNCE_MS 50` рядом с существующими константами.
1.2. Заменить `static uint8_t rcDisarmTicksTicks` на `static timeMs_t rcDisarmStartMs`.
1.3. Заменить tick-based проверку на time-based debounce (50 мс через `millis()` + `cmpTimeUs()`).
1.4. Убедиться, что `#include "common/time.h"` присутствует (для `millis()` и `cmpTimeUs()`).

### Шаг 2: Проверить компиляцию
- Выполнить сборку для проверки.

### Шаг 3: Обновить документацию
3.1. CHANGES.md — добавить запись об изменениях.
3.2. PROMPTS.md — добавить запись о промпте.
3.3. docs/ai/PLAN.md — отметить прогресс.
3.4. memory-bank/activeContext.md — обновить при необходимости.

### Шаг 4: Финальная проверка
- Соответствие coding-style.
- Нет регрессий (ARM через стики, ARM через переключатель, failsafe).
- Definition of Done выполнен.

## Изменения в коде

### Файл: `src/main/fc/rc_controls.c`

**Изменение 1:** Добавить константу debounce рядом с существующими:

```c
#define ARM_DELAY_MS        500
#define STICK_DELAY_MS      50
#define STICK_AUTOREPEAT_MS 250
#define ARM_DEBOUNCE_MS     50   // debounce time for switch-based ARM/DISARM
```

**Изменение 2:** Заменить счётчик на time-based переменную:

```c
// было: static uint8_t rcDisarmTicks;
static timeMs_t rcDisarmStartMs;
```

**Изменение 3:** Заменить tick-based проверку на time-based debounce:

Было:
```c
if (!isUsingSticksToArm) {
    if (IS_RC_MODE_ACTIVE(BOXARM)) {
        rcDisarmTicks = 0;
        // Arming via ARM BOX
        tryArm();
    } else {
        resetTryingToArm();
        // Disarming via ARM BOX
        disarmUserRequested = true;
        resetArmingDisabled();
        const bool boxFailsafeSwitchIsOn = IS_RC_MODE_ACTIVE(BOXFAILSAFE);
        if (ARMING_FLAG(ARMED) && (failsafeIsReceivingRxData() || boxFailsafeSwitchIsOn)) {
            rcDisarmTicks++;
            if (rcDisarmTicks > 3) {
                // require three duplicate disarm values in a row before we disarm
                disarm(DISARM_REASON_SWITCH);
            }
        }
    }
}
```

Стало:
```c
if (!isUsingSticksToArm) {
    if (IS_RC_MODE_ACTIVE(BOXARM)) {
        rcDisarmStartMs = 0;
        // Arming via ARM BOX
        tryArm();
    } else {
        resetTryingToArm();
        // Disarming via ARM BOX
        disarmUserRequested = true;
        resetArmingDisabled();
        const bool boxFailsafeSwitchIsOn = IS_RC_MODE_ACTIVE(BOXFAILSAFE);
        if (ARMING_FLAG(ARMED) && (failsafeIsReceivingRxData() || boxFailsafeSwitchIsOn)) {
            if (rcDisarmStartMs == 0) {
                rcDisarmStartMs = millis();
            } else if (cmpTimeUs(millis(), rcDisarmStartMs) >= ARM_DEBOUNCE_MS) {
                // require stable switch position for ARM_DEBOUNCE_MS before we disarm
                disarm(DISARM_REASON_SWITCH);
            }
        }
    }
}
```

## Пояснение решений

1. **Time-based вместо tick-based:** Частота обновления RX варьируется между протоколами. Time-based гарантирует одинаковые 50 мс.
2. **50 мс:** Стандартный debounce для RC, достаточно для вибраций, незаметно для пилота.
3. **`millis()`:** Достаточное разрешение (1 мс), не требует микросекунд.
4. **`cmpTimeUs()`:** Корректно обрабатывает переполнение счётчика.
5. **`rcDisarmStartMs = 0` как флаг:** При BOXARM активен — сбрасываем таймер. Первый кадр с неактивным — старттанавливаем время.

## Критерии готовности

- [ ] Ложные DISARM от вибраций устранены
- [ ] Debounce 50 мс (конфигурируемая константа `ARM_DEBOUNCE_MS`)
- [ ] Задержка не мешает нормальному переключению
- [ ] Нет регрессий в существующей ARM-логике
- [ ] Код соответствует `.clinerules/coding-style.md`