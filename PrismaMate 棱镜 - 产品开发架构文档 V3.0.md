# PrismaMate 棱镜 - 产品开发架构文档

> **文档版本**：V3.0  
> **修订日期**：2026-05-15  
> **文档用途**：本文件是发给 CodeBuddy 的开发指令。请严格按照此架构规划，分阶段完成 PrismaMate 产品的全部开发工作。  

---

## 一、产品定位（V3.0 重大更新）

> **产品定位**：GEO 行业的"查博士"——独立的第三方 GEO 效果检测认证平台。不做 GEO 优化、不评测服务商、不出优化建议。只做一件事：**检测品牌在 AI 搜索中的真实表现，并生成标准化、可溯源、不可篡改的检测报告。**

### 三大核心模块

**模块 A：AI 可见度体检（品牌体检中心）**
- 目标用户：未做 GEO 推广的品牌方
- 功能描述：输入品牌/关键词/平台，进行定期"体检"，查看自身在 AI 大模型中的自然表现
- 核心特性：
  - 支持与历史同模板报告自动对比，发现变化趋势
  - 体检模板系统：一键复用，保证同模板历史报告可比性
  - 历史对比引擎：自动关联同模板报告，输出对比页（新增/消失提及、位次变化、提及率变化）

**模块 B：GEO 效果检测（交付验证中心）**
- 目标用户：品牌方（甲方）验证 GEO 机构（乙方）承诺的效果
- 功能描述：PrismaMate 独立检测来验证 GEO 机构承诺的效果
- 子场景：
  - **进度验证**：GEO 优化进行中，定期检测进度
  - **交付验证**：GEO 优化完成后，验证最终效果
- 核心特性：支持上传 GEO 机构数据进行差异对比（Phase 2 实现）

**模块 C：PrismaMate 报告验真**
- 目标用户：GEO 机构的客户
- 功能描述：GEO 机构用本平台出具的报告，客户可通过验证码验证报告是否原版且未被篡改
- 状态：**已完成**

---

## 二、技术栈选型（请严格遵循）

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端框架** | Vue 3 + Vite | 用户后台、报告展示、验证查询页面 |
| **前端UI库** | Element Plus | 成熟的企业级组件库 |
| **后端框架** | Python FastAPI | 高性能异步框架，适合 API 服务 |
| **数据库** | PostgreSQL + Redis | PG 存业务数据，Redis 做任务队列和缓存 |
| **任务队列** | Celery + Redis | 异步执行检测任务，Celery Beat 定时调度 |
| **浏览器自动化** | Playwright (Python) | 模拟真实用户访问 AI 平台 |
| **报告生成** | WeasyPrint | HTML 转 PDF，支持图表嵌入 |
| **图表库** | ECharts (前端) / Matplotlib (后端备选) | 数据可视化 |
| **区块链存证** | 哈希存证（SHA-256），对接国内合规存证服务 | V2.0 阶段实现（预留字段，暂不实现） |
| **配置管理** | YAML 配置文件 | 平台配置与代码解耦 |
| **部署** | Docker + Nginx | 容器化部署 |

---

## 三、核心功能模块与开发任务拆解

### 模块 1：数据采集引擎（最高优先级，核心壁垒）

#### 1.1 AI 平台适配器架构

**架构要求**：每个 AI 平台对应一个独立的适配器类，继承自 `BasePlatformAdapter` 基类。适配器之间完全解耦，一个平台适配器故障不影响其他平台运行。

**基类接口定义**（V2.0 扩展版）：

```python
class BasePlatformAdapter:
    """AI 平台适配器基类，所有平台适配器必须继承此类"""
    
    platform_name: str          # 平台名称，如 "DeepSeek"
    platform_domain: str        # 平台域名，如 "chat.deepseek.com"
    detection_mode: str         # 检测模式: "api" 或 "browser"
    
    # ============ 核心接口 ============
    
    async def search(self, keyword: str) -> SearchResult:
        """执行关键词搜索，返回结构化结果"""
        pass
    
    async def extract_brand_mentions(self, raw_text: str, brand_names: List[str]) -> List[BrandMention]:
        """从原始返回文本中提取品牌提及"""
        pass
    
    async def extract_citations(self, raw_text: str) -> List[Citation]:
        """提取引用来源URL列表"""
        pass
    
    # ============ V2.0 新增接口 ============
    
    async def is_available(self) -> bool:
        """检测平台是否可达（网络连通性 + 反爬状态检查）
        
        实现指引（请按此实现）：
        1. 轻量探测：发送 HEAD 请求到平台首页，验证 HTTP 状态码为 200
        2. 验证码检查：用无痕浏览器上下文访问搜索页面，检查是否直接出现验证码
        3. 搜索功能验证：执行一次真实搜索（用固定测试关键词），验证能正常返回结果
        
        返回值：
        - True：平台可用（网络可达 + 无验证码 + 搜索功能正常）
        - False：平台不可用（任一检查项失败）
        
        注意事项：
        - 探测应轻量化，避免消耗过多资源
        - 验证码检查建议使用简化流程（不等待完整加载）
        - 探测失败不触发冷却期，仅记录日志
        """
        pass
    
    async def login_if_needed(self) -> bool:
        """确保登录态有效，返回是否成功
        
        实现要求：
        - 检查当前会话是否需要登录
        - 如需要登录，执行登录流程
        - 返回 True 表示登录成功或无需登录，False 表示登录失败
        """
        pass
    
    async def handle_captcha(self) -> CaptchaResult:
        """处理验证码，返回处理结果
        
        返回值类型 CaptchaResult:
        - status: "skipped" | "paused" | "retry"
        - message: 说明信息
        
        实现要求：
        - 检测到验证码时，记录日志
        - 默认策略：暂停任务，不尝试自动过验证码
        - 返回暂停状态，供任务调度器决策
        """
        pass
    
    def get_last_dom_change(self) -> datetime:
        """记录最后一次 DOM 结构变更检测时间
        
        用于维护追踪：
        - 当冒烟测试失败时，更新此时间戳
        - 连续失败超过阈值时触发告警
        """
        pass
```

**数据模型定义**（请严格按此结构定义数据库模型）：

```python
class SearchResult:
    keyword: str                # 查询关键词
    platform: str               # AI 平台名称
    detection_mode: str         # 检测模式: "api" 或 "browser"
    raw_response: str           # AI 完整回答文本
    timestamp: datetime         # 查询时间戳
    query_params: dict          # 查询参数快照

class BrandMention:
    brand_name: str             # 被提及的品牌名
    position: int               # 在回答中的位次（第几个被提及）
    context_snippet: str        # 提及上下文字段
    sentiment: str               # 情感极性: positive/neutral/negative
    is_primary_mention: bool    # 是否为主要提及（非顺带提及）

class Citation:
    url: str                    # 引用来源URL
    source_domain: str          # 来源域名
    anchor_text: str            # 链接锚文本
    position_in_response: int   # 在回答中的出现顺序
```

#### 1.2 第一阶段需适配的 AI 平台（MVP 必须完成）

**平台 1：DeepSeek**
- 访问方式：网页端 `chat.deepseek.com` 或官方 API
- 注意：需要处理登录态和会话保持
- 实现要点：
  - **双模式支持**：优先使用官方 API（`api_mode`），API 不可用时降级到 Playwright（`browser_mode`）
  - Browser 模式：使用 Playwright 打开页面，输入关键词，等待 AI 完成回答，提取完整响应文本

