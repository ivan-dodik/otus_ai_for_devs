# Анализ кода приёма и обработки сигналов от пульта

**Дата составления**: 2026-05-12
**Анализируемые файлы**: `src/main/rx/rx.c`, `src/main/fc/rc_adjustments.c`, `src/main/fc/rc_controls.c`, `src/main/fc/runtime_config.h`, `src/main/fc/rc_modes.c`, `src/main/fc/core.c`, `src/main/fc/rc.c`, `src/main/flight/failsafe.c`, `src/main/flight/pid.c`, `src/main/flight/mixer.c`, `src/main/flight/imu.c`
**Источники проблем**: анализ кода + отчёт `docs/unresolved-issues-report.md`

---

## 1. Общая схема потока сигналов

```
RX драйверы → rcRaw[] → detectAndApplySignalLossBehaviour() → rcData[] (float[18], [1000;2000])
    → updateRcCommands() → rcCommand[] (float[4], [-500;+500] для R/P/Y, [1000;2000] для THR)
    → processRcCommand() → setpointRate[] (целевая угловая скорость в °/с)
    → pidController() → pidData[].Sum
    → mixTable() → motor[]
```

**Ключевые точки ветвления:**
1. `rxFrameCheck()` — детекция потери сигнала
2. `detectAndApplySignalLossBehaviour()` — per-channel failsafe
3. `processRcStickPositions()` — ARM/DISARM через стики или переключатель
4. `updateActivatedModes()` — режимы полёта (ANGLE, HORIZON, ALT_HOLD, GPS_RESCUE и т.д.)
5. `processRxModes()` — логика активации режимов с учётом ARM статуса
6. `processRcCommand()` — rates, feedforward, RC smoothing
7. `pidController()` — PID-регулятор
8. `mixTable()` — микширование → motor[]

---

## 2. Анализ по этапам

### 2.1. Обработка и маппинг каналов (rx.c)

**Файл**: `src/main/rx/rx.c`

#### Найденные проблемы:

| # | Проблема | Тип | Серьёзность | Описание |
|---|----------|-----|-------------|----------|
| 1 | **TODO: move to rc_mode.c** (rx.c:357) | Антипаттерн | Low | Логика инициализации ARM-переключателя находится в rx.c, хотя должна быть в rc_mode.c. Нарушение разделения ответственности. |
| 2 | **FIXME: sumh.c — value 'c' unused** (п.2.14 отчёта) | Логическая ошибка | Medium | Неиспользуемая и непроверенная переменная 'c' в sumh.c. Может скрывать логическую ошибку в парсинге протокола SUMH. |
| 3 | **FIXME: runtime_config.h — flight modes vs status** (п.2.15 отчёта) | Антипаттерн | Medium | Смешение режимов полёта (ANGLE_MODE, HORIZON_MODE) и индикаторов статуса (ARMED, WAS_EVER_ARMED) в одном enum. Может привести к путанице при добавлении новых режимов. |
| 4 | **FIXME: dependency on mw.c** (п.2.4 отчёта) | Антипаттерн | Medium | Прямая зависимость от глобальной переменной `rssi` из mw.c через extern. Нарушение инкапсуляции. |
| 5 | **FIXME: magic number 50 в current.c** (п.2.5 отчёта) | Best practice | Low | Магическое число 50 в расчёте throttleFactor. Предлагается использовать thrustLinearization. |
| 6 | **Отсутствие валидации rcData после constrainf** (rx.c:804) | Безопасность | Low | `constrainf(sample, PWM_PULSE_MIN, PWM_PULSE_MAX)` — значение ограничивается, но нет проверки на NaN/Inf, которые могут возникнуть при ошибках в драйверах. |
| 7 | **RSSI smoothing — потенциальное деление на ноль** (rx.c:955) | Безопасность | Low | `if (lastRssiSmoothingUs != currentTimeUs)` — защита от деления на 0 есть, но при равенстве значений фильтр не обновляется, что может привести к залипанию RSSI. |

### 2.2. Переключение режимов полёта (rc_adjustments.c, rc_controls.c, rc_modes.c, core.c)

