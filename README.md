# Personal Skills

## 重点

- **仓库定位**：集中维护 CatNum 自研的个人 Agent Skills，不复制或修改 Anthropic 上游 skill。
- **使用边界**：个人 skill 从本仓库安装；上游 skill 直接从官方仓库安装，两个来源独立更新。
- **当前内容**：仓库包含模拟面试、转写稿处理、文档编写与面试复盘，
  以及项目文档目录管理、AI 生成代码隐患检查与修复能力。

## 一、仓库说明

本仓库用于维护个人编写和持续迭代的 Agent Skills。每个 skill 位于 `skills/<skill-name>/`，入口文件为 `SKILL.md`，并可按需携带 `assets/`、`evals/`、`references/` 或 `project-docs/`。

Anthropic 官方 skill 不再复制到本仓库，也不在本仓库中二次修改。需要官方能力时，应直接从官方仓库安装和更新。

## 二、Skill 列表

| Skill | 含义与作用 |
|---|---|
| `interview-mock` | 分级模拟面试；按 Go、MySQL、Redis、系统设计、Agent、项目经历或 JD 等方向进行一问一答，并沉淀复习材料。 |
| `document-writing` | 按文档目的编写和整理内容；面试复盘包含评分、考点、回答改进和短板卡片。所有类型支持 Markdown，面试复盘另支持 HTML。 |
| `project-structure` | 文件与目录管理；在指定范围统一使用编号、句点和空格排序，保留固定名称，并维护 `docs/` 布局与 PRD、技术方案的一一配对。 |
| `ai-code-audit` | AI 代码隐患检查与修复；按通用分类检查性能、并发、一致性、身份、反馈及业务边界隐患，并完成最小修复和验证。 |
| `transcript-refine` | 转写稿清理与精炼；面试稿逐问逐答保留现场回答和细节，JD 使用可读的 Markdown 分区，课程稿保留完整教学知识。 |

## 三、目录结构

```text
personal-skills/
├── .claude-plugin/
│   └── marketplace.json
├── docs/
├── skills/
│   ├── interview-mock/
│   ├── document-writing/
│   ├── project-structure/
│   ├── transcript-refine/
│   └── ai-code-audit/
├── AGENTS.md
└── README.md
```

## 四、维护原则

1. 自研 skill 只在本仓库开发和提交。
2. 上游 skill 直接从官方来源安装，不复制进本仓库。
3. 个人 skill 名称避免与上游 skill 重复。
4. 修改 skill 后同步更新相应测试、参考资料和变更记录。
5. 同步到 Codex、Claude Code 等工具前，先检查预览结果和目标范围。

## 五、使用方式

本仓库提供 `.claude-plugin/marketplace.json`，用于按类别安装个人 skill。其他工具可直接扫描 `skills/` 下的各个 `SKILL.md`，或通过本地 Skills Manager 统一安装和同步。

- `engineering-skills` 提供 `ai-code-audit`，用于 AI 生成代码的隐形问题排查与修复。
- `interview-skills` 提供 `interview-mock`，用于现场模拟面试。
- `content-skills` 提供 `project-structure`、`transcript-refine` 与
  `document-writing`。面试稿清理与复盘需要安装这一组，
  单独安装面试插件不再包含复盘能力。
- `md-formatting` 已升级并改名为 `document-writing`；
  原 `interview-transcript-review` 的清理能力迁入 `transcript-refine`，
  分析与成文能力迁入 `document-writing`。
  已安装旧版本的环境需要重新同步技能列表，移除旧入口后使用新名称。

新建普通文件与文件夹的命名由 `project-structure` 统一维护，
格式为 `00. 名称`、`01. 名称`，句点后有一个半角空格。
文档编写、转写处理和面试学习资料创建时引用该规则；
用户指定的完整路径与工具要求的固定名称优先，更新旧文件时保留原路径。

### 5.1 面试材料处理

只清理时使用 `transcript-refine`，默认另存清理稿，不生成复盘。
要求清理并复盘时，先清理，再由 `document-writing` 分析和成文。
复盘默认 Markdown，明确要求时提供 HTML 或双格式；
仅格式化已有复盘时保留已有评分和结论。

### 5.2 AI 代码隐患检查与修复

`ai-code-audit` 默认定位问题后完成最小修复与必要验证；明确只审查时不修改代码。
六类通用问题为性能与依赖、状态与并发、一致性与提交语义、身份与缓存、交互与可观测性、业务与运行边界。
技能只沉淀可复用的失效机制、检查方法和修复原则，不保存具体项目故障或单次执行记录。
详情见 [技能入口](skills/ai-code-audit/SKILL.md)、[分类细则](skills/ai-code-audit/references/hidden-problems.md)。

安装或同步到目标工具后，可使用：

```text
使用 $ai-code-audit 检查这个项目中 AI 生成代码的隐形问题，确认原因后修复并验证。
```

仓库收录与工具安装是两个步骤。未安装时，可明确要求工具读取 `skills/ai-code-audit/SKILL.md` 后执行；需要全局调用时，再安装或同步到目标工具。
