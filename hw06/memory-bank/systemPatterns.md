# System Architecture

## High-Level Architecture

Betaflight firmware follows a layered architecture typical of embedded real-time systems:

```
┌─────────────────────────────────────────────────────┐
│                    Application Layer                │
│  FC (Flight Control)  │  CLI  │  CMS  │  MSP  │ OSD │
├─────────────────────────────────────────────────────┤
│                    Feature Layer                    │
│  Flight  │  RX  │  Telemetry  │  Blackbox  │  GPS   │
│  Sensors │  IO  │  LED Strip  │  VTX       │  etc.  │
├─────────────────────────────────────────────────────┤
│                   Hardware Abstraction Layer (HAL)  │
│  Drivers: ADC, SPI, I2C, UART, DMA, Timer, PWM, etc.│
├─────────────────────────────────────────────────────┤
│                    MCU Abstraction Layer            │
│  STM32 F4/G4/F7/H7 │ AT32 │ GD32 │ APM32 │ ESP32 │  │
└─────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Parameter Group (PG) System
- Persistent configuration storage system
- Uses `PG_DECLARE` / `PG_REGISTER` macros for defining configurable parameters
- Supports reset-to-defaults and save/load from flash/EEPROM
- Located in `src/main/pg/`

### 2. Task Scheduler
- Cooperative round-robin scheduler for real-time tasks
- Tasks defined in `src/main/fc/tasks.c`
- Each task has a desired frequency and priority
- Main loop in `src/main/fc/core.c` drives the scheduler

### 3. Driver Abstraction
- Hardware drivers in `src/main/drivers/` provide platform-independent interfaces
- Platform-specific implementations in `src/platform/` (e.g., STM32, AT32)
- MCU-agnostic interfaces (e.g., `bus_spi.h`, `serial.h`, `motor.h`)

### 4. Target System
- Board-specific configurations in `src/main/target/`
- Each target defines pin mappings, peripheral configurations, and feature enable/disable
- Build system selects target via `TARGET=<name>` make parameter

### 5. MSP Protocol
- Multwii Serial Protocol for communication with configurator/Betaflight App
- Message-based protocol over serial/UART
- Handlers in `src/main/msp/`

### 6. CMS (On-Screen Menu)
- OSD-based configuration menu system
- Allows field configuration without a computer
- Located in `src/main/cms/`

## Component Relationships

### Flight Control Loop
```
Sensors (Gyro/Accel) → PID Controller → Mixer → Motor Output
       ↑                                        │
       └────────── Filtering ←──────────────────┘
```

### Data Flow
```
RX Input → RC Controls → Flight Modes → PID Controller → Mixer → Motors
                │                                              │
                ↓                                              ↓
          Adjustments                                    Servo/Motor Output

Autopilot (Flight Plan Guidance) → Waypoint Navigation → RC Override → Mixer
```

### Configuration Flow
```
Betaflight App (PWA) ←→ MSP Protocol ←→ FC Firmware ←→ PG Storage
       │                                              │
       ↓                                              ↓
    CLI Interface                              Flash/EEPROM
```

## Supplementary Documentation
- **Architecture Overview**: `docs/architecture-overview.md` — full architecture breakdown, directory structure, entrypoints, module table, recommended reading order
- **RC Signal Flow**: `docs/rc_signals_flow.md` — detailed 8-step execution flow from RC receiver to motors, with branching points, flight mode influence, ARM/DISARM logic
- **Unresolved Issues Report**: `docs/unresolved-issues-report.md` — 125 issues across 5 categories (incomplete features, workarounds, pending decisions, refactoring needs, missing documentation)
- **RC Signals Analysis**: `docs/rc_signals_analysis.md` — 29 problems in RC signal processing pipeline (logical errors, security vulnerabilities, best practices violations, antipatterns) with recommendations

## Critical Implementation Paths

1. **Initialization**: `src/main/fc/init.c` - System boot sequence, hardware init, PG loading
2. **Main Loop**: `src/main/fc/core.c` - Scheduler execution, task dispatch
3. **PID Control**: `src/main/flight/` - Rate and attitude PID controllers
4. **Motor Mixing**: `src/main/flight/mixer.c` - Motor output calculation
5. **RC Processing**: `src/main/fc/rc_controls.c` - RC input interpretation
6. **Sensor Reading**: `src/main/sensors/` - Gyro, accel, baro, mag, GPS
7. **Autopilot Guidance**: `src/main/flight/` - Flight plan waypoint navigation