**平台 2：豆包 (Doubao)**
- 访问方式：网页端 `www.doubao.com`
- 注意：字节跳动产品，反爬机制较强
- 实现要点：需要模拟真实用户行为（鼠标移动、随机延迟、正常打字速度）

**平台 3：Kimi**
- 访问方式：网页端 `kimi.moonshot.cn`
- 注意：长文本回答场景下的完整内容提取
- 实现要点：需处理"继续生成"按钮的点击

**CodeBuddy 开发指令 - 平台适配器实现要点**：

```
【重要】请为每个平台适配器实现以下通用反爬策略：
1. 使用 Playwright 的 stealth 模式（playwright-stealth 库）
2. 设置真实的浏览器 User-Agent（Chrome 最新稳定版）
3. 每次查询间隔随机 3-8 秒
4. 模拟真实键盘输入速度（每个字符间隔 50-150ms）
5. 随机鼠标移动轨迹（使用 page.mouse.move）
6. 每个平台使用独立的浏览器上下文，cookie 隔离
7. 遇到验证码时，暂停任务并记录日志（不要尝试自动过验证码）
8. 每个平台每日查询上限可配置，超过上限自动暂停

【V2.0 新增】双模式切换策略：
1. detection_mode 字段定义在平台配置文件中
2. 适配器初始化时读取配置，决定使用 API 模式还是 Browser 模式
3. API 模式优先：调用平台官方 API 获取结果
4. Browser 模式降级：当 API 不可用或结果与用户端不一致时启用
5. 同一平台内部也可实现自动降级：先尝试 API，失败后尝试 Browser
```

#### 1.3 数据采集任务调度

**实现要求**：
- 使用 Celery 异步任务队列
- 每个检测请求拆分为多个子任务（每个关键词×每个平台为一个独立子任务）
- 子任务支持并发执行（但同一平台的子任务需串行，间隔 3-8 秒）
- 任务失败自动重试（最多 3 次，指数退避）
- 任务状态实时可查（见 1.4 节状态机定义）

**V2.0 新增：冷却期机制**

```
冷却期机制（必须在任务调度器中实现）：
1. 单平台连续失败 3 次后，该平台自动进入冷却期
2. 冷却时长：2 小时（可配置）
3. 冷却期内该平台不接收新任务
4. 已排队的任务自动标记为"paused"状态，等待平台恢复
5. 冷却期结束后自动执行一次 is_available() 探测
6. 确认恢复后重新接单，任务从 paused 状态恢复执行
7. 冷却事件需记录日志（platform_cooldown_events 表）
8. 管理后台可查看各平台的冷却状态和历史记录
```

**CodeBuddy 开发指令**：
```
【注意】Celery 任务设计时：
- 不要在一个任务中循环查询多个平台（会导致任务阻塞）
- 使用 Celery Chain 或 Group 来编排多平台查询的依赖关系
- 任务结果存储在 Redis，设置 24 小时过期时间
- 每个任务必须记录详细的执行日志（平台、关键词、耗时、是否成功）

【V2.0 任务调度增强】：
- 任务调度器需集成冷却期管理逻辑
- 使用 Redis Set 存储正在冷却的平台列表
- 每个平台记录 last_failure_time，支持按时间窗口计算失败次数
```

#### 1.4 任务状态机（V2.0 细化版）

**状态定义**：

```
pending → running → collecting → parsing → generating → completed
                     ↓              ↓            ↓
                  failed        failed       failed
                     ↓
                 retrying → paused
```

**状态说明**：

| 状态 | 含义 | 可转换至 |
|------|------|---------|
| `pending` | 任务已创建，等待调度 | `running`, `failed` |
| `running` | 任务正在调度中 | `collecting`, `failed` |
| `collecting` | 正在从 AI 平台采集数据 | `parsing`, `failed`, `paused` |
| `parsing` | 正在解析提取品牌提及和引用 | `generating`, `failed`, `paused` |
| `generating` | 正在生成 PDF 报告 | `completed`, `failed` |
| `completed` | 任务完成 | - |
| `failed` | 任务失败 | `retrying`, `pending` |
| `retrying` | 采集失败，正在重试（最多3次） | `collecting`, `paused` |
| `paused` | 平台触发冷却期，任务暂停等待恢复 | `collecting` |

**前端展示约定**：
- `collecting`、`parsing`、`generating` 统一显示为"检测中"
- 使用分阶段进度条展示各子阶段进度
- `paused` 状态显示"等待平台恢复"提示
- 用户可查看详细状态日志

#### 1.5 平台可用性定时检测（V2.0 新增：冒烟测试）

**实现要求**：

```
冒烟测试机制（使用 Celery Beat 定时任务）：
1. 每周对全部已接入平台执行一次冒烟测试
2. 冒烟测试内容：
   - 使用固定测试关键词执行一次搜索
   - 验证是否能成功获取 AI 回答
   - 检测 is_available() 返回值
3. 测试结果记录到日志表（platform_smoke_tests 表）
4. 告警规则：
   - 连续 2 周测试失败 → 触发告警（邮件/站内通知管理员）
   - 记录 get_last_dom_change() 时间戳，辅助排查问题
5. 冒烟测试不消耗用户的检测额度
6. 测试日志包含：测试时间、平台名称、测试关键词、结果状态、响应时间、错误信息
```

---

### 模块 2：语义解析引擎

#### 2.1 品牌提及提取

**V2.0 品牌别名处理策略**：

```
品牌别名处理（用户输入 + 系统辅助）：
1. 用户创建检测任务时，输入核心品牌名（如"华为"）
2. 系统自动生成常见变体建议：
   - 完整公司名（如"华为技术有限公司"）
   - 英文名（如"Huawei"）
   - 产品线名（如"华为手机"）- 可选
3. 用户确认或编辑后生效，作为本次检测的精确匹配词列表
4. 匹配时只做精确匹配（检查输入内容是否完整出现在回答中）
5. 同一个品牌在回答中多次出现，只记录第一次出现的位次
6. 需要返回提及的上下文（提及位置前后 50 个字符）
7. 情感极性在 MVP 阶段默认为 neutral，V1.0 引入大模型判断
```

**V2.0 精确匹配规则**：

```
匹配规则说明：
1. 精确匹配：品牌全名（如"华为技术有限公司"）
2. 模糊匹配：暂不实现，留待 V1.0 引入 NLP 模型
3. 排除误报：
   - 排除 URL 中出现的品牌名
   - 排除引用来源标注中的品牌名
   - 排除引号内的搜索查询本身
4. 位次计算：按品牌在回答中第一次出现的位置排序
5. 使用正则表达式匹配，但要处理中文分词边界
```

#### 2.2 引用来源提取

**实现要求**：
1. 提取 AI 回答中所有引用的 URL
2. 解析 URL 的域名（作为来源域）
3. 提取链接的锚文本（如果有）
4. 记录引用出现在回答中的位置

**CodeBuddy 开发指令**：
```
【注意】URL 提取注意事项：
- 不同 AI 平台的引用格式不同，需要在适配器中分别处理
- DeepSeek 引用格式：[数字] URL 或直接内联链接
- 豆包引用格式：通常在回答末尾的"参考资料"部分
- Kimi 引用格式：行内数字标记，末尾附详细来源
- 需要排除非引用链接（如广告、推荐阅读等，域名匹配规则可配置）
```

---

### 模块 3：检测报告生成引擎

#### 3.1 报告数据结构

