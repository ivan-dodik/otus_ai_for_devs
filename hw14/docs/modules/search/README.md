# Модуль поиска (`src/search/`)

## Назначение

Модуль поиска предоставляет утилиты для текстового поиска по SDK и парсинга различных типов файлов. Используется инструментами для поиска API, примеров, CINT скриптов и трассировки.

## Файлы модуля

| Файл | Назначение |
|------|-----------|
| `__init__.py` | Пакетный инициализатор |
| `rg_search.py` | Обёртка над ripgrep (subprocess) |
| `api_parser.py` | Парсинг C-деклараций функций и Doxygen-комментариев |
| `macro_parser.py` | Парсинг #define, #ifdef, chip guards |
| `cint_parser.py` | Парсинг заголовков CINT скриптов |

## Диаграмма зависимостей

```mermaid
graph TD
    subgraph Search["src/search/"]
        RG["rg_search.py"]
        AP["api_parser.py"]
        MP["macro_parser.py"]
        CP["cint_parser.py"]
    end

    subgraph Consumers["Потребители"]
        IDX["indexer/sdk_indexer.py"]
        T_EX["tools/find_api_examples.py"]
        T_TR["tools/trace_implementation.py"]
        T_CI["tools/get_chip_info.py"]
        T_CI2["tools/find_cint_scripts.py"]
    end

    subgraph External["Внешние"]
        RG_CMD["ripgrep (rg)"]
    end

    RG --> RG_CMD
    AP --> RG
    MP --> RG
    CP --> RG
    IDX --> AP
    IDX --> MP
    IDX --> RG
    T_EX --> CP
    T_EX --> RG
    T_TR --> MP
    T_TR --> RG
    T_CI --> CP
    T_CI --> RG
    T_CI2 --> CP
    T_CI2 --> RG
```

## Поток данных

```mermaid
flowchart LR
    QUERY["Поисковый запрос"] --> RG["rg_search()"]
    RG --> JSON["JSON-вывод rg"]
    JSON --> PARSE["_parse_rg_json_output()"]
    PARSE --> MATCHES["RgMatch[]"]

    MATCHES --> AP["api_parser.py<br/>→ FunctionDecl"]
    MATCHES --> MP["macro_parser.py<br/>→ MacroDef / chip guards"]
    MATCHES --> CP["cint_parser.py<br/>→ header / APIs"]