# Отчёт о незавершённых решениях, нереализованных функциях и временных решениях

**Дата составления**: 2026-05-11
**Источники**: комментарии в коде (TODO/FIXME/HACK/XXX) и история коммитов с 2025-01-01

---

## 1. Незавершённые функции (частичная реализация)

### 1.1. AUTOPILOT: Flight plan guidance — только "Step one"
- **Тип**: Незавершённая функция
- **Файл**: `src/main/flight/flight_plan_nav.c:167-168`
- **Комментарий**: `// TODO: WAYPOINT_TYPE_LAND — trigger descent/disarm path.` / `// TODO: WAYPOINT_PATTERN_ORBIT / FIGURE8 sub-target generation for HOLD.`
- **Связанный коммит**: `eb5cf57cc` — AUTOPILOT: Step one, Flight plan guidance implementation (#14923)
- **Описание**: Реализован только первый шаг системы управления полётным планом. Отсутствует обработка WAYPOINT_TYPE_LAND (снижение/дизарм) и генерация подцелей для HOLD (ORBIT/FIGURE8).

### 1.2. CLI: runtime status для waypoint tracker (Phase 3)
- **Тип**: Незавершённая функция
- **Файл**: `src/main/cli/cli.c:2852`
- **Комментарий**: `// TODO: Add runtime status when Phase 3 (waypoint tracker) is complete`
- **Связанный коммит**: `eb5cf57cc` — AUTOPILOT: Step one, Flight plan guidance implementation (#14923)
- **Описание**: Статус трекера путевых точек в CLI отложен до завершения Phase 3.

### 1.3. CLKIN gyro 2/3/4 на отдельных пинах не поддерживается
- **Тип**: Незавершённая функция
- **Файл**: `src/main/pg/gyrodev.c:266,276,286`
- **Комментарий**: `// TODO: CLKIN gyro 2 on separate pin is not supported yet. need to implement it` (аналогично для gyro 3 и 4)
- **Связанный коммит**: `64abf9135` — PICO: gyro_clkin platform abstraction so RP2350 can use USE_GYRO_CLKIN (#15162)
- **Описание**: Поддержка CLKIN для дополнительных гироскопов (2, 3, 4) на отдельных пинах не реализована.

### 1.4. FB_OSD: флаг не выделен, Configurator не обновлён
- **Тип**: Незавершённая функция
- **Файл**: `src/main/msp/msp.c:976`
- **Комментарий**: `// TODO allocated a new flag for FB_OSD (maybe reuse 1 << 1 ? ), and update Configurator accordingly.`
- **Связанный коммит**: `73d0224ee` — PICO: Initial commit for framebuffer OSD displayport device (FB_OSD) with RP2350 implementation. (#14882)
- **Описание**: Для FB_OSD не выделен отдельный флаг в MSP-протоколе, требуется обновление Configurator.

### 1.5. Rangefinder: новый расширяемый протокол не реализован
- **Тип**: Незавершённая функция
- **Файл**: `src/main/msp/msp_protocol_v2_common.h:26`
- **Комментарий**: `// TODO: implement new, extensible rangefinder protocol`
- **Описание**: Требуется реализация нового расширяемого протокола для дальномеров.

### 1.6. Displayport profiles: настройки не добавлены в settings.c
- **Тип**: Незавершённая функция
- **Файл**: `src/main/pg/displayport_profiles.c:67`
- **Комментарий**: `// TODO add entries in settings.c, so we can set from Configurator / CLI.`
- **Описание**: Настройки профилей дисплейпортов не добавлены в settings.c, недоступны из Configurator/CLI.

### 1.7. GPS: отправка ublox сообщения на NMEA GPS
- **Тип**: Незавершённая функция
- **Файл**: `src/main/io/gps.c:1564`
- **Комментарий**: `// TODO Send ublox message to nmea GPS?`
- **Описание**: Неопределённость с отправкой ublox-сообщений на NMEA GPS.

### 1.8. GPS_numCh: закомментированная строка
- **Тип**: Незавершённая функция
- **Файл**: `src/main/io/gps.c:2543`
- **Комментарий**: `// TODO: GPS_numCh = MAX(GPS_numCh, GPS_SV_MAXSATS_LEGACY + 1);`
- **Описание**: Закомментированная строка обновления количества каналов GPS.

### 1.9. ExpressLRS SX127x: DMA не реализован
- **Тип**: Незавершённая функция
- **Файл**: `src/main/rx/expresslrs.c:1183-1184`
- **Комментарий**: `// TODO No need to handle this on SX1280, but will on SX127x` / `// TODO this needs to be DMA aswell, SX127x unlikely to work right now`
- **Связанный коммит**: `49a0393f5` — SPI ExpressLRS 4.0 support (#14932)
- **Описание**: Для SX127x требуется DMA, без него работа маловероятна.

### 1.10. SX1280: динамический таймаут на основе ожидаемого эфирного времени
- **Тип**: Незавершённая функция
- **Файл**: `src/main/drivers/rx/rx_sx1280.c:502,982`
- **Комментарий**: `// TODO dynamic timeout based on expected onairtime`
- **Описание**: Таймауты захардкожены (0xFF), требуется динамический расчёт.

### 1.11. SX127x: возможный баг в исходном коде
- **Тип**: Незавершённая функция / Возможный баг
- **Файл**: `src/main/drivers/rx/rx_sx127x.c:208`
- **Комментарий**: `//TODO: possible bug in original code`
- **Описание**: Отмечен возможный баг в оригинальном коде записи sync word.

### 1.12. ICM42686P: только начальная поддержка
- **Тип**: Незавершённая функция
- **Файл**: (сенсор добавлен)
- **Связанный коммит**: `dfe1b35e7` — Sensors: Add initial support for ICM42686P (#14941)
- **Описание**: Добавлена только начальная поддержка сенсора ICM42686P.

### 1.13. MT29F flash: "First cut" поддержки
- **Тип**: Незавершённая функция
- **Файл**: `src/main/drivers/flash/flash_mt29f.c:579,881`
- **Комментарий**: `// XXX Test if write enable is reset after each data loading.` / `// XXX Don't need this?`
- **Связанный коммит**: `1f59645aa` — Flash/MT29F - First cut of support for the MT29F1G01ABAFDWB-IT:F flash chips (1Gb NAND) (#14828)
- **Описание**: Первая версия поддержки NAND flash MT29F, требует проверки и доработки.

### 1.14. BMP580 барометр: новая функция
- **Тип**: Незавершённая функция
- **Связанный коммит**: `a433da0fd` — Feature/bmp580 barometer (#14925)
- **Описание**: Добавлена поддержка нового барометра BMP580.

### 1.15. CRSF AHRS: новая функция
- **Тип**: Незавершённая функция
- **Связанный коммит**: `de35bd96b` — CRSF AHRS Support (#14870)
- **Описание**: Добавлена поддержка CRSF AHRS (Attitude Heading Reference System).

### 1.16. DroneCAN GNSS Fix2: новый провайдер
- **Тип**: Незавершённая функция
- **Связанный коммит**: `2dd7019b6` — feat: DroneCAN GNSS Fix2 provider (drives gpsSol) (#15143)
- **Описание**: Добавлен провайдер GNSS Fix2 для DroneCAN.

### 1.17. LCD console subsystem: новая подсистема
- **Тип**: Незавершённая функция
- **Связанный коммит**: `9916c4ab6` — feat: LCD console subsystem for runtime debug output (#15148)
- **Описание**: Новая подсистема LCD-консоли для отладки.

### 1.18. Chirp debug channels: расширение
- **Тип**: Незавершённая функция
- **Связанный коммит**: `da3559756` — Expand chirp debug channels for offline system identification (#15113)
- **Описание**: Расширение каналов chirp debug для идентификации системы.

---

## 2. Временные решения (workaround / kludge / костыли)

### 2.1. XXX Kludge: zombie VCP port
- **Тип**: HACK / XXX
- **Файл**: `src/main/msp/msp_serial.c:652,683`
- **Комментарий**: `// XXX Kludge!!! Avoid zombie VCP port (avoid VCP entirely for now)`
- **Описание**: Грязное решение для избежания "зомби" VCP-порта. VCP полностью исключён из обработки.

### 2.2. HoTT: временный workaround для Hardware serial
- **Тип**: FIXME
- **Файл**: `src/main/telemetry/hott.c:385,397`
- **Комментарий**: `// FIXME temorary workaround for HoTT not working on Hardware serial ports due to hardware/softserial serial port initialisation differences`
- **Описание**: Временное решение для работы HoTT на аппаратных UART из-за различий в инициализации hardware/softserial.

### 2.3. HoTT: первый байт запроса
- **Тип**: FIXME
- **Файл**: `src/main/telemetry/hott.c:613`
- **Комментарий**: `// FIXME the first byte of the HoTT request frame is ONLY either 0x80 (binary mode) or 0x7F (text mode).`
- **Описание**: Закомментированное предупреждение о формате запроса HoTT.

### 2.4. FIXME dependency on mw.c
- **Тип**: FIXME
- **Файл**: `src/main/telemetry/mavlink.c:91`
- **Комментарий**: `extern uint16_t rssi; // FIXME dependency on mw.c`
- **Описание**: Прямая зависимость от глобальной переменной из mw.c.

### 2.5. Magic number 50 в current.c
- **Тип**: FIXME
- **Файл**: `src/main/sensors/current.c:194`
- **Комментарий**: `int throttleFactor = throttleOffset + (throttleOffset * throttleOffset / 50); // FIXME magic number 50. Possibly use thrustLinearization if configured.`
- **Описание**: Магическое число 50 в расчёте throttleFactor. Предлагается использовать thrustLinearization.

### 2.6. HC-SR04: нет детекции подключения
- **Тип**: FIXME
- **Файл**: `src/main/sensors/rangefinder.c:106`
- **Комментарий**: `if (hcsr04Detect(dev, sonarConfig())) {   // FIXME: Do actual detection if HC-SR04 is plugged in`
- **Описание**: Детекция HC-SR04 не реализована, всегда возвращает true.

### 2.7. BEEPER_MULTI_BEEPS: не должен вызываться напрямую
- **Тип**: FIXME
- **Файл**: `src/main/io/beeper.c:226`
- **Комментарий**: `{ BEEPER_ENTRY(BEEPER_MULTI_BEEPS, 14, beep_multiBeeps, "MULTI_BEEPS") }, // FIXME This entry must not be called directly.`
- **Описание**: Запись BEEPER_MULTI_BEEPS не предназначена для прямого вызова.

### 2.8. MSP_OSD_MAX_STRING_LENGTH: неправильное расположение
- **Тип**: FIXME
- **Файл**: `src/main/io/displayport_msp.c:113`
- **Комментарий**: `#define MSP_OSD_MAX_STRING_LENGTH 30 // FIXME move this`
- **Описание**: Определение константы в неправильном месте.

### 2.9. FIXME remove this for targets that don't need a CLI
- **Тип**: FIXME
- **Файл**: `src/main/cli/cli.c:32`
- **Комментарий**: `// FIXME remove this for targets that don't need a CLI. Perhaps use a no-op macro when USE_CLI is not enabled`
- **Описание**: CLI-код присутствует даже для таргетов, где он не нужен.

### 2.10. FIXME rename servoIndex_e
- **Тип**: FIXME
- **Файл**: `src/main/flight/servos.h:73`
- **Комментарий**: `} servoIndex_e; // FIXME rename to servoChannel_e`
- **Описание**: Требуется переименование типа.

### 2.11. FIXME: magic numbers repeated в rc_adjustments.c
- **Тип**: FIXME
- **Файл**: `src/main/fc/rc_adjustments.c:329,356,366,372,381,387,396,401,406,411,443,492,519,529,535,544,550,559,564,569,574,606,642`
- **Комментарий**: `// FIXME magic numbers repeated in cli.c` (и аналогичные)
- **Описание**: Магические числа (0, 100, 200, 1) повторяются в rc_adjustments.c и cli.c. Требуется вынести в константы.

### 2.12. FIXME: пользователи не должны менять flash/pin конфиги
- **Тип**: FIXME
- **Файл**: `src/main/fc/init.c:318,364`
- **Комментарий**: `// FIXME For now, users must NOT change flash/pin configs needed for the system to boot and/or to save the config.`
- **Описание**: Ограничение на изменение конфигурации flash/pin для пользователей.

### 2.13. FIXME: CMS зависит от OSD
- **Тип**: FIXME
- **Файл**: `src/main/cms/cms.c:933`
- **Комментарий**: `// FIXME this should probably not have a dependency on the OSD or OSD slave code`
- **Описание**: CMS имеет нежелательную зависимость от OSD.

### 2.14. FIXME: sumh — значение 'c' не используется
- **Тип**: FIXME
- **Файл**: `src/main/rx/sumh.c:80`
- **Комментарий**: `// FIXME at this point the value of 'c' is unused and un tested, what should it be, is it important?`
- **Описание**: Неиспользуемая и непроверенная переменная 'c'.

### 2.15. FIXME: runtime_config.h — flight modes vs status indicators
- **Тип**: FIXME
- **Файл**: `src/main/fc/runtime_config.h:25`
- **Комментарий**: `// FIXME some of these are flight modes, some of these are general status indicators`
- **Описание**: Смешение режимов полёта и индикаторов статуса.

### 2.16. FIXME: mavlink.c
- **Тип**: FIXME
- **Файл**: `src/main/rx/mavlink.c:45`
- **Комментарий**: `// FIXME`
- **Описание**: Пустой FIXME без описания.

### 2.17. FIXME: OSD элемент — временный символ
- **Тип**: FIXME
- **Файл**: `src/main/osd/osd_elements.c:580`
- **Комментарий**: `return SYM_MAIN_BATT; // FIXME: currently the BAT- symbol, ideally replace with a battery with exclamation mark`
- **Описание**: Временный символ батареи, требуется замена.

### 2.18. XXX: rangefinder — интерфейс к legacy коду CF/BF
- **Тип**: XXX
- **Файл**: `src/main/sensors/rangefinder.c:63-64,200-201`
- **Комментарий**: `// XXX Interface to CF/BF legacy(?) altitude estimation code.` / `// XXX Will be gone once iNav's estimator is ported.`
- **Описание**: Интерфейс к устаревшему коду оценки высоты. Будет удалён после портирования оценки iNav.

### 2.19. XXX: SmartAudio — возможные проблемы с compliance
- **Тип**: XXX
- **Файл**: `src/main/io/vtx_smartaudio.c:128`
- **Комментарий**: `// XXX Possible compliance problem here. Need LOCK/UNLOCK menu?`
- **Описание**: Возможные проблемы с регуляторными требованиями.

### 2.20. XXX: SmartAudio — буфер с запасом 4 байта
- **Тип**: XXX
- **Файл**: `src/main/io/vtx_smartaudio.c:146`
- **Комментарий**: `static uint8_t sa_rbuf[SA_MAX_RCVLEN + 4]; // XXX delete 4 byte guard`
- **Описание**: Защитный запас в 4 байта в буфере, требуется удаление.

### 2.21. XXX: VTX common — эффект USE_VTX_COMMON
- **Тип**: XXX
- **Файл**: `src/main/io/vtx_msp.c:381`, `src/main/io/vtx_tramp.c:669`
- **Комментарий**: `// XXX Effect of USE_VTX_COMMON should be reviewed, as following call to vtxInit will do nothing if vtxCommonSetDevice is not called.`
- **Описание**: Побочный эффект USE_VTX_COMMON — vtxInit ничего не делает без vtxCommonSetDevice.

### 2.22. XXX: CMS — LEFT_MENU_COLUMN и RIGHT_MENU_COLUMN
- **Тип**: XXX
- **Файл**: `src/main/cms/cms.c:145`
- **Комментарий**: `// XXX LEFT_MENU_COLUMN and RIGHT_MENU_COLUMN must be adjusted`
- **Описание**: Константы колонок меню CMS требуют настройки.

### 2.23. XXX: CMS — polled values
- **Тип**: XXX
- **Файл**: `src/main/cms/cms.c:796-797`
- **Комментарий**: `// XXX Polled values at latter positions in the list may not be` / `// XXX printed if not enough room in the middle of the list.`
- **Описание**: Значения в конце списка могут не отображаться.

### 2.24. XXX: CMS — константы подобраны прагматически
- **Тип**: XXX
- **Файл**: `src/main/cms/cms.c:1442-1443`
- **Комментарий**: `// XXX Caveat: Most constants are adjusted pragmatically.` / `// XXX Rewrite this someday, so it uses actual hold time instead`
- **Описание**: Константы времени удержания подобраны эмпирически, требуется переработка.

### 2.25. XXX: CMS — OME должны быть переименованы в CME
- **Тип**: XXX
- **Файл**: `src/main/cms/cms_types.h:23`
- **Комментарий**: `// XXX Upon separation, all OME would be renamed to CME_ or similar.`
- **Описание**: Префиксы OME должны быть переименованы в CME.

### 2.26. XXX: common_post.h — неявные зависимости
- **Тип**: XXX
- **Файл**: `src/main/target/common_post.h:279-280`
- **Комментарий**: `// XXX Followup implicit dependencies among DASHBOARD, display_xxx and USE_I2C.` / `// XXX This should eventually be cleaned up.`
- **Описание**: Неявные зависимости между DASHBOARD, display_xxx и USE_I2C.

### 2.27. XXX: ESC sensor — требуется ревью
- **Тип**: XXX
- **Файл**: `src/main/sensors/esc_sensor.c:301`
- **Комментарий**: `// XXX Review ESC sensor under refactored motor handling`
- **Описание**: Требуется ревью ESC сенсора после рефакторинга motor handling.

### 2.28. XXX: CLI — ESC pass through
- **Тип**: XXX
- **Файл**: `src/main/cli/cli.c:1768`
- **Комментарий**: `// XXX Review ESC pass through under refactored motor handling`
- **Описание**: Требуется ревью ESC pass through после рефакторинга motor handling.

### 2.29. XXX: flashfs — FREE_BLOCK_SIZE
- **Тип**: XXX
- **Файл**: `src/main/io/flashfs.c:571`
- **Комментарий**: `FREE_BLOCK_SIZE = 2048, // XXX This can't be smaller than page size for underlying flash device.`
- **Описание**: FREE_BLOCK_SIZE не может быть меньше размера страницы flash.

### 2.30. XXX: emfat_file — хардкод 2048
- **Тип**: XXX
- **Файл**: `src/main/msc/emfat_file.c:325`
- **Комментарий**: `for ( ; currOffset < flashfsUsedSpace ; currOffset += 2048) { // XXX 2048 = FREE_BLOCK_SIZE in io/flashfs.c`
- **Описание**: Хардкод значения FREE_BLOCK_SIZE.

### 2.31. XXX: bus_spi_config — ожидание RTC6705 cleanup
- **Тип**: XXX
- **Файл**: `src/main/drivers/bus_spi_config.c:50`
- **Комментарий**: `// XXX Waiting for "RTC6705 cleanup #7114" to be done`
- **Описание**: Ожидание завершения рефакторинга RTC6705.

### 2.32. XXX: softserial — future work
- **Тип**: XXX
- **Файл**: `src/main/drivers/serial_softserial.c:354`
- **Комментарий**: `// XXX Otherwise, we may be able to reload counter and continue. (Future work.)`
- **Описание**: Потенциальная оптимизация softserial отложена.

### 2.33. XXX: time.c — синхронизация с dateTimeFormat
- **Тип**: XXX
- **Файл**: `src/main/common/time.c:221`
- **Комментарий**: `// XXX: Keep in sync with dateTimeFormat()`
- **Описание**: Требуется поддержание синхронизации с dateTimeFormat().

### 2.34. XXX: init.c — задержка для оседания конфигурации
- **Тип**: XXX
- **Файл**: `src/main/fc/init.c:449`
- **Комментарий**: `delayMicroseconds(10);  // allow configuration to settle // XXX Could be removed, too?`
- **Описание**: Задержка 10 мкс для оседания конфигурации, возможно, избыточна.

### 2.35. XXX: CMS SmartAudio — pit mode
- **Тип**: XXX
- **Файл**: `src/main/cms/cms_menu_vtx_smartaudio.c:87,136`
- **Комментарий**: `// XXX Take care of pit mode update somewhere???` / `// XXX These should be done somewhere else`
- **Описание**: Обновление pit mode в неправильном месте.

### 2.36. XXX: gyrodev — I2CINVALID
- **Тип**: XXX
- **Файл**: `src/main/pg/gyrodev.c:303`
- **Комментарий**: `devconf[0].i2cBus = I2C_DEV_TO_CFG(I2CINVALID); // XXX Not required?`
- **Описание**: Возможно, избыточная инициализация I2C.

### 2.37. XXX: barometer.h — лишний include
- **Тип**: XXX
- **Файл**: `src/main/drivers/barometer/barometer.h:23`
- **Комментарий**: `#include "drivers/bus.h" // XXX`
- **Описание**: Возможно, лишний include.

### 2.38. XXX: dshot_command — оптимизация
- **Тип**: XXX
- **Файл**: `src/main/drivers/dshot_command.c:62`
- **Комментарий**: `// XXX Optimization opportunity here.`
- **Описание**: Потенциальная оптимизация.

### 2.39. XXX: timer.h — dmaChannel
- **Тип**: XXX
- **Файл**: `src/main/drivers/timer.h:83`
- **Комментарий**: `uint32_t dmaChannel; // XXX Can be much smaller (e.g. uint8_t)`
- **Описание**: Избыточный размер поля dmaChannel.

### 2.40. XXX: serial_uart_impl.h — аллокация UART
- **Тип**: XXX
- **Файл**: `src/main/drivers/serial_uart_impl.h:149`
- **Комментарий**: `// XXX Instances are allocated for uarts defined by USE_UARTx atm.`
- **Описание**: Экземпляры UART аллоцируются на основе USE_UARTx.

### 2.41. XXX: max7456 — CHARS_PER_LINE
- **Тип**: XXX
- **Файл**: `src/main/drivers/max7456.c:180`
- **Комментарий**: `#define CHARS_PER_LINE 30 // XXX Should be related to VIDEO_BUFFER_CHARS_*?`
- **Описание**: Константа CHARS_PER_LINE должна быть связана с VIDEO_BUFFER_CHARS_*.

### 2.42. XXX: flash_mt29f / flash_w25n — тестирование
- **Тип**: XXX
- **Файл**: `src/main/drivers/flash/flash_mt29f.c:579,881`, `src/main/drivers/flash/flash_w25n.c:601,911`
- **Комментарий**: `// XXX Test if write enable is reset after each data loading.` / `// XXX Don't need this?`
- **Описание**: Требуется тестирование сброса write enable и проверка необходимости кода.

### 2.43. XXX: CMS — уровень счётчика
- **Тип**: XXX
- **Файл**: `src/main/cli/cli.c:3610`
- **Комментарий**: `// XXX Show current level count?`
- **Описание**: Неопределённость с отображением количества уровней.

---

## 3. Отложенные решения (disabled / pending / temporary)

### 3.1. STM32N6: SDIO драйвер отключён
- **Тип**: Отложенное решение
- **Связанный коммит**: `e48fe3d32` — STM32N6: SDIO driver (disabled pending hardware validation)
- **Описание**: SDIO драйвер для STM32N6 отключён до аппаратной валидации.

### 3.2. ESP32-S3: временное исключение из CI
- **Тип**: Отложенное решение
- **Связанный коммит**: `4ead22485` — Adding temporary exclusion for ESP32S3 until build is completed.
- **Описание**: ESP32-S3 временно исключён из CI до завершения сборки.

### 3.3. ESP32-S3: scaffold с заглушками
- **Тип**: Отложенное решение
- **Связанный коммит**: `9982f6f2d` — Add ESP32-S3 platform scaffold with stub drivers, build system integration, and split platform-specific tools into platform mk directories (#15016)
- **Описание**: Платформа ESP32-S3 добавлена с драйверами-заглушками.

### 3.4. STM32C5: ICACHE намеренно отключён
- **Тип**: Отложенное решение
- **Связанный коммит**: `79c83e2f2` — STM32C5: document why ICACHE is intentionally left disabled (#15176)
- **Описание**: ICACHE на STM32C5 намеренно отключён, требуется документация причин.

### 3.5. STM32C5: initial driver stubs
- **Тип**: Отложенное решение
- **Связанный коммит**: `c9188ca4e` — STM32C5: add build infrastructure, target, and initial driver stubs
- **Описание**: Начальные заглушки драйверов для STM32C5.

### 3.6. PICO: UART — pending updates for PIO UART
- **Тип**: Отложенное решение
- **Связанный коммит**: `c390aba08` — PICO: Revert uartPinConfigure code (pending updates for PIO UART) (#14499)
- **Описание**: Откат кода uartPinConfigure в ожидании обновлений PIO UART.

### 3.7. PICO: stub функции
- **Тип**: Отложенное решение
- **Связанные коммиты**: `f80df5c3d` — PICO: Stub functions for system reboot and IO unused pin init implementation; `766c7c019` — SPI Bus stub functions for RP PICO; `4648ca7a8` — EXTI Stub functions for RP PICO
- **Описание**: Функции-заглушки для RP PICO (reboot, SPI, EXTI).

### 3.8. PICO: work in progress — bus_spi_pico
- **Тип**: Отложенное решение
- **Связанный коммит**: `de04ac1f1` — PICO bus_spi_pico changes - work in progress...
- **Описание**: Незавершённые изменения bus_spi_pico.

### 3.9. PICO: stdio_pico_stub
- **Тип**: Отложенное решение
- **Связанный коммит**: `12ca97eac` — PICO define away stdio_pico_stub.c.
- **Описание**: Заглушка stdio для PICO.

### 3.10. Config in flash: initial (untested) implementation
- **Тип**: Отложенное решение
- **Связанный коммит**: `bb5a38d11` — Initial (untested) implementation of config in flash 16kb (#14107)
- **Описание**: Непротестированная реализация конфигурации во flash.

### 3.11. PG ID: TODO TBC
- **Тип**: Отложенное решение
- **Файл**: `src/main/pg/pg_ids.h:168`
- **Комментарий**: `// TODO TBC`
- **Описание**: Неопределённый ID параметр-группы.

### 3.12. UARTDEV_CONFIG_MAX: не хватает для всех UART
- **Тип**: Отложенное решение
- **Файл**: `src/main/pg/serial_uart.c:39`
- **Комментарий**: `// TODO(hertz@): UARTDEV_CONFIG_MAX is measured to be exactly 8, which cannot accommodate even all the UARTs below`
- **Описание**: UARTDEV_CONFIG_MAX = 8 недостаточно для всех UART.

### 3.13. SITL: bridge-specific transforms
- **Тип**: Отложенное решение
- **Связанный коммит**: `035a4d655` — SITL: gate bridge-specific transforms on SITL_BRIDGE_GAZEBO (#15158)
- **Описание**: Трансформации для SITL-моста ограничены флагом SITL_BRIDGE_GAZEBO.

### 3.14. RX provider: restore selectable on SITL
- **Тип**: Отложенное решение
- **Связанный коммит**: `389004ed4` — fix: restore selectable RX provider on SITL via FEATURE_RX_UDP (#15164)
- **Описание**: Восстановление выбора RX-провайдера на SITL.

---

## 4. Необходим рефакторинг

### 4.1. DShot bitbang: должен быть деталью реализации
- **Тип**: TODO
- **Файл**: `src/main/drivers/motor.c:36`, `src/main/drivers/dshot.h:30`
- **Комментарий**: `#include "drivers/dshot_bitbang.h" // TODO: bitbang should be behind the veil of dshot (it is an implementation)` / `// TODO: move bitbang as implementation detail of dshot (i.e. dshot should be the interface)`
- **Описание**: Bitbang является деталью реализации DShot, но напрямую инклюдится.

### 4.2. Timers: платформенно-зависимый код
- **Тип**: TODO
- **Файл**: `src/main/pg/motor.h:35,42`
- **Комментарий**: `//TODO: Timers are platform specific. This should be moved to platform specific code.` / `//TODO: DMAR is platform specific. This should be moved to platform specific code.`
- **Описание**: Таймеры и DMAR должны быть перенесены в платформенно-зависимый код.

### 4.3. uartPort_t и uartDevice_t: слияние
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_uart_impl.h:157`
- **Комментарий**: `// TODO: merge uartPort_t and uartDevice_t`
- **Описание**: Требуется слияние двух структур UART.

### 4.4. serialPortIdentifier_e: вынести в отдельный заголовок
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_uart.h:25`
- **Комментарий**: `#include "io/serial.h" // TODO: maybe move serialPortIdentifier_e into separate header`
- **Описание**: Зависимость от io/serial.h через drivers.

### 4.5. CLI: переписать с самостоятельными line feeds
- **Тип**: TODO
- **Файл**: `src/main/cli/cli.c:499`
- **Комментарий**: `// TODO: Fix this by rewriting the entire CLI to have self contained line feeds`
- **Описание**: CLI требует переписывания для корректной обработки line feeds.

### 4.6. Pin-specific names: удалить
- **Тип**: TODO
- **Файл**: `src/main/cli/settings.c:1940`
- **Комментарий**: `// TODO: remove pin specific names`
- **Описание**: Имена, привязанные к конкретным пинам, должны быть удалены.

### 4.7. rc_mode.c: переместить логику
- **Тип**: TODO
- **Файл**: `src/main/rx/rx.c:357`
- **Комментарий**: `// TODO - move to rc_mode.c`
- **Описание**: Логика должна быть перенесена в rc_mode.c.

### 4.8. IMU: согласование постоянной времени
- **Тип**: TODO
- **Файл**: `src/main/flight/imu.c:629`
- **Комментарий**: `// TODO: intent is to match IMU time constant, approximately, but I don't exactly know how to do that`
- **Описание**: Неизвестно, как точно согласовать постоянную времени IMU.

### 4.9. GPS heading: удалить static
- **Тип**: TODO
- **Файл**: `src/main/flight/imu.c:681`
- **Комментарий**: `static bool gpsHeadingInitialized = false;  // TODO - remove`
- **Описание**: Static переменная должна быть удалена.

### 4.10. Mixer: sanity checks
- **Тип**: TODO
- **Файл**: `src/main/flight/mixer.c:597`
- **Комментарий**: `// TODO sanity checks like number of sats, dop, accuracy?`
- **Описание**: Отсутствуют проверки количества спутников, DOP, точности.

### 4.11. Voltage: сделать пользовательской настройкой
- **Тип**: TODO
- **Файл**: `src/main/flight/mixer_init.c:368`
- **Комментарий**: `//TODO: Make this voltage user configurable`
- **Описание**: Напряжение должно быть настраиваемым пользователем.

### 4.12. Cell full voltage: сделать настраиваемым
- **Тип**: TODO
- **Файл**: `src/main/sensors/battery.h:30`
- **Комментарий**: `//TODO: Make the 'cell full' voltage user adjustble`
- **Описание**: Напряжение полной ячейки должно настраиваться пользователем.

### 4.13. asyncfatfs: fileUpdateFilesize
- **Тип**: TODO
- **Файл**: `src/main/io/asyncfatfs/asyncfatfs.c:2063`
- **Комментарий**: `afatfs_fileUpdateFilesize(file); // TODO do we need this?`
- **Описание**: Неопределённость с необходимостью вызова.

### 4.14. Transponder: random jitter
- **Тип**: TODO
- **Файл**: `src/main/io/transponder_ir.c:97`
- **Комментарий**: `// TODO use a random number generator for random jitter? The idea here is to avoid multiple transmitters transmitting at the same time.`
- **Описание**: Отсутствует генератор случайных чисел для jitter.

### 4.15. Dashboard: bus singleton
- **Тип**: TODO
- **Файл**: `src/main/io/dashboard.c:718`
- **Комментарий**: `// TODO Use bus singleton`
- **Описание**: Должен использоваться singleton шины.

### 4.16. LED strip: улучшить партиционирование
- **Тип**: TODO
- **Файл**: `src/main/io/ledstrip.c:237`
- **Комментарий**: `// TODO - improve partitioning (15 leds -> 3x5)`
- **Описание**: Партиционирование 15 светодиодов на 3x5.

### 4.17. LED strip: проверка длины буфера
- **Тип**: TODO
- **Файл**: `src/main/io/ledstrip.c:493`
- **Комментарий**: `// TODO - check buffer length`
- **Описание**: Отсутствует проверка длины буфера.

### 4.18. LED strip: user color
- **Тип**: TODO
- **Файл**: `src/main/io/ledstrip.c:980`
- **Комментарий**: `const hsvColor_t *flashColor = &HSV(ORANGE); // TODO - use user color?`
- **Описание**: Цвет вспышки должен настраиваться пользователем.

### 4.19. FrSky OSD: videoSystem
- **Тип**: TODO
- **Файл**: `src/main/io/frsky_osd.c:513`
- **Комментарий**: `// TODO: Use videoSystem to set the signal standard when`
- **Описание**: Должен использоваться videoSystem для установки стандарта сигнала.

### 4.20. Displayport FrSky OSD: flush screen
- **Тип**: TODO
- **Файл**: `src/main/io/displayport_frsky_osd.c:107`
- **Комментарий**: `// TODO(agh): Do we need to flush the screen here?`
- **Описание**: Неопределённость с необходимостью flush экрана.

### 4.21. Serial: ожидание передачи данных
- **Тип**: TODO
- **Файл**: `src/main/io/serial.c:629`
- **Комментарий**: `// TODO wait until data has been transmitted.`
- **Описание**: Отсутствует ожидание завершения передачи.

### 4.22. Serial: timestamp последних данных
- **Тип**: TODO
- **Файл**: `src/main/io/serial.c:709`
- **Комментарий**: `// TODO: maintain a timestamp of last data received. Use this to`
- **Описание**: Не реализовано ведение timestamp последних полученных данных.

### 4.23. CMS blackbox: неблокирующий режим
- **Тип**: TODO
- **Файл**: `src/main/cms/cms_menu_blackbox.c:181`
- **Комментарий**: `//TODO: Make this non-blocking!`
- **Описание**: Операция blackbox в CMS должна быть неблокирующей.

### 4.24. Compass IST8310: cross axis compensation
- **Тип**: TODO
- **Файл**: `src/main/drivers/compass/compass_ist8310.c:171`
- **Комментарий**: `// TODO: do cross axis compensation`
- **Описание**: Отсутствует компенсация перекрёстных осей.

### 4.25. Barometer MS5611: PROM + CRC
- **Тип**: TODO
- **Файл**: `src/main/drivers/barometer/barometer_ms5611.c:261`
- **Комментарий**: `// TODO prom + CRC`
- **Описание**: Не реализована проверка PROM + CRC.

### 4.26. IO types: конфликт с warning/error
- **Тип**: TODO
- **Файл**: `src/main/drivers/io_types.h:40`
- **Комментарий**: `// TODO - this may conflict with requirement to generate warning/error on IO_t - ioTag_t assignment`
- **Описание**: Потенциальный конфликт с генерацией warning/error.

### 4.27. IO def: макрос для pinid NONE
- **Тип**: TODO
- **Файл**: `src/main/drivers/io_def.h:39`
- **Комментарий**: `// TODO - macro to check for pinid NONE (fully in preprocessor)`
- **Описание**: Отсутствует макрос для проверки pinid NONE на этапе препроцессора.

### 4.28. ESC serial: определение baud
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_escserial.c:343`
- **Комментарий**: `// TODO unable to continue, unable to determine clock and timerPeriods for the given baud`
- **Описание**: Невозможно определить clock и timerPeriods для заданного baud.

### 4.29. Softserial: нет AF для input port
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_softserial.c:151`
- **Комментарий**: `// TODO: there in no AF associated with input port`
- **Описание**: Отсутствует альтернативная функция для входного порта.

### 4.30. Softserial: лишняя деактивация
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_softserial.c:326`
- **Комментарий**: `serialOutputPortDeActivate(softSerial); // TODO: not necessary`
- **Описание**: Возможно, лишняя деактивация порта.

### 4.31. Rangefinder TF: TODO
- **Тип**: TODO
- **Файл**: `src/main/drivers/rangefinder/rangefinder_lidartf.c:112,275`
- **Комментарий**: `#define TF_DETECTION_CONE_DECIDEGREES 900  // TODO` / `// TODO - handle timeout; return value only once (see lidarMT)`
- **Описание**: Необработанный timeout и неопределённый угол конуса обнаружения.

### 4.32. HC-SR04: priority
- **Тип**: TODO
- **Файл**: `src/main/drivers/rangefinder/rangefinder_hcsr04.c:188`
- **Комментарий**: `EXTIConfig(echoIO, &hcsr04_extiCallbackRec, NVIC_PRIO_SONAR_EXTI, IOCFG_IN_FLOATING, BETAFLIGHT_EXTI_TRIGGER_BOTH); // TODO - priority!`
- **Описание**: Приоритет EXTI требует внимания.

### 4.33. RX PWM: timer clocks ticks
- **Тип**: TODO
- **Файл**: `src/main/drivers/rx/rx_pwm.c:53`
- **Комментарий**: `// TODO - change to timer clocks ticks`
- **Описание**: Требуется переход на timer clocks ticks.

### 4.34. RX PWM: fail на недостаток каналов
- **Тип**: TODO
- **Файл**: `src/main/drivers/rx/rx_pwm.c:331,380`
- **Комментарий**: `/* TODO: maybe fail here if not enough channels? */` / `/* TODO: fail here? */`
- **Описание**: Неопределённость с обработкой ошибок при недостатке каналов.

### 4.35. RX A7105: resource
- **Тип**: TODO
- **Файл**: `src/main/drivers/rx/rx_a7105.c:42`
- **Комментарий**: `//TODO: Create resource for this if it ever gets used`
- **Описание**: Ресурс не создан, ожидание использования.

### 4.36. SPI: move to GPIO
- **Тип**: TODO
- **Файл**: `src/main/drivers/bus_spi_impl.h:37`
- **Комментарий**: `#if SPI_TRAIT_AF_PIN //TODO: move to GPIO`
- **Описание**: Логика должна быть перенесена в GPIO.

### 4.37. NVIC: WS2811 DMA priority
- **Тип**: TODO
- **Файл**: `src/main/drivers/nvic.h:39`
- **Комментарий**: `#define NVIC_PRIO_WS2811_DMA NVIC_BUILD_PRIORITY(1, 2) // TODO - is there some reason to use high priority?`
- **Описание**: Высокий приоритет DMA для WS2811 требует обоснования.

### 4.38. UART buffers: naming
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_uart.c:106`
- **Комментарий**: `UART_BUFFERS(Lp1);  // TODO - maybe some other naming scheme ?`
- **Описание**: Схема именования буферов UART требует пересмотра.

### 4.39. UART: TODO ...
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_uart.c:165`
- **Комментарий**: `#if 1 // TODO ...`
- **Описание**: Пустой TODO с заглушкой #if 1.

### 4.40. Serial TCP: clean up & re-init
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_tcp.c:98,104`
- **Комментарий**: `// TODO: clean up & re-init`
- **Описание**: Отсутствует очистка и реинициализация TCP-соединения.

### 4.41. Motor: failure mode
- **Тип**: TODO
- **Файл**: `src/main/drivers/motor.c:232`
- **Комментарий**: `// TODO: perhaps a failure mode here?`
- **Описание**: Отсутствует обработка режима отказа.

### 4.42. MSC emfat: changing filesize
- **Тип**: TODO
- **Файл**: `src/main/msc/emfat.c:678`
- **Комментарий**: `// TODO: handle changing a filesize`
- **Описание**: Не обрабатывается изменение размера файла.

### 4.43. FC init: проверка инициализации моторов
- **Тип**: TODO
- **Файл**: `src/main/fc/init.c:561`
- **Комментарий**: `// TODO: add check here that motors actually initialised correctly`
- **Описание**: Отсутствует проверка корректной инициализации моторов.

### 4.44. Config eeprom: move sdcard and external flash
- **Тип**: TODO
- **Файл**: `src/main/config/config_eeprom_impl.h:24`
- **Комментарий**: `// TODO: potentially move sdcard and external flash also`
- **Описание**: Возможно, требуется перенос sdcard и external flash.

### 4.45. Serial UART impl: obsolete comment
- **Тип**: TODO
- **Файл**: `src/main/drivers/serial_uart_impl.h:25`
- **Комментарий**: `// TODO: this comment is obsolete`
- **Описание**: Устаревший комментарий.

---

## 5. Неполная документация

### 5.1. HoTT: TODO more info
- **Тип**: TODO
- **Файл**: `src/main/telemetry/hott.h:239,255,257,377,379,452,453,479`
- **Комментарий**: `//TODO: more info` (многократно)
- **Описание**: Многочисленные поля структур HoTT не документированы.

### 5.2. HoTT: general_error_number
- **Тип**: TODO
- **Файл**: `src/main/telemetry/hott.h:206`
- **Комментарий**: `uint8_t general_error_number;//#41 Voice error == 12. TODO: more docu`
- **Описание**: Неполная документация поля.

### 5.3. HoTT: version
- **Тип**: TODO
- **Файл**: `src/main/telemetry/hott.h:208`
- **Комментарий**: `uint8_t version; //#43 version number TODO: more info?`
- **Описание**: Неполная документация поля версии.

### 5.4. HoTT: free_char3
- **Тип**: TODO
- **Файл**: `src/main/telemetry/hott.h:255`
- **Комментарий**: `uint8_t free_char3; //#41 Free ASCII character. appears? TODO: Check where this char appears`
- **Описание**: Неизвестно, где используется символ.

### 5.5. HoTT: alarm_invers / bec_current_max
- **Тип**: TODO
- **Файл**: `src/main/telemetry/hott.h:452-453,479`
- **Комментарий**: `//#05 TODO: more info` / `//#32 TODO: not really clear why 2 bytes...`
- **Описание**: Непонятное назначение полей.

---

## 6. Сводная статистика

| Категория | Количество |
|-----------|-----------|
| Незавершённые функции | 18 |
| Временные решения (workaround/kludge) | 43 |
| Отложенные решения | 14 |
| Необходим рефакторинг | 45 |
| Неполная документация | 5 |
| **Всего** | **125** |

### Распределение по типу маркера

| Маркер | Количество |
|--------|-----------|
| TODO | ~70 |
| FIXME | ~30 |
| XXX | ~40 |
| HACK | ~1 |