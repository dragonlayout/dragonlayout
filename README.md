# Chenlong (dragonlayout)

Building calm, native macOS tools with SwiftUI.

用 SwiftUI 打造轻量、原生、可长期使用的 macOS 工具。

[Current Build: Klipu](https://github.com/dragonlayout/Klipu) • [Weekly Build Log](#weekly-build-log) • [Focus Radar](#focus-radar)

## Now / 现在

| Lens | What I am doing now |
| --- | --- |
| Building / 在做什么 | Shipping Klipu as a fast, native clipboard manager for macOS. 目前主线是把 Klipu 做成稳定、顺手、可长期使用的剪切板工具。 |
| Learning / 在学什么 | SwiftUI motion details, drag-and-drop edge cases, and state architecture under real usage pressure. 在真实使用场景里打磨动画、拖拽边界和状态管理。 |
| Optimizing / 在优化什么 | Interaction latency, keyboard-first workflows, and predictable behavior. 持续优化响应速度、键盘工作流与可预测交互。 |
| Not Doing / 刻意不做 | No feature bloat, no flashy-but-fragile UI, no premature plugin ecosystem. 不做功能堆砌、不做脆弱炫技动画、不提前扩张插件生态。 |

<details>
<summary>Operating Cadence / 工作节奏</summary>

- Weekly review: Sunday
- Shipping window: Tuesday to Thursday
- Refactor window: Friday

</details>

<a id="weekly-build-log"></a>
## Weekly Build Log / 每周构建日志

<!--START_BUILD_LOG-->
## Week 2026-W07

### Shipped / 已完成
- Stabilized drag-and-drop settle behavior in clipboard cards.
- Improved keyboard navigation consistency in the main panel.
- Reduced visual noise in item actions to keep the list scannable.

### Learning / 本周洞察
- Small animation timing differences can strongly affect perceived quality.
- Clipboard workflows fail when edge states are not explicit.

### Next / 下周计划
- Add more regression tests around drag transfer behavior.
- Polish panel open/close transitions for faster perceived response.

## Week 2026-W06

### Shipped / 已完成
- Refined pinboard card hierarchy and spacing.
- Cleaned up settings grouping to reduce decision fatigue.
- Improved source-app attribution visibility.

### Learning / 本周洞察
- Fewer controls with clearer defaults outperformed "fully configurable" options.
- Naming consistency reduced support-like confusion during dogfooding.

### Next / 下周计划
- Revisit search behavior for mixed content types.
- Make quick actions easier to discover without visual clutter.

## Week 2026-W05

### Shipped / 已完成
- Improved clipboard history rendering for long multiline entries.
- Added clearer empty-state guidance for first-time users.
- Tightened spacing and typography rhythm across list items.

### Learning / 本周洞察
- Empty states are part of product trust, not just decorative copy.
- Better defaults reduced the need for onboarding explanations.

### Next / 下周计划
- Evaluate latency hotspots in list updates.
- Expand UI test coverage for basic keyboard flows.

## Week 2026-W04

### Shipped / 已完成
- Reworked list item actions for cleaner pointer and keyboard behavior.
- Simplified filter labels and reduced ambiguity in type switching.
- Improved consistency between menu bar entry and panel state.

### Learning / 本周洞察
- Behavioral consistency matters more than adding one more feature.
- Product clarity improved when language matched user intent.

### Next / 下周计划
- Continue reducing accidental complexity in advanced settings.
- Draft a lightweight checklist for weekly release quality.
<!--END_BUILD_LOG-->

<a id="focus-radar"></a>
## Focus Radar / 关注雷达

- `Applying` SwiftUI list and card interactions for high-density clipboard data
- `Deepening` AppKit + SwiftUI boundary handling in panel-style windows
- `Exploring` Clipboard privacy patterns and sensitive-content exclusion heuristics
- `Applying` Test design for drag-transfer and interaction regressions

## Auto Activity / 自动活动

This section is refreshed by GitHub Actions.
以下内容由 GitHub Actions 定时刷新。

<!--START_ACTIVITY-->
- Activity refresh will appear here after the first workflow run.
- 首次 workflow 运行后，这里会自动显示近期活动。
<!--END_ACTIVITY-->

## Collaboration / 协作方向

I am happy to talk about:

- macOS utility product design and interaction tradeoffs
- SwiftUI architecture for long-lived desktop apps
- performance, UX consistency, and product iteration loops

Topics are welcome in English or Chinese.
欢迎中英文交流。
