-- SQLite схема для индексации SDK

CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    signature TEXT,
    return_type TEXT,
    file_path TEXT NOT NULL,
    line INTEGER NOT NULL,
    line_end INTEGER,
    module TEXT,
    description TEXT,
    doc_comment TEXT,
    chip_macros TEXT,  -- JSON: ["BCM_TOMAHAWK4_SUPPORT", ...]
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, file_path)
);

CREATE TABLE IF NOT EXISTS function_params (
    function_id INTEGER NOT NULL,
    param_index INTEGER NOT NULL,
    name TEXT,
    param_type TEXT,
    description TEXT,
    FOREIGN KEY(function_id) REFERENCES functions(id)
);

CREATE TABLE IF NOT EXISTS macros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    definition_file TEXT,
    definition_line INTEGER,
    definition_value TEXT,
    chip_association TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS api_macros (
    api_name TEXT NOT NULL,
    macro_name TEXT NOT NULL,
    PRIMARY KEY(api_name, macro_name)
);

CREATE INDEX IF NOT EXISTS idx_functions_name ON functions(name);
CREATE INDEX IF NOT EXISTS idx_functions_module ON functions(module);
CREATE INDEX IF NOT EXISTS idx_macros_name ON macros(name);