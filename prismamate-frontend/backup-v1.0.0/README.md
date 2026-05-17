# PrismaMate Frontend 首页定稿备份

## 版本信息
- **版本号**: v1.0.0
- **备份日期**: 2026-05-16
- **描述**: 首页定稿版本 - Hero区域优化、导航栏重设计、Beta标识

## 修改文件清单
1. `src/views/Home.vue` - 首页Hero区域重构
2. `src/components/PublicLayout.vue` - 导航栏重设计
3. `src/components/AppFooter.vue` - 页脚样式适配
4. `src/assets/logo-dark.svg` - Logo + Beta标识
5. `src/assets/logo-light.svg` - 浅色模式Logo

## 回滚操作
如需回滚到该版本，请将上述文件替换回备份版本即可。

## 主要改动点
- Hero区域保留，删除下方所有板块
- 导航栏：首页、关于我们、订阅价格、语言切换、主题切换、登录/注册
- 登录/注册按钮样式一致，中间有 | 分隔
- Logo右侧添加Beta标识（紧挨棱镜报告四字）
- Logo悬停有scale动效
- 中英文切换：默认显示EN，切换后显示中文
- 背景色统一为纯黑#000000
