CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    read_rights TEXT NOT NULL,
    write_rights TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    severity REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    endpoint TEXT,
    input_data TEXT,
    output_data TEXT,
    timestamp TEXT,
    processing_time REAL
);

CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY,
    test_name TEXT NOT NULL,
    result BOOLEAN NOT NULL,
    timestamp TEXT NOT NULL
);