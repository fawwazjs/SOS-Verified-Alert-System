-- ==================================================================
-- schema.sql - Skema database Supabase PostgreSQL
-- SOS Verified Alert System
--
-- CATATAN:
-- * Semua angka RSA (pub_e, pub_n, signature) disimpan sebagai TEXT
--   agar tidak ada kehilangan presisi saat dibaca oleh JavaScript.
-- * ciphertext berupa JSONB: daftar blok sebagai array of string.
-- * PRIVATE KEY TIDAK PERNAH disimpan di database.
-- ==================================================================

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    role        TEXT        NOT NULL CHECK (role IN ('sender', 'center')),
    pub_e       TEXT        NOT NULL,           -- eksponen publik (string)
    pub_n       TEXT        NOT NULL,           -- modulus publik (string)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sos_messages (
    id                  BIGSERIAL PRIMARY KEY,
    sender_id           BIGINT  NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    center_id           BIGINT  NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    ciphertext          JSONB   NOT NULL,        -- blok cipher saat ini (bisa sudah ditamper)
    original_ciphertext JSONB   NOT NULL,        -- blok cipher asli (untuk fitur Reset)
    signature           TEXT    NOT NULL,        -- signature RSA (string)
    status              TEXT    NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'valid', 'invalid')),
    tampered            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sos_messages_center
    ON sos_messages (center_id, created_at DESC);
