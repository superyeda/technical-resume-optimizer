---
name: technical-resume-optimizer
description: This skill should be used when a user asks to score, review, improve, create, tailor, render, or incrementally update a resume for any technical role. Supports PDF, Markdown, DOCX, and PNG resumes; can derive evidence from a user-specified project workspace; produces ATS-safe Markdown and HTML resumes plus an assessment report.
agent_created: true
---

# 技术岗简历优化与生成

## 目标

为后端、前端、全栈、移动端、测试、数据、算法/机器学习、AI Agent、DevOps/SRE、云原生、安全、嵌入式等技术岗位，基于**可追溯的真实证据**完成简历评分、优化、生成、JD 定制或增量更新。

始终交付：

1. `姓名-目标岗位-版本日期-简历.md`：主稿。
2. `姓名-目标岗位-版本日期-简历-ATS.html`：单列 ATS 版，可 A4 打印为 PDF。
3. `姓名-目标岗位-版本日期-简历-现代.html`：现代视觉版，可 A4 打印为 PDF。
4. `姓名-目标岗位-版本日期-评估报告.md`：评分、检查清单、证据缺口、变更说明。

增量更新额外交付：

5. `姓名-目标岗位-版本日期-增量变更报告.md`。
6. `resume_ir_vN.yaml` 与 `source_manifest_vN.json`。

默认在用户明确指定工作区的 `outputs/` 或用户指定交付目录创建输出。不得覆盖用户原始简历；增量更新必须保留全部历史版本。

## 强制约束

- 先建立带来源的 Resume IR，再生成最终简历；不得从原始材料直接推断、虚构或升级经历。
- 不得编造公司、岗位、项目、技术、奖项、数字、规模、个人贡献或时间；团队成果必须明确标记“参与/团队/独立负责”。
- 将量化数据分为 `用户明确提供`、`材料明确记录`、`可计算推导`、`待确认`。只有前两类可直接写入；可计算推导必须说明依据并取得确认；待确认不得写入最终简历。
- 只扫描用户明确指定的工作区。先读取文件清单并过滤依赖目录、构建产物、密钥、环境变量、二进制缓存与无关日志；不修改源文件。
- 遇到姓名、联系方式、目标岗位、工作区路径、日期/公司冲突、个人贡献归属或关键指标不清时，先集中询问 3–6 个高价值问题，再生成。
- 无 JD 时允许进行通用技术岗评分；有 JD 时必须额外输出关键词覆盖前后对比和差距矩阵。
- 生成后必须执行事实回溯、ATS 检查与 HTML 打印检查。将无法确认项列入报告，不应悄悄省略或补写。

## 场景判定

### 场景 A：单份简历评分与优化

触发：用户上传或引用一份 PDF、Markdown、DOCX 或 PNG 简历，要求评分、润色、优化、导出或重写。

1. 读取文件并识别格式。PDF 提取文本并检查页数；DOCX 读取段落、标题和表格；PNG 执行 OCR 并为低置信字段建待确认项；Markdown 直接解析结构。
2. 提取个人信息、目标方向、教育、经历、项目、技能、成果、日期和版式风险，构建 Resume IR。
3. 没有 JD 时按通用技术岗 100 分模型评分；有 JD 时读取 `references/jd-tailoring.md`。
4. 对阻塞问题先提问；非阻塞项按照默认值执行并在报告中声明。
5. 读取 `references/technical-resume-principles.md`、`references/ats-and-pdf-checklist.md` 与 `references/chinese-english-typesetting.md`，生成精修稿。
6. 输出 Markdown、ATS HTML、现代 HTML 与评估报告；执行 `scripts/validate_resume_output.py` 校验。

### 场景 B：从工作区生成简历

触发：用户要求根据指定工作区、项目、实习记录、Git 仓库、文档或已有材料生成技术岗简历。

1. 先确认工作区路径；未给出目标岗位时使用通用技术岗默认值，未给出城市/页数/模板时采用中文、2 页上限、双 HTML 模板并在交付中声明。
2. 运行 `scripts/scan_workspace_manifest.py` 生成只读清单；优先读取旧简历、README、设计文档、复盘、项目文档、论文、奖项与 Git 元数据。
3. 按项目/组织/时间建立证据卡片。每张卡片至少包含：问题、个人动作、技术方案、结果、指标、ownership、来源文件、原文摘录、置信度。
4. 识别重复项目、同一成果不同版本、团队与个人成果冲突、无证据的技术关键词；将冲突列入 `open_questions`。
5. 确认问题后，按目标岗位选择相应 `references/role-profiles/` 指南，构建 Resume IR 并生成交付物。
6. 在评估报告中增加“证据覆盖表”和“未采用材料清单”。

