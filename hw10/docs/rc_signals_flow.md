# Execution Flow: Сигнал от пульта до двигателей в Betaflight

## Пошаговая схема (8 шагов)

### Шаг 1: Приём сигнала от пульта
**Файл:** `src/main/rx/rx.c` — `rxInit()` (строка 321)
- Определяется тип приёмника: Serial (CRSF/SBUS/Spektrum/etc.), PPM, PWM, SPI, MSP, UDP
- Устанавливаются callback-функции: `rcReadRawFn`, `rcFrameStatusFn`, `rcProcessFrameFn`
- Конкретные протоколы: `crsfRxInit()`, `sbusInit()`, `spektrumInit()`, `ibusInit()`, `ghstRxInit()`, `fportRxInit()`, `srxl2RxInit()`, `sumdInit()`, `sumhInit()`, `xBusInit()`, `jetiExBusInit()`, `mavlinkRxInit()`, `rxSpiInit()`, `rxMspInit()`, `rxPwmInit()`

### Шаг 2: Проверка новых фреймов
**Файл:** `src/main/rx/rx.c` — `rxFrameCheck()` (строка 562)
- Опрашивает `rcFrameStatusFn()` для каждого провайдера
- Устанавливает `rxSignalReceived`, `rxDataProcessingRequired`

### Шаг 3: Обработка RX (taskUpdateRxMain → processRx)
**Файл:** `src/main/fc/tasks.c:183` → `src/main/fc/core.c:809`
- `calculateRxChannelsAndUpdateFailsafe()` (rx.c:830):
  - `readRxChannelsApplyRanges()` → читает сырые каналы через `rcReadRawFn()`, применяет калибровку → **rcRaw[]**
  - `detectAndApplySignalLossBehaviour()` → применяет failsafe логику → **rcData[]** (float[18], диапазон [1000;2000])
- `updateRSSI()`, `failsaveStartMonitoring()`, управление Airmode/iTerm

### Шаг 4: Обработка режимов полёта и ARM/DISARM
**Файл:** `src/main/fc/core.c` — `processRxModes()` (строка 950)
- `processRcStickPositions()` (rc_controls.c:145):
  - **ARM через стики:** THROTTLE LOW + YAW HIGH → `tryArm()` (core.c:549)
  - **DISARM через стики:** THROTTLE LOW + YAW LOW → `disarm()`
  - **ARM через переключатель:** `IS_RC_MODE_ACTIVE(BOXARM)` → `tryArm()`
- `updateActivatedModes()` (rc_modes.c:139) — устанавливает flight mode flags (ANGLE, HORIZON, ALT_HOLD, POS_HOLD, GPS_RESCUE, MAG, HEADFREE, PASSTHRU, AUTOPILOT)

### Шаг 5: Преобразование rcData в rcCommand
**Файл:** `src/main/fc/rc.c` — `updateRcCommands()` (строка 695)
- ROLL/PITCH/YAW: `rcCommand[axis] = constrain(rcData[axis] - midrc, -500, 500)` + deadband
- THROTTLE: через lookup-таблицу с экспонентой → **rcCommand[]** (float[4])

### Шаг 6: Применение rates и расчёт setpoint
**Файл:** `src/main/fc/rc.c` — `processRcCommand()` (строка 617) — вызывается из `subTaskRcCommand()` (core.c:1346)
- `rcCommandf = rcCommand[axis] / divider` → [-1.0; 1.0]
- `angleRate = applyRates(axis, rcCommandf, rcCommandfAbs)` — выбор функции rates:
  - `applyBetaflightRates()` (по умолчанию)
  - `applyRaceFlightRates()`, `applyKissRates()`, `applyActualRates()`, `applyQuickRates()`
- `rawSetpoint[axis] = constrainf(angleRate, -rate_limit, rate_limit)` → **setpointRate[]** (целевая угловая скорость в °/с)
- `calculateFeedforward()` → **feedforwardRaw[]**
- RC smoothing (PT3-фильтр)

### Шаг 7: PID-регулятор
**Файл:** `src/main/fc/core.c` — `subTaskPidController()` (строка 1217) → `pidController()` (flight/pid.c)
- Использует `setpointRate[]` как задание, `gyro.gyroADCf[]` как обратную связь
- Вычисляет **pidData[FD_ROLL].Sum**, **pidData[FD_PITCH].Sum**, **pidData[FD_YAW].Sum**
- Runaway Takeoff detection

