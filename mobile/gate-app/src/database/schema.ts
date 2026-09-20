export const CREATE_TABLES = `
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY NOT NULL,
    ticket_code TEXT NOT NULL UNIQUE,
    event_id TEXT NOT NULL,
    status TEXT NOT NULL,
    valid_from TEXT,
    valid_until TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS credentials (
    id TEXT PRIMARY KEY NOT NULL,
    credential_code TEXT NOT NULL UNIQUE,
    athlete_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_events (
    id TEXT PRIMARY KEY NOT NULL,
    ticket_id TEXT,
    credential_id TEXT,
    gate_id TEXT NOT NULL,
    validated_at TEXT NOT NULL,
    result TEXT NOT NULL,
    synced INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (credential_id) REFERENCES credentials(id)
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS device_state (
    id TEXT PRIMARY KEY NOT NULL,
    device_id TEXT NOT NULL,
    last_sync_at TEXT,
    updated_at TEXT NOT NULL
);
`;