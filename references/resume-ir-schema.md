# Resume IR Schema

```yaml
schema_version: 1
candidate:
  name: ""
  contact:
    phone: ""
    email: ""
    location: ""
  target_roles: []
  target_locations: []
  language: zh-CN
education: []
experiences:
  - id: exp-001
    organization: ""
    role: ""
    start: YYYY-MM
    end: YYYY-MM|至今
    tech_stack: []
    bullets:
      - id: bullet-001
        situation: ""
        action: ""
        highlight: "句首加粗总结短语（≤12 字），仅项目/经历 bullet 使用，如「DDD 三域建模与全链路交付」"
        technology: []
        result: ""
        metrics: []
        ownership: individual|lead|team|unclear
        evidence:
          - source_file: ""
            locator: "页码/标题/行号"
            quote: ""
        confidence: high|medium|low
projects: []
skills:
  languages: []
  frameworks: []
  databases_middleware: []
  cloud_engineering: []
  ai_domain: []
source_snapshot: []
open_questions: []
conflicts: []
versions:
  current: v1
  parent: null
  generated_at: ""
```

所有可以影响最终简历事实的字段都要关联 `evidence`。将被 OCR 读取且不确定的字段放入 `open_questions`，不得直接生成最终断言。