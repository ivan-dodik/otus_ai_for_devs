# Active Context

## Current Work Focus
The project is in active development for the **2026.6 release** (currently in RC phase as of May 2026). Recent commits show ongoing work across multiple areas. Comprehensive analyses have been completed: unresolved issues (125 items), RC signal processing code (29 problems), and a full code review report (29 problems with dependency map and ARM/DISARM analysis).

### AI Agent Infrastructure
The project has been augmented with a comprehensive AI agent instruction system:
- `.clinerules/coding-style.md` — coding style rules derived from `betaflight_coding_style.md`
- `.clinerules/project-guide.md` — main project guide with context, boundaries, output requirements
- `.clinerules/default-rules.md` — Memory Bank structure and update rules
- `.clinerules/update_prompts.md` — documentation rules for PROMPTS.md and CHANGES.md
- `docs/ai/TASKS.md` — 4 template task scenarios with prompts and criteria
- `docs/ai/DEFINITION_OF_DONE.md` — task completion checklist
- `docs/ai/PLAN.md` — execution plan with progress tracking

### Recent Activity (from git log — latest 20 commits as of 2026-05-11)
- **MAVLink telemetry**: Sending GLOBAL_POSITION_INT heading in centidegrees (#15205)
- **Build system**: Git worktree detection fix for REVISION (#15209)
- **Flash drivers**: OctoSPI multichip support + MX66UW1G45G driver (#15199)
- **Autopilot**: Flight plan guidance implementation — step one (#14923)
- **Config fixes**: Failsafe procedure clamping (#15192), CLI race condition fix in MSP serial processing (#15193)
- **Sensor fixes**: QMC5883P magnetometer fix (#15174)
- **New hardware bring-up**: STM32N6570-DK (#15153), NUCLEO-H563ZI (#15180)
- **GPS**: CRSF GPS time message (#15167), calendar/epoch conversion optimization (#15184)
- **USB**: Product name derivation from BOARD_NAME (#15182)
- **Code quality**: clang-format devcontainer (#15059)
- **Build system**: Auto-include rangefinder/opticalflow drivers for cloud build options (#15156)
- **Drivers**: NULL-check dev->bus in busBusy() (#15188)
- **STM32C5**: SYSCLK source from HSE via PSI with HSI fallback (#15177), ICACHE documentation (#15176)

## Recent Changes
- New MCU support: STM32H5 (NUCLEO-H563ZI), STM32N6 (STM32N6570-DK)
- Autopilot feature development (flight plan guidance — step one)
- Flash driver improvements (OctoSPI multichip support)
- Various bug fixes and optimizations
- clang-format devcontainer for consistent code formatting
- USB product name now derived from BOARD_NAME
- **Unresolved issues analysis**: Created `docs/unresolved-issues-report.md` — 125 issues found across 5 categories (incomplete features, workarounds, pending decisions, refactoring needs, missing documentation)
- **RC signals analysis**: Created `docs/rc_signals_analysis.md` — 29 problems found across 4 categories (logical errors, security vulnerabilities, best practices violations, antipatterns) in the RC signal processing pipeline from channel mapping to PID input
- **Code review report**: Created `docs/review_report.md` — comprehensive review of RC signal handling and ARM/DISARM logic with dependency maps, code examples, and improvement recommendations (29 problems across 4 categories)
- **AI agent infrastructure** (2026-05-17 22:39–23:19): Created `.clinerules/coding-style.md`, `.clinerules/project-guide.md`, `docs/ai/TASKS.md`, `docs/ai/DEFINITION_OF_DONE.md`, `docs/ai/PLAN.md`
- **Debounce for DISARM switch** (2026-05-17 23:32): Replaced tick-based counter with time-based debounce (50 ms via `millis()` + `cmpTimeMs()`) in `src/main/fc/rc_controls.c`
- **Blackbox refactor** (2026-05-18 00:40): Extracted initialization functions from `blackbox.c` into `blackbox_init.c` / `blackbox_init.h`. Reduced `blackbox.c` by ~60 lines.
- **Unit tests for RX module** (2026-05-18 01:15): Added 13 unit tests covering 4 functions (`isPulseValid()`, `applyRxChannelRangeConfiguraton()`, `updateLinkQualitySamples()`, `resetAllRxChannelRangeConfigurations()`). All tests pass.

## Next Steps
Based on the release schedule:
1. Complete **2026.6 RC** phase (May 2026) — currently active
2. **2026.6 Release** (June 2026)
3. Begin **2026.12 Alpha** development

AI agent tasks completed so far:
- ✅ Coding style rules (`.clinerules/coding-style.md`)
- ✅ Project guide for AI agents (`.clinerules/project-guide.md`)
- ✅ Template tasks and Definition of Done (`docs/ai/TASKS.md`, `docs/ai/DEFINITION_OF_DONE.md`)
- ✅ Debounce for DISARM switch (Задача №2)
- ✅ Blackbox refactor — extraction of initialization (Задача №3)
- ✅ Unit tests for RX module (Задача №4)

## Active Decisions and Considerations

### Architecture Decisions
- **Autopilot integration**: New flight plan guidance system being added (step one merged)
- **MCU expansion**: Ongoing support for new STM32 families (H5, N6, C5)
- **Build system improvements**: Devcontainer support, clang-format integration
- **Flash storage**: OctoSPI multichip support for larger flash configurations
- **Blackbox module refactored**: Initialization logic extracted to `blackbox_init.c/h` for better separation of concerns

### Technical Considerations
- Real-time performance must be maintained as features are added
- Flash/RAM usage must be managed across diverse target configurations
- Backward compatibility with existing configurations and hardware
- Git worktree support in build system for REVISION detection

### Key Findings from RC Signals Analysis
- **Most critical issue**: 30+ magic numbers in `rc_adjustments.c` duplicated in `cli.c` — PID tuning limits are not synchronized
- **Most dangerous vulnerability**: Race condition in ARM/DISARM logic — static variables and switch/stick mode switching can cause unintended ARM/DISARM
- **Most problematic file**: `src/main/fc/rc_adjustments.c` — copy-paste code, no constants
- **Most problematic module**: ARM/DISARM logic in `rc_controls.c` — race condition, insufficient debounce, inconsistent checks

## Important Patterns and Preferences

### Code Style
- C coding style defined in project coding style documentation
- clang-format configuration being introduced for consistent formatting
- Clear separation between driver layer and application logic
- AI agent coding style rules defined in `.clinerules/coding-style.md` (1TBS, 4 spaces, no tabs, lowerCamelCase, braces required)

### Development Workflow
- Pull request review process with thorough review requirements
- GitHub Actions for CI/CD
- Docker/devcontainer for consistent build environments
- Config submodule for target configurations
- AI agent documentation workflow: `CHANGES.md` → `PROMPTS.md` → `docs/ai/PLAN.md` → `memory-bank/activeContext.md`

## Documentation References
- **Architecture Overview**: `docs/architecture-overview.md` — comprehensive project structure, entrypoints, module descriptions, recommended reading order
- **RC Signal Flow**: `docs/rc_signals_flow.md` — detailed 8-step execution flow from RC receiver to motors
- **Unresolved Issues Report**: `docs/unresolved-issues-report.md` — 125 issues across 5 categories (incomplete features, workarounds, pending decisions, refactoring needs, missing documentation)
- **RC Signals Analysis**: `docs/rc_signals_analysis.md` — 29 problems in RC signal processing pipeline (logical errors, security vulnerabilities, best practices violations, antipatterns) with recommendations
- **Code Review Report**: `docs/review_report.md` — comprehensive code review of RC signal handling and ARM/DISARM logic with dependency maps, code examples, and improvement recommendations (29 problems across 4 categories)
- **Project Guide for AI**: `.clinerules/project-guide.md` — main instructions for AI agents working on Betaflight
- **Coding Style Rules**: `.clinerules/coding-style.md` — C coding style rules derived from `betaflight_coding_style.md`
- **Template Tasks**: `docs/ai/TASKS.md` — 4 typical task scenarios with prompts and completion criteria
- **Definition of Done**: `docs/ai/DEFINITION_OF_DONE.md` — checklist for task completion
- **Prompt History**: `PROMPTS.md` — chronological log of all agent prompts and results
- **Change History**: `CHANGES.md` — chronological log of all project changes

## 2026-05-17 22:39 — Правила стиля кодирования для CLine

**Описание:** Создан файл `.clinerules/coding-style.md` на основе `betaflight_coding_style.md` с правилами для агента CLine по стилю C-кода в проекте Betaflight (форматирование, именование, typedef, переменные, типы данных, функции, include, комментарии).

**Затронутые файлы:**
- `.clinerules/coding-style.md` — создан

**Статус:** ✅ Завершено.

## 2026-05-17 23:19 — Дополнение проекта инструкциями для ИИ (ДЗ)

**Описание:** Создан набор AI-инструкций для проекта Betaflight в соответствии с задачей `task2.md`. Добавлены файлы контекста, правил взаимодействия, типовых задач и чеклиста завершения.

**Затронутые файлы:**
- `.clinerules/project-guide.md` — создан
- `docs/ai/TASKS.md` — создан
- `docs/ai/DEFINITION_OF_DONE.md` — создан
- `docs/ai/PLAN.md` — создан

**Статус:** ✅ Завершено.

## 2026-05-17 23:32 — Debounce для DISARM через переключатель (Задача №2)

**Описание:** Реализован программный антидребезг для DISARM через переключатель в `src/main/fc/rc_controls.c`. Заменён tick-based счётчик `rcDisarmTicks` (3 тика ≈ 12 мс для CRSF) на time-based debounce (50 мс через `millis()` + `cmpTimeMs()`). Добавлена константа `ARM_DEBOUNCE_MS 50`. Добавлен `#include "drivers/time.h"`.

**Затронутые файлы:**
- `src/main/fc/rc_controls.c` — изменён
- `docs/ai/task2-debounce-plan.md` — создан
- `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`, `memory-bank/activeContext.md` — обновлены

**Статус:** ✅ Код написан, документация обновлена. Ожидается проверка компиляции после установки ARM toolchain.

## 2026-05-18 00:40 — Рефакторинг blackbox (выделение инициализации) (Задача №3)

**Описание:** Выполнен рефакторинг модуля blackbox: функции инициализации, валидации конфигурации, управления состоянием (`blackboxFinish`) и сброса таймеров итераций выделены в отдельные файлы `blackbox_init.c` / `blackbox_init.h`. Исходный файл `blackbox.c` сокращён на ~60 строк. Добавлен `blackbox_init.c` в `COMMON_SRC` в `mk/source.mk`.

Перемещённые функции:
- `blackboxInit()` — основная инициализация
- `blackboxValidateConfig()` — валидация конфигурации
- `blackboxResetIterationTimers()` — сброс таймеров
- `blackboxStart()` — запуск логирования
- `blackboxFinish()` — завершение логирования
- `blackboxSetState()` — управление состояниями
- `blackboxMayEditConfig()` — проверка возможности редактирования
- `startInTestMode()` / `stopInTestMode()` / `inMotorTestMode()` — тестовый режим

Переменные, изменённые с `static` на `extern`: `blackboxState`, `blackboxPInterval`, `blackboxIInterval`, `blackboxHighResolutionScale`, `blackboxLoggedAnyFrames`, `startedLoggingInTestMode`, `blackboxIteration`, `blackboxLoopIndex`, `blackboxPFrameIndex`, `blackboxIFrameIndex`.

**Затронутые файлы:**
- `src/main/blackbox/blackbox_init.h` — создан
- `src/main/blackbox/blackbox_init.c` — создан
- `src/main/blackbox/blackbox.c` — изменён
- `mk/source.mk` — изменён
- `docs/ai/task3-blackbox-refactor-plan.md` — создан
- `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`, `memory-bank/activeContext.md` — обновлены

**Статус:** ✅ Код написан, сборка для STM32F405 прошла успешно, документация обновлена.

## 2026-05-18 01:15 — Unit-тесты для модуля RX (Задача №4)

**Описание:** Написаны unit-тесты для функций обработки RC каналов из `src/main/rx/rx.c`. Покрыты функции: `isPulseValid()` (4 теста), `applyRxChannelRangeConfiguraton()` (4 теста), `updateLinkQualitySamples()` (4 теста), `resetAllRxChannelRangeConfigurations()` (1 тест). Все 13 тестов собраны и проходят (gcc, без clang). Ранее закомментированные тесты удалены.

**Затронутые файлы:**
- `src/test/unit/rx_rx_unittest.cc` — изменён (добавлены тесты, stubs, удалён #if 0 блок)
- `docs/ai/task4-unit-tests-plan.md` — создан
- `CHANGES.md`, `PROMPTS.md`, `docs/ai/PLAN.md`, `memory-bank/activeContext.md` — обновлены

**Статус:** ✅ Тесты написаны, собраны, проходят (13/13 PASS). Makefile не требует изменений — используется существующая конфигурация `rx_rx_unittest_SRC`.

## Learnings and Project Insights
- The project supports an extensive range of MCU families beyond just STM32
- Build system is Make-based with Python helper scripts
- Target configurations are managed via a git submodule
- The project has a well-defined release cadence with Alpha/Beta/RC phases
- Community contributions are managed through Discord and GitHub
- STM32C5 requires specific SYSCLK configuration (HSE via PSI with HSI fallback)
- OctoSPI multichip support enables larger flash configurations on supported MCUs
- Autopilot feature is being developed incrementally (flight plan guidance as step one)
- RC signal processing code has significant quality issues: 30+ magic numbers in rc_adjustments.c, race conditions in ARM/DISARM logic, potential infinite loop in failsafe state machine
- AI agent infrastructure is now in place: `.clinerules/` directory with coding-style, project-guide, default-rules, update_prompts
- Blackbox module has been refactored: initialization logic extracted to `blackbox_init.c/h` for cleaner separation
- Unit test infrastructure (Google Test) works for RX module — 13 tests pass covering 4 functions