```python
class DetectionReport:
    report_id: str              # 唯一报告编号，格式：PM-YYYYMMDD-XXXX
    brand_names: List[str]      # 检测的品牌名列表
    keywords: List[str]         # 检测的关键词列表
    platforms: List[str]        # 检测的 AI 平台列表
    detection_time: datetime    # 检测执行时间
    overall_results: dict       # 各品牌×各平台×各关键词的检测结果矩阵
    competitor_results: dict    # 竞品检测结果（如有）
    report_hash: str            # 报告内容哈希值，用于防篡改
    blockchain_tx_id: str       # 区块链存证交易ID（V2.0 预留字段，暂不实现）
    
    # V3.0 新增字段
    template_id: str            # 关联的体检模板ID（可选）
    parent_report_id: str       # 上一次同模板报告ID，用于历史对比（可选）
    report_type: str            # 报告类型: "health_check" | "geo_verification"
```

#### 3.2 PDF 报告模板

**报告结构**（请按此生成 PDF）：
1. **封面**：报告标题、检测品牌、检测时间、报告编号、PrismaMate 标识
2. **检测概要**：一页纸总结，总分结构，关键发现突出显示
3. **AI 可见度详情**：每个平台的品牌提及率、引用位次、引用内容摘要
4. **竞品对比**（如有）：横向对比雷达图
5. **信源分析**：引用来源域名分布、权威信源占比
6. **历史对比**（如有同模板历史报告）：新增/消失提及、位次变化、提及率变化
7. **检测方法说明**：附录，说明检测环境、技术路径、数据采集时间
8. **验证信息**：报告编号、哈希值、验证网址（prismamate.com/verify）

**CodeBuddy 开发指令 - 报告生成注意事项**：
```
【关键要求】PDF 报告生成：
1. 使用 WeasyPrint 从 HTML 模板生成 PDF（支持中文字体）
2. 中文字体使用"思源黑体"或系统默认中文字体，确保跨平台显示正常
3. 图表使用 ECharts 渲染为图片后嵌入（或使用 Matplotlib 后端生成）
4. 报告文件命名格式：PrismaMate_Report_{报告编号}_{品牌名}_{日期}.pdf
5. 报告生成后自动上传至 OSS（阿里云/腾讯云），返回下载链接
6. 报告需同时存储：原始 JSON 数据 + PDF 文件 + 哈希值

【V2.0 存储策略调整】：
- raw_response 设置 90 天自动过期
- 超期数据自动删除或归档压缩存储
- 用户注册协议中增加数据留存期限说明
- 敏感关键词检测结果存储前进行脱敏处理

【V3.0 报告增强】：
- 当存在同模板历史报告时，自动生成对比页
- 报告封面增加报告类型标识（品牌体检 / GEO验证）
- 支持体检报告和GEO验证报告的差异化模板
```

#### 3.3 报告验证系统

**实现要求**：
1. 每份报告生成唯一 12 位验证码（字母数字混合）
2. 用户可在 `prismamate.com/verify` 页面输入验证码
3. 验证页面显示：报告基本信息 + 哈希值比对结果 + "此报告由 PrismaMate 出具且未被篡改"
4. 提供 API 接口供第三方系统自动验证

**CodeBuddy 开发指令**：
```
【注意】验证系统需要：
- 验证页面是纯前端页面（Vue），无需登录即可使用
- 验证接口需要做限流（防止暴力破解验证码）
- 报告哈希值存储在数据库，验证时对比当前报告内容的哈希值
- 如果哈希值不匹配，页面显示"⚠️ 此报告可能已被篡改"
```

---

### 模块 4：体检模板与历史对比引擎（V3.0 新增）

#### 4.1 体检模板系统

**功能描述**：用户可保存体检配置为模板，一键复用，保证同模板历史报告可比性。

**核心特性**：
1. 创建体检时，可选择"保存为模板"
2. 输入模板名称，系统保存：品牌列表、关键词列表、平台列表
3. 模板列表页支持：一键复用、编辑模板、删除模板
4. 复用模板时，自动填充历史配置，可微调后发起检测

**数据模型 - HealthCheckTemplate**：

```python
class HealthCheckTemplate:
    template_id: str            # 模板唯一ID，格式：TPL-YYYYMMDD-XXXX
    user_id: int                # 所属用户ID
    name: str                   # 模板名称（用户自定义）
    brands: List[dict]          # 品牌配置 [{"full_name":"华为","short_names":["华为","Huawei"]}]
    keywords: List[str]         # 关键词列表
    platforms: List[str]        # 平台列表 ["DeepSeek", "Kimi", "豆包"]
    created_at: datetime        # 创建时间
    updated_at: datetime        # 更新时间
    last_used_at: datetime      # 最后使用时间
```

#### 4.2 历史对比引擎

**功能描述**：同模板的报告自动关联，新报告生成时自动匹配上一份同模板报告，输出对比页。

**核心特性**：
1. 新报告生成时，自动查找 `template_id` 相同的最新历史报告
2. 自动设置 `parent_report_id` 关联
3. 生成对比数据结构 `ComparisonResult`

**数据模型 - ComparisonResult**：

```python
class ComparisonResult:
    """体检对比结果"""
    new_report_id: str          # 新报告ID
    previous_report_id: str     # 历史报告ID
    comparison_time_gap: int    # 两次体检间隔天数
    
    # 品牌提及变化
    new_mentions: List[dict]   # 新增提及 [{"brand": "华为", "platform": "DeepSeek", "keyword": "AI手机"}]
    lost_mentions: List[dict]  # 消失提及 [{"brand": "华为", "platform": "DeepSeek", "keyword": "AI手机"}]
    unchanged_mentions: int     # 保持提及数量
    
    # 位次变化
    ranking_changes: List[dict] # [{"brand": "华为", "platform": "DeepSeek", "keyword": "AI手机", "old_position": 3, "new_position": 1, "change": -2}]
    
    # 提及率变化
    mention_rate_change: dict   # {"brand": "华为", "old_rate": 0.6, "new_rate": 0.8, "change": +0.2}
```

#### 4.3 GEO 数据上传与差异计算（Phase 2）

**功能描述**：支持手动输入或粘贴 GEO 机构提供的优化数据，与 PrismaMate 独立检测结果逐项对比，标注差异。

**核心特性**（Phase 2 详细设计，本次文档先占位）：
1. 支持上传 GEO 机构提供的检测数据（Excel/CSV/手动输入）
2. 与 PrismaMate 独立检测结果按品牌×关键词×平台维度对齐
3. 计算差异：提及状态差异、位次差异、提及率差异
4. 生成差异报告，标注"优于承诺" / "未达承诺" / "与承诺一致"

---

### 模块 5：GEO 效果检测（交付验证中心）（V3.0 新增）

#### 5.1 验证场景

**进度验证**：
- 场景：GEO 优化进行中，品牌方定期检测进度
- 功能：按模板定期体检，对比历史数据，观察趋势变化

**交付验证**：
- 场景：GEO 优化完成后，品牌方验证最终效果
- 功能：
  1. 品牌方发起独立检测（PrismaMate 自主检测）
  2. 上传 GEO 机构提供的检测报告（Phase 2）
  3. 系统计算差异，输出验证结论

#### 5.2 数据上传接口（Phase 2 预留）

```
【Phase 2 实现】GEO 数据上传：
- POST /api/v1/verification/upload
- 支持文件上传（Excel/CSV）或 JSON 数据
- 数据格式：[{brand, keyword, platform, is_mentioned, position, mention_rate}]
- 返回：对比分析结果
```

