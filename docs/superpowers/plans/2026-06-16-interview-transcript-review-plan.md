# Interview Transcript Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `interview-transcript-review` skill for turning real mock-interview transcript Markdown into interview-review documents in Markdown, HTML, or both.

**Architecture:** Add one self-contained skill directory under `skills/interview-transcript-review/`. Keep the main workflow in `SKILL.md`, put reusable output templates in `assets/`, and store trigger/behavior eval prompts in `evals/`. Update repository docs only after the skill files are in place and validated.

**Tech Stack:** Markdown skill instructions, optional HTML artifact output instructions, JSON eval prompt file, existing repository README/AGENTS conventions.

---

## File Structure

- Create: `skills/interview-transcript-review/SKILL.md`
  - Main skill metadata and workflow instructions.
  - Uses English frontmatter for triggering and Chinese body instructions.
  - Covers input intake, raw transcript readability cleanup, review generation, Markdown/HTML output selection, scoring, answer directions, shortcoming cards, and quality self-check.
- Create: `skills/interview-transcript-review/assets/review-template.md`
  - Markdown review template that mirrors the approved spec.
  - Used when the user asks for Markdown or Markdown + HTML.
- Create: `skills/interview-transcript-review/assets/review-template.html`
  - HTML review template with visually structured sections, score tags, answer-direction blocks, and shortcoming cards.
  - Used when the user asks for HTML or Markdown + HTML.
- Create: `skills/interview-transcript-review/evals/trigger-eval.json`
  - Prompt-only evals for trigger and behavior coverage.
- Modify: `README.md`
  - Add `interview-transcript-review` to fork-specific skills and current inventory.
- Modify: `README.zh-CN.md`
  - Add the same skill entry in Chinese.
- Modify: `AGENTS.md`
  - Add the generated available-skill entry only if `npx openskills sync` is available; otherwise update manually in the existing generated section with a note in final verification.

---

### Task 1: Create Skill Skeleton

**Files:**
- Create: `skills/interview-transcript-review/SKILL.md`
- Create: `skills/interview-transcript-review/assets/review-template.md`
- Create: `skills/interview-transcript-review/assets/review-template.html`
- Create: `skills/interview-transcript-review/evals/trigger-eval.json`

- [x] **Step 1: Create directories**

Run:

```bash
mkdir -p skills/interview-transcript-review/assets skills/interview-transcript-review/evals
```

Expected: directories exist.

- [x] **Step 2: Add placeholder-free `SKILL.md` scaffold**

Create `skills/interview-transcript-review/SKILL.md` with:

