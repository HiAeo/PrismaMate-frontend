# PrismaMate v1.0.2 回滚说明

**版本号：** v1.0.2  
**生成时间：** 2026-05-17 10:29  
**备份文件：** `PrismaMate_v1.0.2_20260517.zip`

---

## 版本变更记录

### v1.0.2 (2026-05-17)

**功能更新：**
- 定价页支持从后台动态获取价格（`/subscription/plans` API）
- 单棱MINI版价格同步（支持月付/年付）
- 定价页卡片添加 hover 蓝色发光效果
- 定价页按钮 hover 变色效果（各卡片对应橙/蓝/红色）
- 单棱MINI版添加"特惠体验"橙色标签
- 晶曜PLUS版添加"深度使用"红色标签
- 管理后台全站卡片/按钮 hover 交互
- 下拉菜单统一深色主题样式

**修改文件：**
```
prismamate-frontend/src/views/Pricing.vue
prismamate-frontend/src/api/subscription.ts
prismamate-frontend/src/styles/global.css
prismamate-frontend/src/views/admin/AdminDashboard.vue
prismamate-frontend/src/views/admin/AdminUsers.vue
prismamate-frontend/src/views/admin/AdminPlans.vue
prismamate-frontend/src/views/admin/AdminSubscriptions.vue
prismamate-frontend/src/views/admin/AdminPoints.vue
```

---

## 回滚方法

### 方法一：使用备份文件恢复（推荐）

1. 解压 `PrismaMate_v1.0.2_20260517.zip`
2. 用解压出的文件覆盖对应目录

### 方法二：Git 回滚（如已上传 Git）

```bash
# 查看提交历史
git log --oneline

# 回滚到上一版本
git reset --hard HEAD~1

# 强制推送到远程
git push --force origin main
```

### 方法三：手动还原指定文件

如需保留其他更新，只回滚定价页相关改动，可从备份或历史版本恢复：
- `prismamate-frontend/src/views/Pricing.vue`

---

## 上一版本
- 备份文件：`PrismaMate_v1.0.1_恢复说明.md`
- 发布时间：2026-05-14
