# 01 — ハードウェアとピン

**言語：** [Español](01-hardware.md) · [English](01-hardware.en.md) · [简体中文](01-hardware.zh-CN.md) · **日本語**

## 仕様

| | |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8（デュアルコア LX7、240 MHz） |
| Flash | 16 MB |
| PSRAM | 8 MB Octal（OPI） |
| 画面 | ED047TC1、4.7 インチ、960×540、16 階調、234 PPI |
| 画面インターフェース | 8 ビットパラレル、**IT8951 コントローラーなし** |
| ボタン | A=GPIO4、B=GPIO3（アクティブ Low）。電源は M5PM1 管理 |
| バッテリー | 140 mAh、M5PM1 で充電 |
| SD | SPI 接続 microSD（SCLK39/MISO40/MOSI38/CS47）、CARD_DET GPIO48 アクティブ Low |
| USB | ESP32-S3 ネイティブ USB-C（Serial/JTAG） |
| 無線 | 2.4 GHz Wi-Fi、BLE 5.0 |
| 非搭載 | タッチ、フロントライト、RTC、IMU、オーディオ、Grove |

## ピンマップ

### パネル（M5Paper S3 と同一）

| 信号 | GPIO | 備考 |
|---|---:|---|
| D0 | 6 | データバス |
| D1 | 14 | |
| D2 | 7 | |
| D3 | 12 | |
| D4 | 9 | |
| D5 | 11 | |
| D6 | 8 | |
| D7 | 10 | |
| XCL / CL | 16 | ピクセルクロック |
| XLE / LE | 15 | ラッチ |
| XSTL / SPH | 13 | 水平スタートパルス |
| XOE / OE | 45 | 出力イネーブル |
| CKV | 18 | ゲートクロック |
| SPV | 17 | 垂直スタートパルス |
| PWR | 46 | パネル昇圧イネーブル |
| PM1 GPIO2 | — | 追加 EPD レール、I²C 経由 |

移植版の `LgfxEpdConfig` はまさにこれらのピンを使用します。LovyanGFX の
`Panel_EPD` は OE → PWR → SPV の順に制御し、PM1 のレールは `prepare()`
フックで先に立ち上げます。

### SD

| 信号 | GPIO |
|---|---:|
| SCLK | 39 |
| MISO | 40 |
| MOSI | 38 |
| CS | 47 |

SPI、SdFat、FAT32/exFAT。SD はパネルと SPI バスを共有する？いいえ。パネル
はパラレルで、SD は専用 SPI です。それでも SDK は SPI 上の `SdFat` を
使います。

### ボタン

| ボタン | GPIO | 種類 |
|---|---:|---|
| A | 4 | アクティブ Low、外部プルアップ |
| B | 3 | アクティブ Low、外部プルアップ |
| Power | — | M5PM1。シングルクリックで電源オン/リセット、ダブルクリックで電源オフ、長押しでダウンロードモード |

`InputStyle::DigitalTwoButton` の割り当て：

- A 短押し → `BTN_UP`
- B 短押し → `BTN_DOWN`
- A 長押し → `BTN_BACK`
- B 長押し → `BTN_CONFIRM`
- A+B → `BTN_POWER`

### M5PM1

| 信号 | GPIO |
|---|---:|
| I²C SDA | 41 |
| I²C SCL | 42 |
| アドレス | 0x6E |
| GPIO2 | EPD レール |
| GPIO3 | CHG_STAT（入力、アクティブ Low） |

PM1 は充電、電源ボタン、シャットダウンも管理します。ファームウェアでの
用途：

- パネル初期化前に EPD レールを立ち上げる；
- VBAT/VIN/VOUT と充電状態を読む；
- 本体を電源オフする（`SYS_CMD 0xA1`）；
- ディープスリープ前に EPD レールを切る。

## パネルリフレッシュ

M5GFX は 4 つのモードを公開します：

| モード | 典型的な用途 | トレードオフ |
|---|---|---|
| `epd_quality` | 表紙、画像、初回描画 | 遅いが階調/品質が良い |
| `epd_text` | テキストの全ページ | きれいだがちらつくことがある |
| `epd_fast` | 小さな変更、UI | 速いが残像が増える |
| `epd_fastest` | アニメーション/フィードバック | 非常に速いが残像が強い |