```markdown
---
name: interview-transcript-review
description: Use when the user wants to turn a real mock-interview video transcript or Markdown interview transcript into a post-interview review, retrospective, scoring report, shortcoming cards, answer improvement notes, or interview复盘 document. Trigger for 面试复盘, 模拟面试转写稿, interview transcript review, 面试视频转文稿复盘, 技术面复盘, HR面复盘, JD/resume-aware interview review.
---

---

**名称（中文）**：面试转写稿复盘
**描述（中文）**：将真实模拟面试视频转写后的 Markdown 文稿整理为面试后复盘材料，支持 Markdown、HTML 或两者同时输出。

---

# 面试转写稿复盘

## 何时使用

- 用户提供或引用真实模拟面试视频转写稿，要求生成面试后复盘。
- 用户提到“面试复盘”“模拟面试转写稿”“面试视频转文稿复盘”“技术面复盘”“HR 面复盘”等。
- 用户希望基于转写稿分析回答质量、面试官考点、短板、评分、补充答案或下一步训练计划。

## 何时不使用

- 用户只是要学习课程/直播转写稿精炼：使用 `transcript-refine`。
- 用户要进行一问一答式模拟面试：使用 `project-mock-interview`。
- 用户只是要维护项目设计文档、变更日志或简历面试素材：不使用本 skill。

## 启动询问

处理前先问用户两类信息，但不要把建议材料作为硬门槛：

1. **输出格式**：请用户选择 `仅 Markdown`、`仅 HTML`、或 `Markdown + HTML`，不设置默认值。
2. **建议补充上下文**：提醒用户可提供简历、岗位 JD、面试类型、面试轮次、目标岗位、面试时间/批次。若用户不提供，继续流程，并在复盘中标注分析限制。

## 输入材料

| 材料 | 是否必需 | 作用 |
| --- | --- | --- |
| 面试转写稿 `.md` | 必需 | 复盘主输入，必须来自真实模拟面试视频或真实模拟面试过程 |
| 简历 | 建议 | 判断项目经验、技术背景、职责边界和可追溯素材 |
| 岗位 JD | 建议 | 判断岗位关注点、级别预期和复盘优先级 |
| 面试基础信息 | 建议 | 判断面试类型、轮次、目标岗位和归档命名 |

## 原稿可读化清洗

如果原稿不可读，可以直接在原文件上做可读化清洗。清洗只允许：

- 整理自然说话段落。
- 调整标点、换行、断句。
- 修正识别错字。
- 修正拼写、英文缩写、技术术语、专有名词。
- 统一术语写法。
- 保留原始问答顺序和原意。

禁止：

- 不把原回答改写成标准答案。
- 不强制拆成“第 N 题 / 面试官 / 候选人 / 追问”结构。
- 不在原稿中加入评分、短板、补充答案或复盘结论。
- 不删除会影响复盘判断的错误表达、犹豫、遗漏和逻辑断裂。

## 复盘输出规则

复盘文件必须新建，不能覆盖原稿。

- Markdown 文件命名：`<原文件名>-复盘.md`
- HTML 文件命名：`<原文件名>-复盘.html`
- 用户指定输出路径或文件名时，优先使用用户指定。
- 用户要求两者都要时，同时创建 `.md` 和 `.html`。

## 每题固定字段

每道题都必须包含：

- **原题**：面试官原始问题或等价整理。
- **面试官考点**：说明这道题考察什么能力或风险点，不要复述题干。
- **回答评分**：`通过` / `勉强通过` / `不通过`。
- **项目经验方向**：有经验就写清真实项目背景、动作、结果和边界；没有就写“本次面试未体现对应项目经验”或“过往项目中未直接涉及”。
- **技术扩展方向**：无论是否有项目经验，都补充技术知识、原理机制、设计方案、优缺点、适用场景和追问方向。

## 评分标准

| 档次 | 含义 | 判定标准 |
| --- | --- | --- |
| 通过 | 当前回答基本能支撑面试官继续往下聊 | 回答切题，有清晰主线，关键事实可信，能讲出必要的背景、做法、结果或取舍 |
| 勉强通过 | 方向大体对，但存在明显扣分点 | 有部分有效信息，但结构松散、关键细节不足、指标/取舍/边界不清，容易被追问打穿 |
| 不通过 | 当前回答会显著损害面试评价 | 答非所问、概念错误、项目事实缺失、逻辑断裂、无法说明个人贡献，或暴露严重知识短板 |

评分维度：

- **切题性**：是否回答面试官真正问的问题。
- **结构性**：是否有背景、动作、结果、取舍或边界。
- **可信度**：项目经验方向是否有真实项目细节、指标、角色边界或落地证据；技术扩展方向是否有清晰定义、机制、边界和推理依据。
- **技术深度**：是否讲清原理、难点、方案比较或故障处理。
- **表达稳定性**：是否能让面试官听懂并愿意继续追问。

## 问题分层

### 答得还可以的问题

只做记忆唤醒，不生成长篇标准答案。记录：

- 原题。
- 面试官考点。
- 回答评分与一句依据。
- 项目经验方向。
- 技术扩展方向，控制在 1 到 3 条要点。
- 回答记忆点，控制在 2 到 5 条。
- 一句复习提示。

### 答得不好的问题

必须补充：

- 原题。
- 面试官考点。
- 回答评分。
- 项目经验方向。
- 技术扩展方向。
- 原回答问题。
- 简单精炼版答案。
- 详细面试版答案。

详细面试版答案要能直接口头复述；不要把不存在的项目经历说成做过，但可以写“技术上可以如何设计”“我学习后对这个问题的认识”“如果项目要补齐会怎么做”。

## 短板卡片

每个短板使用固定字段：

- **面试暴露**：来自哪一题、哪段回答或哪类表达问题。
- **问题本质**：知识缺口、表达结构差、缺指标、缺 trade-off、缺故障复盘、可信细节不足等。
- **影响等级**：高 / 中 / 低。
- **对应评分影响**：导致哪些题从“通过”降为“勉强通过”或“不通过”。
- **需要补齐的知识**：后续应补的具体知识或材料。
- **下次回答抓手**：下一次回答时可直接使用的结构。
- **训练题**：1 到 3 道针对性训练题。

## 输出结构

按需读取 `assets/review-template.md` 或 `assets/review-template.html`。HTML 与 Markdown 内容结构一致，只增强视觉层级。

## 质量自检

- [ ] 是否先询问输出格式，且没有设置默认值？
- [ ] 是否提醒用户可补充简历、岗位 JD 和面试基础信息？
- [ ] 缺少建议材料时，是否继续流程并标注分析限制？
- [ ] 原稿可读化是否只改段落、断句、标点、错字、拼写和术语？
- [ ] 复盘是否写入新文件，未覆盖原稿？
- [ ] 每道题是否都有面试官考点、评分、项目经验方向和技术扩展方向？
- [ ] 答得还可以的问题是否只做记忆唤醒式精炼？
- [ ] 答得不好的问题是否包含简单精炼版答案和详细面试版答案？
- [ ] 是否没有生成“可复用回答素材”章节？
- [ ] 短板是否使用卡片结构记录并扩展？
```

