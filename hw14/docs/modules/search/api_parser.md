# `api_parser.py` — Парсинг C-деклараций

## Назначение

Парсинг деклараций C-функций (BCM API) и Doxygen-комментариев. Используется индексатором SDK для извлечения сигнатур функций, параметров и документации.

## Классы

### `FunctionDecl`

```python
@dataclass
class FunctionDecl:
    return_type: str        # Возвращаемый тип (int, uint32, void)
    name: str               # Имя функции (bcm_vlan_create)
    signature: str          # Полная сигнатура
    parameters: list[dict]  # [{name, type, description}]
```

### `DocComment`

```python
@dataclass
class DocComment:
    brief: str              # @brief описание
    params: dict[str, str]  # @param name -> description
    returns: str            # @return описание
```

## Функции

### `parse_function_declaration()`

```python
def parse_function_declaration(text: str) -> FunctionDecl | None
```

Парсинг строки декларации C-функции.

**Паттерн:** `^(return_type) (bcm_\w+)\(params\);`

**Пример:** `int bcm_vlan_create(int unit, bcm_vlan_t vlan);`

### `extract_doxygen_comment()`

```python
def extract_doxygen_comment(lines: list[str], func_line: int) -> DocComment | None
```

Извлечение Doxygen-комментария перед функцией. Ищет многострочный комментарий (`/** ... */`) непосредственно перед строкой функции.

**Парсит:**
- `@brief` — краткое описание
- `@param [in] name desc` — описание параметров
- `@return` — описание возвращаемого значения

### `extract_module()`

```python
def extract_module(name: str) -> str
```

Определение модуля по префиксу функции.

**Примеры:**
- `bcm_vlan_create` → `VLAN`
- `bcm_l2_addr_add` → `L2`
- `bcm_l3_route_add` → `L3`

### `extract_function_name()`

```python
def extract_function_name(text: str) -> str | None
```

Извлечение имени функции из строки декларации.

## Регулярные выражения

| Паттерн | Назначение |
|---------|-----------|
| `FUNC_PATTERN` | Декларация BCM функции: `return_type bcm_name(params);` |
| `PARAM_PATTERN` | Отдельный параметр: `type name /*< desc */` |
| `BRIEF_PATTERN` | Doxygen `@brief` |
| `PARAM_DESC_PATTERN` | Doxygen `@param` |
| `RETURN_PATTERN` | Doxygen `@return` |
| `MODULE_PATTERN` | Префикс модуля: `bcm_<module>_*` |