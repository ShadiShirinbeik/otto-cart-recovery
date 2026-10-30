CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE raw.events (
    session  INTEGER,
    aid      INTEGER,
    ts       BIGINT,
    type     TEXT
);