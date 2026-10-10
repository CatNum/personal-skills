---
name: project-structure
description: Manage a project's documentation directory and file naming under docs, including the required one-to-one pairing of PRD and technical solution files. Use when creating, checking, renaming, or reorganizing project documentation paths; currently covers only docs.
---

# 项目目录结构管理

## 范围

管理目标项目的文档目录与文件名。目前只处理项目根目录下的 `docs/`；不规定源码、配置、测试等其他目录的结构。正文写作与排版由相应文档任务决定，本 skill 负责把项目文档放在正确位置，并保持 PRD 与技术方案的文件配对。

## 目录结构

```text
<项目根目录>/
└── docs/
    ├── 00. ROADMAP/
    │   └── 00. ROADMAP.md
    ├── 01. PRD/
    │   └── 00. v0.0.1-MVP.md
    └── 02. ARCHITECTURE/
        └── 00. v0.0.1-MVP的技术方案.md
```

- 项目文档统一放在项目根目录的 `docs/` 下。`00. ROADMAP/`、`01. PRD/`、`02. ARCHITECTURE/` 三个目录名和 `00. ROADMAP/00. ROADMAP.md` 的路径固定。
- 树中的 `00. v0.0.1-MVP.md` 与 `00. v0.0.1-MVP的技术方案.md` 仅为文件名示例。PRD 文件名可按项目实际内容命名，不强制使用 `00.`、版本号或固定序号。
- 每份 PRD 都有一份技术方案，技术方案文件名由对应 PRD 的文件名去掉 `.md` 后加上 `的技术方案.md` 得到。例如 `用户登录.md` 对应 `用户登录的技术方案.md`；若 PRD 名称包含序号或版本标识，技术方案保留完全相同的主干名称。

## 操作规则

1. 确认目标项目根目录，检查现有 `docs/`、相关文件和引用，再创建或调整路径。不要把本 skill 所在仓库误当成用户目标项目。
2. 创建 PRD 时，同时创建对应路径的技术方案文件；创建技术方案时，也要保证同名主干的 PRD 文件存在。若尚无内容，配对文件只写明对应关系与待补充状态，不编造产品要求、架构、接口或技术决策。
3. 重命名或移动 PRD 时，同步调整对应技术方案的文件名及相关相对链接。整理旧文档时保留原文；目标位置已有不同内容、配对关系不明确或文件名冲突时，先列出冲突并确认处理方式，不覆盖或合并文件。
4. 检查目录时逐一核对每份 PRD 是否有按规则命名的技术方案，也检查技术方案是否有对应 PRD；报告缺失、重名与错配。用户要求修复时补齐缺失文件或更正路径；只要求审查时不修改文件。
5. 完成后给出实际目录或路径，以及 PRD 与技术方案的配对结果。涉及搬迁时检查受影响的相对链接。
