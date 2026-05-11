# Technical Context

## Technologies Used

### Programming Languages
- **C** (primary): Firmware implementation
- **Python**: Build scripts, code generation utilities
- **Make**: Build system (GNU Make)

### Target MCU Families
- **STM32**: F4, G4, F7, H7, C5, H5, N6 (ARM Cortex-M)
- **AT32**: AT32F43x (Artery Technology)
- **GD32**: GD32F4, GD32H7 (GigaDevice)
- **APM32**: APM32F4 (Geehy)
- **ESP32**: Espressif Systems
- **PICO**: Raspberry Pi RP2040
- **SIMULATOR**: For testing/development

### Toolchains
- **ARM GCC**: Primary compiler for ARM targets (`arm-none-eabi-gcc`)
- **Make**: Build orchestration
- **Docker/Devcontainers**: Consistent build environment

### Libraries (in `lib/main/`)
- **CMSIS**: ARM Cortex Microcontroller Software Interface Standard
- **STM32 HAL/LL**: Hardware abstraction for STM32
- **AT32 Drivers**: Hardware abstraction for AT32
- **GD32 Drivers**: Hardware abstraction for GD32
- **APM32 Drivers**: Hardware abstraction for APM32
- **ESP-IDF**: ESP32 development framework
- **Pico-SDK**: Raspberry Pi Pico SDK
- **MAVLink**: Micro Air Vehicle Link protocol
- **DroneCAN**: Drone CAN bus protocol
- **Dyad**: Async networking library
- **Bosch Sensortec**: BMI270 sensor API
- **Google OLC**: Open Location Code

## Development Setup

### Build System
```bash
make TARGET=<target_name>          # Build firmware for a specific target
make TARGET=<target_name> flash    # Build and flash firmware
make TARGET=<target_name> clean    # Clean build artifacts
make help                          # List all available targets
```

### Build Options
- `TARGET`: Target board configuration (e.g., `SPEEDYBEEF405WING`)
- `CONFIG`: Configuration variant
- `OPTIONS`: Compile-time feature flags
- `DEBUG`: Debug level (empty=release, INFO, GDB)
- `EXST`: External Storage Bootloader support
- `SERIAL_DEVICE`: Serial port for flashing

### Docker Build
```bash
docker build -t betaflight-dev -f .devcontainer/containerfile .devcontainer/
docker run --rm -v "${PWD}:/workspace" -w /workspace betaflight-dev make TARGET=SPEEDYBEEF405WING
```

## Technical Constraints

### Real-Time Requirements
- Main PID loop runs at 1-8 kHz depending on target
- Sensor reading, filtering, and control must complete within loop period
- Task scheduler must prioritize critical flight tasks

### Memory Constraints
- Flash: 64KB-2MB depending on MCU
- RAM: 16KB-1MB depending on MCU
- Blackbox logging requires additional storage (flash or SD card)

### Hardware Interfaces
- **SPI**: Gyro, accel, baro, flash, SD card, OSD (MAX7456)
- **I2C**: Compass, baro (some targets)
- **UART**: Serial RX, telemetry, GPS, MSP, VTX
- **ADC**: Battery voltage/current, RSSI
- **PWM/DShot**: Motor outputs
- **USB**: VCP for MSP/CLI, MSC for Blackbox

## Dependencies

### Build Dependencies
- `arm-none-eabi-gcc` (GCC ARM Embedded)
- `make`
- `python3` (for build scripts)
- `docker` (optional, for devcontainer)

### Runtime Dependencies
- None (standalone firmware)

## Tool Usage Patterns

### Configuration
- **CLI**: Text-based configuration via serial terminal
- **CMS**: On-screen display menu (field configuration)
- **Betaflight App**: PWA for full configuration via MSP

### Debugging
- **Blackbox**: Flight data logging for post-flight analysis
- **LED signals**: Status indication via onboard LEDs
- **Serial console**: CLI for debugging and configuration
- **GDB**: Debug builds for development

### Testing
- Unit tests in `src/test/` using Google Test
- Hardware-in-the-loop testing
- Community flight testing