Студент: Евгений Ж. (aka ivan-dodik)
Ссылка на репозиторий: [https://github.com/betaflight/betaflight](https://github.com/betaflight/betaflight)

---

# Ревью прошивки Betaflight (анализ обработки RC сигналов и ARM/DISARM логики)

## 1. Краткое описание проекта и выбранной области анализа

**Проект:** Betaflight — прошивка для полётных контроллеров мультироторных и самолётных БПЛА. Основной фокус: производительность полёта, широкий набор функций, поддержка большого количества целевых плат (STM32 F4/G4/F7/H7/C5/H5/N6, AT32, GD32, APM32, PICO и др.). Код написан на C, объём исходников — несколько сотен тысяч строк.

Репозиторий: [https://github.com/betaflight/betaflight](https://github.com/betaflight/betaflight).

Текущая фаза разработки: **2026.6 Release Candidate** (май 2026). Проект активно развивается: добавляются новые MCU, автопилот, улучшается телеметрия.

**Выбранная область анализа:**

* Обработка сигналов от пульта (RC) — от приёма радиосигнала до подачи в PID-регулятор и на двигатели
* Логика ARM/DISARM — механизмы, обеспечивающие включение/выключение полётного режима, включая:
  * ARM через стики (sticks)
  * ARM через переключатель (switch, BOXARM)
  * Взаимодействие с failsafe, crashflip, runaway takeoff
  * Проверки и блокировки, предотвращающие нежелательный ARM
* Выявление возможных проблем: логических ошибок, уязвимостей безопасности, нарушений best practices, антипаттернов

**Источники анализа:**

* Исходный код: `src/main/rx/rx.c`, `src/main/fc/rc_controls.c`,`src/main/fc/rc_controls.h`, `src/main/fc/rc_modes.c`, `src/main/fc/runtime_config.h`, `src/main/fc/core.c`, `src/main/fc/rc_adjustments.c`, `src/main/fc/rc.c`, `src/main/flight/failsafe.c`, `src/main/flight/pid.c`, `src/main/flight/mixer.c`, `src/main/flight/imu.c`
* Ранее подготовленные отчёты: `docs/unresolved-issues-report.md` (125 проблем), `docs/rc_signals_analysis.md` (29 проблем)

---

## 2. Найденные проблемы

### 2.1. Логические ошибки

| #   | Проблема                                              | Файл                        | Серьёзность | Описание                                                                                                                                                                                                 |
| --- | ----------------------------------------------------- | --------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Неиспользуемая переменная 'c' в sumh.c**            | rx/sumh.c                   | Medium      | Неиспользуемая и непроверенная переменная 'c' в парсинге протокола SUMH. Может скрывать логическую ошибку.                                                                                               |
| 2   | **Linked modes — потенциально неожиданная активация** | fc/rc_modes.c (160–165)     | Medium      | Логика linked modes использует `bitArrayGet(&andMask, mac->linkedTo) != bitArrayGet(&newMask, mac->linkedTo)` — сравнение XOR битовых масок. При сложных связках возможны неожиданные активации режимов. |
| 3   | **ANGLE_MODE принудительно при ALT_HOLD/POS_HOLD**    | fc/core.c (1028–1042)       | Medium      | Если активен ALT_HOLD или POS_HOLD, ANGLE_MODE принудительно включается, даже если пользователь его не запрашивал. Может конфликтовать с HORIZON_MODE.                                                   |
| 4   | **GPS_RESCUE отключает ALT_HOLD/POS_HOLD**            | fc/core.c (1051, 1072)      | Low         | GPS_RESCUE_MODE имеет приоритет и отключает ALT_HOLD и POS_HOLD. Документировано, но может быть неочевидно для пользователя.                                                                             |
| 5   | **Потенциальный infinite loop в failsafe**            | flight/failsafe.c (260–434) | Medium      | Цикл `do { reprocessState = false; ... } while (reprocessState)` — при неправильной конфигурации может привести к бесконечному циклу. Защита отсутствует.                                                |
| 6   | **Выход из GPS Rescue по стикам**                     | flight/failsafe.c (371–378) | Low         | Выход из GPS Rescue при `areSticksActive()` — если стики были активны до потери сигнала, выход произойдёт немедленно при восстановлении.                                                                 |
| 7   | **IMU time constant подобрана эмпирически**           | flight/imu.c (629)          | Medium      | `// TODO: intent is to match IMU time constant, approximately, but I don't exactly know how to do that` — комментарий в коде прямо указывает на отсутствие точного расчёта.                              |
| 8   | **PID iTerm reset — рывки при переключении throttle** | fc/core.c (848–854)         | Medium      | iTerm сбрасывается при низком throttle, если Airmode неактивен. При быстром переключении throttle может привести к рывкам.                                                                               |
| 9   | **Runaway Takeoff — деактивация навсегда**            | fc/core.c (901)             | Medium      | После деактивации `runawayTakeoffCheckDisabled = true` навсегда (до перезагрузки). При повторном возникновении проблемы защита не сработает.                                                             |
| 10  | **RC Smoothing — сброс при частых сбоях**             | fc/rc.c (602–605)           | Low         | При 3+ outlier'ах сбрасывается smoothedRxRateHz. При частых сбоях RX-линка может привести к некорректной работе фильтра.                                                                                 |
| 11  | **HEADFREE — не для всех режимов**                    | fc/rc.c (744–750)           | Low         | HEADFREE_MODE трансформирует rcCommand через кватернион, но не для ANGLE, ALT_HOLD, POS_HOLD, HORIZON, GPS_RESCUE. Неожиданное поведение при комбинации режимов.                                         |

### 2.2. Уязвимости безопасности

| #   | Проблема                                                        | Файл                        | Серьёзность | Описание                                                                                                                                                                                                                             |
| --- | --------------------------------------------------------------- | --------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 12  | **Race condition в ARM/DISARM логике** — статические переменные | fc/rc_controls.c (145–242)  | **High**    | Логика ARM/DISARM использует статические переменные (`rcDelayMs`, `rcSticks`, `rcDisarmTicks`). При переключении между стиками и переключателем возможны состояния гонки, которые могут привести к непреднамеренному ARM или DISARM. |
| 13  | **DISARM через стики не проверяет BOXSTICKCOMMANDDISABLE**      | fc/rc_controls.c (202)      | Medium      | DISARM через стики (THR_LO + YAW_LO) не проверяет `IS_RC_MODE_ACTIVE(BOXSTICKCOMMANDDISABLE)`, в отличие от ARM (строка 225). Несоответствие в логике.                                                                               |
| 14  | **Недостаточный debounce для DISARM через переключатель**       | fc/rc_controls.c (196)      | Medium      | Для DISARM через переключатель требуется всего 3 подтверждения (`rcDisarmTicks > 3`). При частоте PID-цикла ~8 кГц это ~375 мкс — недостаточная защита от ложных срабатываний.                                                       |
| 15  | **BOXFAILSAFE — немедленный переход в STAGE2**                  | flight/failsafe.c (248–251) | Medium      | При `failsafe_switch_mode == FAILSAFE_SWITCH_MODE_STAGE2` BOXFAILSAFE форсирует `receivingRxData = false`, что может привести к немедленному дизарму.                                                                                |
| 16  | **KILL switch — немедленный disarm**                            | flight/failsafe.c (272–281) | Medium      | KILL switch немедленно переводит в FAILSAFE_LANDED, вызывая `disarm()`. Нет подтверждения или задержки.                                                                                                                              |
| 17  | **Отсутствие проверки NaN/Inf в rcData**                        | rx/rx.c (804)               | Low         | `constrainf(sample, PWM_PULSE_MIN, PWM_PULSE_MAX)` — значение ограничивается, но нет проверки на NaN/Inf, которые могут возникнуть при ошибках в драйверах.                                                                          |
| 18  | **Потенциальное деление на ноль в RSSI smoothing**              | rx/rx.c (955)               | Low         | При равенстве временных меток фильтр не обновляется, что может привести к залипанию RSSI.                                                                                                                                            |

### 2.3. Нарушения best practices и антипаттерны

| #   | Проблема                                    | Файл                | Серьёзность | Описание                                                                                                                                                                                                         |
| --- | ------------------------------------------- | ------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 19  | **30+ magic numbers в rc_adjustments.c**    | fc/rc_adjustments.c | **High**    | В `applyStepAdjustment()` и `applyAbsoluteAdjustment()` повторяются магические числа (0, 100, 200, 1) без констант. При изменении лимитов PID-параметров в одном случае, другие останутся несинхронизированными. |
| 20  | **Magic numbers дублируются в cli.c**       | cli/cli.c           | Medium      | Те же магические числа дублируются в cli.c. Отсутствие единого источника истины для констант.                                                                                                                    |
| 21  | **Magic number 50 в current.c**             | sensors/current.c   | Low         | Магическое число 50 в расчёте throttleFactor. Предлагается использовать thrustLinearization.                                                                                                                     |
| 22  | **Отсутствие sanity checks в mixer.c**      | flight/mixer.c      | Low         | TODO: отсутствуют проверки количества спутников, DOP, точности перед использованием GPS данных.                                                                                                                  |
| 23  | **Static переменная gpsHeadingInitialized** | flight/imu.c (681)  | Low         | `static bool gpsHeadingInitialized = false;` — static переменная должна быть удалена.                                                                                                                            |

### 2.4. Антипаттерны в архитектуре

| #   | Проблема                                      | Файл                               | Серьёзность | Описание                                                                                                                                                                                                                                       |
| --- | --------------------------------------------- | ---------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 24  | **Логика ARM в rx.c, не в rc_mode.c**         | rx/rx.c (357)                      | Low         | TODO: логика инициализации ARM-переключателя находится в rx.c, хотя должна быть в rc_mode.c. Нарушение разделения ответственности.                                                                                                             |
| 25  | **Смешение flight modes и status indicators** | fc/runtime_config.h (25–96)        | Medium      | FIXME в коде: `// FIXME some of these are flight modes, some of these are general status indicators`. Режимы полёта (ANGLE_MODE, HORIZON_MODE) и индикаторы статуса (ARMED, WAS_EVER_ARMED) находятся в одном enum. Может привести к путанице. |
| 26  | **extern зависимость от mw.c**                | telemetry                          | Medium      | Прямая зависимость от глобальной переменной `rssi` из mw.c через extern. Нарушение инкапсуляции.                                                                                                                                               |
| 27  | **God-функция processRcStickPositions()**     | fc/rc_controls.c (145)             | Medium      | Функция обрабатывает ARM/DISARM, калибровку гироскопа, сброс home-позиции GPS, калибровку барометра, смену PID-профилей, калибровку ACC/MAG, триммирование, управление VTX и камерой — около 10 различных задач в одной функции.               |
| 28  | **AUTOPILOT — только "Step one"**             | flight/flight_plan_nav.c (167–168) | Medium      | Реализован только первый шаг. Отсутствует обработка WAYPOINT_TYPE_LAND и генерация подцелей для HOLD (ORBIT/FIGURE8).                                                                                                                          |
| 29  | **PID_AUDIO — pending реализации**            | fc/rc_adjustments.c (86)           | Low         | Последние 3 позиции в pidAudioPositionToModeMap используют PID_AUDIO_OFF. Требуется реализация.                                                                                                                                                |

### 2.5. Сопоставление с Memory Bank

Большинство найденных проблем согласуются с задачами, зафиксированными в Memory Bank проекта:

* **Наиболее критичная проблема (High):** 30+ magic numbers в `rc_adjustments.c` — подтверждено в Memory Bank как "most problematic file".
* **Наиболее опасная уязвимость (High):** Race condition в ARM/DISARM — подтверждено в Memory Bank как "most dangerous vulnerability".
* **Соответствие TODO:** Многие проблемы имеют соответствующие TODO/FIXME-комментарии в коде, что указывает на осознанный подход команды к техническому долгу.
* **Приоритеты:** High-приоритетные проблемы (race condition, magic numbers) требуют немедленного внимания. Medium-проблемы (рефакторинг, god-функции, смешение enum) соответствуют планам по подготовке к следующей мажорной версии.

---

## 3. Конкретные примеры кода (карта зависимостей RC сигналов и ARM/DISARM логики)

Ниже представлена детальная карта зависимостей — как RC-сигнал проходит от приёмника до двигателей, какие функции и переменные участвуют в обработке, и как корректировки (adjustments) влияют на ARM/DISARM логику.

### 3.1. Полная схема прохождения сигнала

```text
RX драйверы (CRSF/SBUS/IBUS/etc.)
    → rcRaw[] (uint16_t)  — сырые значения каналов [1000;2000]
    → calculateRxChannelsAndUpdateFailsafe() + readRxChannelsApplyRanges()
    → detectAndApplySignalLossBehaviour() — per-channel failsafe
    → rcData[] (float[18], [1000;2000])
        │
        ▼
processRx() [core.c:809]
    ├── updateRSSI()
    ├── ARM/DISARM: if (featureIsEnabled(FEATURE_3D) && !IS_RC_MODE_ACTIVE(BOXARM)) disarm()
    ├── Airmode / iTerm management
    ├── Runaway Takeoff detection
    └── Launch Control
        │
        ▼
processRxModes() [core.c:950]
    ├── Auto-disarm при MOTOR_STOP
    ├── processRcStickPositions() [rc_controls.c:145]
    │   ├── ARM через стики: rcSticks == THR_LO + YAW_HI + PIT_CE + ROL_CE → tryArm()
    │   ├── DISARM через стики: rcSticks == THR_LO + YAW_LO + PIT_CE + ROL_CE → disarm()
    │   ├── ARM через переключатель: IS_RC_MODE_ACTIVE(BOXARM) → tryArm()
    │   ├── DISARM через переключатель: !IS_RC_MODE_ACTIVE(BOXARM) → disarm() (после debounce 3 тиков)
    │   ├── GYRO calibration, GPS home reset, BARO ground level
    │   ├── PID profile change, ACC calibration, MAG calibration
    │   ├── Accelerometer trims (в ANGLE/HORIZON mode)
    │   ├── RATE profile change (в ACRO mode)
    │   ├── VTX control, Camera control, Dashboard control
    │   └── STICK COMMAND DISABLE проверка (только для ARM, НЕ для DISARM!)
    ├── updateActivatedModes() [rc_modes.c:139] — flight mode flags
    ├── processRcAdjustments() — корректировки PID, rates, filter
    ├── ANGLE_MODE / HORIZON_MODE / ALT_HOLD / POS_HOLD / GPS_RESCUE / AUTOPILOT
    └── MAG_MODE / HEADFREE / CHIRP
        │
        ▼
updateRcCommands() [rc.c:695]
    → rcCommand[ROLL/PITCH/YAW] = constrain(rcData[axis] * midrc, -500, +500) + deadband
    → rcCommand[THROTTLE] — через lookup-таблицу с экспонентой
        │
        ▼
processRcCommand() [rc.c:617]
    → applyRates() — Betaflight/Raceflight/KISS/Actual/Quick
    → setpointRate[] — целевая угловая скорость в °/с
    → calculateFeedforward() — feedforwardRaw[]
    → RC smoothing (PT3 filter)
        │
        ▼
pidController() [flight/pid.c]
    → pidData[FD_ROLL/PITCH/YAW].Sum
        │
        ▼
mixTable() [flight/mixer.c:674]
    → motorMix[] → applyMixToMotors() → motor[]
        │
        ▼
writeMotors() [mixer.c:88] → ESC → двигатели
```

### 3.2. Детальный анализ ARM/DISARM логики

**Ключевые файлы и функции:**

| Файл                  | Функция                                  | Роль                                                                    |
| --------------------- | ---------------------------------------- | ----------------------------------------------------------------------- |
| `fc/rc_controls.c`    | `processRcStickPositions()` (строка 145) | Главная функция: определяет стики, ARM/DISARM, калибровки, профили, VTX |
| `fc/rc_controls.c`    | `rcControlsInit()` (строка 427)          | Инициализация: определяет, используется ли ARM через стики              |
| `fc/core.c`           | `tryArm()` (строка 549)                  | Попытка ARM: проверяет все блокировки, устанавливает ARMED              |
| `fc/core.c`           | `disarm()` (строка 492)                  | DISARM: снимает ARMED, логирует, завершает полёт                        |
| `fc/core.c`           | `updateArmingStatus()` (строка 283)      | Устанавливает/снимает флаги блокировки ARM                              |
| `fc/runtime_config.h` | `armingFlag_e` / `armingDisableFlags_e`  | Определения флагов состояния                                            |

**Переменные состояния (статик, разделяемые между вызовами):**

```c
// rc_controls.c — статические переменные в processRcStickPositions()
static int16_t rcDelayMs;           // время удержания стиков (мс)
static uint8_t rcSticks;            // позиции стиков на предыдущем тике
static uint8_t rcDisarmTicks;       // счётчик для debounce DISARM через переключатель
static bool doNotRepeat;            // флаг предотвращения повторения команды

// rc_controls.c — глобальные статические переменные
static bool isUsingSticksToArm = true;     // true — ARM через стики, false — через переключатель
static bool disarmUserRequested = false;   // запрос DISARM от пользователя

// core.c — статические переменные
static int tryingToArm = ARMING_DELAYED_DISARMED;
static bool crashFlipModeActive = false;
static timeUs_t disarmAt;                  // время авто-DISARM
static bool runawayTakeoffCheckDisabled = false;
```

**ARM через стики (строки 225–239):**

```c
} else if (rcSticks == THR_LO + YAW_HI + PIT_CE + ROL_CE
           && !IS_RC_MODE_ACTIVE(BOXSTICKCOMMANDDISABLE)) {   // проверка блокировки
    if (rcDelayMs >= ARM_DELAY_MS && !doNotRepeat) {          // 500 мс задержка
        doNotRepeat = true;
        if (!ARMING_FLAG(ARMED)) {
            tryArm();                                        // попытка ARM
        }
    }
}
```

**DISARM через стики (строки 202–223):**

```c
} else if (rcSticks == THR_LO + YAW_LO + PIT_CE + ROL_CE) {
    if (rcDelayMs >= ARM_DELAY_MS && !doNotRepeat) {
        doNotRepeat = true;
        disarmUserRequested = true;
        resetTryingToArm();
        if (ARMING_FLAG(ARMED)) {
            disarm(DISARM_REASON_STICKS);
        } else {
            // сброс флагов RUNAWAY_TAKEOFF и CRASH_DETECTED
        }
    }
}
```

**Проблема:** DISARM через стики НЕ проверяет `BOXSTICKCOMMANDDISABLE` (строка 202), хотя ARM через стики проверяет (строка 225).

**ARM/DISARM через переключатель (строки 178–201):**

```c
if (!isUsingSticksToArm) {
    if (IS_RC_MODE_ACTIVE(BOXARM)) {
        rcDisarmTicks = 0;
        tryArm();
    } else {
        resetTryingToArm();
        disarmUserRequested = true;
        resetArmingDisabled();
        if (ARMING_FLAG(ARMED) && (failsafeIsReceivingRxData() || boxFailsafeSwitchIsOn)) {
            rcDisarmTicks++;
            if (rcDisarmTicks > 3) {        // debounce — всего 3 тика!
                disarm(DISARM_REASON_SWITCH);
            }
        }
    }
}
```

**Проблема:** debounce составляет всего 3 тика. При частоте ~8 кГц это ~375 мкс — недостаточно для защиты от дребезга.

**Функция tryArm() (core.c:549):**

```c
void tryArm(void) {
    updateArmingStatus();        // устанавливает все armingDisableFlags
    if (!isArmingDisabled()) {   // проверка: если хоть один флаг блокировки активен — ARM не произойдёт
        if (ARMING_FLAG(ARMED)) return;
        // инициализация tryingToArm
        // ... через ARMING_DELAYED_NORMAL или ARMING_DELAYED_LAUNCH_CONTROL
        ENABLE_ARMING_FLAG(ARMED);  // *** ARM NOW ***
    }
}
```

**Проверки блокировки ARM (updateArmingStatus(), core.c:283–490):**

Насчитывается **19 различных блокировок ARM**:

| Флаг                              | Условие блокировки                               |
| --------------------------------- | ------------------------------------------------ |
| `ARMING_DISABLED_NO_GYRO`         | Нет гироскопа                                    |
| `ARMING_DISABLED_FAILSAFE`        | Активен failsafe                                 |
| `ARMING_DISABLED_RX_FAILSAFE`     | Потеря сигнала RX                                |
| `ARMING_DISABLED_NOT_DISARMED`    | Не был дизармлен после потери RX                 |
| `ARMING_DISABLED_BOXFAILSAFE`     | Активен BOXFAILSAFE                              |
| `ARMING_DISABLED_RUNAWAY_TAKEOFF` | Сработал runaway takeoff                         |
| `ARMING_DISABLED_CRASH_DETECTED`  | Обнаружена авария                                |
| `ARMING_DISABLED_THROTTLE`        | Throttle не в LOW                                |
| `ARMING_DISABLED_ANGLE`           | Дрон не в вертикальном положении                 |
| `ARMING_DISABLED_BOOT_GRACE_TIME` | Grace time после включения                       |
| `ARMING_DISABLED_NOPREARM`        | Не активирован PREARM                            |
| `ARMING_DISABLED_LOAD`            | Высокая загрузка CPU                             |
| `ARMING_DISABLED_CALIBRATING`     | Идёт калибровка                                  |
| `ARMING_DISABLED_CLI`             | Активен CLI                                      |
| `ARMING_DISABLED_CMS_MENU`        | Активно CMS-меню                                 |
| `ARMING_DISABLED_MSP`             | Подключён MSP                                    |
| `ARMING_DISABLED_PARALYZE`        | Активен BOXPARALYZE                              |
| `ARMING_DISABLED_GPS`             | Нет GPS fix                                      |
| `ARMING_DISABLED_RESC`            | Активен GPS RESCUE                               |
| `ARMING_DISABLED_DSHOT_TELEM`     | Нет DSHOT телеметрии                             |
| `ARMING_DISABLED_ACC_CALIBRATION` | ACC не откалиброван                              |
| `ARMING_DISABLED_MOTOR_PROTOCOL`  | Не выбран протокол моторов                       |
| `ARMING_DISABLED_ARM_SWITCH`      | ARM switch включён при наличии других блокировок |

### 3.3. Как корректировки (adjustments) влияют на ARM/DISARM

**processRcAdjustments()** (вызывается из `processRxModes()` в core.c:1024) обрабатывает in-flight корректировки через стики и переключатели:

* **Типы корректировок:**
  * `ADJUSTMENT_STEP` — шаговое изменение (например, PID P +1/-1)
  * `ADJUSTMENT_ABSOLUTE` — установка абсолютного значения (например, RATE = 70)

* **Что может быть откорректировано:**
  * PID-коэффициенты (P, I, D)
  * Rate/Expo/Feedforward
  * Фильтры (угол среза D-term, RPM-фильтр)
  * Throttle expo / mid
  * Vbat PID compensation
  * Активные режимы полёта

* **Влияние на ARM/DISARM:**
  * Прямого влияния нет — adjustments не могут вызвать ARM/DISARM
  * Косвенное влияние: корректировка PID-параметров может повлиять на runaway takeoff detection (высокие P/I/D → больший pidSum → возможен runaway takeoff → DISARM)
  * Корректировка типов микшера (passthru) может повлиять на поведение при ARM

* **Проблема:** магические числа (0, 100, 200, 1) в rc_adjustments.c означают, что лимиты PID-параметров не синхронизированы с cli.c. При изменении в одном месте, другое остаётся несинхронизированным.

### 3.4. Файлы-источники карты зависимостей

| Файл                           | Роль                                                                    |
| ------------------------------ | ----------------------------------------------------------------------- |
| `src/main/rx/rx.c`             | Приём сигнала, маппинг каналов, failsafe per-channel                    |
| `src/main/fc/rc_controls.c`    | Логика ARM/DISARM, обработка стиков                                     |
| `src/main/fc/rc_controls.h`    | Определения констант (PWM_RANGE_MIN, PWM_RANGE_MAX, ROL_LO и т.д.)      |
| `src/main/fc/rc_modes.c`       | Управление режимами полёта (updateActivatedModes)                       |
| `src/main/fc/runtime_config.h` | Флаги ARM и режимов полёта                                              |
| `src/main/fc/core.c`           | tryArm(), disarm(), updateArmingStatus(), processRx(), processRxModes() |
| `src/main/fc/rc_adjustments.c` | In-flight корректировки, magic numbers                                  |
| `src/main/fc/rc.c`             | Преобразование rcData → rcCommand, rates, smoothing                     |
| `src/main/flight/failsafe.c`   | Failsafe state machine (потенциальный infinite loop, KILL switch)       |
| `src/main/flight/pid.c`        | PID-регулятор                                                           |
| `src/main/flight/mixer.c`      | Микширование → motor[]                                                  |
| `src/main/flight/imu.c`        | IMU, GPS heading time constant                                          |
| `src/main/cli/cli.c`           | CLI-интерфейс (дублирование magic numbers)                              |

### 3.5. Примеры кода: критические участки

**Пример 1: Race condition в ARM/DISARM (rc_controls.c:145–242)**

```c
static int16_t rcDelayMs;     // статик — разделяется между всеми вызовами
static uint8_t rcSticks;      // статик — предыдущее состояние стиков
static uint8_t rcDisarmTicks; // статик — счётчик debounce

void processRcStickPositions(void) {
    // ... вычисление stTmp на основе rcData[] ...

    if (stTmp == rcSticks) {
        rcDelayMs += getTaskDeltaTimeUs(TASK_SELF) / 1000;
    } else {
        rcDelayMs = 0;         // сброс при изменении стиков
    }
    rcSticks = stTmp;

    // ARM через переключатель
    if (!isUsingSticksToArm) {
        if (IS_RC_MODE_ACTIVE(BOXARM)) {
            rcDisarmTicks = 0;
            tryArm();
        } else {
            // DISARM через переключатель
            rcDisarmTicks++;
            if (rcDisarmTicks > 3) {
                disarm(DISARM_REASON_SWITCH);
            }
        }
    }
    // ARM через стики
    else if (rcSticks == THR_LO + YAW_HI + ...) {
        // ...
    }
}
```

**Проблема:** При переключении между стиками и переключателем во время работы `processRcStickPositions()`, статические переменные `rcDelayMs`, `rcSticks`, `rcDisarmTicks` могут находиться в несогласованном состоянии. Например, если пользователь начал ARM через стики (rcDelayMs начал накапливаться), а затем переключился на BOXARM — проверка `isUsingSticksToArm` (строка 178) изменится, но rcDelayMs не сбросится.

**Пример 2: Debounce DISARM (rc_controls.c:195–200)**

```c
rcDisarmTicks++;
if (rcDisarmTicks > 3) {
    // require three duplicate disarm values in a row before we disarm
    disarm(DISARM_REASON_SWITCH);
}
```

**Проблема:** 3 тика при частоте ~8 кГц ≈ 375 мкс. Рекомендация: увеличить до 10+ (соответствует ~1.25 мс).

**Пример 3: Failsafe infinite loop (failsafe.c)**

```c
do {
    reprocessState = false;
    // ... сложная логика переходов между состояниями ...
} while (reprocessState);
```

**Проблема:** Нет защиты от бесконечного цикла. При неправильной конфигурации или редких условиях может привести к зависанию.

**Пример 4: Магические числа в rc_adjustments.c**

```c
void applyStepAdjustment(uint8_t adjustmentStepFunction) {
    // ...
    case ADJUSTMENT_PID_P:
        currentPidProfile->pid[pidIndex].P += stepValue;
        currentPidProfile->pid[pidIndex].P = constrain(currentPidProfile->pid[pidIndex].P, 0, 200);  // magic 200
        break;
    case ADJUSTMENT_PID_I:
        currentPidProfile->pid[pidIndex].I += stepValue;
        currentPidProfile->pid[pidIndex].I = constrain(currentPidProfile->pid[pidIndex].I, 0, 200);  // magic 200
        break;
    // ... magic numbers повторяются десятки раз
}
```

**Проблема:** Более 30 вхождений чисел 0, 100, 200, 1 без единых #define. Если лимит PID P изменится в CLI, rc_adjustments.c останется со старым значением.

---

### 4. Предложения улучшений

### Срочные (высокий риск)

1. **Устранить race condition в ARM/DISARM логике:**
   * Добавить атомарные операции для флагов ARM
   * Сбросить статические переменные `rcDelayMs`, `rcSticks`, `rcDisarmTicks` при переключении между стиками и переключателем
   * Увеличить debounce для DISARM через переключатель с 3 до 10+ тиков

2. **Добавить проверку BOXSTICKCOMMANDDISABLE для DISARM через стики:**
   * В `rc_controls.c:202` добавить `!IS_RC_MODE_ACTIVE(BOXSTICKCOMMANDDISABLE)`, как это сделано для ARM (строка 225)

3. **Вынести magic numbers в константы в rc_adjustments.c:**
   * Создать `#define PID_P_LIMIT 200`, `#define PID_I_LIMIT 200`, `#define PID_D_LIMIT 200`, `#define RC_RATE_MAX 255` и т.д.
   * Заменить все вхождения магических чисел на эти константы
   * Синхронизировать с cli.c

### Среднесрочные (улучшение кода)

4. **Рефакторинг processRcStickPositions():**
   * Разделить на отдельные функции: `processArmDisarm()`, `processCalibration()`, `processProfileChange()`, `processVtxControl()`, `processCameraControl()`
   * Перенести логику инициализации ARM-переключателя из rx.c в rc_mode.c

5. **Улучшить failsafe:**
   * Добавить защиту от infinite loop (максимальное количество итераций, например 100)
   * Добавить задержку перед KILL switch (хотя бы 100 мс)
   * Добавить sanity checks для GPS данных

6. **Разделить flightModeFlags_e и armingFlag_e:**
   * В `runtime_config.h` вынести статусные индикаторы (ARMED, WAS_EVER_ARMED) в отдельный enum
   * Убрать FIXME-комментарий

7. **Улучшить IMU:**
   * Документировать или исправить расчёт постоянной времени GPS heading
   * Удалить static переменную `gpsHeadingInitialized`

8. **Улучшить Runaway Takeoff:**
   * Добавить возможность повторной активации (сейчас `runawayTakeoffCheckDisabled = true` навсегда)

### Долгосрочные (архитектурные)

9. **Устранить extern зависимости:**
   * Убрать extern `rssi` из mw.c
   * Использовать getter/setter функции

10. **Реализовать недостающие функции автопилота:**
    * WAYPOINT_TYPE_LAND (снижение/дизарм)
    * Генерация подцелей для HOLD (ORBIT/FIGURE8)

11. **Добавить валидацию NaN/Inf:**
    * В `detectAndApplySignalLossBehaviour()` после `constrainf()`
    * В `updateRSSI()` перед фильтрацией

12. **Обновить runtime_config.h:**
    * Убрать закомментированные режимы (GPS_HOME_MODE, RANGEFINDER_MODE)
    * Добавить документацию для каждого флага

---

## **5. Итоговый вывод**

Код Betaflight демонстрирует высокое качество и хорошую организацию для проекта такого масштаба. Несмотря на то, что это прошивка реального времени для критически важного применения (полёт дрона), в ней присутствуют серьёзные проблемы:

**Критические проблемы (должны быть исправлены немедленно):**

1. **Race condition в ARM/DISARM логике** — статические переменные и переключение между стиками и переключателем могут привести к непреднамеренному ARM/DISARM в полёте
2. **30+ magic numbers в rc_adjustments.c** — при изменении лимитов PID в одном месте, другие останутся несинхронизированными
3. **Недостаточный debounce DISARM** — всего 3 тика (~375 мкс)
4. **Отсутствие проверки BOXSTICKCOMMANDDISABLE для DISARM через стики**

**Архитектурные проблемы:**

* God-функция `processRcStickPositions()` — около 10 различных задач в одной функции
* Смешение режимов полёта и статусных индикаторов в одном enum
* extern-зависимости, нарушающие инкапсуляцию
* Магические числа без единого источника истины

**Позитивные аспекты:**

* Большинство проблем имеют TODO/FIXME-комментарии, что указывает на осознанный подход команды к техническому долгу
* Хорошая организация модулей, чёткое разделение ответственности
* Наличие модульных тестов (Google Test)
* Активное развитие и регулярные релизы

**Сводная статистика:**

| Категория                | High  | Medium | Low    | Всего  |
| ------------------------ | ----- | ------ | ------ | ------ |
| Логические ошибки        | 0     | 6      | 4      | 10     |
| Уязвимости безопасности  | 1     | 5      | 1      | 7      |
| Нарушения best practices | 1     | 2      | 3      | 6      |
| Антипаттерны             | 0     | 4      | 2      | 6      |
| **Всего**                | **2** | **17** | **10** | **29** |

---

## **Приложение: использованные промпты**

Все промпты сохранены в файле `PROMPTS.md` (корень проекта). Ниже приведён список:

| №   | Дата       | Промпт                                                                                                                                                                                                                                                           | Результат                                        |
| --- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| 1   | 2026-05-11 | Сформируй архитектурный обзор проекта: назначение; ключевые директории; entrypoints; основные модули; порядок чтения кода.                                                                                                                                       | `docs/architecture-overview.md`                  |
| 2   | 2026-05-11 | Построй execution flow для управляющих воздействий (сигналов) от пульта до двигателей. Определи: в каком файле и в какой функции принимается сигнал; через какие ключевые функции проходит обработка; какие модули и пакеты участвуют; основные точки ветвления. | `docs/rc_signals_flow.md`                        |
| 3   | 2026-05-11 | Подготовь план для агента по анализу проекта на возможные незавершённые решения, нереализованные функции и временные решения. Источники: TODO/FIXME/HACK-комментарии, история коммитов с 2025-01-01.                                                             | `docs/unresolved-issues-report.md` (125 проблем) |
| 4   | 2026-05-12 | Составь план для агента по анализу кода приёма и обработки сигналов от пульта, переключению режимов полёта, до подачи в PID-регулятор. Анализ на логические ошибки, уязвимости, best practices, антипаттерны.                                                    | `docs/rc_signals_analysis.md` (29 проблем)       |
| 5   | 2026-05-12 | Подготовь отчёт о ревью кода по шаблону `review_example.md`. Проанализировать ARM/DISARM логику, построить карту зависимостей RC сигналов. Скомпилировать итоговый документ `docs/review_report.md`.                                                             | `docs/review_report.md` (данный документ)        |
