# AGENTS

## 重点

- **代码说明**：介绍具体代码字段和函数时，必须同时解释名称含义与实际作用。
- **提交规范**：Git 提交信息使用中文 conventional commit 主信息，并包含两个及以上具体分点。
- **Skill 范围**：本仓库只维护下方列出的个人 skill；上游 skill 从官方来源直接使用。

## 一、全局约束

- 介绍具体代码字段和函数时，都要解释字段和函数的含义、作用。例如：`name` 表示姓名，`getName` 表示获取姓名。

## 二、Git 提交信息规范

当用户要求创建 `git commit` 时，提交信息遵循以下规则：

- 整体使用中文。
- 主信息使用 conventional commit 风格，例如 `feat(...)`、`fix(...)`、`refactor(...)`、`docs(...)`、`test(...)`、`chore(...)`。
- 使用“主信息 + 两个及以上具体分点”的固定结构。
- 分点必须描述实际改动或目的。
- 除非用户明确要求，否则不使用英文提交信息。

示例：

```text
feat(scope): 中文主信息

- 具体改动一
- 具体改动二
```

## 三、Skill 使用说明

<skills_system priority="1">

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check whether one of the available skills below can complete the task more effectively.

How to use skills:
- Invoke: `npx openskills read <skill-name>`
- For multiple skills: `npx openskills read skill-one,skill-two`
- Resolve bundled resources from the base directory returned by the command

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in the current context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>interview-mock</name>
<description>Use for realistic one-question-at-a-time mock interviews with selectable difficulty across Go, MySQL, Redis, system design, engineering, Agent systems, project experience, or full JD-based interviews.</description>
<location>global</location>
</skill>

<skill>
<name>interview-transcript-review</name>
<description>Use when turning a real technical or HR interview transcript into a retrospective, scoring report, interviewer-intent analysis, answer improvements, and shortcoming cards.</description>
<location>global</location>
</skill>

<skill>
<name>md-formatting</name>
<description>Use when creating or updating Markdown documents that need normalized headings, a scannable key-points section, and consistent structure.</description>
<location>global</location>
</skill>

<skill>
<name>transcript-refine</name>
<description>Use when refining long video or livestream course transcripts into structured first-study reading materials or spoken-script variants.</description>
<location>global</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
