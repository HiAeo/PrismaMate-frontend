# PrismaMate 棱镜

> 独立的第三方 GEO 效果检测认证平台

## 项目结构

```
prismamate/
├── prismamate-backend/     # FastAPI 后端
├── prismamate-frontend/   # Vue 3 前端
├── docker-compose.yml     # Docker 编排配置
└── README.md
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 启动开发环境

```bash
# 1. 启动基础设施（PostgreSQL + Redis）
docker-compose up -d postgres redis

# 2. 启动后端
cd prismamate-backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. 启动前端
cd prismamate-frontend
npm install
npm run dev
```

### 使用 Docker 启动全部服务

```bash
docker-compose up -d
```

访问地址：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
