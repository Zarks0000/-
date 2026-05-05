CREATE TABLE IF NOT EXISTS user_vehicles (
    user_id VARCHAR(100) NOT NULL REFERENCES users(openid) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    displacement VARCHAR(50) DEFAULT '',
    plate_no VARCHAR(50) DEFAULT '',
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_vehicles_user_id ON user_vehicles(user_id);

CREATE TABLE IF NOT EXISTS user_equipments (
    user_id VARCHAR(100) NOT NULL REFERENCES users(openid) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT '',
    weight_kg DECIMAL(10, 2),
    note TEXT DEFAULT '',
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_equipments_user_id ON user_equipments(user_id);

CREATE TABLE IF NOT EXISTS user_templates (
    user_id VARCHAR(100) NOT NULL REFERENCES users(openid) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    days INTEGER DEFAULT 1,
    schedule JSONB DEFAULT '[]'::jsonb,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_templates_user_id ON user_templates(user_id);
