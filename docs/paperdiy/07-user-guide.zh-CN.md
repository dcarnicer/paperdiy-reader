# 07 — 用户指南（PaperDIY）

**语言：** [Español](07-user-guide.md) · [English](07-user-guide.en.md) · **简体中文** · [日本語](07-user-guide.ja.md)

本指南假设你已经烧录好固件。如果还没有，请先看
[README](../../README.zh-CN.md) 和 `06-porting.md`。

## 首次启动

1. 将 `.epub` 图书复制到 SD 卡（FAT32 或 exFAT）。可以使用文件夹。
2. 插入 SD 卡。
3. 短按电源键开机。
4. 第一个界面是书库/主页。用 A/B 移动；长按 B 确认；长按 A 返回。

首次打开一本书时会在 `/.crosspoint/` 生成缓存（需要几秒钟）。之后打开会
快很多。

## 操作

| 操作 | 动作 |
|---|---|
| A 短按 | 上 / 上一页 |
| B 短按 | 下 / 下一页 |
| A 长按 | 返回 / 退出 |
| B 长按 | 确认 / 选择 |
| A+B | 电源（菜单/休眠） |
| 电源单击 | 开机；运行中执行配置的动作（默认休眠/关机） |
| 电源双击 | 关机（硬件关机，如果 PM1 保持启用） |
| 电源约 10 秒 | 下载模式（红色 LED；屏幕可能冻结） |

电源单击不再执行出厂复位：PM1 会把点击事件交给固件。如果你更喜欢原始
行为，可使用 `-DPAPERDIY_PM1_APP_POWER_BUTTON=0` 编译，并用 A+B 休眠。

在阅读器中，A/B 翻页。在列表中，它们移动选择；长按 B 打开项目；长按 A
返回。

在 `设置 > 控制 > Orient Side Buttons`（侧边按键随方向）中可以让 A/B 在
横向时反向；在倒置竖屏中始终反向。默认关闭，从旧版本升级时也保持关闭。

短按在**松开**时触发，而不是按下时：这是只用两个按键区分短按和长按的
关键。如果改成“按下即翻页”，长按可能会在打开菜单前先触发一次翻页/移动；
这是一个仍待决定的 UX 取舍。

## 书库

- 主页显示最近阅读/封面；文件浏览器可以进入文件夹。
- 在书上长按 B 打开菜单（打开、详情、删除等）。
- 元数据和封面缓存于 `/.crosspoint/`；如果显示异常，删除该文件夹后会重新
  生成。

## 阅读

- 长按 B 打开阅读器菜单：目录、书签、高亮、词典、跳转到百分比、文字
  设置、屏幕方向等。
- 长按 A 返回上一级菜单。
- 阅读位置会自动保存。
- 高亮/摘录保存到 SD 卡（见阅读器菜单）。

## 漫画

- 固件不能直接打开 `.cbz`/`.cbr`，需要先转换为每张图片对应一个 XHTML 页面
  的 EPUB。
- **最佳画质（推荐）：Kindle Comic Converter（KCC）**。使用 `Other` 配置，
  宽度 540、高度 960，漫画模式，裁切页边距和页码，拆分双页，灰度，16 级
  PNG。在桌面应用中开启专家模式，选择 `Other` 和自定义尺寸。KCC 12.1.3
  命令行：

  ```sh
  kcc-c2e tome.pdf -p OTHER --customwidth 540 --customheight 960 \
    -f EPUB --nokepub -c 2 -r 0 -m -q -u --forcepng \
    -t "第 1 卷" -a "作者" -o tome.epub
  ```

  KCC 会裁掉页边距，把宽度调整到面板真实的 540 px，避免阅读器再次缩放。
  在 TOMO2 上内容放大约 20%，文件从 23 MB 降到 13 MB。
- **无 KCC 的替代方案**：`scripts/comic_to_epub.py`，为每张图片生成一个
  XHTML 页面。支持 CBZ/ZIP 或 PDF：

  ```sh
  python3 scripts/comic_to_epub.py tome.cbz tome.epub
  python3 scripts/comic_to_epub.py tome.pdf tome.epub --title "第 1 卷" --author "作者"
  ```

  PDF 需要 `pdftoppm`（macOS 上 `brew install poppler`）。
- Calibre 也可以把 CBZ 转换为 EPUB，但不会裁切或适配面板；没有 KCC 时再用。
- 把 EPUB 复制到 SD 卡的 `/Comics/`。首次打开时阅读器会建立索引，可能需要
  几十秒，期间按键无响应。