**Файлы**: `src/main/fc/rc_adjustments.c`, `src/main/fc/rc_controls.c`, `src/main/fc/rc_modes.c`, `src/main/fc/core.c`

#### Найденные проблемы:

| # | Проблема | Тип | Серьёзность | Описание |
|---|----------|-----|-------------|----------|
| 8 | **FIXME: magic numbers repeated в rc_adjustments.c** (п.2.11 отчёта) | Best practice | **High** | 30+ магических чисел (0, 100, 200, 1) повторяются в `applyStepAdjustment()` и `applyAbsoluteAdjustment()`. При изменении лимитов в одном месте легко забыть изменить в другом. |
| 9 | **FIXME: magic numbers repeated в cli.c** (п.2.11 отчёта) | Best practice | Medium | Те же магические числа дублируются в cli.c. Отсутствие единого источника истины для констант. |
| 10 | **ARM/DISARM через стики — потенциальный race condition** (rc_controls.c:145-242) | Безопасность | **High** | Логика ARM/DISARM использует статические переменные (`rcDelayMs`, `rcSticks`, `rcDisarmTicks`). При переключении между стиками и переключателем возможны состояния гонки. |
| 11 | **ARM через стики — отсутствие проверки BOXSTICKCOMMANDDISABLE для DISARM** (rc_controls.c:202) | Безопасность | Medium | DISARM через стики (THR_LO + YAW_LO) не проверяет `IS_RC_MODE_ACTIVE(BOXSTICKCOMMANDDISABLE)`, в отличие от ARM (строка 225). Несоответствие в логике. |
| 12 | **ARM через переключатель — debounce только 3 тика** (rc_controls.c:196) | Безопасность | Medium | Для DISARM через переключатель требуется всего 3 подтверждения (`rcDisarmTicks > 3`). При частоте PID-цикла ~8 кГц это ~375 мкс — недостаточная защита от ложных срабатываний. |
| 13 | **processRcStickPositions() — смешение ответственности** (rc_controls.c:145) | Антипаттерн | Medium | Функция обрабатывает ARM/DISARM, калибровку гироскопа, сброс home-позиции GPS, калибровку барометра, смена PID-профилей, калибровку ACC/MAG, триммирование, управление VTX и камерой. God-функция. |
| 14 | **updateActivatedModes() — потенциальная проблема с linked modes** (rc_modes.c:160-165) | Логическая ошибка | Medium | Логика linked modes использует `bitArrayGet(&andMask, mac->linkedTo) != bitArrayGet(&newMask, mac->linkedTo)` — сравнение XOR битовых масок. При сложных связках возможны неожиданные активации. |
| 15 | **ANGLE_MODE принудительно включается при ALT_HOLD/POS_HOLD** (core.c:1028-1042) | Логическая ошибка | Medium | Если активен ALT_HOLD или POS_HOLD, ANGLE_MODE принудительно включается, даже если пользователь его не запрашивал. Может конфликтовать с HORIZON_MODE. |
| 16 | **GPS_RESCUE_MODE имеет приоритет над ALT_HOLD и POS_HOLD** (core.c:1051,1072) | Логическая ошибка | Low | GPS_RESCUE_MODE отключает ALT_HOLD и POS_HOLD. Документировано, но может быть неочевидно для пользователя. |
| 17 | **AUTOPILOT_MODE — только "Step one"** (п.1.1 отчёта) | Незавершённая функция | Medium | Реализован только первый шаг. Отсутствует обработка WAYPOINT_TYPE_LAND и генерация подцелей для HOLD (ORBIT/FIGURE8). |
| 18 | **PID_AUDIO — последние 3 позиции pending** (rc_adjustments.c:86) | Незавершённая функция | Low | Последние 3 позиции в pidAudioPositionToModeMap используют PID_AUDIO_OFF. Требуется реализация. |

### 2.3. Failsafe (failsafe.c, rx.c)

**Файлы**: `src/main/flight/failsafe.c`, `src/main/rx/rx.c`

#### Найденные проблемы:

| # | Проблема | Тип | Серьёзность | Описание |
|---|----------|-----|-------------|----------|
| 19 | **Failsafe stage transition — потенциальный infinite loop** (failsafe.c:260-434) | Логическая ошибка | Medium | Цикл `do { reprocessState = false; ... } while (reprocessState)` — при неправильной конфигурации может привести к бесконечному циклу. Защита отсутствует. |
| 20 | **BOXFAILSAFE — немедленный переход в STAGE2** (failsafe.c:248-251) | Безопасность | Medium | При `failsafe_switch_mode == FAILSAFE_SWITCH_MODE_STAGE2` BOXFAILSAFE форсирует `receivingRxData = false`, что может привести к немедленному дизарму. |
| 21 | **Failsafe KILL switch — немедленный LANDED** (failsafe.c:272-281) | Безопасность | Medium | KILL switch немедленно переводит в FAILSAFE_LANDED, вызывая `disarm()`. Нет подтверждения или задержки. |
| 22 | **Failsafe GPS Rescue — выход по стикам** (failsafe.c:371-378) | Логическая ошибка | Low | Выход из GPS Rescue при `areSticksActive()` — если стики были активны до потери сигнала, выход произойдёт немедленно при восстановлении. |
| 23 | **Failsafe — отсутствие sanity checks в mixer.c** (п.4.10 отчёта) | Best practice | Low | TODO: отсутствуют проверки количества спутников, DOP, точности перед использованием GPS данных в failsafe. |

### 2.4. Подача в PID (pid.c, mixer.c, imu.c, rc.c)

**Файлы**: `src/main/flight/pid.c`, `src/main/flight/mixer.c`, `src/main/flight/imu.c`, `src/main/fc/rc.c`

#### Найденные проблемы:

| # | Проблема | Тип | Серьёзность | Описание |
|---|----------|-----|-------------|----------|
| 24 | **TODO: IMU time constant** (imu.c:629) | Логическая ошибка | Medium | `// TODO: intent is to match IMU time constant, approximately, but I don't exactly know how to do that` — постоянная времени GPS heading confidence подобрана эмпирически. |
| 25 | **TODO: GPS heading remove static** (imu.c:681) | Best practice | Low | `static bool gpsHeadingInitialized = false;` — static переменная должна быть удалена. |
| 26 | **TODO: mixer sanity checks** (mixer.c:597) | Best practice | Low | Отсутствуют sanity checks (количество спутников, DOP, точность) перед использованием GPS данных в микшере. |
| 27 | **PID iTerm reset — зависимость от throttle** (core.c:848-854) | Логическая ошибка | Medium | iTerm сбрасывается при низком throttle, если Airmode неактивен. При быстром переключении throttle может привести к рывкам. |
| 28 | **Runaway Takeoff — деактивация на всё время полёта** (core.c:901) | Логическая ошибка | Medium | После деактивации `runawayTakeoffCheckDisabled = true` навсегда (до перезагрузки). При повторном возникновении проблемы защита не сработает. |
| 29 | **RC Smoothing — outlier detection** (rc.c:602-605) | Логическая ошибка | Low | При 3+ outlier'ах сбрасывается smoothedRxRateHz. При частых сбоях RX-линка может привести к некорректной работе фильтра. |
| 30 | **HEADFREE_MODE — трансформация rcCommand** (rc.c:744-750) | Логическая ошибка | Low | HEADFREE_MODE трансформирует rcCommand через кватернион, но не для всех режимов (ANGLE, ALT_HOLD, POS_HOLD, HORIZON, GPS_RESCUE). Может привести к неожиданному поведению при комбинации режимов. |

---

## 3. Классификация проблем

### 3.1. Логические ошибки

