PrismaMate支付链路设计文档

## 总体架构：Lemon Squeezy 支付链接 + 国内代账公司报税

**核心原则**：Lemon Squeezy 负责面向用户的**收款 + 全球税务代缴**，你负责通过代账公司完成**国内企业所得税/增值税申报**。

**支付流程四步走**：

```
用户点击"升级套餐" → 跳转 Lemon Squeezy 支付链接 → 用户完成支付（支付宝/微信/银行卡）
                                                              ↓
                                                    你手动在管理后台激活用户套餐
                                                              ↓
                                                    定期从 Lemon Squeezy 提现到公司账户
                                                              ↓
                                                    代账公司帮你申报国内税务
```

这个方案的好处是：
- 开发成本几乎为零，只需要把前端的"升级套餐"按钮换成 Lemon Squeezy 的支付链接
- 用户支付体验顺畅，支持支付宝和微信支付
- 你不需要处理任何支付接口、密钥、回调等复杂技术问题
- 税务合规由 Lemon Squeezy（处理海外部分）和代账公司（处理国内部分）共同保障


## 一、你需要做的事

### 第一步：在 Lemon Squeezy 后台创建产品

1. 打开 [lemonsqueezy.com](https://www.lemonsqueezy.com)，注册账号
2. 在 Settings → Stores 创建一个 Store，名称设为 **PrismaMate**（或棱镜数据）
3. 在 Products 页面，创建以下产品：

| 产品名称 | 类型 | 价格 |
|---------|------|------|
| 复棱MAX版 - 月度订阅 | Subscription | ¥299/月 |
| 复棱MAX版 - 年度订阅 | Subscription | ¥2,999/年 |
| 晶曜PLUS版 - 月度订阅 | Subscription | ¥999/月 |
| 晶曜PLUS版 - 年度订阅 | Subscription | ¥9,999/年 |
| 积分充值 - 100积分 | One-time | ¥100 |
| 积分充值 - 500积分 | One-time | ¥450 |

4. 每个产品创建完成后，点击 **Share**，复制支付链接（Checkout URL）
5. 把所有支付链接整理好，填入下一步的代码中

### 第二步：把支付链接嵌入 PrismaMate 前端

这一步直接发给 CodeBuddy 完成：

---

**CodeBuddy，修改以下前端页面，把套餐升级按钮改为 Lemon Squeezy 支付链接。**

**1. 修改 `src/views/Subscription.vue`（我的订阅页面）**

在“升级套餐”按钮处，根据当前套餐和目标套餐，跳转到对应的支付链接。

支付链接映射表（我来提供）：
```javascript
const PAYMENT_LINKS = {
  plan_max_monthly: "https://prismamate.lemonsqueezy.com/checkout/...",  // 复棱MAX版 月付
  plan_max_yearly: "https://prismamate.lemonsqueezy.com/checkout/...",   // 复棱MAX版 年付
  plan_plus_monthly: "https://prismamate.lemonsqueezy.com/checkout/...", // 晶曜PLUS版 月付
  plan_plus_yearly: "https://prismamate.lemonsqueezy.com/checkout/...",  // 晶曜PLUS版 年付
  points_100: "https://prismamate.lemonsqueezy.com/checkout/...",        // 积分充值 - 100积分
  points_500: "https://prismamate.lemonsqueezy.com/checkout/...",        // 积分充值 - 500积分
};
```

按钮点击逻辑：
- 如果用户未登录，先跳转 `/login`
- 如果用户已登录，直接跳转 Lemon Squeezy 支付链接
- 在支付链接中附加 `?checkout[custom][user_id]={user_id}` 参数，方便后续手动激活时识别

**2. 修改 `src/views/Points.vue`（积分中心页面）**

在“充值”按钮处，同样替换为对应的 Lemon Squeezy 支付链接。

**3. 修改 `src/views/Pricing.vue`（定价页）**

在“立即升级”按钮处，同样替换为对应的 Lemon Squeezy 支付链接。对于“单棱MINI版”的“免费开始”按钮，保持跳转注册页的逻辑。

**4. 新增：支付成功后的手动激活流程**

在 `app/api/v1/admin.py` 中新增一个接口：
- `POST /admin/users/{user_id}/activate-subscription`：管理员手动激活用户套餐
  - 接收 `plan_id` 和 `duration`（月数）
  - 更新用户的 `plan_id`、`subscription_expires_at`、`monthly_points`
  - 记录操作日志

在管理后台 `AdminDashboard.vue` 的用户详情页中，增加“手动激活套餐”按钮和表单。

**重要约束**：
- 支付链接先留空或填占位符，等我去 Lemon Squeezy 创建产品后替换
- 完成后告知

---

### 第三步：打通提现与报税流程

1. **提现路径**：Lemon Squeezy → PayPal → 公司银行对公账户
2. **报税流程**：
   - 每月初，从 Lemon Squeezy 下载上月交易账单
   - 从 PayPal 下载提现记录
   - 将以上账单 + 公司银行流水，一并交给代账公司
   - 代账公司帮你申报增值税（信息技术服务，6%）和企业所得税


## 二、关于品牌展示

Lemon Squeezy 的支付页面上，收款方显示的是你的 **Store 名称**（即 PrismaMate），**不会显示你邢台的公司名称**。用户在银行对账单上看到的也是 Lemon Squeezy 的标识，而非你的公司名。这个顾虑完全不存在。


## 三、总结

| 环节 | 负责方 | 你做的事 |
|------|--------|---------|
| 收款 + 全球税务 | Lemon Squeezy | 创建产品，获取支付链接 |
| 国内税务申报 | 代账公司 | 每月提供账单，代账公司申报 |
| 套餐激活 | 你自己（管理后台） | 确认收款后，手动激活用户套餐 |
| 前端改造 | CodeBuddy | 替换按钮链接 |
| 对公账户收款 | 你的公司 | Lemon Squeezy → PayPal → 对公账户 |

---

你先去 Lemon Squeezy 注册创建产品，拿到支付链接后填入占位符。CodeBuddy 改完前端后告诉我，我们验证一下完整链路。