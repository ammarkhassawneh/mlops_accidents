-- Création de la table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,      -- Le nom d'utilisateur doit être unique
    email TEXT NOT NULL UNIQUE,     -- L'email doit être unique
    hashed_password TEXT NOT NULL,  -- Mot de passe haché
    read_rights TEXT NOT NULL,      -- Droits de lecture
    write_rights TEXT NOT NULL,     -- Droits d'écriture
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),  -- Le rôle peut être 'admin' ou 'user'
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))  -- Date de création en UTC
);

-- Création de la table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    severity REAL NOT NULL CHECK(severity >= 0 AND severity <= 1),  -- La gravité doit être entre 0 et 1
    latitude REAL NOT NULL CHECK(latitude >= -90 AND latitude <= 90),  -- Latitude valide
    longitude REAL NOT NULL CHECK(longitude >= -180 AND longitude <= 180),  -- Longitude valide
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc')),  -- Enregistrer le moment de la prédiction en UTC
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE  -- Supprimer les prédictions si l'utilisateur est supprimé
);

-- Création de la table des journaux de requêtes
CREATE TABLE IF NOT EXISTS request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,      -- Adresse IP de la requête
    endpoint TEXT NOT NULL,        -- L'endpoint accédé
    input_data TEXT,               -- Données d'entrée de la requête
    output_data TEXT,              -- Données de sortie de la requête
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc')),  -- Enregistrer le moment de la requête en UTC
    processing_time REAL NOT NULL  -- Temps de traitement en secondes
);

-- Création de la table des journaux d'activités
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity TEXT NOT NULL,  -- Description de l'activité
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc')),  -- Moment de l'activité en UTC
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE  -- Supprimer les logs si l'utilisateur est supprimé
);

-- Création de la table des résultats de tests
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,   -- Nom du test
    result BOOLEAN NOT NULL,   -- Résultat du test
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc'))  -- Moment du résultat en UTC
);
