# technical-resume-optimizer

**Evidence-based resume generator & optimizer for technical roles（技术简历生成与优化 Skill）**

> AI 写简历最大的问题是**编造**：QPS、用户数、性能提升张口就来，面试一问就穿帮。
> 这个 Skill 只写**有证据的事实**——简历上的每个数字都能回溯到你的项目源码或你的明确确认。

适用于：后端 · 前端 · 全栈 · 测试 · 数据 · 算法/ML · AI Agent · DevOps/SRE · 云原生 · 安全 · 嵌入式

[![License](https://img.shields.io/badge/License-MIT-green)](#license)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-2f6fed)](https://github.com/superyeda/technical-resume-optimizer)

---

## 效果预览

从项目工作区自动生成，一个项目产出两种版式（浏览器打开 HTML，点「导出 PDF」即得简历）：

| 现代视觉版 | ATS 单列版 |
| :---: | :---: |
| <img src="docs/images/demo-resume-modern.png" height="420"> | <img src="docs/images/demo-resume-ats.png" height="420"> |

---

## 3 秒上手

**① 安装**（支持任意支持 Skills 的 Agent：Claude Code / Cursor / CodeBuddy 等）

```bash
git clone https://github.com/superyeda/technical-resume-optimizer.git \
  ~/.claude/skills/technical-resume-optimizer   # 或其他 Agent 的技能目录
```

**② 对 Agent 说一句话**

```text
根据这个项目文件夹生成简历，目标岗位是 Java 后端
```

**③ 得到四件套**

```
简历.md          Markdown 主稿
简历-ATS.html    ATS 单列版（可打印 PDF）
简历-现代.html   现代视觉版（可打印 PDF）
评估报告.md      100 分制评分 + 证据覆盖表 + 改进计划
```

生成后自动打开本地微调器，可在浏览器里实时调字号 / 间距 / 内容 / 主题色 / 证件照，再导出或写回。

---

## 特性

- **三种场景**：优化已有简历 / 从工作区生成 / 增量更新
- **100 分制评分**：内容 30 · 排版 25 · 语言 20 · ATS 15 · 影响力 10，附 P0/P1/P2 改进建议
- **ATS 友好**：单列结构、纯文本、标准栏目，可直接投递给招聘系统
- **一键导出 PDF**：两份 HTML 内置打印按钮，A4 样式
- **页数自动控制**：默认 2 页内，超页先压缩排版，再让你选「加页」或「删内容」
- **Resume IR 事实层**：所有内容先落成带来源的结构化数据再渲染，杜绝凭空发挥
- **证据可追溯**：每条 bullet 都能回溯到源码文件，无法确认的写进「待确认项」
- **本地微调器**：生成后在浏览器实时编辑，所见即所得

---

## 为什么值得用

普通 AI 写简历 = 编故事。本 Skill 的核心不是"写得好"，而是**写的东西是真的**：

- 证据分级：`用户确认` > `材料明确记录` > `可计算推导` > `待确认（禁止写入）`
- 每条项目 bullet 以「加粗总结 + 动作 + 技术 + 可验证结果」呈现，HR 3 秒看懂价值
- 团队成果明确标注「参与 / 团队 / 独立负责」，不冒认功劳

真实输出示例（来自演示项目）：

> **DDD 三域建模与全链路交付**：按 DDD 划分 activity / trade / tag 三个领域，设计并实现活动试算 → 锁单 → 支付回调 → 结算 → 组队通知完整业务链路，交付 6 个 Maven 模块、10 张数据库表、3 个 RPC 接口、4 个 Controller 与 17 个业务测试类。
>
> **责任链 + 分布式锁保障并发一致性**：实现锁单与结算责任链过滤，通过 bizId 唯一索引保证幂等，使用 Redisson RLock 分布式锁保障并发场景下的数据一致性。

完整示例见 [examples/demo-java-backend/](examples/demo-java-backend/)。

---

## 工作原理

```
用户指定工作区 + 目标岗位
      ↓
① 扫描工作区（只读，过滤依赖/构建产物/密钥）
      ↓
② 建立证据卡片（问题/动作/方案/结果/指标/来源/置信度）
      ↓
③ 集中询问 3–6 个高价值问题
      ↓
④ 构建 Resume IR（事实中间层，全部带来源）
      ↓
⑤ 按岗位画像生成 Markdown + ATS HTML + 现代 HTML
      ↓
⑥ 评估报告 + 校验脚本 + 事实回溯
```

技术栈：纯 Python（标准库，零依赖）· HTML/CSS 模板 · YAML/JSON。平台无关，不依赖任何 Agent 框架 API。

---

## 项目结构

```
technical-resume-optimizer/
├── SKILL.md               # 技能主文件：场景判定、规则、流程
├── references/            # 写作原则 / ATS 清单 / IR 规范 / 岗位画像等
├── assets/
│   ├── html-*-template.html   # 两套简历模板（现代 / ATS）
│   └── editor/                # 本地微调器（预览 + 控制面板）
├── scripts/               # 工作区扫描 / 校验 / 页数检查 / 微调器服务
└── examples/              # 完整示例产出
```

---

## 贡献

- 新增岗位画像（`references/role-profiles/`）
- 优化写作原则与模板
- 补充测试与校验脚本
- 完善示例与文档

提交前请确保：不引入编造性引导、不破坏 ATS 兼容性、示例数据使用占位信息。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

[MIT](LICENSE)