---

### 模块 6：用户系统与前端界面

#### 6.1 用户角色

| 角色 | 说明 | 权限 |
|------|------|------|
| **品牌方（甲方）** | 需要验证 GEO 效果的企业 | 创建检测任务、管理体检模板、查看报告、发起 GEO 验证 |
| **服务商（乙方）** | GEO 优化服务提供商 | 创建检测任务、生成交付报告、批量购买检测额度 |
| **管理员** | PrismaMate 运营方 | 用户管理、平台配置、数据查看 |

#### 6.2 核心页面（V3.0 更新）

**页面 1：首页**
- 入口优化：开始检测 → 登录判断，验证报告 → 弹窗验证码输入框
- 快速入口：新建体检、历史报告、我的模板

**页面 2：体检中心首页 `/health-check`**
- 入口：新建体检、我的模板、历史报告
- 最近体检记录快速访问
- 体检趋势图（提及率变化趋势）

**页面 3：新建体检页 `/health-check/new`**
- 复用检测表单（品牌、关键词、平台选择）
- 新增：模板名称输入框（保存为模板时使用）
- 支持选择已有模板一键填充

**页面 4：我的模板页 `/health-check/templates`**
- 模板列表：显示名称、品牌数、关键词数、平台数、最后使用时间
- 操作：一键发起体检、编辑模板、删除模板

**页面 5：报告对比页 `/reports/{id}/comparison`**
- 展示与上次体检的差异
- 新增提及 / 消失提及列表
- 位次变化排名（进步最大 / 退步最多）
- 提及率变化趋势图

**页面 6：检测任务创建页 `/detect`**
- 保留（可逐步引导至体检中心）
- 入口：发起独立检测（非模板体检）

**页面 7：报告列表页**
- 历史报告列表，按时间排序
- 每条记录显示：报告编号、类型（体检/验证）、品牌、检测时间、关键词数、平台数、状态
- 支持下载 PDF、在线预览、分享链接

**页面 8：报告详情页**
- 完整报告内容的在线预览
- 交互式图表（可悬停查看详细数据）
- 竞品对比切换
- 一键下载 PDF
- 如有历史报告，显示"查看对比"入口

**页面 9：用户中心**
- 账户信息、套餐管理、消费记录
- API Key 管理（企业版）
- 品牌和关键词库管理

**页面 10：报告验证页 `/verify`**
- 保持不变
- 输入验证码，验证报告真伪

**CodeBuddy 开发指令 - 前端开发注意事项**：
```
【要求】前端实现：
1. 使用 Vue 3 Composition API + TypeScript
2. 使用 Element Plus 组件库（表格、表单、对话框、消息提示等）
3. 图表使用 ECharts，封装为 Vue 组件
4. 响应式设计，支持桌面端和平板端
5. 所有 API 请求使用 Axios，统一错误处理
6. 使用 Pinia 做状态管理（用户信息、当前检测任务等）
7. 路由使用 Vue Router，需登录的页面添加路由守卫

【V3.0 前端路由新增】：
- /health-check：体检中心首页
- /health-check/new：新建体检页
- /health-check/templates：我的模板列表
- /reports/:id/comparison：报告对比页
```

---

### 模块 7：区块链存证（V2.0 阶段，预留字段，暂不实现）

**V2.0 说明**：区块链存证功能预留数据库字段，暂不实现代码。V1.0 上线稳定后再规划。

**预留字段**：
- `reports.blockchain_tx_id`：存储区块链交易 ID
- `reports.blockchain_status`：存证状态（pending/completed/failed）

---

## 四、风险应对策略（V2.0 新增章节）

### 4.1 冷却期管理

```
冷却期机制：
- 触发条件：单平台连续失败 3 次
- 冷却时长：2 小时（可配置）
- 执行动作：
  1. 将平台加入 Redis 冷却集合
  2. 标记所有等待该平台的任务状态为 "paused"
  3. 设置定时器，2 小时后自动恢复
  4. 恢复时执行 is_available() 探测
  5. 探测成功后将平台移出冷却集合，任务自动恢复执行
- 日志记录：platform_cooldown_events 表
- 告警：进入冷却期时通知管理员
```

### 4.2 冒烟测试机制

```
冒烟测试（Celery Beat 定时任务）：
- 执行频率：每周一次
- 测试内容：对每个已接入平台执行固定关键词搜索
- 结果判定：
  - 成功：能获取完整 AI 回答
  - 失败：超时、验证码、拦截、解析错误
- 告警规则：连续 2 周失败 → 触发管理员告警
- 日志表：platform_smoke_tests
```

### 4.3 优雅降级策略

```
降级链路（按优先级）：
1. API 模式优先：调用平台官方 API
2. API 失败 → 自动降级到 Browser 模式
3. Browser 模式失败 → 进入冷却期
4. 所有模式失败 → 任务标记为 failed，通知用户

平台级别降级：
- 当平台 is_available() 返回 False 时，自动标记为不可用
- 不可用平台不接收新任务
- 定期探测恢复，恢复后自动重新接单
```

### 4.4 验证码处理策略

```
验证码处理流程：
1. 检测到验证码 → 暂停任务执行
2. 记录日志（captcha_events 表）
3. 返回 CaptchaResult(status="paused")
4. 任务状态更新为 "paused"
5. 不尝试自动过验证码
6. 通知管理员有验证码事件
```

### 4.5 存储与合规策略

```
数据存储策略（V2.0）：
1. raw_response 保留 90 天，过期后自动删除
2. 压缩归档：超过 30 天的数据压缩存储
3. 敏感数据脱敏：关键词检测结果存储前脱敏
4. 用户协议明确数据留存期限
5. 支持用户申请删除个人数据（GDPR/个保法合规）
```

---

## 五、配置中心（V2.0 新增）

### 5.1 配置目录结构

```
config/
├── platforms/
│   ├── deepseek.yaml      # URL、选择器、限流配置、detection_mode
│   ├── doubao.yaml
│   └── kimi.yaml
├── detection/
│   ├── retry.yaml         # 重试次数、退避策略
│   └── throttle.yaml      # 请求间隔、冷却期参数
└── report/
    └── templates/         # 报告模板文件
```

### 5.2 平台配置示例（deepseek.yaml）

```yaml
platform:
  name: "DeepSeek"
  domain: "chat.deepseek.com"
  detection_mode: "api"  # api 或 browser

# API 模式配置
api:
  enabled: true
  endpoint: "https://api.deepseek.com/v1/chat/completions"
  api_key_env: "DEEPSEEK_API_KEY"  # 从环境变量读取
  model: "deepseek-chat"
  timeout: 60

# Browser 模式配置
browser:
  enabled: true
  stealth: true
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
  selectors:
    # ⚠️ 【重要】执行前必须手动检查 DeepSeek 实际 DOM 结构并替换以下占位符
    # 检查方式：打开 https://chat.deepseek.com，按 F12 打开开发者工具，
    # 在 Elements 面板中定位输入框、发送按钮、响应内容容器等元素，
    # 复制其 CSS 选择器或 XPath 填入下方
    input: "CHANGE_ME_INPUT_SELECTOR"       # 例如: "#chat-input" 或 ".input-box"
    submit: "CHANGE_ME_SUBMIT_SELECTOR"      # 例如: "#submit-button" 或 ".send-btn"
    response: "CHANGE_ME_RESPONSE_SELECTOR"  # 例如: ".response-content" 或 "[data-testid='response']"
    continue_button: "CHANGE_ME_CONTINUE_SELECTOR"  # 例如: "text=继续生成" 或 ".continue-btn"
  wait_times:
    typing_char_delay: [50, 150]  # ms
    search_interval: [3, 8]  # 秒
    response_timeout: 120

# 限流配置
rate_limit:
  daily_max: 1000
  cooldown_on_failure: 3  # 连续失败次数触发冷却
  cooldown_duration: 7200  # 冷却时长（秒）

# DOM 选择器版本（用于追踪变更，每次手动更新选择器后修改此日期）
dom_version: "CHANGE_ME_DATE"  # 例如: "2026-05-14"
last_change_detected: null
```

