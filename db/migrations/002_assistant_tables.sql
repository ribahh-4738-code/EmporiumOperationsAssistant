-- Assistant conversational tables (persona, prompts, message audit).
BEGIN;

CREATE TABLE IF NOT EXISTS assistant_profile (
    id            SERIAL PRIMARY KEY,
    profile_name  VARCHAR(64) NOT NULL UNIQUE,
    display_name  VARCHAR(128) NOT NULL,
    timezone      VARCHAR(64) NOT NULL DEFAULT 'America/Campo_Grande',
    system_prompt TEXT NOT NULL,
    enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE assistant_profile IS 'Assistant persona configuration (e.g. Maiara)';

CREATE TABLE IF NOT EXISTS assistant_prompt (
    id          SERIAL PRIMARY KEY,
    profile_id  INTEGER NOT NULL REFERENCES assistant_profile (id) ON DELETE CASCADE,
    module_key  VARCHAR(64) NOT NULL,
    prompt      TEXT NOT NULL,
    enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (profile_id, module_key)
);

CREATE INDEX IF NOT EXISTS idx_assistant_prompt_profile_id ON assistant_prompt (profile_id);

COMMENT ON TABLE assistant_prompt IS 'Optional prompts keyed by module (e.g. reformulate_request)';

CREATE TABLE IF NOT EXISTS assistant_chat_message (
    id            BIGSERIAL PRIMARY KEY,
    profile_id    INTEGER NOT NULL REFERENCES assistant_profile (id) ON DELETE CASCADE,
    role          VARCHAR(32) NOT NULL,
    message_text  TEXT NOT NULL,
    model         VARCHAR(128),
    channel       VARCHAR(32),
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assistant_chat_message_profile_id ON assistant_chat_message (profile_id);
CREATE INDEX IF NOT EXISTS idx_assistant_chat_message_created_at ON assistant_chat_message (created_at);

COMMENT ON TABLE assistant_chat_message IS 'Persisted chat turns for audit and future semantic retrieval';

COMMIT;
