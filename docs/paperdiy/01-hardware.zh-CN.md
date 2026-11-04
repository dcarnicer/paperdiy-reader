# 01 — 硬件与引脚

**语言：** [Español](01-hardware.md) · [English](01-hardware.en.md) · **简体中文** · [日本語](01-hardware.ja.md)

## 规格

| | |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8（双核 LX7，240 MHz） |
| Flash | 16 MB |
| PSRAM | 8 MB Octal（OPI） |
| 屏幕 | ED047TC1，4.7 英寸，960×540，16 级灰度，234 PPI |
| 屏幕接口 | 8 位并行，**没有 IT8951 控制器** |
| 按键 | A=GPIO4，B=GPIO3（低电平有效）；电源由 M5PM1 管理 |
| 电池 | 140 mAh，由 M5PM1 充电 |
| SD | SPI microSD（SCLK39/MISO40/MOSI38/CS47），CARD_DET GPIO48 低电平有效 |
| USB | ESP32-S3 原生 USB-C（Serial/JTAG） |
| 无线 | 2.4 GHz Wi-Fi，BLE 5.0 |
| 不支持 | 触摸、前置灯、RTC、IMU、音频、Grove |

## 引脚图

### 屏幕（与 M5Paper S3 相同）

| 信号 | GPIO | 说明 |
|---|---:|---|
| D0 | 6 | 数据总线 |
| D1 | 14 | |
| D2 | 7 | |
| D3 | 12 | |
| D4 | 9 | |
| D5 | 11 | |
| D6 | 8 | |
| D7 | 10 | |
| XCL / CL | 16 | 像素时钟 |
| XLE / LE | 15 | 锁存 |
| XSTL / SPH | 13 | 水平起始脉冲 |
| XOE / OE | 45 | 输出使能 |
| CKV | 18 | 栅极时钟 |
| SPV | 17 | 垂直起始脉冲 |
| PWR | 46 | 屏幕升压使能 |
| PM1 GPIO2 | — | 额外的 EPD 电源轨，通过 I²C |

移植层的 `LgfxEpdConfig` 使用的正是这些引脚。LovyanGFX 的 `Panel_EPD`
按 OE → PWR → SPV 的顺序操作；PM1 的电源轨会在 `prepare()` 钩子中提前
拉高。

### SD

| 信号 | GPIO |
|---|---:|
| SCLK | 39 |
| MISO | 40 |
| MOSI | 38 |
| CS | 47 |

SPI、SdFat、FAT32/exFAT。SD 和屏幕共用 SPI 总线吗？不：屏幕是并行接口，
SD 使用独立的 SPI。即便如此，SDK 仍通过 SPI 使用 `SdFat`。

### 按键

| 按键 | GPIO | 类型 |
|---|---:|---|
| A | 4 | 低电平有效，外部上拉 |
| B | 3 | 低电平有效，外部上拉 |
| Power | — | M5PM1；单击开机/复位，双击关机，长按下载模式 |

`InputStyle::DigitalTwoButton` 映射：

- A 短按 → `BTN_UP`
- B 短按 → `BTN_DOWN`
- A 长按 → `BTN_BACK`
- B 长按 → `BTN_CONFIRM`
- A+B → `BTN_POWER`

### M5PM1

| 信号 | GPIO |
|---|---:|
| I²C SDA | 41 |
| I²C SCL | 42 |
| 地址 | 0x6E |
| GPIO2 | EPD 电源轨 |
| GPIO3 | CHG_STAT（输入，低电平有效） |

PM1 还管理充电、电源键和关机。固件用它来：

- 在初始化屏幕前拉高 EPD 电源轨；
- 读取 VBAT/VIN/VOUT 和充电状态；
- 关闭设备（`SYS_CMD 0xA1`）；
- 在深度休眠前切断 EPD 电源轨。

## 屏幕刷新

M5GFX 提供四种模式：

| 模式 | 典型用途 | 取舍 |
|---|---|---|
| `epd_quality` | 封面、图片、首次绘制 | 较慢，灰度/质量更好 |
| `epd_text` | 整页文字 | 干净，可能闪烁 |
| `epd_fast` | 小范围变化、UI | 快，残影更多 |
| `epd_fastest` | 动画/反馈 | 很快，残影明显 |

