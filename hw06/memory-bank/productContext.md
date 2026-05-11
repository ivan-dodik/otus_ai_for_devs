# Product Context

## Why This Project Exists
Betaflight exists to provide high-performance, open-source flight controller firmware for the FPV (First Person View) drone community and fixed-wing aircraft enthusiasts. It evolved from the Baseflight/Cleanflight lineage to focus specifically on flight performance and rapid feature innovation.

## Problems It Solves
- **Flight Performance**: Provides optimized PID control loops, filtering, and motor mixing for stable and responsive flight
- **Hardware Flexibility**: Supports a wide range of MCU targets (STM32 F4, G4, F7, H7, AT32, GD32, APM32, etc.), allowing users to choose hardware that fits their needs
- **Configuration Complexity**: Offers extensive configurability via CLI, CMS (on-screen menu), and the Betaflight App (PWA)
- **Feature Integration**: Combines OSD, Blackbox logging, telemetry, GPS, LED strip control, VTX control, and more into a single firmware
- **Community Standard**: Serves as the de-facto standard firmware for the FPV drone community

## How It Should Work
- **Reliability**: Must maintain stable flight characteristics across diverse hardware and flight conditions
- **Performance**: Real-time control loops with minimal latency (motor protocols like DShot, Multishot, Oneshot)
- **Configurability**: Users should be able to tune PIDs, rates, filters, and features to their preference
- **Safety**: Includes failsafe detection, RSSI monitoring, GPS rescue, and other safety features
- **Diagnostics**: Blackbox logging for post-flight analysis, OSD for real-time telemetry display

## User Experience Goals
- **Pilots**: Smooth, responsive flight with minimal tuning required out of the box
- **Developers**: Well-structured codebase with clear contribution guidelines and build system
- **Manufacturers**: Easy target configuration and hardware support
- **Translators**: Accessible localization system for the configurator app