### 5.3 检测配置（detection/retry.yaml）

```yaml
retry:
  max_attempts: 3
  backoff_strategy: "exponential"
  initial_delay: 5  # 秒
  max_delay: 300  # 秒

task:
  result_ttl: 86400  # Redis 结果保留 24 小时
  timeout: 600  # 任务超时 10 分钟
```

---

## 六、数据库核心表结构（V3.0 新增表）

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'client',  -- client/vendor/admin
    company_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 检测任务表
CREATE TABLE detection_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    task_type VARCHAR(20) NOT NULL,  -- single/recurring
    report_type VARCHAR(20) DEFAULT 'health_check',  -- health_check / geo_verification
    template_id INTEGER REFERENCES health_check_templates(id),  -- V3.0: 关联模板
    status VARCHAR(20) DEFAULT 'pending',  -- pending/running/collecting/parsing/generating/completed/failed/retrying/paused
    brands JSONB NOT NULL,  -- [{"full_name":"华为","short_names":["华为","Huawei"]}]
    keywords TEXT[] NOT NULL,
    platforms TEXT[] NOT NULL,
    competitors JSONB,  -- 竞品品牌信息，同 brands 格式
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 检测结果表
CREATE TABLE detection_results (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES detection_tasks(id),
    platform VARCHAR(50) NOT NULL,
    keyword VARCHAR(500) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    is_mentioned BOOLEAN DEFAULT FALSE,
    mention_position INTEGER,  -- 在回答中的位次，未提及则为 NULL
    context_snippet TEXT,      -- 提及上下文
    citations JSONB,           -- 引用来源列表
    raw_response TEXT,         -- AI 完整回答
    raw_response_expires_at TIMESTAMP,  -- V2.0: 90天后过期
    detection_mode VARCHAR(20),  -- V2.0: api 或 browser
    detected_at TIMESTAMP DEFAULT NOW()
);

-- 报告表
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(20) UNIQUE NOT NULL,  -- PM-20260115-ABCD
    task_id INTEGER REFERENCES detection_tasks(id),
    user_id INTEGER REFERENCES users(id),
    report_hash VARCHAR(64) NOT NULL,        -- SHA-256
    blockchain_tx_id VARCHAR(255),           -- V2.0 预留字段
    blockchain_status VARCHAR(20),           -- V2.0 预留字段: pending/completed/failed
    pdf_url VARCHAR(500),
    json_data JSONB,
    verification_code VARCHAR(12) UNIQUE NOT NULL,
    
    -- V3.0 新增字段
    report_type VARCHAR(20) DEFAULT 'health_check',  -- health_check / geo_verification
    template_id INTEGER REFERENCES health_check_templates(id),  -- 关联模板
    parent_report_id INTEGER REFERENCES reports(id),  -- 上一次同模板报告，用于历史对比
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- V3.0 新增：体检模板表
CREATE TABLE health_check_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(20) UNIQUE NOT NULL,  -- TPL-20260515-ABCD
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,  -- 模板名称
    brands JSONB NOT NULL,  -- [{"full_name":"华为","short_names":["华为","Huawei"]}]
    keywords TEXT[] NOT NULL,
    platforms TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- V3.0 新增：报告对比记录表
CREATE TABLE report_comparisons (
    id SERIAL PRIMARY KEY,
    new_report_id INTEGER REFERENCES reports(id) NOT NULL,
    previous_report_id INTEGER REFERENCES reports(id) NOT NULL,
    comparison_result JSONB NOT NULL,  -- ComparisonResult 结构
    created_at TIMESTAMP DEFAULT NOW()
);

-- V2.0 新增：平台冷却事件表
CREATE TABLE platform_cooldown_events (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    reason VARCHAR(255),  -- 触发冷却的原因
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    recovered_successfully BOOLEAN DEFAULT FALSE
);

-- V2.0 新增：冒烟测试记录表
CREATE TABLE platform_smoke_tests (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    test_keyword VARCHAR(255),  -- 测试用的固定关键词
    status VARCHAR(20) NOT NULL,  -- success/failed
    response_time_ms INTEGER,
    error_message TEXT,
    tested_at TIMESTAMP DEFAULT NOW()
);

-- V2.0 新增：验证码事件表
CREATE TABLE captcha_events (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES detection_tasks(id),
    platform VARCHAR(50) NOT NULL,
    occurred_at TIMESTAMP DEFAULT NOW(),
    handled_status VARCHAR(20) DEFAULT 'paused'
);

-- V2.0 新增：数据清理任务记录表（用于追踪自动清理执行情况）
CREATE TABLE data_cleanup_logs (
    id SERIAL PRIMARY KEY,
    cleanup_type VARCHAR(50) NOT NULL,  -- 例如: "raw_response_cleanup"
    records_deleted INTEGER DEFAULT 0,
    executed_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'success'  -- success/failed
);