| # | Описание | Файл | Серьёзность |
|---|----------|------|-------------|
| 2 | Неиспользуемая переменная 'c' в sumh.c | rx/sumh.c | Medium |
| 14 | Linked modes — потенциально неожиданная активация | fc/rc_modes.c | Medium |
| 15 | ANGLE_MODE принудительно при ALT_HOLD/POS_HOLD | fc/core.c | Medium |
| 16 | GPS_RESCUE отключает ALT_HOLD/POS_HOLD | fc/core.c | Low |
| 19 | Потенциальный infinite loop в failsafe | flight/failsafe.c | Medium |
| 22 | Выход из GPS Rescue по стикам | flight/failsafe.c | Low |
| 24 | IMU time constant подобрана эмпирически | flight/imu.c | Medium |
| 27 | PID iTerm reset — рывки при переключении throttle | fc/core.c | Medium |
| 28 | Runaway Takeoff — деактивация навсегда | fc/core.c | Medium |
| 29 | RC Smoothing — сброс при частых сбоях | fc/rc.c | Low |
| 30 | HEADFREE — не для всех режимов | fc/rc.c | Low |

### 3.2. Уязвимости безопасности

| # | Описание | Файл | Серьёзность |
|---|----------|------|-------------|
| 6 | Отсутствие проверки NaN/Inf в rcData | rx/rx.c | Low |
| 7 | Потенциальное деление на ноль в RSSI smoothing | rx/rx.c | Low |
| 10 | Race condition в ARM/DISARM логике | fc/rc_controls.c | **High** |
| 11 | DISARM через стики не проверяет BOXSTICKCOMMANDDISABLE | fc/rc_controls.c | Medium |
| 12 | Недостаточный debounce для DISARM через переключатель | fc/rc_controls.c | Medium |
| 20 | BOXFAILSAFE — немедленный переход в STAGE2 | flight/failsafe.c | Medium |
| 21 | KILL switch — немедленный disarm | flight/failsafe.c | Medium |

### 3.3. Нарушения best practices

| # | Описание | Файл | Серьёзность |
|---|----------|------|-------------|
| 5 | Magic number 50 в current.c | sensors/current.c | Low |
| 8 | **30+ magic numbers в rc_adjustments.c** | fc/rc_adjustments.c | **High** |
| 9 | Magic numbers дублируются в cli.c | cli/cli.c | Medium |
| 23 | Отсутствие sanity checks в mixer.c | flight/mixer.c | Low |
| 25 | Static переменная gpsHeadingInitialized | flight/imu.c | Low |
| 26 | Отсутствие sanity checks для GPS | flight/mixer.c | Low |

### 3.4. Антипаттерны

| # | Описание | Файл | Серьёзность |
|---|----------|------|-------------|
| 1 | Логика ARM в rx.c, не в rc_mode.c | rx/rx.c | Low |
| 3 | Смешение flight modes и status indicators | fc/runtime_config.h | Medium |
| 4 | extern зависимость от mw.c | telemetry/mavlink.c | Medium |
| 13 | God-функция processRcStickPositions() | fc/rc_controls.c | Medium |
| 17 | AUTOPILOT — только "Step one" | flight/flight_plan_nav.c | Medium |
| 18 | PID_AUDIO — pending реализации | fc/rc_adjustments.c | Low |

---

## 4. Критичность проблем

### High (требуют немедленного внимания)

1. **FIXME: 30+ magic numbers в rc_adjustments.c** — при изменении лимитов в одном случае, другие останутся несинхронизированными. Может привести к некорректной работе PID-тюнинга в полёте.
2. **Race condition в ARM/DISARM логике** — статические переменные и переключение между стиками/переключателем могут привести к непреднамеренному ARM/DISARM.

### Medium (требуют внимания в ближайшее время)

3. DISARM через стики не проверяет BOXSTICKCOMMANDDISABLE
4. Недостаточный debounce для DISARM через переключатель
5. BOXFAILSAFE — немедленный переход в STAGE2
6. KILL switch — немедленный disarm
7. Потенциальный infinite loop в failsafe
8. IMU time constant подобрана эмпирически
9. PID iTerm reset — рывки при переключении throttle
10. Runaway Takeoff — деактивация навсегда
11. Смешение flight modes и status indicators
12. extern зависимость от mw.c
13. God-функция processRcStickPositions()
14. AUTOPILOT — только "Step one"
15. Linked modes — потенциально неожиданная активация
16. ANGLE_MODE принудительно при ALT_HOLD/POS_HOLD
17. Magic numbers дублируются в cli.c

