CREATE TABLE IF NOT EXISTS agents (
    guid       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(256) NOT NULL,
    status     VARCHAR(64),
    last_seen  TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    guid        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(256) NOT NULL,
    role        VARCHAR(64) NOT NULL,
    platform    VARCHAR(64) NOT NULL,
    platform_id VARCHAR(256) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (platform, platform_id)
);

CREATE TABLE IF NOT EXISTS user_agents (
    user_guid  UUID NOT NULL REFERENCES users(guid) ON DELETE CASCADE,
    agent_guid UUID NOT NULL REFERENCES agents(guid) ON DELETE CASCADE,
    PRIMARY KEY (user_guid, agent_guid)
);

CREATE TABLE IF NOT EXISTS stats (
    guid        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_guid  UUID NOT NULL REFERENCES agents(guid) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status      VARCHAR(64) NOT NULL
);
