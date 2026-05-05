ALTER TABLE users ADD COLUMN IF NOT EXISTS unionid VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS session_key TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

CREATE TABLE IF NOT EXISTS user_sessions (
    token VARCHAR(100) PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    openid VARCHAR(100) NOT NULL,
    unionid VARCHAR(100),
    session_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_openid ON user_sessions(openid);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
