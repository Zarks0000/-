CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
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
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    route_name VARCHAR(255),
    origin_name VARCHAR(255),
    origin_lat DECIMAL(10, 6),
    origin_lng DECIMAL(10, 6),
    dest_name VARCHAR(255),
    dest_lat DECIMAL(10, 6),
    dest_lng DECIMAL(10, 6),
    waypoints JSONB, -- 存储途经点数组
    total_distance INTEGER, -- 单位：米
    total_duration INTEGER, -- 单位：秒
    travel_mode VARCHAR(50) DEFAULT 'motorcycle',
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_routes_user_id ON routes(user_id);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50), -- weather/policy/news
    severity VARCHAR(20),   -- low/medium/high
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