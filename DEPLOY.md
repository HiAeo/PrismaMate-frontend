# PrismaMate 棱镜 - 部署文档

## 环境要求

- **Python**: 3.12+
- **Node.js**: 24+
- **操作系统**: Windows 10+/Linux/macOS
- **内存**: 最少 2GB RAM

---

## 快速开始（Docker 部署）

### 1. 克隆代码

```bash
git clone <repository-url>
cd PrismaMate
```

### 2. 配置环境变量

```bash
# 复制环境变量示例
cp prismamate-backend/.env.example prismamate-backend/.env

# 编辑并填写必要的配置
# Windows: notepad prismamate-backend\.env
# Linux/Mac: nano prismamate-backend/.env
```

必需配置：
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（必填）

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问地址：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 手动部署

### 后端部署

#### 1. 创建虚拟环境

```bash
cd prismamate-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

必需的环境变量：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | 是 | DeepSeek API 密钥 |
| `KIMI_API_KEY` | 否 | Kimi API 密钥（备用） |
| `SECRET_KEY` | 是 | JWT 密钥（生产环境必须修改） |
| `CORS_ORIGINS` | 否 | 允许的域名，逗号分隔 |
| `DEBUG` | 否 | 调试模式，默认 false |

#### 4. 启动后端

```bash
# Windows PowerShell
.\start_backend.ps1

# Linux/Mac
chmod +x start_backend.sh
./start_backend.sh
```

或直接使用 uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

---

### 前端部署

#### 1. 安装依赖

```bash
cd prismamate-frontend
npm install
```

#### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

#### 3. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

#### 4. 预览（仅用于测试）

```bash
npm run preview
```

---

## Nginx 配置示例

生产环境建议使用 Nginx 托管前端静态文件：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/prismamate-frontend/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 常用运维命令

### 查看服务状态

```bash
# Docker 部署
docker-compose ps

# 直接运行
curl http://localhost:8000/health
```

### 查看日志

```bash
# Docker 部署
docker-compose logs -f backend
docker-compose logs -f frontend

# 直接运行
# 日志输出到终端
```

### 重启服务

```bash
# Docker 部署
docker-compose restart backend
docker-compose restart frontend

# 直接运行
# Ctrl+C 停止，然后重新启动
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 预期响应:
# {"status":"healthy","mvp_mode":true}
```

---

## 目录结构

```
PrismaMate/
├── docker-compose.yml          # Docker 编排配置
├── DEPLOY.md                   # 本部署文档
├── prismamate-backend/         # 后端代码
│   ├── .env.example            # 环境变量示例
│   ├── Dockerfile              # 后端 Docker 镜像
│   ├── start_backend.ps1       # Windows 启动脚本
│   ├── start_backend.sh        # Linux/Mac 启动脚本
│   ├── requirements.txt        # Python 依赖
│   └── app/                    # 应用代码
│       └── main.py             # FastAPI 入口
└── prismamate-frontend/        # 前端代码
    ├── .env.example            # 环境变量示例
    ├── .env.production         # 生产环境变量
    ├── Dockerfile               # 前端 Docker 镜像
    ├── nginx.conf              # Nginx 配置
    ├── start_frontend.ps1      # Windows 启动脚本
    ├── start_frontend.sh       # Linux/Mac 启动脚本
    ├── package.json             # Node.js 依赖
    ├── vite.config.ts          # Vite 配置
    └── dist/                   # 构建产物（构建后生成）
```

---

## 故障排除

### 问题：API 请求返回 401 未授权

**原因**: JWT token 过期或无效

**解决方案**:
1. 清除浏览器 localStorage 中的 token
2. 重新登录

### 问题：CORS 跨域错误

**原因**: `CORS_ORIGINS` 未包含前端域名

**解决方案**:
1. 检查后端 `.env` 中的 `CORS_ORIGINS` 配置
2. 确保包含前端实际访问的域名

### 问题：后端启动失败

**原因**: 端口被占用或缺少依赖

**解决方案**:
1. 检查端口占用: `netstat -an | grep 8000`
2. 重新安装依赖: `pip install -r requirements.txt`

### 问题：前端构建失败

**原因**: Node.js 版本过低或依赖缺失

**解决方案**:
1. 确认 Node.js 版本 24+: `node --version`
2. 删除 node_modules 并重新安装: `rm -rf node_modules && npm install`

---

## 安全建议

1. **API 密钥**: 生产环境务必设置强密码的 `SECRET_KEY`
2. **CORS**: 生产环境只允许信任的域名
3. **HTTPS**: 生产环境务必使用 HTTPS
4. **环境变量**: 不要将 `.env` 文件提交到代码仓库
5. **日志**: 生产环境关闭 DEBUG 模式

---

## 获取帮助

- 提交 Issue: https://github.com/your-repo/issues
- 文档更新: 请提交 PR 或联系维护者