### Шаг 8: Микширование и запись на двигатели
**Файл:** `src/main/fc/core.c` — `subTaskMotorUpdate()` (строка 1309)

**8a. `mixTable()` (flight/mixer.c:674):**
- `calculateThrottleAndCurrentMotorEndpoints()` — throttle с учётом 3D, dynamic idle, sag compensation
- Crash Flip mode (если активен — выход)
- PID sum scaling: `scaledAxisPid = constrain(pidData.Sum, -pidSumLimit, pidSumLimit) / PID_MIXER_SCALING`
- Throttle limit, anti-gravity, TPA, dynamic LPF, throttle boost, thrust linearization, RPM limiter
- **Микширование:** `motorMix[i] = scaledPidRoll * mixer[i].roll + scaledPidPitch * mixer[i].pitch + scaledPidYaw * mixer[i].yaw`
- Alt Hold / GPS Rescue переопределяют throttle
- `applyMixerAdjustment()` / `applyMixerAdjustmentLinear()` / `applyMixerAdjustmentEzLand()` — нормализация
- `applyMixToMotors()` → **motor[]** (float[MAX_SUPPORTED_MOTORS])

**8b. `writeMotors()` (mixer.c:88) → `motorWriteAll(motor)`** — драйверный уровень → ESC → двигатели

---

## Ключевые точки ветвления

| Ветвление | Файл | Строка |
|-----------|------|--------|
| Выбор провайдера RX | rx.c | 321-340 |
| Failsafe per-channel | rx.c | 744-828 |
| ARM/DISARM (стики vs BOXARM) | rc_controls.c | 145-242 |
| Режимы полёта (ANGLE/HORIZON/ALT/GPS_RESCUE) | core.c | 1027-1178 |
| Выбор rates (Betaflight/Raceflight/KISS/Actual/Quick) | rc.c | 864-881 |
| Тип микшера (LEGACY/LINEAR/DYNAMIC/EZLANDING) | mixer.c | 816-830 |
| 3D-режим | mixer.c | 125-226 |
| Crash Flip | mixer.c | 278-400 |
| Motor Stop | mixer.c | 832-842 |

## Влияние режимов полёта

- **ANGLE/HORIZON** — PID использует угол (attitude) вместо угловой скорости
- **ALT_HOLD** — throttle переопределяется `getAutopilotThrottle()`
- **GPS_RESCUE** — throttle и yaw rate переопределяются GPS Rescue
- **PASSTHRU** — PID-суммы не используются, rcCommand идёт напрямую
- **HEADFREE** — rcCommand трансформируется через кватернион
- **LAUNCH_CONTROL** — throttle = 0, специальный mixer для pitch-only

## ARM/DISARM

- **ARM стики:** THR_LO + YAW_HI + PIT_CE + ROL_CE → `tryArm()` → `ENABLE_ARMING_FLAG(ARMED)`
- **ARM переключатель:** `IS_RC_MODE_ACTIVE(BOXARM)` → `tryArm()`
- **DISARM стики:** THR_LO + YAW_LO + PIT_CE + ROL_CE → `disarm(DISARM_REASON_STICKS)`
- **DISARM переключатель:** BOXARM неактивен → `disarm(DISARM_REASON_SWITCH)`
- **Автоматический:** Runaway Takeoff, throttle timeout, crash flip

## Файлы для первоочередного чтения

1. `src/main/rx/rx.c` — главный RX-обработчик
2. `src/main/fc/core.c` — главный полётный цикл
3. `src/main/fc/rc.c` — rates, feedforward, RC smoothing
4. `src/main/fc/rc_controls.c` — ARM/DISARM логика
5. `src/main/fc/rc_modes.c` — режимы полёта
6. `src/main/flight/mixer.c` — микширование → motor[]
7. `src/main/fc/tasks.c` — taskUpdateRxMain (state machine)
8. `src/main/flight/pid.c` — PID-регулятор
9. `src/main/fc/runtime_config.h` — ARMING_FLAG/FLIGHT_MODE макросы
10. `src/main/rx/crsf.c` (пример) — конкретная реализация протокола