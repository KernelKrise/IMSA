CREATE TABLE IF NOT EXISTS agents (
    id_             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    key             UUID NOT NULL UNIQUE,
    name            VARCHAR(256) NOT NULL,
    description     VARCHAR(1024),
    status          VARCHAR(64) NOT NULL,
    last_seen       TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id_             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR(256) NOT NULL,
    description     VARCHAR(1024),
    role            VARCHAR(64) NOT NULL,
    platform        VARCHAR(64) NOT NULL,
    platform_id     VARCHAR(256) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    UNIQUE (platform, platform_id)
);

CREATE TABLE IF NOT EXISTS user_agents (
    user_id  BIGINT   NOT NULL REFERENCES users(id_) ON DELETE CASCADE,
    agent_id BIGINT   NOT NULL REFERENCES agents(id_) ON DELETE CASCADE,
    PRIMARY KEY (user_id, agent_id)
);

CREATE TABLE IF NOT EXISTS stats (
    id_         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    BIGINT NOT NULL REFERENCES agents(id_) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL,
    status      VARCHAR(64) NOT NULL
);