CrossPoint はアンチエイリアスのため 1 bpp フレームバッファ + グレー平面を
使います。`LgfxEpdDriver` は `Full/Half` を `epd_text` に、`Fast/Fastest` を
`epd_fast` にマップします。移植版は `quality` と `text` に `Panel_EPD` の
標準 LUT を維持します。`fast`/`fastest` には LilyGo T5 S3 で検証された
ED047TC1 の AA 波形を使います。B/W ベースとグレー平面を同じ LUT オフセット
に保ち、アンチエイリアスで生成されるグレーレベルを専用に駆動します。
PMIC/VCOM が異なるため、PaperDIY での検証はまだ必要です。
[`06-porting.ja.md`](06-porting.ja.md#ページ送りの残像) を参照。

## 電源

- 140 mAh バッテリー：容量は小さい。ピークより平均消費電力が重要。
- ディープスリープ：ESP32-S3 は数十 µA まで下がりますが、PM1 のレール、
  SD、パネルで数 mA 増える可能性があります。移植版は
  `PowerManager::powerDownRailsForSleep()` で PM1 の EPD レールを切ります。
  実測が必要です。
- 復帰：GPIO3/4 の `ext1`（S3 の RTC GPIO）、アクティブ Low。どちらの
  ボタンでも復帰します。
- 充電：PM1 の `CHG_EN` が LGS4056H を有効にします。K159 の回路図では
  `R11=2K` で 500 mA に設定。純正 140 mAh セルでは約 3.6C、約 2000 mAh の
  604050 では約 0.25C になります。
- `CHG_STAT` は PM1 GPIO3、アクティブ Low。USB があるかだけでなく、実際に
  充電中かを読むために使います。
- 低電圧保護：`REG_BATT_LVP` を 3.4 V に設定。
- 物理電源ボタンは ESP32 の GPIO ではないため、ファームウェアから直接
  読めません。UI からスリープするには A+B を使います。

### 概算バジェット（要実測）

| 状態 | 予想電流 | 140 mAh での駆動時間 |
|---|---:|---:|
| 読書中（Wi-Fi オフ） | 40–80 mA | 2–3.5 時間 |
| Wi-Fi オン | 100–150 mA | 1.5 時間未満 |
| ディープスリープ（適切に設定） | 20–100 µA | 数週間/数か月 |
| ディープスリープ（レール未切断） | 1–5 mA | 数日 |

実用上の結論：リーダーは短いタイムアウト後とセッション間にスリープする
必要があります。ページボタンで復帰し、描画して再びスリープします。
CrossPoint には自動スリープがあるため、タイムアウトを調整して実測します。

## 3D ケース

Complete Kit のモデルは
[`hardware/3d/PaperDIY_kit_completo.3mf`](../../hardware/3d/PaperDIY_kit_completo.3mf)
にあります。M5Stack が公開している **PaperDIY Complete Kit（K159-B）** の
公式 STL の改造版で、元ファイルは
[`M5_Hardware/Products/K159-B_PaperDIY_Complete_Kit/Structures`](https://github.com/m5stack/M5_Hardware/tree/master/Products/K159-B_PaperDIY_Complete_Kit/Structures)
です。リアシェル、フロントフレーム、ボタンを含み、Bambu Studio 向けの
プロジェクトです。MIT ライセンス（オリジナル © 2021 M5Stack、改造版 © 2026
PaperDIY Reader contributors）。[`hardware/README.ja.md`](../../hardware/README.ja.md)
を参照。

## オプションのハードウェア改造

- **大容量バッテリー**：キットは 140 mAh。ケース内の空きに 500–1000 mAh
  セルを入れると駆動時間が大幅に伸びます。空間、コネクタ、充電（PM1 が
  制御）を確認する必要があります。
- **I²C RTC**：内部バス（41/42）に DS3231/PCF8563 を付ければ実時刻と
  アラームが使えます。`BoardConfig`/`Rtc` にサポート追加が必要です。
- **ロータリーエンコーダーまたは 5 方向キー**：追加 GPIO + I²C/ADC で
  ホイール型 UI が可能。ケースの改造が必要です。
- **カバー内 Hall センサー**：開閉でスリープ/復帰。空き GPIO と磁石を
  使います。
- **フロントライト**：簡単ではありません。現実的な解は外付けライトクリップ
  です。レールも内蔵 LED もありません。

## ダウンロードモードと復旧

- 電源を約 2 秒長押しして赤 LED が点滅 → ダウンロードモード。
- `esptool --chip esp32s3 --port ... write_flash 0x0 firmware.factory.bin`
  で、アプリが壊れていても復旧できます。
- 初回インストール前に元のファームウェアをバックアップしてください。
