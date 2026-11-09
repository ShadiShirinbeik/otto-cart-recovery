CREATE SCHEMA IF NOT EXISTS otto;

CREATE TABLE otto.raw_events (
    session  INTEGER,
    aid      INTEGER,
    ts       BIGINT,
    type     TEXT
);