- EPUB 必须是一张图片对应一个 XHTML 页面。单个 HTML 的 PDF-reflow EPUB
  （或经过 Calibre 插件优化的版本）可能显示为 `1/1` 并无法翻页。
- 菜单可能显示 `章：1/1 页`，因为每页都是独立文档；实际进度看
  `第 N 页`/`全书 %`。

## 字体

- 将 `.ttf`、`.otf` 或 `.ttc` 复制到 SD 卡的 `/fonts/` 或 `/.fonts/`。
- 可以将同一字体家族放在子文件夹中。
- 在阅读设置中选择字体；常规/粗体/斜体按字体家族匹配。
- 词典 IPA 需要包含这些字形的字体。

## 词典

- 将每个 StarDict 词典复制到 `/dictionaries/<名称>/`（或
  `/.dictionaries/`），包含未压缩的 `.idx` 和 `.dict`/`.dict.dz`。
- 在 **Settings → Reader → Dictionary** 中选择词典。
- 第一次查词会建立索引（生成 `.qidx`/`.sidx`）；之后会很快。
- 西班牙语可以尝试 Wiktionary/RAE/WikDict 的 StarDict 词典。

## Wi-Fi、Calibre、OPDS 和网页界面

- **Settings → Network**：扫描/连接 Wi-Fi（2.4 GHz）。
- **网页界面**：屏幕上会显示地址；可以在浏览器中上传图书、查看文件、
  修改设置和更新。
- **Calibre**：在 Calibre 中使用“Connect to wireless device”；阅读器会
  显示流程。
- **OPDS**：添加目录（Project Gutenberg、Standard Ebooks 等），然后在
  阅读器中浏览。
- **KOReader Sync**：配置凭据，并向官方或自建 KOSync 服务器同步进度。
- **OTA**：在设置中检查更新；也可以通过 USB 烧录。

## 电源与休眠

- 阅读器在无操作超时后会自动休眠。
- 手动休眠：按住 A+B 或按电源键（取决于配置的动作）。
- 电池模式下，休眠时会请求 PM1 **关机**：设备关闭，单击后重新开机
  （页面仍保留在屏幕上）。
- 连接 USB 时，PM1 也可能切断电源；这种情况下只能用电源键重新开机。
  只有 USB 保持主板供电时，才会回退到**深度休眠**并用 A/B 唤醒。
- 如果长时间不使用，请双击电源键关机。
- 电池为 140 mAh：续航取决于是否休眠。开着 Wi-Fi 阅读会大幅缩短续航。

## SD 卡：推荐目录结构

```
/
├── Books/                 # 你的 EPUB（可以使用文件夹）
├── Comics/                # 转换为 EPUB 的漫画
├── fonts/                 # TTF/OTF
├── dictionaries/          # 每个词典一个 StarDict 文件夹
└── .crosspoint/           # 阅读器缓存（除非重置，不要动）
```

`设置 > 关于` 会显示 SD 卡的总容量、已用和可用空间。第一次查看可能需要几
秒钟，因为要遍历 FAT。

## 常见问题

| 症状 | 可以尝试 |
|---|---|
| 白屏 | PM1 GPIO2/GPIO46？DCDC？完整烧录？ |
| 图像倒置 | 修改 `paperdiyLgfxConfig` 中的 `rotation`（0 ↔ 2） |
| 翻页残影 | 在 设置 > 显示 中把 `Refresh Frequency` 试为 5，再试 1；新的快速 LUT 仍在验证中 |
| SD 无法挂载 | FAT32/exFAT、接触、换一张卡；启动时没有卡的话，插入后设备会重启 |
| 无法翻页 | 电池？A/B？是否处于休眠？ |
| 无法唤醒 | 按键是否正常？`ext1` GPIO3/4？ |
| 电量显示异常 | 查看 `About > Battery`（VBAT/状态）或 `[PWR] Battery:` 日志；更换电池后重新校准 |
| Wi-Fi 连不上 | 2.4 GHz、密码、AP 隔离；试试手机热点 |
| 图书打不开 | EPUB 是否有效、大小、RAM；删除该书缓存 |
| 更新后界面异常 | 删除 `/.crosspoint/` 并重启 |

## 恢复

如果出现问题：

1. 长按电源约 10 秒直到红色 LED 亮起 → 下载模式。
2. 在 `0x0` 烧录发布中的 `crosspoint-paperdiy-latest.bin`（本地构建则为
   `firmware.factory.bin`）。
3. 如果无法进入下载模式，换一根线/USB 口；ESP32-S3 原生 USB 不需要
   转接器。

实验前请始终保留原始固件的备份。
