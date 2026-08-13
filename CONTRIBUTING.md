# Contributing Guide ｜ 贡献指南

感谢你愿意参与 `technical-resume-optimizer` 的改进。本指南帮助你把贡献做得又快又稳。

## 你可以贡献什么

- **新增岗位画像**：`references/role-profiles/` 下按岗位补充写作重点与优先指标（如新岗位「大模型应用开发」）。
- **优化写作原则与模板**：`references/technical-resume-principles.md`、`assets/*.html`、`assets/css/print-a4.css`。
- **完善校验与扫描脚本**：`scripts/` 下补充检查项与单元测试。
- **补充示例与文档**：`examples/`、`README.md`。
- **修复 Bug / 错别字 / 排版问题**：任何你发现的问题都欢迎。

## 红线（务必遵守）

本技能的核心价值是**真实性与可追溯性**。任何贡献都不得：

- 引导生成或补造数字、规模、奖项、公司、时间等事实；
- 破坏 ATS 兼容性（单列结构、纯文本、标准栏目名）；
- 引入未经脱敏的真实个人信息示例。

## 工作流

1. Fork 本仓库，创建特性分支：`git checkout -b feat/xxx`
2. 提交改动，commit message 用语义化风格：`feat:`, `fix:`, `docs:`, `refactor:`
3. 如果改动影响生成逻辑，请运行校验脚本确认：
   ```bash
   python scripts/validate_resume_output.py <delivery-directory>
   ```
4. 发起 Pull Request，说明改动动机、影响范围与验证方式。

## 代码风格

- Python 脚本：标准库优先，零第三方依赖，兼容 Python 3.8+。
- HTML 模板：内联样式、中文可用字体回退、A4 打印样式齐全。
- 文档：中文为主，技术名词保留英文原文，中英文之间加空格。

## 问题与讨论

遇到问题请先开 Issue 描述场景与期望，再动手改代码；大改动建议先在 Issue 中讨论方案。
