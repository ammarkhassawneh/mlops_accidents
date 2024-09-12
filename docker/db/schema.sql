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
    user_id INTEGER NOT NULL,                         -- L'ID de l'utilisateur qui a fait la prédiction
    predicted_severity REAL NOT NULL CHECK(predicted_severity >= 0 AND predicted_severity <= 1),  -- La gravité de l'accident prédite
    lat REAL NOT NULL CHECK(lat >= -90 AND lat <= 90),  -- Latitude valide
    long REAL NOT NULL CHECK(long >= -180 AND long <= 180),  -- Longitude valide
    place INTEGER NOT NULL,                           -- Lieu de l'accident
    catu INTEGER NOT NULL,                            -- Catégorie d'usager impliqué
    sexe INTEGER NOT NULL,                            -- Sexe de l'usager impliqué
    secu1 REAL NOT NULL,                              -- Moyens de sécurité utilisés
    year_acc INTEGER NOT NULL,                        -- Année de l'accident
    victim_age INTEGER NOT NULL,                      -- Âge de la victime
    catv INTEGER NOT NULL,                            -- Catégorie de véhicule
    obsm INTEGER NOT NULL,                            -- État d'observation du conducteur
    motor INTEGER NOT NULL,                           -- Type de véhicule à moteur
    catr INTEGER NOT NULL,                            -- Catégorie de la route
    circ INTEGER NOT NULL,                            -- Circulation routière
    surf INTEGER NOT NULL,                            -- État de la surface de la route
    situ INTEGER NOT NULL,                            -- Situation de l'accident
    vma INTEGER NOT NULL,                             -- Vitesse maximale autorisée
    jour INTEGER NOT NULL,                            -- Jour de l'accident
    mois INTEGER NOT NULL,                            -- Mois de l'accident
    lum INTEGER NOT NULL,                             -- Conditions d'éclairage
    dep INTEGER NOT NULL,                             -- Département où a eu lieu l'accident
    com INTEGER NOT NULL,                             -- Commune où a eu lieu l'accident
    agg_ INTEGER NOT NULL,                            -- Agglomération
    intt INTEGER NOT NULL,                             -- Type d'intersection
    atm INTEGER NOT NULL,                             -- Conditions météorologiques
    col INTEGER NOT NULL,                             -- Type de collision
    hour INTEGER NOT NULL,                            -- Heure de l'accident
    nb_victim INTEGER NOT NULL,                       -- Nombre de victimes
    nb_vehicules INTEGER NOT NULL,                    -- Nombre de véhicules impliqués
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc')),  -- Timestamp de la prédiction en UTC
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE  -- Suppression en cascade des prédictions si l'utilisateur est supprimé
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
