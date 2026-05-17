# PrismaMate v1.0.2 回滚指南

> 生成时间：2026-05-16 10:50
> 版本：v1.0.2

---

## 备份内容

| 文件 | 版本 | 大小 | 说明 |
|------|------|------|------|
| `prismamate-frontend_src_v1.0.2.zip` | v1.0.2 | 0.23 MB | 前端源代码 |
| `prismamate-backend_v1.0.2.zip` | v1.0.2 | 61 MB | 后端完整代码 |

---

## 回滚步骤

### 方案一：完整回滚

> **重要**：备份文件只包含源代码（约0.23MB），不包含 `node_modules`。恢复后需要重新安装依赖。

#### 前端回滚
```powershell
# 1. 进入工作目录
cd D:\PrismaMate专用文件夹

# 2. 备份当前版本（可选）
Rename-Item prismamate-frontend prismamate-frontend_current

# 3. 解压备份
Expand-Archive -Path backup\prismamate-frontend_src_v1.0.2.zip -DestinationPath prismamate-frontend -Force

# 4. 安装依赖
cd prismamate-frontend
npm install

# 5. 重启前端服务
npm run dev
```

#### 后端回滚
```powershell
# 1. 进入工作目录
cd D:\PrismaMate专用文件夹

# 2. 备份当前版本（可选）
Rename-Item prismamate-backend prismamate-backend_current

# 3. 解压备份
Expand-Archive -Path backup\prismamate-backend_v1.0.2.zip -DestinationPath prismamate-backend -Force

# 4. 安装依赖
cd prismamate-backend
pip install -r requirements.txt

# 5. 重启后端服务
python main.py
```

---

### 方案二：Git 回滚（推荐）

如果项目使用 Git 管理：
```powershell
cd D:\PrismaMate专用文件夹\prismamate-frontend
git checkout v1.0.2
```

---

## 验证清单

回滚完成后请验证以下功能：

- [ ] 首页正常加载
- [ ] 导航菜单正常
- [ ] 页面样式正常
- [ ] 功能按钮可点击
- [ ] 移动端响应式正常

---

## 本版本更新内容

- 新增媒体信源板块（特别鸣谢 + 友情链接）
- 优化深色主题 Logo 显示效果
- 添加 Logo 卡片交互动画
- 响应式布局优化

---

## 联系方式

如有问题，请联系开发团队。
