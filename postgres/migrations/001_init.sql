CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE NOT NULL,
    nickname VARCHAR(100),
    avatar VARCHAR(255),
    phone VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);

CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    route_name VARCHAR(255),
    origin_name VARCHAR(255),
    origin_lat DECIMAL(10, 6),
    origin_lng DECIMAL(10, 6),
    dest_name VARCHAR(255),
    dest_lat DECIMAL(10, 6),
    dest_lng DECIMAL(10, 6),
    waypoints JSONB DEFAULT '{}'::jsonb,
    total_distance INTEGER,
    total_duration INTEGER,
    travel_mode VARCHAR(50) DEFAULT 'motorcycle',
    is_favorite BOOLEAN DEFAULT FALSE,
    start_date DATE,
    end_date DATE,
    estimated_days INTEGER,
    schedule JSONB DEFAULT '[]'::jsonb,
    manual_todos JSONB DEFAULT '[]'::jsonb,
    polyline TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routes_user_id ON routes(user_id);
CREATE INDEX IF NOT EXISTS idx_routes_start_date ON routes(start_date);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(255),
    description TEXT,
    suggestion TEXT,
    location_name VARCHAR(255),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    is_read BOOLEAN DEFAULT FALSE,
    is_handled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_route_id ON alerts(route_id);

CREATE TABLE IF NOT EXISTS user_vehicles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    displacement VARCHAR(50) DEFAULT '',
    plate_no VARCHAR(50) DEFAULT '',
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_vehicles_user_id ON user_vehicles(user_id);

CREATE TABLE IF NOT EXISTS user_equipments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT '',
    weight_kg DECIMAL(10, 2),
    note TEXT DEFAULT '',
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_equipments_user_id ON user_equipments(user_id);

CREATE TABLE IF NOT EXISTS user_templates (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    days INTEGER DEFAULT 1,
    schedule JSONB DEFAULT '[]'::jsonb,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_user_templates_user_id ON user_templates(user_id);