CrossPoint 使用 1 bpp 帧缓冲 + 灰度平面进行抗锯齿；`LgfxEpdDriver` 将
`Full/Half` 映射到 `epd_text`，将 `Fast/Fastest` 映射到 `epd_fast`。
移植层保留 `Panel_EPD` 的标准 LUT 用于 `quality` 和 `text`。
对于 `fast`/`fastest`，使用在 LilyGo T5 S3 上验证过的 ED047TC1 AA
波形：黑白基础和灰度平面使用同一个 LUT，并针对抗锯齿产生的灰度级别做
专门驱动。由于 PMIC/VCOM 不同，仍需在 PaperDIY 上验证。见
[`06-porting.zh-CN.md`](06-porting.zh-CN.md#翻页残影)。

## 电源

- 140 mAh 电池：容量很小。平均功耗比峰值更重要。
- 深度休眠：ESP32-S3 可降到几十 µA，但 PM1 电源轨、SD 和屏幕可能增加几
  mA。移植层在 `PowerManager::powerDownRailsForSleep()` 中切断 PM1 的 EPD
  电源轨；需要实测。
- 唤醒：GPIO3/4 上的 `ext1`（S3 的 RTC GPIO），低电平有效。任意按键都能
  唤醒。
- 充电：PM1 的 `CHG_EN` 使能 LGS4056H。K159 原理图中 `R11=2K`，设定
  500 mA；原装 140 mAh 电池约为 3.6C，约 2000 mAh 的 604050 电池约为
  0.25C。
- `CHG_STAT` 是 PM1 GPIO3，低电平有效：用于判断是否真的在充电，而不仅是
  是否插入 USB。
- 低压保护：`REG_BATT_LVP` 设为 3.4 V。
- 物理电源键不是 ESP32 的 GPIO，固件无法直接读取。要从 UI 休眠，使用
  A+B。

### 粗略功耗预算（待测量）

| 状态 | 预期电流 | 140 mAh 续航 |
|---|---:|---:|
| 阅读中（Wi-Fi 关闭） | 40–80 mA | 2–3.5 小时 |
| 开启 Wi-Fi | 100–150 mA | <1.5 小时 |
| 深度休眠（配置正确） | 20–100 µA | 数周/数月 |
| 深度休眠（电源轨未切断） | 1–5 mA | 数天 |

实际结论：阅读器必须在短超时后以及两次会话之间休眠；翻页键唤醒、绘制，
然后再次休眠。CrossPoint 已有自动休眠；需要调整超时并实测。

## 3D 外壳

完整套件的模型位于
[`hardware/3d/PaperDIY_kit_completo.3mf`](../../hardware/3d/PaperDIY_kit_completo.3mf)。
它是 M5Stack 发布的 **PaperDIY Complete Kit（K159-B）** 官方 STL 的修改版，
原始文件在
[`M5_Hardware/Products/K159-B_PaperDIY_Complete_Kit/Structures`](https://github.com/m5stack/M5_Hardware/tree/master/Products/K159-B_PaperDIY_Complete_Kit/Structures)。
包含后壳、前框和按键；项目面向 Bambu Studio。MIT 许可（原始模型 © 2021
M5Stack；修改版 © 2026 PaperDIY Reader contributors）。见
[`hardware/README.zh-CN.md`](../../hardware/README.zh-CN.md)。

## 可选硬件改造

- **更大电池**：套件标配 140 mAh；在外壳空间内放 500–1000 mAh 电池可显著
  提升续航。需要检查空间、连接器和充电（PM1 负责调节）。
- **I²C RTC**：在内部总线（41/42）上接 DS3231/PCF8563 可获得真实时间和
  闹钟；需要在 `BoardConfig`/`Rtc` 中增加支持。
- **旋转编码器或五向键**：额外 GPIO + I²C/ADC 可实现滚轮式 UI；需要修改
  外壳。
- **保护套霍尔传感器**：开合时休眠/唤醒；使用一个空闲 GPIO 和磁铁。
- **前置灯**：并不简单；现实方案是外置阅读灯夹。没有电源轨或集成 LED。

## 下载模式与恢复

- 长按电源约 2 秒，直到红色 LED 闪烁 → 下载模式。
- `esptool --chip esp32s3 --port ... write_flash 0x0 firmware.factory.bin`
  可以在应用损坏时恢复设备。
- 首次安装前请备份原始固件。