-- V3.0 Phase 2 预留：GEO 验证数据表
CREATE TABLE geo_verification_data (
    id SERIAL PRIMARY KEY,
    verification_id VARCHAR(50) NOT NULL,  -- 验证批次ID
    user_id INTEGER REFERENCES users(id),
    platform VARCHAR(50) NOT NULL,
    keyword VARCHAR(500) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    is_mentioned BOOLEAN,
    mention_position INTEGER,
    mention_rate DECIMAL(5,4),
    data_source VARCHAR(20) NOT NULL,  -- 'agency' (GEO机构提供) / 'prismamate' (平台检测)
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### 6.1 数据清理机制（V2.1 新增）

**raw_response 数据过期清理**：

```
清理策略：检测结果表中的 raw_response 字段在 90 天后自动清理。

实现方案（二选一）：

【方案 A】使用 Celery Beat 每日任务（推荐）
- 创建每日定时任务 cleanup_expired_raw_responses
- 执行时间建议设置在业务低峰期（如凌晨 3:00）
- 清理逻辑：
  1. 查询 detection_results 表中 raw_response_expires_at < NOW() 的记录
  2. 将 raw_response 字段置为 NULL 或空字符串（保留其他结构化数据）
  3. 可选：将原始数据压缩后存入冷存储（需评估成本）
  4. 记录清理日志到 data_cleanup_logs 表
- Celery Beat 配置示例：
  celerybeat_schedule = {
      'cleanup-expired-raw-responses': {
          'task': 'app.tasks.cleanup.cleanup_expired_raw_responses',
          'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点
      },
  }

【方案 B】使用 pg_cron（PostgreSQL 定时任务）
- 优点：不依赖 Python 服务
- 配置方式：
  1. 安装 pg_cron 扩展
  2. 创建清理函数 cleanup_expired_raw_responses()
  3. 配置 cron 任务：SELECT cron.schedule('cleanup-raw-responses', '0 3 * * *', 'SELECT cleanup_expired_raw_responses()');
- 清理 SQL 示例：
  UPDATE detection_results 
  SET raw_response = NULL, 
      raw_response_expires_at = NULL
  WHERE raw_response IS NOT NULL 
    AND detected_at < NOW() - INTERVAL '90 days';

注意事项：
- 清理前建议先备份或归档重要数据
- 清理操作应在业务低峰期执行，避免影响正常请求
- 定期检查清理任务的执行日志，确保正常运行
```

---

## 七、API 接口设计（V3.0 新增体检相关接口）

| 接口路径 | 方法 | 说明 | 备注 |
|---------|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 | |
| `/api/v1/auth/login` | POST | 用户登录，返回 JWT | |
| `/api/v1/tasks` | POST | 创建检测任务 | |
| `/api/v1/tasks/{task_id}` | GET | 查询任务状态（含详细子状态） | V2.0 返回 collecting/parsing/generating |
| `/api/v1/tasks/{task_id}/results` | GET | 获取检测原始结果 | |
| `/api/v1/reports` | POST | 基于已完成任务生成报告 | |
| `/api/v1/reports` | GET | 获取报告列表 | V3.0 新增 |
| `/api/v1/reports/{report_id}` | GET | 获取报告详情/下载链接 | |
| `/api/v1/reports/{report_id}/comparison` | GET | 获取报告对比数据 | V3.0 新增 |
| `/api/v1/reports/verify/{code}` | GET | 验证报告真伪 | 无需登录 |
| **V3.0 体检模板接口** | | | |
| `/api/v1/templates` | GET | 获取我的模板列表 | V3.0 新增 |
| `/api/v1/templates` | POST | 创建体检模板 | V3.0 新增 |
| `/api/v1/templates/{template_id}` | GET | 获取模板详情 | V3.0 新增 |
| `/api/v1/templates/{template_id}` | PUT | 更新模板 | V3.0 新增 |
| `/api/v1/templates/{template_id}` | DELETE | 删除模板 | V3.0 新增 |
| `/api/v1/templates/{template_id}/start` | POST | 使用模板发起体检 | V3.0 新增 |
| **V3.0 Phase 2 GEO验证接口** | | | |
| `/api/v1/verification/upload` | POST | 上传 GEO 机构检测数据 | Phase 2 |
| `/api/v1/verification/compare` | POST | 对比 GEO 数据与平台检测结果 | Phase 2 |
| **用户与管理员接口** | | | |
| `/api/v1/user/profile` | GET | 获取用户信息 | |
| `/api/v1/user/usage` | GET | 查询用量统计 | |
| `/api/v1/admin/platforms` | GET | 获取平台状态列表（含冷却状态） | 管理员专用 |
| `/api/v1/admin/smoke-tests` | GET | 获取冒烟测试历史 | 管理员专用 |

**CodeBuddy 开发指令 - API 开发注意事项**：
```
【要求】API 实现：
1. 所有接口使用 FastAPI + Pydantic 模型做请求验证
2. JWT 鉴权，除 /verify 接口外均需登录
3. 创建检测任务时，需要校验用户的剩余检测额度
4. 接口限流：单用户每分钟最多 10 次请求
5. 所有接口返回统一格式：{"code": 200, "data": {...}, "message": "success"}
6. 错误时返回适当的 HTTP 状态码和错误描述

【V2.0 新增】：
7. 平台状态接口需返回各平台的冷却状态、最后测试时间、可用性状态
8. 冒烟测试接口需返回历史测试记录和连续失败告警状态

【V3.0 新增】：
9. 模板相关接口需支持 CRUD 操作
10. 报告对比接口返回 ComparisonResult 结构
11. Phase 2 GEO 验证接口支持文件上传和批量数据对比
```

---

## 八、开发阶段调整（V3.0 "5+2+2" 模式）

### Phase 1（第 1-3 周）：核心闭环验证

**交付物：**
1. 项目骨架搭建（FastAPI + Vue 3 + Docker + 数据库）
2. DeepSeek 适配器（含双模式：API + Playwright Browser）
3. 品牌提及提取（精确匹配规则引擎）
4. 一个极简 Web 页面（输入框 + 发起检测 + 查看/下载纯文本检测结果）
5. 基础 PDF 报告生成

**验证标准（必须全部通过）：**
- [ ] DeepSeek 适配器能处理登录状态
- [ ] 能提取品牌提及（含上下文和引用来源）
- [ ] 单次检测耗时 < 60 秒（不含人为添加的请求间隔延迟的纯技术耗时）
- [ ] 连续 3 次相同关键词检测，结果一致
- [ ] 极简 Web 页面可正常发起检测并获得结果

**注意：此阶段不做用户系统、不做完整前端后台、不做多平台。目标是先跑通闭环并拿给 1-2 个潜在客户试用反馈。**

### Phase 2（第 4-5 周）：Web 化 + 多平台扩展

**交付物：**
1. 用户注册登录系统（JWT 鉴权）
2. Vue 3 前端基础框架（检测任务创建页 + 报告列表页）
3. 豆包平台适配器
4. Kimi 平台适配器
5. 竞品对比功能
6. 冷却期机制实现

### Phase 3（第 6-8 周）：产品化上线

**交付物：**
1. 完整前端用户后台（报告详情页、用户中心、用量统计）
2. 报告验证查询系统（prismamate.com/verify）
3. Celery 异步任务队列全量接入
4. 平台冒烟测试定时任务
5. 部署上线（Docker + Nginx + HTTPS）

### Phase 4（未来迭代，不在此次 MVP 范围）：
- 区块链存证（预留数据库字段，暂不实现）
- 开放 API 接口
- 周期性自动监测
- 更多 AI 平台适配器

---

## 九、Phase 1 开发：品牌体检中心（V3.0 新增）

> **说明**：Phase 1 和 Phase 2 是对原十一阶段之后的功能扩展规划。

### Phase 1 概述

**目标**：新增体检模板管理、历史报告关联、对比引擎、前端新页面。

**新增功能点**：
1. 体检模板系统（CRUD + 复用发起）
2. 历史对比引擎（同模板自动关联）
3. 报告对比页面（新增/消失提及、位次变化）
4. 前端体检中心页面

### Phase 1 详细任务

#### 1. 后端：体检模板服务

```
任务 1.1：创建体检模板数据模型
- 创建 health_check_templates 表
- 定义 HealthCheckTemplate Pydantic 模型
- 实现模板 CRUD API

任务 1.2：模板关联与历史查询
- 新建检测任务时，支持传入 template_id
- 查询时，自动查找同模板的最新历史报告
- 设置 parent_report_id 关联

任务 1.3：历史对比引擎
- 实现 ComparisonResult 计算逻辑
- 计算：新增提及、消失提及、位次变化、提及率变化
- 存储对比结果到 report_comparisons 表
```

#### 2. 后端：报告服务增强

```
任务 2.1：报告类型区分
- reports 表新增 report_type 字段
- 支持 "health_check" 和 "geo_verification" 两种类型

任务 2.2：对比报告生成
- 新报告生成时，如存在同模板历史报告，自动生成对比数据
- 报告 JSON 增加 comparison_result 字段
```

#### 3. 前端：体检中心页面

```
任务 3.1：体检中心首页 /health-check
- 布局：新建体检按钮、我的模板入口、历史报告入口
- 最近体检趋势图（ECharts 提及率折线图）

任务 3.2：新建体检页 /health-check/new
- 复用检测表单组件
- 新增：模板名称输入框（保存为模板选项）
- 支持选择已有模板一键填充

任务 3.3：我的模板页 /health-check/templates
- 模板列表展示
- 一键发起体检
- 编辑/删除模板

任务 3.4：报告对比页 /reports/:id/comparison
- 对比概要卡片（新增/消失/位次变化数）
- 新增提及列表
- 消失提及列表
- 位次变化排行榜
- 提及率变化趋势图
```

### Phase 1 验收标准

- [ ] 用户可创建、保存、编辑、删除体检模板
- [ ] 使用模板发起体检，自动关联历史报告
- [ ] 新报告生成后，可查看与历史报告的对比
- [ ] 对比页展示完整对比数据
- [ ] 体检中心页面功能完整、交互流畅

---

## 十、Phase 2 开发：GEO 效果检测（V3.0 新增）

> **说明**：Phase 2 是 GEO 效果检测功能的详细设计，本次文档先占位。

### Phase 2 概述

**目标**：GEO 数据上传、差异计算、平台覆盖校验。

### Phase 2 详细任务（占位）

#### 1. GEO 数据上传

```
任务 1.1：文件上传接口
- POST /api/v1/verification/upload
- 支持 Excel (.xlsx, .xls) 和 CSV 文件
- 支持 JSON 格式批量上传
- 文件大小限制：10MB

任务 1.2：数据解析与校验
- 解析 Excel/CSV 数据
- 校验必填字段：brand, keyword, platform
- 支持可选字段：is_mentioned, position, mention_rate
- 返回解析结果和错误列表

任务 1.3：数据存储
- 存储到 geo_verification_data 表
- 生成 verification_id 批次ID
- 关联用户和任务
```

#### 2. 差异计算

```
任务 2.1：数据对齐
- 按 brand × keyword × platform 维度对齐
- PrismaMate 检测数据 vs GEO 机构提供数据

任务 2.2：差异计算
- 提及状态差异：PrismaMate 有 / GEO 有 = 一致
- 位次差异：位次变化值
- 提及率差异：提及率差值

任务 2.3：结论生成
- 优于承诺：PrismaMate 检测结果优于 GEO 机构承诺
- 未达承诺：PrismaMate 检测结果弱于 GEO 机构承诺
- 与承诺一致：两者结果一致
```

#### 3. 差异报告

```
任务 3.1：差异报告生成
- 按 brand 生成差异汇总
- 按 platform 生成差异汇总
- 生成整体验证结论

任务 3.2：差异报告展示
- 新增差异报告页面
- 展示与 GEO 机构数据的对比
- 支持导出差异报告 PDF
```

---

## 十一、MVP 启动前必须做的验证（V2.0 新增）

### 任务：DeepSeek 平台可行性测试

编写一个独立的 Playwright 脚本（不依赖项目框架），完成以下测试：

1. 未登录状态下，模拟真实用户搜索一个常见关键词
2. 连续执行 5 次搜索，每次间隔 5-10 秒随机延迟
3. 记录每次搜索的结果状态：成功获取回答 / 触发验证码 / 被拦截 / 其他异常
4. 检查返回的回答文本中是否包含品牌引用和来源 URL
5. 输出测试报告，包含：每次搜索的响应时间、是否成功、遇到的问题

**测试脚本要求**：
```python
# deepseek_feasibility_test.py
# 独立运行，不依赖项目框架
#
# ⚠️ 【重要】执行前必须手动检查 DeepSeek 实际 DOM 结构
# 检查方式：
# 1. 打开 https://chat.deepseek.com
# 2. 按 F12 打开开发者工具
# 3. 在 Elements 面板中定位输入框、发送按钮、响应内容容器等元素
# 4. 复制对应的 CSS 选择器，替换下方代码中的占位符
# 5. 如果 DeepSeek 页面结构发生变化，需要重新检查并更新选择器

import asyncio
from playwright.async_api import async_playwright
import random
import json
from datetime import datetime

# ⚠️ 【必须修改】手动检查 DeepSeek 页面后填入实际选择器
SELECTORS = {
    "input": "CHANGE_ME_INPUT_SELECTOR",       # 例如: "#chat-input" 或 ".input-box" 或 "textarea"
    "submit": "CHANGE_ME_SUBMIT_SELECTOR",      # 例如: "#submit-button" 或 "button[type='submit']"
    "response": "CHANGE_ME_RESPONSE_SELECTOR",  # 例如: ".response-content" 或 "[data-message-role='assistant']"
}

async def test_deepseek():
    """DeepSeek 平台可行性测试脚本"""
    
    results = []
    
    # ⚠️ 【必须确认】验证选择器是否已配置
    for key, value in SELECTORS.items():
        if value.startswith("CHANGE_ME_"):
            raise ValueError(f"❌ 错误：选择器 '{key}' 未配置！请先手动检查 DeepSeek 页面 DOM 结构并替换占位符。")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = await context.new_page()
        
        for i in range(5):
            try:
                # 记录开始时间
                start_time = datetime.now()
                
                # 打开 DeepSeek
                await page.goto("https://chat.deepseek.com", timeout=30000)
                
                # ⚠️ 等待输入框出现（使用配置的选择器）
                await page.wait_for_selector(SELECTORS["input"], timeout=10000)
                
                # 模拟输入关键词
                keyword = "人工智能发展趋势"
                await page.fill(SELECTORS["input"], keyword)
                
                # 点击发送（使用配置的选择器）
                await page.click(SELECTORS["submit"])
                
                # ⚠️ 等待回答完成（使用配置的选择器）
                await page.wait_for_selector(SELECTORS["response"], timeout=120000)
                
                # 获取回答内容（使用配置的选择器）
                response = await page.text_content(SELECTORS["response"])
                
                # 计算响应时间
                elapsed = (datetime.now() - start_time).total_seconds()
                
                # 检查是否包含引用
                has_citations = bool(response and ("http" in response or "[1]" in response))
                
                results.append({
                    "attempt": i + 1,
                    "status": "success",
                    "response_time": elapsed,
                    "has_citations": has_citations,
                    "response_length": len(response) if response else 0,
                    "error": None
                })
                
                print(f"✓ 第 {i+1} 次尝试成功，响应时间: {elapsed:.2f}秒")
                
            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                results.append({
                    "attempt": i + 1,
                    "status": "failed",
                    "response_time": elapsed,
                    "has_citations": False,
                    "response_length": 0,
                    "error": str(e)
                })
                print(f"✗ 第 {i+1} 次尝试失败: {str(e)}")
            
            # 随机延迟 5-10 秒
            if i < 4:
                delay = random.uniform(5, 10)
                await asyncio.sleep(delay)
        
        await browser.close()
    
    # 生成测试报告
    report = {
        "test_date": datetime.now().isoformat(),
        "platform": "DeepSeek",
        "total_attempts": 5,
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "failure_count": sum(1 for r in results if r["status"] == "failed"),
        "selectors_used": SELECTORS,  # 记录本次测试使用的选择器
        "results": results
    }
    
    # 保存报告
    with open("deepseek_feasibility_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print("\n" + "="*50)
    print("DeepSeek 可行性测试报告摘要")
    print("="*50)
    print(f"测试时间: {report['test_date']}")
    print(f"使用的选择器: {SELECTORS}")
    print(f"总尝试次数: {report['total_attempts']}")
    print(f"成功次数: {report['success_count']}")
    print(f"失败次数: {report['failure_count']}")
    print(f"成功率: {report['success_count']/report['total_attempts']*100:.1f}%")
    
    return report

if __name__ == "__main__":
    asyncio.run(test_deepseek())
```

**测试结论将决定 MVP 的技术路径**：
- 如果 5 次搜索全部成功且无验证码 → Playwright 路径可行，按原计划推进
- 如果出现验证码或拦截 → 需要优先评估官方 API 方案的可用性和结果一致性

---

## 十二、部署架构（V2.0 更新）

```
Docker Compose 编排：
├── nginx              # 反向代理 + 静态文件
├── frontend           # Vue 3 前端（Nginx 静态托管）
├── backend            # FastAPI 后端服务
├── celery_worker      # Celery 异步任务 Worker
├── celery_beat        # Celery 定时任务调度器（V2.0 新增：冒烟测试）
├── postgres           # PostgreSQL 数据库
└── redis              # Redis 缓存 + 消息队列
```

**CodeBuddy 开发指令 - 部署注意事项**：
```
【重要】部署配置：
1. 编写 docker-compose.yml，所有服务容器化
2. 前端 Nginx 配置：API 请求反向代理到 backend 服务，缓存静态资源
3. Playwright 需要在 Celery Worker 容器中安装浏览器依赖
4. Celery Worker 容器需要足够内存（每个浏览器实例约消耗 200-500MB）
   - 设置内存限制：--memory=2g
   - 实现浏览器上下文池复用
5. 生产环境务必配置 HTTPS（Let's Encrypt 自动续签）
6. 数据库和 Redis 需要持久化存储（挂载 Volume）

【V2.0 浏览器资源管理】：
- 单 Worker 内存限制 2GB
- 实现浏览器上下文池（复用而非每次新建）
- 同一平台的任务在 Worker 中串行执行
```

---

## 十三、开发过程中的关键提醒

**CodeBuddy，在开发过程中请注意以下核心原则**：

1. **平台适配器是核心竞争力**：不要试图写一个通用的爬虫适配所有 AI 平台。每个平台必须独立适配，独立维护。当一个平台页面改版时，只需修改对应的适配器文件。

2. **反爬策略要保守**：宁可检测速度慢一些，也不要触发 AI 平台的封禁。模拟真实用户行为比追求检测速度更重要。

3. **数据完整性高于性能**：每次检测必须记录完整的原始数据（raw_response 字段），即使当前解析不出有用的信息。未来解析算法升级时，可以基于原始数据重新分析。

4. **报告的"信任感"是设计出来的**：报告的版式、措辞、数据呈现方式，都要给人"这是一份严肃的第三方检测报告"的感觉，而不是一份花哨的营销材料。

5. **MVP 只做 3 个平台**：DeepSeek、豆包、Kimi。不要贪多。这 3 个平台的检测能力做到稳定可靠后，再考虑扩展。

6. **所有代码加注释，所有配置可修改**：AI 平台的 URL、DOM 选择器、等待时间等，全部写在配置文件中，不要硬编码。

7. **V2.0 新增原则 - 双模式优先**：优先使用官方 API，Browser 模式作为降级方案。官方 API 不稳定时自动降级，不需要人工干预。

8. **V2.0 新增原则 - 监控先行**：冒烟测试和冷却期机制必须在 MVP 上线前完成。平台不可用时必须能自动检测、自动告警、自动恢复。

9. **V3.0 新增原则 - 模板可比性**：体检模板是历史对比的基础。确保同模板的报告数据格式一致，保证对比的准确性。

10. **V3.0 新增原则 - 验证独立性**：GEO 效果检测的核心是 PrismaMate 独立检测。确保检测结果不受 GEO 机构数据影响，保证第三方独立性。

---

## 十四、开发执行顺序（V3.0 更新）

**CodeBuddy，请按照以下顺序开始开发**：

**第一步**：搭建项目骨架（FastAPI 后端 + Vue 3 前端 + Docker 编排 + 数据库模型）

**第二步**（前置任务）：执行 DeepSeek 平台可行性测试，确认技术路径

**第三步**：实现 DeepSeek 平台适配器（双模式：API + Browser）

**第四步**：实现品牌提及提取规则引擎（精确匹配 + 品牌别名处理）

**第五步**：实现基础 PDF 报告生成

**第六步**：搭建极简 Web 页面（验证核心闭环）

**第七步**：搭建用户注册登录系统和检测任务创建页面

**第八步**：实现豆包和 Kimi 平台适配器

**第九步**：实现冷却期机制和冒烟测试定时任务

**第十步**：实现报告验证查询系统

**第十一步**：部署上线

**Phase 1（第 12-14 周）：品牌体检中心**
- 第十二步：体检模板系统后端（CRUD API + 关联逻辑）
- 第十三年：历史对比引擎（ComparisonResult 计算）
- 第十四步：体检中心前端页面（/health-check, /health-check/new, /health-check/templates）
- 第十五步：报告对比页面（/reports/:id/comparison）

**Phase 2（第 15-16 周）：GEO 效果检测）
- 第十六步：GEO 数据上传接口（文件解析 + 数据存储）
- 第十七步：差异计算与验证报告生成
- 第十八步：GEO 验证结果展示页面

---

## 文档修订记录

- **V1.0（初始版本）**：2026-05-13
- **V2.0（修订版本）**：2026-05-14
  - 适配器基类扩展（新增4个方法）
  - 增加冷却期机制
  - 增加平台可用性定时检测（冒烟测试）
  - raw_response 存储策略调整（90天过期）
  - 增加官方 API 与 Playwright 双模式支持
  - 增加 YAML 配置中心结构
  - 任务状态机细化（6个状态）
  - 品牌别名处理策略
  - 浏览器资源管理优化
  - 开发阶段调整为 "5+2" 模式
  - 增加 MVP 前 DeepSeek 可行性测试要求
  - 新增"风险应对策略"章节
- **V2.1（本次修订）**：2026-05-14
  - 可行性测试脚本：CSS 选择器改为占位符，增加"执行前必须手动检查 DOM 结构"的强制提示
  - deepseek.yaml 配置示例：选择器部分改为 CHANGE_ME_* 占位符，强调需手动获取
  - 数据库设计：增加数据清理机制说明（Celery Beat 每日任务或 pg_cron 清理过期 raw_response）
  - BasePlatformAdapter.is_available()：补充实现指引（轻量探测、验证码检查、搜索功能验证）
  - Phase 1 验证标准：明确"单次检测耗时 < 60 秒"为不含人为请求延迟的纯技术耗时
- **V3.0（本次重大修订）**：2026-05-15
  - **产品定位重大更新**：从单一"GEO效果检测认证平台"扩展为三大核心模块
    - AI 可见度体检（品牌体检中心）
    - GEO 效果检测（交付验证中心）
    - PrismaMate 报告验真（已完成）
  - **新增体检模板系统**：模板 CRUD、复用发起、历史关联
  - **新增历史对比引擎**：同模板报告自动关联、ComparisonResult 数据结构
  - **新增数据模型**：health_check_templates 表、report_comparisons 表、geo_verification_data 表（Phase 2）
  - **报告结构增强**：新增历史对比页、报告类型区分（体检/验证）
  - **前端页面更新**：新增 /health-check 系列页面、报告对比页面
  - **API 接口扩展**：新增模板相关 API、报告对比 API、Phase 2 GEO 验证 API
  - **开发阶段调整为 "5+2+2" 模式**：新增 Phase 1（品牌体检中心）和 Phase 2（GEO 效果检测）
  - **新增开发原则**：模板可比性、验证独立性

---

*本文档最终解释权归 PrismaMate 产品团队所有。*
