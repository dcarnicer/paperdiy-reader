# PaperDIY 文档

**语言：** [Español](README.md) · [English](README.en.md) · **简体中文** · [日本語](README.ja.md)

本仓库自有移植文档的索引（CrossPoint 原始文档仍位于 `docs/` 和
`docs/upstream/`）。

> 主 README、用户指南以及硬件与移植笔记已翻译为英语、简体中文和日语。
> 其余详细文档目前仍为西班牙语。

1. [研究与当前状态](00-research.md)
2. [硬件与引脚](01-hardware.zh-CN.md) — [Español](01-hardware.md) · [English](01-hardware.en.md) · [日本語](01-hardware.ja.md)
3. [POC 与生态分析](02-current-state.md)
4. [功能矩阵](03-feature-matrix.md)
5. [架构](04-architecture.md)
6. [路线图](05-roadmap.md)
7. [移植笔记与验证](06-porting.zh-CN.md) — [Español](06-porting.md) · [English](06-porting.en.md) · [日本語](06-porting.ja.md)
8. [用户指南](07-user-guide.zh-CN.md) — [Español](07-user-guide.md) · [English](07-user-guide.en.md) · [日本語](07-user-guide.ja.md)
9. [来源](08-sources.md)
10. [先前工作：issue #4005 和 PaperDIY PR](09-prior-art.md)
11. [维护 fork 与更新上游](10-fork-maintenance.md)
12. [issue #4005 评论草稿](11-upstream-note.md)
13. [USB 测试](12-serial-testing.md)（西班牙语）

## 一句话状态

移植已**编译、启动并在真实 PaperDIY 上验证**（屏幕、按键、SD、电池、Wi-Fi、
EPUB 阅读、OPDS 和 Calibre 无线传输）。自动休眠和封面休眠画面也已验证。
长时间阅读于 2026-11-06 完成 250+ 次翻页，无错误、无泄漏。KOReader Sync
已于 2026-11-06 通过本地 KOSync 服务器验证。仍待完成：配对 BLE 遥控器、
休眠电流/续航、604050 电池，以及残影的实机目视检查。请从 `06-porting.md`
开始。