- [x] **Step 3: Verify scaffold has required metadata**

Run:

```bash
sed -n '1,80p' skills/interview-transcript-review/SKILL.md
```

Expected:
- YAML frontmatter has `name: interview-transcript-review`.
- YAML description is English.
- Chinese metadata block exists immediately after frontmatter.
- Body has `启动询问`, `原稿可读化清洗`, `每题固定字段`, `评分标准`, `短板卡片`, `质量自检`.

---

### Task 2: Add Markdown And HTML Templates

**Files:**
- Create: `skills/interview-transcript-review/assets/review-template.md`
- Create: `skills/interview-transcript-review/assets/review-template.html`

- [x] **Step 1: Create Markdown template**

Create `skills/interview-transcript-review/assets/review-template.md` with:

```markdown
# 面试复盘：<主题/日期>

## 重点

- **总体表现**：...
- **主要短板**：...
- **优先补齐**：...
- **下次训练重点**：...

## 一、面试概览

- **面试主题**：...
- **目标岗位**：...
- **岗位 JD 匹配重点**：...
- **面试类型**：技术面 / HR 面 / 项目深挖 / 系统设计 / 其他
- **面试轮次**：技术一面 / 技术二面 / 终面 / HR 面 / 其他
- **回答方向要求**：每题均从项目经验方向和技术扩展方向复盘
- **总体评分**：通过 / 勉强通过 / 不通过
- **分析限制**：若缺少简历、JD 或面试基础信息，在这里说明限制
- **整体判断**：...

## 二、答得还可以的问题

### 2.1 <问题标题>

- **原题**：...
- **面试官考点**：...
- **回答评分**：通过 / 勉强通过
- **项目经验方向**：...
- **技术扩展方向**：...
- **回答记忆点**：
  - ...
  - ...
- **复习提示**：...

## 三、答得不好的问题

### 3.1 <问题标题>

- **原题**：...
- **面试官考点**：...
- **回答评分**：不通过
- **项目经验方向**：...
- **技术扩展方向**：...
- **原回答问题**：
  - ...
- **简单精炼版答案**：
  - ...
  - ...
- **详细面试版答案**：

  ...

## 四、短板卡片

### 短板 1：<短板名称>

- **面试暴露**：...
- **问题本质**：...
- **影响等级**：高 / 中 / 低
- **对应评分影响**：...
- **需要补齐的知识**：
  - ...
- **下次回答抓手**：
  - ...
- **训练题**：
  - ...

## 五、下一步复习计划

- **今天先补**：...
- **下次模拟前必须准备**：...
- **后续训练题**：...
```

- [x] **Step 2: Create HTML template**

