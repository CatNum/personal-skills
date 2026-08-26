---
name: weknora-pr-description
description: Draft or calibrate pull-request titles, descriptions, testing evidence, checklists, and bilingual PR Markdown for the WeKnora repository. Use only when the current repository or explicit task is WeKnora; do not use for other projects.
---

# WeKnora PR 信息编写

## 目标

基于 **WeKnora 整个分支** 的可验证变更，生成或校准真实、可复制的 PR 信息。输出应帮助 Reviewer 快速理解变更边界、验证证据与尚未执行的检查，不得把单个 commit、未运行命令或无关失败包装成整个 PR 的结论。

## 使用边界

- 仅用于 WeKnora 仓库，或用户明确说明目标 PR 属于 WeKnora。
- 用于 PR title、Description、Type of Change、Related Issue、Testing、Checklist、Screenshots / Recordings 的生成、改写、补全或校验。
- 不用于实现代码、修复测试、创建 Git 分支、提交 commit、推送远端或创建 PR；这些动作需要用户单独请求。
- 用户只要求某一部分时，只修改或输出该部分；不要擅自重写其他已确认内容。

## 一、先确定 PR 范围

在写 PR 内容前，先收集分支范围的证据。默认基线为 `origin/main`；若用户指定其他基线，以用户指定为准。

```bash
git status --short --branch
git log --oneline origin/main..HEAD
git diff --name-status origin/main...HEAD
git diff --stat origin/main...HEAD
```

- 标题和 Description 必须概括 `origin/main...HEAD` 的整体变化，不能只复用最后一个 commit 的标题。
- 同一主题在多个 commit 中分层实现时，按业务行为归纳，而非按文件列表或 commit 顺序罗列。
- PR 描述按 diff 中真实存在的业务行为、配置变化、运行时影响、前端表现与测试证据归纳；不要把元数据、配置、接口、运行时行为或测试覆盖混为同一类能力。

## 二、PR 标题

- 先查看近期仓库历史的标题风格，再选择英文 Conventional Commit 标题，例如 `fix(models): ...`、`feat(chat): ...`。
- 标题要同时覆盖分支中独立且重要的行为。例如“thinking 覆盖逻辑修复”与“DeepSeek / 智谱模型配置维护”同时存在时，标题必须表达两者，不能只写最后一个 Chat 适配改动。
- 用户要求双语时，按区块成对输出：先给英文 PR 标题，再给语义等价的中文 PR 标题；随后才进入英文 Description 和中文 Description。除非用户明确要求，不要把标题翻译夹在完整英文 PR 内容与完整中文 PR 内容之间。
- 不凭空添加 Issue 编号、版本号、性能指标或破坏性变更。

## 三、固定 PR 模板

WeKnora PR 信息使用以下**固定模板**。生成或更新时不得增删、改名或调换区块顺序；只能将占位内容替换为经分支 diff、已运行命令或用户明确提供的信息。

双语输出固定为四个连续大块：**英文 PR 标题 → 中文 PR 标题 → 完整英文 PR 描述 → `---` 横线 → 完整中文 PR 描述**。这里的“完整描述”分别包含 Description、Type of Change、Related Issue、Testing、Checklist 与 Screenshots / Recordings；不要把这些描述子区块改成交替的英文一段、中文一段。英文描述结束后必须使用单独一行 `---` 分隔，再开始中文描述。

```md
## PR Title (English)

<!-- Title should follow Conventional Commits, e.g. `feat: ...`, `fix: ...`, `docs: ...` -->
<!-- Follow the repository's English Conventional Commit style. -->
<English PR title>

## PR 标题（中文）

<对应中文 PR 标题>

<!-- English PR description block begins. -->

## Description

<!-- Briefly describe the purpose and changes of this PR. -->
<English description based on the whole branch>

## Type of Change

<!-- Check applicable items. -->
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 💥 Breaking change
- [ ] 📚 Documentation update
- [ ] 🎨 Refactor
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test
- [ ] 🔧 Configuration / Build / CI

## Related Issue

<!-- If this PR resolves an issue, use "Fixes #123" or "Closes #123". -->
Fixes #

## Testing

<!-- Describe how these changes were tested. Include reproduction or verification steps. -->
<!--
For a focused change, run checks scoped to the files/packages you changed.
See the Contributing section in README.md for examples. If a full-repository
check is blocked by unrelated baseline or environment failures, record the
exact command and failure here.
-->
<!-- Record only checks actually run for this PR. -->
<English verification evidence>

## Checklist

- [ ] `git diff --check origin/main...HEAD` passes
- [ ] Changed source files are formatted
- [ ] Targeted tests for the changed packages/components pass
- [ ] Diff-scoped lint passes where applicable (for Go: `golangci-lint run --new-from-rev=origin/main ./...`)
- [ ] Full-repository checks were run, or any unrelated/environment-dependent failures are documented above
- [ ] Self-reviewed the code
- [ ] Added/updated tests covering the change
- [ ] Updated related documentation (README, `docs/`, Swagger annotations, etc.)
- [ ] Breaking changes are clearly called out in the description above

## Screenshots / Recordings

<!-- Required for user-visible UI changes -->
<!-- Do not claim a screenshot exists unless it was provided. -->
<English screenshot or TODO status>

---

<!-- Chinese PR description block begins. -->

## 描述

<对应中文描述，覆盖相同的分支范围>

## 变更类型

<!-- 勾选对应的中文变更类型。 -->
- [ ] 🐛 缺陷修复
- [ ] ✨ 新功能
- [ ] 💥 破坏性变更
- [ ] 📚 文档更新
- [ ] 🎨 重构
- [ ] ⚡ 性能优化
- [ ] 🧪 测试
- [ ] 🔧 配置 / 构建 / CI

## 关联 Issue

<!-- 若关联 Issue，使用与英文区块一致的编号；没有则写“不适用”。 -->
不适用

## 测试

<!-- 仅记录本 PR 实际执行过的检查。 -->
<对应中文验证证据>

## 检查清单

- [ ] `git diff --check origin/main...HEAD` 通过
- [ ] 已格式化变更的源文件
- [ ] 已通过变更包/组件的定向测试
- [ ] 已在适用范围内通过 Diff 限定的 lint（Go：`golangci-lint run --new-from-rev=origin/main ./...`）
- [ ] 已运行全仓检查，或已在上文记录无关/依赖环境的失败原因
- [ ] 已自行审查代码
- [ ] 已新增或更新覆盖本次改动的测试
- [ ] 已更新相关文档（README、`docs/`、Swagger 注解等）
- [ ] 已在上方描述中清晰标明破坏性变更

## 截图 / 录屏

<!-- 界面改动必须提供实际截图；未提供时保留准确 TODO。 -->
<对应中文截图或 TODO 状态>
```

