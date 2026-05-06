<p align="center">
  <img src="./icon/app-icon.png" width="96" alt="摩旅工具图标" />
</p>

<h1 align="center">摩旅工具</h1>

<p align="center">
  给摩托车旅行准备的一站式出行助手：路线、日程、装备、车辆、预算、天气、禁摩信息，全都提前整理好。
</p>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/开发版-1.0.0-16a34a" />
  <img alt="UniApp" src="https://img.shields.io/badge/UniApp-Vue%203-2f80ed" />
  <img alt="Backend" src="https://img.shields.io/badge/Backend-Flask-111827" />
  <img alt="Database" src="https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3fcf8e" />
  <img alt="Deploy" src="https://img.shields.io/badge/Deploy-微信云托管-07c160" />
</p>

## 🏍️ 项目简介

**摩旅工具**是一款面向摩托车旅行用户的微信小程序。它把“想去哪、怎么走、带什么、要注意什么”拆成可执行的准备事项，让一次摩旅从灵感到出发都更有条理。

你可以用它创建摩旅行程、查看分日路书、管理出行待办、登记车辆与装备，也可以查询天气、禁摩、预算和装备清单。后端基于 Flask，数据库使用 Supabase PostgreSQL，并已适配微信云托管部署。

## 📱 页面预览

| 首页 | 行程 | 发现 | 我的 |
| --- | --- | --- | --- |
| <img src="./docs/images/home.svg" width="220" alt="首页预览" /> | <img src="./docs/images/routes.svg" width="220" alt="行程页预览" /> | <img src="./docs/images/explore.svg" width="220" alt="发现页预览" /> | <img src="./docs/images/profile.svg" width="220" alt="我的页预览" /> |
| 当前主行程、准备进度、提醒和建议集中展示。 | 管理筹备中、进行中、已完成的全部行程。 | 放路线模板、知识内容和常用摩旅工具。 | 车辆、装备、模板、隐私、反馈和关于信息入口。 |

## ✨ 核心功能

### 🧭 行程规划

- 创建、查看、编辑、删除摩旅行程。
- 根据起终点生成路线规划，并保存到个人账号。
- 支持分日路书，适合长途摩旅拆分每天安排。
- 行程卡片展示日期、天数、里程和当前状态，方便快速扫一眼。

### ✅ 出发准备

- 自动生成出行提醒与准备建议。
- 支持手动补充待办事项。
- 首页聚合关键提醒，避免临出发才发现证件、装备、车辆检查遗漏。
- 新建行程不会等待后台建议全部生成，减少云端请求超时。

### 🧰 工具箱

- 天气查询：查看目的地或沿途城市天气情况。
- 禁摩查询：辅助判断城市骑行限制。
- 预算估算：粗算油费、住宿、餐饮等出行成本。
- 装备计算：根据出行场景整理装备清单。

### 🧍 个人档案

- 微信授权登录后才能使用核心内容，数据与用户 OpenID 绑定。
- 支持登记我的车辆、我的装备、我的模板。
- 个人页同步显示车辆、装备和模板数量。
- 隐私设置、帮助与反馈、关于页面已按当前小程序内容重写。

### 💬 帮助与反馈

- 用户可在小程序内提交反馈。
- 后端通过 SMTP 将反馈发送至指定邮箱。
- 邮件配置不提交到 Git 仓库，通过环境变量维护。

## 🧱 技术架构

| 层级 | 技术 |
| --- | --- |
| 小程序前端 | UniApp、Vue 3、TypeScript、Tailwind CSS |
| 小程序运行端 | 微信小程序 |
| 请求方式 | 本地 `wx.request`，云端支持 `wx.cloud.callContainer` |
| 后端服务 | Flask、Gunicorn |
| 数据库 | Supabase PostgreSQL |
| 地图与路线 | 高德 Web 服务 |
| 部署方式 | Docker、微信云托管 |

## 📂 目录结构

```text
.
├── api/                         # Flask 后端服务
├── docs/images/                 # README 页面预览图
├── icon/                        # 小程序图标
├── src/                         # UniApp 小程序源码
├── scripts/sync-mp-config.mjs   # 同步微信开发者工具配置
├── supabase/migrations/         # Supabase 初始化 SQL
├── Dockerfile                   # 微信云托管构建入口
├── container.config.json        # 云托管容器配置
├── package.json                 # 前端命令与依赖
└── README.md
```

## 🚀 本地启动

### 1. 安装前端依赖

```bash
npm install
```

### 2. 启动微信小程序开发构建

```bash
npm run dev:mp-weixin
```

### 3. 构建微信小程序产物

```bash
npm run build:mp-weixin
```

构建后，用微信开发者工具导入项目根目录，实际小程序产物位于：

```text
dist/build/mp-weixin
```

### 4. 启动后端服务

```bash
cd api
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python main.py
```

## 🔐 环境变量

后端环境变量可参考：

```text
api/.env.example
```

核心配置示例：

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

## 🗄️ Supabase 初始化

在 Supabase 项目后台打开 `SQL Editor`，执行：

```text
supabase/migrations/00006_current_schema.sql
```

执行后应生成：

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

## ☁️ 微信云托管部署

1. 将代码推送到 GitHub。
2. 在微信云托管中绑定 GitHub 仓库。
3. 服务 Dockerfile 路径选择根目录：

```text
Dockerfile
```

4. 容器端口使用：

```text
80
```

5. 在云托管服务环境变量中配置数据库、微信登录、高德 Key、SMTP 邮箱等信息。
6. 发布服务后，在微信开发者工具中重新编译小程序。
7. 真机预览时优先使用云托管调用，避免本地 IP 不在合法域名列表导致请求失败。

## 🧪 常用检查

```bash
npm run check
npm run build:mp-weixin
```

后端冒烟检查可在 `api` 目录执行：

```bash
venv\Scripts\python -c "from main import create_app; app=create_app(); print(len(list(app.url_map.iter_rules())))"
```

## 📌 版本说明

当前版本：**开发版 1.0.0**

- 完成微信授权登录与登录拦截。
- 完成行程创建、管理、详情查看与删除。
- 完成车辆、装备、模板、个人页统计同步。
- 完成天气、禁摩、预算、装备计算等工具入口。
- 完成 Flask 后端、Supabase 数据库、微信云托管部署适配。
- 完成反馈邮件发送能力。

## ⚠️ 注意事项

- 不要将 `.env`、数据库密码、微信密钥、SMTP 授权码提交到仓库。
- 创建行程依赖高德路线查询；查询失败时不会创建兜底假行程。
- 新建行程不会同步等待后台生成提醒，避免云托管请求超时。
- 天气、禁摩、新闻和建议类信息会在创建后后台加载。
- README 里的页面预览图位于 `docs/images/`，后续可直接替换为最新真机截图。
