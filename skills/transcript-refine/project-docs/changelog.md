# Changelog

本项目文档的所有重要变更都记录在此文件中。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

## [Unreleased]

### Added
- 新增面试清理场景，保留真实回答、犹豫、错误判断和问答顺序。
- 新增两种场景的触发、行为与交接验证用例。
- 新增逐问逐答、问题不合并、回答细节保留和 JD Markdown 可读性的行为验证用例。

### Changed
- 将课程内容规则移入 `references/course-refinement.md`，主入口只保留共同规则与路由。
- 默认另存处理稿；课程统一格式和面试分析交给 `document-writing`。
- 保留阅读稿、口播稿、证据扫描、来源引用与案例教学能力。
- 面试清理默认改为逐问逐答，每个主问题或独立追问单独成节，不再按主题合并。
- 禁止把候选人的完整回答压缩成抽象摘要，必须保留论证顺序、例子、取舍、错误和不确定表达。
- 岗位 JD 改为使用 Markdown 标题、概览表、段落和列表分区，禁止整段缩进、引用或代码块包裹。

## [1.0.0] - 2026-03-23

### Added
- 建立 `project-docs/` 统一目录，并新增三文档治理结构：
  - `project-docs/design.md`
  - `project-docs/changelog.md`
  - `project-docs/resume-interview.md`
- 补充 `transcript-refine` 设计文档，沉淀流程边界与 ADR。
- 补充面试复盘文档，沉淀 STAR、量化指标与问答提纲。

### Changed
- 将原“版本变更文档”内容迁移为版本化 changelog 管理。
- 明确 changelog 按版本号与日期记录，不再使用自由叙事时间线作为主结构。
