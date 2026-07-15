# Personal Skills

## 重点

- **仓库定位**：集中维护 CatNum 自研的个人 Agent Skills，不复制或修改 Anthropic 上游 skill。
- **使用边界**：个人 skill 从本仓库安装；上游 skill 直接从官方仓库安装，两个来源独立更新。
- **当前内容**：仓库包含模拟面试、面试复盘、Markdown 格式化和课程文稿精炼能力。

## 一、仓库说明

本仓库用于维护个人编写和持续迭代的 Agent Skills。每个 skill 位于 `skills/<skill-name>/`，入口文件为 `SKILL.md`，并可按需携带 `assets/`、`evals/`、`references/` 或 `project-docs/`。

Anthropic 官方 skill 不再复制到本仓库，也不在本仓库中二次修改。需要官方能力时，应直接从官方仓库安装和更新。

## 二、Skill 列表

| Skill | 含义与作用 |
|---|---|
| `interview-mock` | 分级模拟面试；按 Go、MySQL、Redis、系统设计、Agent、项目经历或 JD 等方向进行一问一答，并沉淀复习材料。 |
| `interview-transcript-review` | 面试转写稿复盘；将真实技术面或 HR 面转写稿整理为评分、考点分析、回答改进和短板卡片。 |
| `md-formatting` | Markdown 格式规范化；统一标题、重点区块和正文编号，提高文档可读性与重点提取效率。 |
| `transcript-refine` | 课程文稿精炼；把视频或直播课程转写稿整理为适合首次学习的阅读稿或口播稿。 |

## 三、目录结构

```text
personal-skills/
├── .claude-plugin/
│   └── marketplace.json
├── docs/
├── skills/
│   ├── interview-mock/
│   ├── interview-transcript-review/
│   ├── md-formatting/
│   └── transcript-refine/
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
