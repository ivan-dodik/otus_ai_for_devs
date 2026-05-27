# Контракты инструментов (Tool Outputs Contract)

Все инструменты возвращают результат в едином формате:

```json
{
  "ok": true/false,
  "result": { ... },
  "error": "сообщение об ошибке (если ok=false)",
  "meta": {
    "elapsed_ms": 45,
    "source": "sqlite|ripgrep|config|internal"
  }
}
```

---

## TOOL 1: `ping`

**Описание:** Health-check сервера.

**Параметры:** нет

**Результат:**
```json
{
  "status": "ok",
  "sdk_configured": true,
  "indexed": false,
  "version": "0.1.0"
}
```

---

## TOOL 2: `get_sdk_info`

**Описание:** Информация о SDK.

**Параметры:**
- `include_modules` (bool, default false) — показать список модулей

**Результат:**
```json
{
  "sdk_path": "/path/to/sdk",
  "version": "6.5.27",
  "indexed": true,
  "modules_count": 15,
  "apis_count": 1847,
  "cache_dir": "./cache",
  "modules": [
    {"name": "L2", "api_count": 120, "header_file": "include/bcm/l2.h"}
  ]
}
```

---

## TOOL 3: `find_bcm_api`

**Описание:** Поиск декларации BCM API.

**Параметры:**
- `api` (string, required) — имя API
- `chip` (string, default "all") — фильтр по чипу
- `fuzzy` (bool, default false) — нечёткий поиск

**Результат:**
```json
{
  "name": "bcm_vlan_create",
  "signature": "int bcm_vlan_create(int unit, bcm_vlan_t vlan)",
  "module": "VLAN",
  "header": "include/bcm/vlan.h",
  "line": 156,
  "description": "Create a new VLAN",
  "parameters": [
    {"name": "unit", "type": "int", "description": "Device unit number"}
  ],
  "returns": {"type": "int", "description": "BCM_E_NONE on success"},
  "chip_availability": [],
  "related_apis": []
}
```

---

## TOOL 4: `find_api_examples`

**Описание:** Поиск примеров использования API.

**Параметры:**
- `api` (string, required) — имя API
- `source_type` (string, default "all") — all/c/cint/bcm_config
- `max_results` (int, default 10, max 50)
- `context_lines` (int, default 3, max 10)
- `include_full_source` (bool, default false)

**Результат:**
```json
{
  "api": "bcm_l3_route_add",
  "total_found": 12,
  "examples": [
    {
      "file": "src/examples/l3/route_basic.c",
      "line": 88,
      "snippet": "bcm_l3_route_add(unit, &route)",
      "source_type": "cint",
      "script_header": "/* L3 Route Basic Example */",
      "related_files": [
        {"path": "route_basic.log", "type": "log", "size_bytes": 12450}
      ]
    }
  ]
}
```

---

## TOOL 5: `trace_api_implementation`

**Описание:** Трассировка цепочки реализации.

**Параметры:**
- `api` (string, required) — имя API
- `chip` (string, optional) — фильтр по чипу
- `max_depth` (int, default 3, max 7)

**Результат:**
```json
{
  "api": "bcm_l2_addr_add",
  "entry_point": {
    "level": 1, "function": "bcm_l2_addr_add",
    "file": "include/bcm/l2.h", "line": 89,
    "chip_conditions": [], "guard_pattern": ""
  },
  "implementation_chain": [
    {"level": 1, "function": "bcm_esw_l2_addr_add", "file": "src/bcm/esw/l2.c", "line": 456, "chip_conditions": ["always"]},
    {"level": 2, "function": "_bcm_esw_l2_addr_add_internal", "file": "src/bcm/esw/l2.c", "line": 1234, "chip_conditions": ["always"]},
    {"level": 3, "function": "th4_l2_entry_insert", "file": "src/bcm/esw/tomahawk4/l2.c", "line": 67, "chip_conditions": ["SOC_IS_TOMAHAWK4(unit)"]}
  ],
  "chip_specific_branches": [
    {"condition": "SOC_IS_TOMAHAWK4(unit)", "functions": ["th4_l2_entry_insert"], "soc_file": "src/bcm/esw/tomahawk4/l2.c"}
  ]
}
```

---

## TOOL 6: `get_chip_info`

**Описание:** Информация о ASIC.

**Параметры:**
- `chip` (string, required) — имя чипа
- `include_apis` (bool, default false)
- `include_cint_scripts` (bool, default false)

**Результат:**
```json
{
  "chip": "Tomahawk4",
  "dev_ids": ["BCM56980_A0", "BCM56980_B0"],
  "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "INCLUDE_L3"],
  "modules": ["L2", "L3", "VLAN", "MPLS"],
  "soc_directories": ["src/bcm/esw/tomahawk4/"],
  "api_count_estimate": 1847,
  "example_apis": ["bcm_l2_addr_add", "bcm_vlan_create"],
  "cint_scripts": []
}
```

---

## TOOL 7: `find_cint_scripts`

**Описание:** Поиск CINT скриптов.

**Параметры:**
- `query` (string, required) — поисковый запрос
- `chip` (string, optional) — фильтр по чипу
- `include_logs` (bool, default false)
- `include_configs` (bool, default false)
- `include_full_source` (bool, default false)

**Результат:**
```json
{
  "query": "L3 route",
  "total_found": 3,
  "scripts": [
    {
      "file": "src/examples/l3/route_basic.c",
      "header_comment": "/* L3 Route Basic Example\n * Tested on: Tomahawk4\n */",
      "apis_used": ["bcm_l3_route_add", "bcm_l3_route_get"],
      "related_files": [
        {"path": "route_basic.log", "type": "log", "size_bytes": 12450}
      ]
    }
  ]
}
```

---

## Коды ошибок

| Условие | ok | error |
|---------|----|-------|
| API не найден | false | "API 'name' not found" |
| Чип не найден | false | "Chip 'name' not found. Available: ..." |
| Неизвестный tool | false | "Unknown tool: name" |
| Ошибка безопасности | false | "Path traversal detected: ..." |
| SDK не сконфигурирован | false | "SDK path does not exist" |