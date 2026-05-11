# Active Context

## Current Work Focus
The project is in active development for the **2026.6 release** (currently in RC phase as of May 2026). Recent commits show ongoing work across multiple areas. Comprehensive analyses have been completed: unresolved issues (125 items), RC signal processing code (29 problems), and a full code review report (29 problems with dependency map and ARM/DISARM analysis).

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

## Next Steps
Based on the release schedule:
1. Complete **2026.6 RC** phase (May 2026) — currently active
2. **2026.6 Release** (June 2026)
3. Begin **2026.12 Alpha** development

## Active Decisions and Considerations

### Architecture Decisions
- **Autopilot integration**: New flight plan guidance system being added (step one merged)
- **MCU expansion**: Ongoing support for new STM32 families (H5, N6, C5)
- **Build system improvements**: Devcontainer support, clang-format integration
- **Flash storage**: OctoSPI multichip support for larger flash configurations

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

### Development Workflow
- Pull request review process with thorough review requirements
- GitHub Actions for CI/CD
- Docker/devcontainer for consistent build environments
- Config submodule for target configurations

## Documentation References
- **Architecture Overview**: `docs/architecture-overview.md` — comprehensive project structure, entrypoints, module descriptions, recommended reading order
- **RC Signal Flow**: `docs/rc_signals_flow.md` — detailed 8-step execution flow from RC receiver to motors
- **Unresolved Issues Report**: `docs/unresolved-issues-report.md` — 125 issues across 5 categories (incomplete features, workarounds, pending decisions, refactoring needs, missing documentation)
- **RC Signals Analysis**: `docs/rc_signals_analysis.md` — 29 problems in RC signal processing pipeline (logical errors, security vulnerabilities, best practices violations, antipatterns) with recommendations
- **Code Review Report**: `docs/review_report.md` — comprehensive code review of RC signal handling and ARM/DISARM logic with dependency maps, code examples, and improvement recommendations (29 problems across 4 categories)
- **Prompt History**: `PROMPTS.md` — chronological log of all agent prompts and results
- **Change History**: `CHANGES.md` — chronological log of all project changes

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