固定的是**四个大块、子区块顺序和 checklist 基线**，不是虚假的状态：只勾选已经验证的事实。若证据要求调整 checklist 文案，保留原条目的语义，并在英文描述块与中文描述块中分别同步改写，随后再勾选。

## 四、确定定向验证

定向验证不是固定命令清单，而是根据本次 PR 的实际 diff 推导。Testing 区块只记录已经执行并得到结果的命令；skill 不得预设某个 Provider、Chat 包、前端测试文件或 lint 命令必然适用。

按以下顺序确定验证范围：

1. **盘点变更边界**：查看变更文件、调用路径、相邻测试和模块配置，明确本次改动影响的是后端包、前端组件/工具、i18n、接口、Compose、文档或其他边界。
2. **寻找最近的现有验证入口**：优先使用同目录或同模块已有的测试文件、`package.json` scripts、Makefile、CI 配置、贡献文档与项目现有检查命令；不要凭记忆复制其他 PR 的测试命令。
3. **选择最小充分验证集**：验证应覆盖本次新增或修改的行为、关键异常路径，以及前后端/配置边界中实际受影响的部分。多个独立模块变更时，分别选择各自的定向验证。
4. **按语言与构建系统补充检查**：只有当本次涉及对应语言、组件或配置时，才考虑格式化、类型检查、i18n 校验、lint、构建或集成测试；具体命令以当前仓库发现到的入口为准。
5. **执行并记录事实**：在 PR 的 Testing 中逐条写入本次实际运行的命令与结果；未执行的检查保持未勾选，或按固定 checklist 的事实校准规则如实改写。

- 不把 diff 检查当成类型检查、格式化检查或完整测试的替代品。
- 当用户只要求 PR 文案且没有执行证据时，保留相应 checklist 未勾选，不要伪造通过记录。
- 与本 PR 改动无关的既有失败，不应自动写入 PR。仅当用户要求披露，或失败确实阻断本 PR 所需验证时，才记录命令、准确失败原因及相关性边界。
- 未运行全仓检查时，在 Testing 中明确写出“未执行全仓检查”以及已执行的定向验证范围；不得写成全仓通过。

## 五、Checklist 事实校准

每个勾选必须与 PR 文案和实际证据一致。

- **格式化**：只在已验证变更源文件符合项目格式化规则后勾选。
- **定向测试与 lint**：仅在相应命令成功后勾选。
- **文档**：若确实无需修改 README、`docs/` 或 Swagger，改写为“已核对相关文档；本次无需更新”后再勾选；不要错误勾选“已更新文档”。
- **破坏性变更**：无破坏性变更时，在 Description 中明确说明公共 API 与已持久化配置结构保持不变，再改写并勾选“无破坏性变更，已在上方说明”。
- **全仓检查**：未运行时，将条目改为“未执行全仓检查；已在上文记录定向验证范围”后再勾选。该勾选表示验证范围已如实披露，不表示全仓检查已通过。
- **截图**：若改动影响 Model Editor、thinking control 或其他用户可见界面，提供实际截图或明确保留 TODO，不能虚构截图已补。

## 六、写入 PR Markdown 文件

每次使用该 skill 生成、改写或校准 WeKnora PR 信息时，都必须写入文件。

1. 固定目标是 WeKnora 工作区中的 `tmp/pr.md`。
2. 第一次写入前，检查目标路径、`git status`，并读取已有 `tmp/pr.md` 的开头与哈希（若文件存在）。
3. 每次生成、改写或校准后，都直接覆盖更新同一个 `tmp/pr.md`；不创建按功能命名的新文件，也不要求为该覆盖操作再次确认。
4. 每次写入后验证文件内容、哈希和 Git 状态，并向用户报告绝对路径。
5. 除非用户要求，不把 `tmp/pr.md` 加入 commit 或推送远端。

## 输出约束

- 技术陈述必须能追溯到分支 diff、已运行命令或用户明确提供的信息。
- 用户要求可直接复制时，输出完整 Markdown，不在 Markdown 外混入额外解释。