Create `skills/interview-transcript-review/assets/review-template.html` with:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>面试复盘：&lt;主题/日期&gt;</title>
  <style>
    :root {
      --bg: #f7f7f4;
      --panel: #ffffff;
      --text: #222222;
      --muted: #666666;
      --line: #d8d8d2;
      --good: #19744a;
      --mid: #9a6700;
      --bad: #b42318;
      --accent: #2458a6;
    }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.65;
    }
    main {
      max-width: 1080px;
      margin: 0 auto;
      padding: 40px 24px 64px;
    }
    h1, h2, h3 {
      line-height: 1.25;
      letter-spacing: 0;
    }
    h1 {
      font-size: 34px;
      margin: 0 0 24px;
    }
    h2 {
      font-size: 22px;
      margin: 36px 0 14px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 8px;
    }
    h3 {
      font-size: 18px;
      margin: 24px 0 10px;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin: 16px 0;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }
    .kv {
      border-left: 3px solid var(--accent);
      padding-left: 10px;
    }
    .muted {
      color: var(--muted);
    }
    .score {
      display: inline-block;
      border-radius: 999px;
      padding: 2px 10px;
      font-weight: 600;
      font-size: 13px;
    }
    .score.good { background: #e8f5ee; color: var(--good); }
    .score.mid { background: #fff4d8; color: var(--mid); }
    .score.bad { background: #fde8e6; color: var(--bad); }
    .direction {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfbf8;
    }
    ul {
      padding-left: 22px;
    }
  </style>
</head>
<body>
  <main>
    <h1>面试复盘：&lt;主题/日期&gt;</h1>

    <section>
      <h2>重点</h2>
      <ul>
        <li><strong>总体表现：</strong>...</li>
        <li><strong>主要短板：</strong>...</li>
        <li><strong>优先补齐：</strong>...</li>
        <li><strong>下次训练重点：</strong>...</li>
      </ul>
    </section>

    <section>
      <h2>一、面试概览</h2>
      <div class="grid">
        <div class="kv"><strong>目标岗位</strong><br>...</div>
        <div class="kv"><strong>面试类型</strong><br>...</div>
        <div class="kv"><strong>面试轮次</strong><br>...</div>
        <div class="kv"><strong>总体评分</strong><br><span class="score mid">勉强通过</span></div>
      </div>
      <p><strong>岗位 JD 匹配重点：</strong>...</p>
      <p class="muted"><strong>分析限制：</strong>若缺少简历、JD 或面试基础信息，在这里说明限制。</p>
    </section>

    <section>
      <h2>二、答得还可以的问题</h2>
      <h3>2.1 &lt;问题标题&gt; <span class="score good">通过</span></h3>
      <p><strong>原题：</strong>...</p>
      <p><strong>面试官考点：</strong>...</p>
      <div class="grid">
        <div class="direction"><strong>项目经验方向</strong><br>...</div>
        <div class="direction"><strong>技术扩展方向</strong><br>...</div>
      </div>
      <p><strong>回答记忆点：</strong></p>
      <ul><li>...</li><li>...</li></ul>
      <p><strong>复习提示：</strong>...</p>
    </section>

    <section>
      <h2>三、答得不好的问题</h2>
      <h3>3.1 &lt;问题标题&gt; <span class="score bad">不通过</span></h3>
      <p><strong>原题：</strong>...</p>
      <p><strong>面试官考点：</strong>...</p>
      <div class="grid">
        <div class="direction"><strong>项目经验方向</strong><br>...</div>
        <div class="direction"><strong>技术扩展方向</strong><br>...</div>
      </div>
      <p><strong>原回答问题：</strong></p>
      <ul><li>...</li></ul>
      <p><strong>简单精炼版答案：</strong></p>
      <ul><li>...</li><li>...</li></ul>
      <p><strong>详细面试版答案：</strong></p>
      <p>...</p>
    </section>

    <section>
      <h2>四、短板卡片</h2>
      <h3>短板 1：&lt;短板名称&gt;</h3>
      <ul>
        <li><strong>面试暴露：</strong>...</li>
        <li><strong>问题本质：</strong>...</li>
        <li><strong>影响等级：</strong>高 / 中 / 低</li>
        <li><strong>对应评分影响：</strong>...</li>
        <li><strong>需要补齐的知识：</strong>...</li>
        <li><strong>下次回答抓手：</strong>...</li>
        <li><strong>训练题：</strong>...</li>
      </ul>
    </section>

    <section>
      <h2>五、下一步复习计划</h2>
      <ul>
        <li><strong>今天先补：</strong>...</li>
        <li><strong>下次模拟前必须准备：</strong>...</li>
        <li><strong>后续训练题：</strong>...</li>
      </ul>
    </section>
  </main>
</body>
</html>
```

- [x] **Step 3: Verify templates contain required sections**

Run:

```bash
rg -n "项目经验方向|技术扩展方向|面试官考点|短板|下一步复习计划" skills/interview-transcript-review/assets
```

Expected: both template files contain the required phrases.

---

### Task 3: Add Trigger Evaluation Prompts

**Files:**
- Create: `skills/interview-transcript-review/evals/trigger-eval.json`

- [x] **Step 1: Add eval prompt file**

Create `skills/interview-transcript-review/evals/trigger-eval.json` with:

```json
{
  "skill_name": "interview-transcript-review",
  "evals": [
    {
      "id": 1,
      "prompt": "请根据 @mock-interview-transcript.md 生成面试复盘。开始前提醒我补充简历和 JD，并问我要输出 md、html 还是两个都要。",
      "expected_output": "Should trigger the skill, ask for output format, remind about optional resume/JD/interview info, and not assume a default output format.",
      "files": []
    },
    {
      "id": 2,
      "prompt": "这个模拟面试视频转出来的 md 是一整段，没有换行。先帮我把原稿整理得易读，再生成 html 复盘。",
      "expected_output": "Should trigger the skill, clean only readability issues in the source transcript, then create a separate HTML review file.",
      "files": []
    },
    {
      "id": 3,
      "prompt": "基于这次技术二面转写稿做复盘。简历和 JD 我暂时没有，直接继续，但要说明分析限制。",
      "expected_output": "Should continue without resume/JD, mark limitations, and still produce review content with project-experience and technical-expansion directions.",
      "files": []
    },
    {
      "id": 4,
      "prompt": "我想整理一份课程转写稿，方便第一次学习。",
      "expected_output": "Should not use this skill; should route to transcript-refine.",
      "files": []
    }
  ]
}
```

- [x] **Step 2: Validate JSON**

Run:

```bash
python3 -m json.tool skills/interview-transcript-review/evals/trigger-eval.json
```

Expected: JSON prints formatted output and exits with code 0.

---

### Task 4: Update Repository Documentation

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`

- [x] **Step 1: Add English README entry**

In `README.md`, add `interview-transcript-review` to the fork-specific skill table near other custom skills:

```markdown
| <next> | `interview-transcript-review` | Turns real mock-interview Markdown transcripts into interview review documents with scoring, interviewer intent, project-experience and technical-expansion directions, shortcoming cards, and Markdown/HTML output options. | [`skills/interview-transcript-review`](./skills/interview-transcript-review) |
```

Expected: numbering remains sequential.

- [x] **Step 2: Add Chinese README entry**

In `README.zh-CN.md`, add:

```markdown
| <next> | `interview-transcript-review` | 将真实模拟面试 Markdown 转写稿整理为面试复盘文档，覆盖评分、面试官考点、项目经验方向、技术扩展方向、短板卡片，并支持 Markdown/HTML 输出。 | [`skills/interview-transcript-review`](./skills/interview-transcript-review) |
```

Expected: numbering remains sequential.

- [x] **Step 3: Verify README references**

Run:

```bash
rg -n "interview-transcript-review" README.md README.zh-CN.md
```

Expected: both README files contain the skill name and path.

---

### Task 5: Update AGENTS Skill Registry

**Files:**
- Modify: `AGENTS.md`

- [x] **Step 1: Try OpenSkills sync**

Run:

```bash
npx openskills sync
```

Expected if network/cache available: command completes and `AGENTS.md` includes `interview-transcript-review`.

If it fails with npm network resolution, do not retry indefinitely.

- [x] **Step 2: Manual fallback if sync fails**

If `npx openskills sync` fails, add this skill entry inside the existing `<available_skills>` block in `AGENTS.md`:

```xml
<skill>
<name>interview-transcript-review</name>
<description>Use when the user wants to turn a real mock-interview video transcript or Markdown interview transcript into a post-interview review, retrospective, scoring report, shortcoming cards, answer improvement notes, or interview复盘 document. Trigger for 面试复盘, 模拟面试转写稿, interview transcript review, 面试视频转文稿复盘, 技术面复盘, HR面复盘, JD/resume-aware interview review.</description>
<location>global</location>
</skill>
```

- [x] **Step 3: Verify AGENTS entry**

Run:

```bash
rg -n "interview-transcript-review" AGENTS.md
```

Expected: one entry exists.

---

### Task 6: Validate Skill Against Spec

**Files:**
- Read: `docs/superpowers/specs/2026-06-15-interview-transcript-review-design.md`
- Read: `skills/interview-transcript-review/SKILL.md`
- Read: `skills/interview-transcript-review/assets/review-template.md`
- Read: `skills/interview-transcript-review/assets/review-template.html`
- Read: `skills/interview-transcript-review/evals/trigger-eval.json`

- [x] **Step 1: Check required phrases**

Run:

```bash
rg -n "输出格式|不设置默认值|简历|岗位 JD|面试基础信息|可读化清洗|项目经验方向|技术扩展方向|面试官考点|通过|勉强通过|不通过|短板卡片|Markdown \\+ HTML" skills/interview-transcript-review
```

Expected: required concepts appear in `SKILL.md` and templates where appropriate.

- [x] **Step 2: Check no forbidden reusable-material section**

Run:

```bash
rg -n "可复用回答素材" skills/interview-transcript-review
```

Expected: either no matches, or only a prohibition in `SKILL.md`.

- [x] **Step 3: Validate JSON eval file**

Run:

```bash
python3 -m json.tool skills/interview-transcript-review/evals/trigger-eval.json >/tmp/interview-transcript-review-eval.json
```

Expected: command exits 0.

- [x] **Step 4: Run Markdown whitespace check**

Run:

```bash
git diff --check -- skills/interview-transcript-review README.md README.zh-CN.md AGENTS.md
```

Expected: no output and exit code 0.

- [x] **Step 5: Inspect changed files**

Run:

```bash
git status --short
```

Expected:
- `skills/interview-transcript-review/` is added.
- README files and AGENTS are modified if documentation/registry tasks were completed.
- The spec and plan files may remain untracked or modified depending on whether the user wants to commit them separately.

---

### Task 7: Commit Implementation

**Files:**
- Stage only files implemented for this skill unless the user explicitly requests including spec/plan docs.

- [ ] **Step 1: Stage implementation files**

Run:

```bash
git add skills/interview-transcript-review README.md README.zh-CN.md AGENTS.md
```

Expected: implementation and documentation files are staged.

- [ ] **Step 2: Confirm spec/plan exclusion or inclusion**

Run:

```bash
git diff --name-only --cached
```

Expected: only intended implementation files are staged. If the user wants spec/plan committed, stage:

```bash
git add docs/superpowers/specs/2026-06-15-interview-transcript-review-design.md docs/superpowers/plans/2026-06-16-interview-transcript-review-plan.md
```

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "feat(skills): 新增面试转写稿复盘技能" -m "- 新增 interview-transcript-review 技能，覆盖面试转写稿清洗与复盘流程" -m "- 增加 Markdown 和 HTML 复盘模板，支持评分、考点、双回答方向与短板卡片" -m "- 补充触发评估用例并更新中英文 README 与技能登记"
```

Expected: commit succeeds.

If `.git/index.lock` permission blocks staging or commit, rerun the same git command with approved elevated permissions.

---

## Self-Review

- **Spec coverage:** The plan covers input context reminders, non-blocking missing resume/JD/basic info, output format inquiry without default, raw transcript readability cleanup, new review files, Markdown/HTML/both outputs, per-question interviewer intent, scoring, project-experience and technical-expansion directions, answer layering, shortcoming cards, docs, registry, evals, and verification.
- **Placeholder scan:** The implementation plan uses concrete file paths, commands, templates, and expected results. Template placeholders such as `<问题标题>` are intentional output-template placeholders, not plan placeholders.
- **Type consistency:** The skill name is consistently `interview-transcript-review`; output names use `<原文件名>-复盘.md` and `<原文件名>-复盘.html`; scoring values are consistently `通过 / 勉强通过 / 不通过`.