### Low (желательно исправить)

18. Неиспользуемая переменная 'c' в sumh.c
19. Отсутствие проверки NaN/Inf в rcData
20. Потенциальное деление на ноль в RSSI smoothing
21. Magic number 50 в current.c
22. Отсутствие sanity checks в mixer.c
23. Static переменная gpsHeadingInitialized
24. HEADFREE — не для всех режимов
25. RC Smoothing — сброс при частых сбоях
26. PID_AUDIO — pending реализации
27. Логика ARM в rx.c, не в rc_mode.c

---

## 5. Рекомендации по исправлению

### 5.1. Немедленные исправления (High)

1. **Вынести magic numbers в константы** в rc_adjustments.c:
   - Создать `#define PID_P_LIMIT 200`, `#define PID_I_LIMIT 200`, `#define PID_D_LIMIT 200`, `#define THROTTLE_EXPO_LIMIT 100`, `#define FEEDFORWARD_TRANSITION_MIN 1`, `#define FEEDFORWARD_TRANSITION_MAX 100`
   - Заменить все вхождения магических чисел на эти константы
   - Синхронизировать с cli.c

2. **Устранить race condition в ARM/DISARM**:
   - Добавить атомарные операции для флагов ARM
   - Увеличить debounce для DISARM через переключатель (с 3 до 10+ тиков)
   - Добавить проверку BOXSTICKCOMMANDDISABLE для DISARM через стики

### 5.2. Среднесрочные исправления (Medium)

3. **Рефакторинг processRcStickPositions()**:
   - Разделить на отдельные функции: `processArmDisarm()`, `processCalibration()`, `processProfileChange()`, `processVtxControl()`, `processCameraControl()`
   - Перенести логику инициализации ARM-переключателя из rx.c в rc_mode.c

4. **Улучшить failsafe**:
   - Добавить защиту от infinite loop (максимальное количество итераций)
   - Добавить задержку перед KILL switch
   - Добавить sanity checks для GPS данных

5. **Улучшить IMU**:
   - Документировать или исправить расчёт постоянной времени GPS heading
   - Удалить static переменную gpsHeadingInitialized

6. **Улучшить PID/Mixer**:
   - Добавить sanity checks в mixer.c
   - Исправить Runaway Takeoff — добавить возможность повторной активации

### 5.3. Долгосрочные исправления (Low)

7. **Рефакторинг runtime_config.h**:
   - Разделить flightModeFlags_e и armingFlag_e
   - Убрать смешение режимов и статусов

8. **Устранить extern зависимости**:
   - Убрать extern rssi из mw.c
   - Использовать getter/setter функции

9. **Добавить валидацию NaN/Inf**:
   - В `detectAndApplySignalLossBehaviour()` после `constrainf()`
   - В `updateRSSI()` перед фильтрацией

---

## 6. Сводная статистика

| Категория | High | Medium | Low | Всего |
|-----------|------|--------|-----|-------|
| Логические ошибки | 0 | 6 | 4 | 10 |
| Уязвимости безопасности | 1 | 5 | 1 | 7 |
| Нарушения best practices | 1 | 2 | 3 | 6 |
| Антипаттерны | 0 | 4 | 2 | 6 |
| **Всего** | **2** | **17** | **10** | **29** |

### Ключевые выводы

1. **Наиболее критичная проблема**: 30+ magic numbers в rc_adjustments.c, которые дублируются в cli.c. При изменении лимитов PID-параметров в одном месте, другие останутся несинхронизированными, что может привести к некорректной работе PID-тюнинга в полёте.

2. **Наиболее опасная уязвимость**: Race condition в ARM/DISARM логике. Статические переменные и переключение между стиками и переключателем могут привести к непреднамеренному ARM/DISARM.

3. **Наиболее проблемный файл**: `src/main/fc/rc_adjustments.c` — 30+ magic numbers, copy-paste код, отсутствие констант.

4. **Наиболее проблемный модуль**: ARM/DISARM логика в `rc_controls.c` — race condition, недостаточный debounce, несоответствие проверок для стиков и переключателя.