### 场景 C：增量更新简历

触发：用户已有简历或 Resume IR，后续完成新实习、新项目、新需求、技术优化或获得新成果，需要基于工作区更新。

1. 定位最近版本的 `resume_ir_vN.yaml` 与 `source_manifest_vN.json`；若不存在，先从上一版简历建立初始 IR。
2. 运行 `scripts/scan_workspace_manifest.py`，比较来源快照、文件内容摘要、修改时间和可用 Git diff。
3. 将新增/修改/删除证据映射到既有经历或项目。仅更新被新证据支持的章节；没有新证据时不得改变措辞强度、数字或个人归属。
4. 对日期、指标、成果归属或旧新材料矛盾先提问。
5. 输出新版本简历、评估报告、IR、来源清单及增量变更报告；变更报告必须按“新增/修改/删除/待确认/未采用”分类并附来源。

## Resume IR 规范

将 Resume IR 作为后续更新的唯一事实中间层。使用 YAML，至少包含以下字段：

```yaml
schema_version: 1
candidate:
  name: ""
  contact: {}
  target_roles: []
  target_locations: []
  language: zh-CN
education: []
experiences: []
projects: []
skills: {}
source_snapshot: []
open_questions: []
conflicts: []
versions:
  current: ""
  parent: ""
```

在每条经历和项目 bullet 中保留：`situation`、`action`、`technology`、`result`、`metrics`、`ownership`、`evidence`、`confidence`、`highlight`（句首加粗总结短语，仅项目/经历 bullet 使用）。详见 `references/resume-ir-schema.md`。

## 写作、评分与 ATS 规则

- 将 bullet 写成“强动作动词 + 个人动作 + 技术/方法 + 可验证结果”；不要以“负责/参与/熟悉”开头，除非个人贡献确实只能表述为参与。
- 项目经历（及长 bullet 列表）中，每条 bullet 句首加一个简练加粗总结短语（如 `**DDD 三域建模与全链路交付**：正文…`），格式为“加粗总结：动作 + 技术 + 结果”。总结短语控制在 12 字以内、以名词短语或短动词短语为主，起到快速扫描作用，不得重复正文细节或引入新事实；同一项目内各条总结短语保持句式平行。Markdown 与两份 HTML 中同步实现（HTML 用 `<strong>`），Resume IR 中对应字段为 bullet 的 `highlight`。
- 按岗位相关性排列栏目与项目；同一栏目按倒序时间线排列。初级岗位优先 1 页，经历充足时最多 2 页。
- 将技术技能按类别分组，并只保留可解释、与岗位相关的技术；不要堆砌关键词或教程级技术。
- 量化优先覆盖吞吐/数据量、性能、稳定性、成本、效率、质量、交付范围和业务影响。没有数字时写可验证的范围、服务链路、版本或覆盖对象。
- 使用标准栏目名、单列 ATS 结构、可复制文本、清晰标题和倒序时间线。避免关键文字放在图片、文本框、复杂表格或多栏布局中。
- 评分采用 100 分：内容质量 30、结构与排版 25、语言与语法 20、ATS 优化 15、影响力与印象 10。报告必须包含总分/等级、五维明细、Top 3 优势、优先级改进项、Before→After、5 步行动计划与回检分数。

## 资源选择

- 技术岗写作与事实边界：`references/technical-resume-principles.md`
- ATS、PDF 与 HTML 回检：`references/ats-and-pdf-checklist.md`
- 指标和证据分级：`references/metric-and-evidence-guide.md`
- JD 解析与定制：`references/jd-tailoring.md`
- 中英文混排：`references/chinese-english-typesetting.md`
- IR 字段：`references/resume-ir-schema.md`
- 增量协议：`references/incremental-update-protocol.md`
- 岗位重点：按需读取 `references/role-profiles/*.md`
- 模板：`assets/html-ats-single-column-template.html`、`assets/html-modern-template.html`、`assets/css/print-a4.css`

## 最终交付前检查

1. 运行 `scripts/validate_resume_output.py <delivery-directory>`。
2. 回溯每个数字、公司、项目、岗位、时间和技术关键词到 Resume IR 或用户明确确认内容。
3. 检查 Markdown、两份 HTML、评估报告、IR 和来源清单是否齐全；增量场景再检查变更报告。
4. 检查 HTML 的 A4 打印分页、截断、乱码、文本可复制性与 ATS 单列结构。
5. 在最终回复中说明：输出文件、基线/回检分数、待确认事实、默认值和下一步可执行动作。
