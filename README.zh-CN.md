# PaperDIY Reader

**语言：** [Español](README.md) · [English](README.en.md) · **简体中文** · [日本語](README.ja.md)

面向 **M5Stack PaperDIY**（ESP32-S3 + 4.7 英寸 ED047TC1 电子墨水屏，960×540，
16 级灰度）的功能丰富的阅读固件，基于
[CrossPoint Reader 2.0](https://github.com/crosspoint-reader/crosspoint-reader)
（MIT）构建。目标不是 POC：而是一个具备书库、设置、字体、词典、同步、
OPDS/Calibre 以及日常使用所需一切功能的电子书阅读器。

> **状态：** 固件**已在真实 PaperDIY 上编译、启动并阅读 EPUB**。
> 验证（2026-11-04）：同步到 CrossPoint `308cd522` 后，启动、屏幕/界面、
> 主页、唤醒、A/B 按键、电池、SD 和导航均正常。
> EPUB 阅读、Wi-Fi、网页界面和图书传输已于 2026-10-28 验证。
> Calibre 无线传输和 OTA 已于 2026-11-04 验证。OPDS（Project Gutenberg）
> 已于 2026-11-05 验证。自动休眠和封面休眠画面也于 2026-11-05 验证。
> 待完成：需要凭据的 KOReader Sync、多页后的可见残影、休眠电流和续航。见
> [`docs/paperdiy/06-porting.md`](docs/paperdiy/06-porting.md)。
>
> **下游分支：** `main` 镜像 `upstream/develop`；`paperdiy` 是我们的工作
> 分支。`freeink-sdk` 已内置到仓库，因此克隆后无需子模块即可编译。见
> [`docs/paperdiy/10-fork-maintenance.md`](docs/paperdiy/10-fork-maintenance.md)。

## 为什么有这个仓库

`melastmohican/m5paperdiy-arduino-examples` 示例仓库证明了屏幕和按键可以
工作，但它的 `EpubReader` 只是 atomic14 阅读器的移植：没有持久化、没有
书库、没有设置、没有 Wi-Fi、没有深度休眠，而且每页都整屏刷新。CrossPoint
已经解决了 EPUB 引擎、排版、字体、SD 缓存、书库、词典、OPDS、Calibre、
KOReader Sync、网页界面和 OTA。缺少的正是 PaperDIY 的板级支持层。

本仓库补上了这一层：

- `freeink-sdk` 中的 `M5PAPER_DIY` 配置（屏幕、按键、电池、电源、唤醒）；
- `BoardPaperDiy`，包含 ED047TC1 并行总线和 **M5PM1** 的 EPD 电源轨；
- 复用 PaperS3 总线的 `paperdiyLgfxConfig`（相同引脚）；
- 通过 M5PM1 读取电池/充电状态；
- 将 PM1 电源键映射为 `BTN_POWER`，电池模式下关机，USB 下回退到深度
  休眠并用 A/B 唤醒；
- PSRAM 中的帧缓冲（`FREEINK_FB_PSRAM`）；
- 可配置的 OTA（`CROSSPOINT_OTA_RELEASES_URL`），避免下载官方固件；
- PlatformIO 环境 `paperdiy`。

## 硬件

| | PaperDIY |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8，240 MHz |
| Flash / PSRAM | 16 MB / 8 MB Octal |
| 屏幕 | ED047TC1 4.7 英寸 960×540，16 级灰度，8 位并行总线 |
| 输入 | 2 个用户按键（GPIO4 = A，GPIO3 = B），电源键由 PM1 管理 |
| 电源 | M5PM1；140 mAh 电池；USB-C |
| SD | SPI microSD（SCLK39 / MISO40 / MOSI38 / CS47） |
| 连接 | 2.4 GHz Wi-Fi + BLE 5 |
| 不支持 | 触摸、前置灯、RTC、IMU、音频 |

屏幕总线与 **M5Paper S3 引脚完全一致**：D0–D7 =
6,14,7,12,9,11,8,10；CL=16，LE=15，SPH=13，SPV=17，CKV=18，OE=45，PWR=46。
区别在于 PaperDIY 还需要 M5PM1 的 EPD 电源轨（GPIO2，通过 SDA41/SCL42 的
I²C 控制）。

### 3D 外壳

M5Stack **PaperDIY Complete Kit** 附带 PLA 打印外壳。我们在
[`hardware/3d/PaperDIY_kit_completo.3mf`](hardware/3d/PaperDIY_kit_completo.3mf)
中保留了一份官方模型的修改版，方便需要打印或改造的人使用。它包含后壳、
前框和按键，可作为 Bambu Studio 项目打开（几何模型也可以在其他切片软件
中复用）。

原始模型、M5Stack 的 MIT 许可证以及 M2 螺丝警告见
[`hardware/README.zh-CN.md`](hardware/README.zh-CN.md)。

## 操作（两个按键）

CrossPoint 使用 `InputStyle::DigitalTwoButton`，专为两个按键设计：

| 操作 | 动作 |
|---|---|
| **A**（GPIO4）短按 | 上 / 上一页 / 选择上移 |
| **B**（GPIO3）短按 | 下 / 下一页 / 选择下移 |
| **A** 长按 | 返回 / 退出 |
| **B** 长按 | 确认 / 选择 |
| **A + B** | 电源键（电源菜单 / 休眠） |
| 电源短按 | 已配置动作；默认休眠/关机（PM1 将点击事件交给固件） |
| 电源双击 | 硬件关机（如果 PM1 保持启用） |
| 电源约 10 秒 | 下载模式（红色 LED；屏幕可能冻结） |
| 关机状态下按电源 | 开机 |

电源行为与出厂固件不同：当
`PAPERDIY_PM1_APP_POWER_BUTTON=1`（默认）时，PM1 的单击复位被禁用，让点击
事件到达 CrossPoint。如果你更喜欢出厂复位，可使用
`-DPAPERDIY_PM1_APP_POWER_BUTTON=0` 编译；然后使用 A+B 休眠。

导航是主要的硬件限制。计划包括按键重映射、上下文快捷键和 **BLE 翻页器**
（已编译），以便用遥控器或手机翻页。

## 包含功能（继承自 CrossPoint 2.0）

- **EPUB 2/3 引擎**：CSS、图片、断词、字距调整、表格、脚注、章节导航、
  CJK 注音、RTL、专注模式、屏幕方向。
- **书库**：标题/作者索引、封面、最近阅读、搜索、文件浏览器、SD 缓存。
- **阅读**：保存进度、书签、高亮/摘录、跳转到百分比、自动翻页、主题、
  夜间模式、字体和字号。
- **StarDict 词典**和查词。
- **同步**：KOReader Sync、Calibre 无线、OPDS（支持搜索和分页）、WebDAV、
  用于上传图书的网页界面、OTA。
- **格式**：`.epub`、`.xtc/.xtch`、`.txt`、`.bmp`。
- **字体**：内置字体 + SD 卡上的 TTF/OTF。
- **国际化**：35 种界面语言（包含西班牙语）。
- **PaperDIY**：在 `paperdiy` 环境中启用 BLE HID 主机（翻页器）和 USB
  大容量存储。

## 编译

要求：PlatformIO Core，首次编译需要联网（隔离的 core 会下载平台、框架和
工具链；约 5 GB）。

```bash
make build
# 等价于：
PLATFORMIO_CORE_DIR="$PWD/.platformio-core" pio run -e paperdiy
```

生成的固件位于：

```
.pio/build/paperdiy/firmware.bin          # 应用（偏移 0x10000）
.pio/build/paperdiy/firmware.factory.bin  # 完整镜像（偏移 0x0）
```

如果你的全局 `~/.platformio` 正常，也可以直接运行 `pio run -e paperdiy`。
`Makefile` 使用隔离的 core，即使系统里有旧包也能保证构建可复现。
`.platformio-core/` 和 `.pio/` 是本地缓存（已被 git 忽略）；可以删除后重新
运行 `make build` 生成。

## 烧录

1. 用 USB-C 连接 PaperDIY。
2. 长按电源键约 10 秒，直到红色 LED 闪烁（下载模式）。
3. 首次安装（完整镜像，包含引导程序和分区表）：

```bash
make flash-factory PORT=/dev/cu.usbmodemXXXX
```

仅更新应用（保留引导程序/分区表）：

```bash
make flash PORT=/dev/cu.usbmodemXXXX
```

或者完全手动控制：

```bash
# 应用更新（保留引导程序/分区表）
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x10000 .pio/build/paperdiy/firmware.bin

# 首次安装 / 恢复（完整镜像）
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x0 .pio/build/paperdiy/firmware.factory.bin
```

首次烧录前，请备份原始固件：

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  read_flash 0 0x1000000 paperdiy-original.bin
```

## 目录结构

```
.
├── src/                  # CrossPoint 应用（活动、阅读器、UI、网络）
├── lib/                  # Epub、GfxRenderer、EpdFont、HAL 等
├── freeink-sdk/          # 硬件 SDK + 板级配置
│   └── libs/hardware/
│       ├── BoardConfig/  # M5PAPER_DIY + M5Pm1
│       └── BoardPaperDiy/# ED047TC1 总线、PM1 电源轨、关机
├── docs/paperdiy/        # 研究、硬件、路线图、移植
├── docs/upstream/        # CrossPoint 原始 README/用户指南
├── hardware/3d/          # 3D 外壳（完整套件修改版）
├── platformio.ini        # `paperdiy` 环境
└── Makefile
```

## 文档

详细文档目前为西班牙语。[文档索引](docs/paperdiy/README.zh-CN.md)、
[用户指南](docs/paperdiy/07-user-guide.zh-CN.md)、
[硬件](docs/paperdiy/01-hardware.zh-CN.md) 和
[移植笔记](docs/paperdiy/06-porting.zh-CN.md) 也提供中文版本。

- [研究与当前状态](docs/paperdiy/00-research.md)
- [硬件与引脚](docs/paperdiy/01-hardware.md)
- [POC 与生态分析](docs/paperdiy/02-current-state.md)
- [功能矩阵](docs/paperdiy/03-feature-matrix.md)
- [架构](docs/paperdiy/04-architecture.md)
- [路线图](docs/paperdiy/05-roadmap.md)
- [移植笔记与验证](docs/paperdiy/06-porting.md)
- [PaperDIY 用户指南](docs/paperdiy/07-user-guide.md)
- [来源](docs/paperdiy/08-sources.md)
- [先前工作：issue #4005 和 PaperDIY PR](docs/paperdiy/09-prior-art.md)
- [维护 fork 与更新上游](docs/paperdiy/10-fork-maintenance.md)
- [issue #4005 评论草稿](docs/paperdiy/11-upstream-note.md)
- [USB 测试（西班牙语）](docs/paperdiy/12-serial-testing.md)

## 已知限制

- 仍待测量：LUT、多页后的残影、休眠电流和续航。
- 不支持触摸、前置灯、RTC、IMU 或音频。界面必须用两个按键操作。
- 140 mAh 电池：休眠时固件会请求 PM1 关机。如果 PM1 切断电源（通常
  如此，USB 连接时也一样），只能用电源键重新开机。2026-11-05 验证：
  USB 连接时 A+B 通过 PM1 关机，A 无法唤醒。如果 USB 保持主板供电，
  则回退到深度休眠并用 A/B 唤醒。续航仍待测量。
- 物理电源键由 M5PM1 管理；固件通过 I²C 事件接收，而不是 GPIO。
- OTA 默认指向官方仓库，但没有 `-paperdiy` 资源，因此不会安装其他固件。
  如需自己的 OTA，请配置 `CROSSPOINT_OTA_RELEASES_URL`。
- CrossPoint 2.0 是开发分支（2.0.0），不是稳定的 1.6.x。

## 致谢与许可

MIT。引擎和大部分代码来自
[CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
（Copyright 2025 CrossPoint Reader organization）；硬件 SDK 是
[FreeInk](https://github.com/crosspoint-reader/crosspoint-reader)（MIT）；
屏幕由 M5GFX/LovyanGFX 驱动。3D 外壳是
[M5Stack](https://github.com/m5stack/M5_Hardware) MIT 模型的修改版。见
[LICENSE](LICENSE) 和 [NOTICE](NOTICE)。

> 本文是西班牙语 README 的翻译；如有出入，以西班牙语版为准。详细文档目前
> 只有西班牙语。
