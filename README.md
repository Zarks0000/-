# 摩旅工具

摩旅工具是一款面向摩托车旅行用户的微信小程序，提供行程规划、分日路书、出行待办、车辆装备管理、个人模板、天气查询、禁摩查询、预算估算、装备计算和反馈提交等功能，帮助用户在出发前完成路线规划、风险排查与出行准备。

## 当前版本

开发版 `1.0.0`

## 主要功能

- 微信授权登录，未登录不可使用核心内容
- 创建、查看、编辑、删除摩旅行程
- 分日路书、手动待办、出行提醒管理
- 车辆、装备、个人模板登记与同步
- 天气查询、禁摩查询、预算估算、装备计算
- 帮助与反馈，反馈内容通过 SMTP 邮件发送
- 后端支持微信云托管部署
- 数据库使用 Supabase PostgreSQL

## 技术栈

- 前端：UniApp、Vue 3、TypeScript、Tailwind CSS
- 小程序端：微信小程序
- 后端：Flask、Gunicorn
- 数据库：Supabase PostgreSQL
- 部署：微信云托管、Docker

## 目录结构

```text
.
├── api/                         # Flask 后端
├── src/                         # UniApp 小程序源码
├── scripts/sync-mp-config.mjs   # 同步微信开发者工具配置
├── supabase/migrations/         # Supabase 初始化 SQL
├── Dockerfile                   # 云托管构建入口
├── container.config.json        # 云托管容器配置
└── package.json
```

## 本地开发

安装前端依赖：

```bash
npm install
```

启动微信小程序开发构建：

```bash
npm run dev:mp-weixin
```

构建微信小程序产物：

```bash
npm run build:mp-weixin
```

构建后使用微信开发者工具导入项目根目录，项目配置会指向：

```text
dist/build/mp-weixin
```

后端本地运行：

```bash
cd api
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python main.py
```

## 环境变量

后端环境变量参考：

```text
api/.env.example
```

核心变量：

```text
SUPABASE_DATABASE_URL=postgresql://postgres.xxx:password@xxx.pooler.supabase.com:5432/postgres?sslmode=require
WECHAT_APPID=微信小程序 AppID
WECHAT_APP_SECRET=微信小程序 AppSecret
AMAP_WEB_API_KEY=高德 Web 服务 Key
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=发信邮箱
SMTP_PASSWORD=邮箱 SMTP 授权码
SMTP_FROM=发信邮箱
```

小程序前端本地环境变量参考：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_WX_CLOUD_ENV_ID=微信云托管环境 ID
VITE_WX_CLOUD_CONTAINER_SERVICE=微信云托管服务名
```

## Supabase 初始化

在 Supabase 项目后台打开 `SQL Editor`，执行：

```text
supabase/migrations/00006_current_schema.sql
```

执行后应生成这些表：

```text
users
user_sessions
routes
alerts
user_vehicles
user_equipments
user_templates
```

推荐使用 Supabase `Session pooler` 连接串，并确保包含：

```text
sslmode=require
```

## 微信云托管部署

1. 将代码推送到 GitHub。
2. 在微信云托管中绑定仓库。
3. 服务 Dockerfile 路径选择根目录：

```text
Dockerfile
```

4. 容器端口使用：

```text
80
```

5. 配置后端环境变量。
6. 发布服务后，在微信开发者工具中重新编译小程序。

## 常用命令

```bash
npm run check
npm run build:mp-weixin
```

后端冒烟检查可在 `api` 目录执行：

```bash
venv\Scripts\python -c "from main import create_app; app=create_app(); print(len(list(app.url_map.iter_rules())))"
```

## 注意事项

- 不要将 `.env`、数据库密码、微信密钥、SMTP 授权码提交到仓库。
- 创建行程依赖高德路线查询；查询失败时不会创建兜底假行程。
- 新建行程不会同步等待大模型生成提醒，避免云托管请求超时。
- 天气、禁摩、新闻和建议类信息会在创建后后台加载。
