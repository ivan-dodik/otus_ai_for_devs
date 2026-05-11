# Progress

## What Works
- **Core flight control**: PID control loops, filtering, motor mixing for multi-rotor and fixed-wing
- **Sensor support**: Gyro, accelerometer, barometer, magnetometer, GPS
- **Motor protocols**: DShot (150/300/600), Multishot, Oneshot (125/42), Proshot1000
- **RX protocols**: PWM, PPM, SPI, SBus, SumH, SumD, Spektrum, XBus, CRSF
- **Telemetry**: CRSF, FrSky, HoTT, MSP, MAVLink
- **OSD**: MAX7456-based, with CMS configuration menu
- **Blackbox**: Flight data logging to onboard flash or SD card
- **LED strip**: WS2811 addressable RGB LED support
- **VTX**: SmartAudio, Tramp, RTC6705
- **CLI**: Full text-based configuration
- **MSP**: Communication protocol for Betaflight App
- **Build system**: Make-based with Docker/devcontainer support
- **Target system**: Extensive board support across multiple MCU families
- **Autopilot**: Flight plan guidance (step one) — merged
- **Flash**: OctoSPI multichip support — merged
- **MCU support**: STM32H5 (NUCLEO-H563ZI), STM32N6 (STM32N6570-DK) — merged

## What's Left to Build

### Current Release (2026.6)
- Complete RC phase bug fixes (May 2026)
- Stabilization for Release (June 2026)
- Autopilot flight plan guidance — further steps beyond step one

### Future (2026.12+)
- Continued autopilot feature development
- Additional MCU family support
- New feature development in Alpha phase

## Current Status

### Release Timeline
| Phase | Date | Status |
|-------|------|--------|
| 2025.12 Release | 26-12-2025 | ✅ Completed |
| 2026.6 Beta | 01-04-2026 | ✅ Completed |
| 2026.6 RC | 01-05-2026 | 🔄 In Progress |
| 2026.6 Release | 01-06-2026 | ⏳ Upcoming |
| 2026.12 Beta | 01-10-2026 | ⏳ Planned |
| 2026.12 RC | 01-11-2026 | ⏳ Planned |
| 2026.12 Release | 01-12-2026 | ⏳ Planned |

### Build Status
- CI: GitHub Actions (push.yml) — passing
- Latest commit: `18309739d` — MAVLink heading fix (centidegrees)

## Known Issues
- CLI entry race condition in MSP serial processing (fixed in #15193)
- QMC5883P magnetometer issues (fixed in #15174)
- Failsafe procedure clamping issue (fixed in #15192)
- **125 unresolved issues documented** in `docs/unresolved-issues-report.md` — including incomplete features (18), workarounds (43), pending decisions (14), refactoring needs (45), and missing documentation (5)
- **29 problems in RC signal processing** documented in `docs/rc_signals_analysis.md` — including 2 High (30+ magic numbers in rc_adjustments.c, race condition in ARM/DISARM), 17 Medium, 10 Low
- **29 problems in code review report** documented in `docs/review_report.md` — comprehensive analysis with dependency maps, ARM/DISARM deep dive, 12 improvement recommendations

## Evolution of Project Decisions

### Versioning Change
- Migrated from `4.x` semantic versioning to `YYYY.M.PATCH` format
- Two releases per year (June and December)
- Structured development phases: Alpha → Beta → RC → Release

### MCU Support Expansion
- Originally STM32-focused (F4, F7)
- Expanded to include G4, H7, AT32, GD32, APM32, ESP32, PICO
- Latest additions: STM32H5, STM32N6, STM32C5

### Build System Evolution
- Traditional Make-based build
- Added Docker/devcontainer support for consistent environments
- clang-format integration for code style consistency
- Configurations managed via git submodule
- Git worktree support for REVISION detection

### Feature Evolution
- Autopilot feature development started (flight plan guidance — step one)
- OctoSPI multichip flash support added
- USB product name derivation from BOARD_NAME
- MAVLink heading in centidegrees for improved precision
- **RC signal processing analysis**: Identified 29 problems including critical magic numbers and ARM/DISARM race conditions