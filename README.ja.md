# PaperDIY Reader

**言語：** [Español](README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md) · **日本語**

**M5Stack PaperDIY**（ESP32-S3 + 4.7 インチ ED047TC1 電子ペーパー、
960×540、16 階調）向けの高機能リーディングファームウェアです。
[CrossPoint Reader 2.0](https://github.com/crosspoint-reader/crosspoint-reader)
（MIT）をベースにしています。目的は POC ではなく、ライブラリ、設定、フォント、
辞書、同期、OPDS/Calibre など、毎日使える電子書籍リーダーにすることです。

`2.0.0-12` からは、実験的に **Waveshare ESP32-S3-ePaper-3.97** でも動作します
（[Waveshare ESP32-S3-ePaper-3.97](#waveshare-esp32-s3-epaper-397実験的) を参照）。

> **状態：** ファームウェアは**実機の PaperDIY でビルド、起動、EPUB の
> 読書まで確認済み**です。
> 検証（2026-11-04）：CrossPoint `308cd522` への同期後、起動、画面/UI、
> ホーム、復帰、A/B ボタン、バッテリー、SD、ナビゲーションが正常でした。
> `5d731041` 同期のスモークテスト（2026-11-06）：起動、ホーム、A/B、
> About の SD サイズ/使用量/空き容量とバッテリー。
> `818a1540` 同期と依存スタックのスモークテスト（2026-11-08）：起動、
> ホーム、メニュー、リーダー、ページ送り、画面の向き、USB MSC、StarDict
> 辞書。`f8db833f` 同期のスモークテスト（2026-11-09）：起動、ホーム、
> リーダー、A/B での複数単語の切り抜き、リンク選択、画面の向き、About、
> USB MSC。スリープ/復帰は再確認していませんが、電源経路は変わっていません。
> `8276d518` 同期のスモークテスト（2026-11-10）：起動、ホーム、A/B、
> リーダーのページ送り、OTA 確認（更新なし）、フォントのダウンロードと
> インストール、画面の向き、OPDS ダウンロード、USB MSC（DABI、書き込み/
> 取り出し）、BLE の有効化/スキャン、Calibre サーバー起動。残り：
> ゴースト/バッテリー持続、スリープ/復帰、BLE の実ペアリング、Calibre の
> 完全送信、OTA の完全インストール。
> `fa17b9ca` 同期のスモークテスト（2026-11-12）：`make smoke` PASS 25 ステップ
> （ホーム、ファイルブラウザー、リーダー、TOC、リンク、脚注、切り抜き、
> 辞書）。`2.0.0-5` の本番ビルドを書き込み、ホームで起動することを確認。
> 残り：ゴースト/バッテリー持続、スリープ/復帰、BLE の実ペアリング、
> Calibre の完全送信、OTA の完全インストール。
> EPUB 読書、Wi-Fi、Web UI、書籍転送は 2026-10-28 に検証済みです。
> Calibre ワイヤレスと OTA は 2026-11-04 に検証済みです。OPDS（Project
> Gutenberg）は 2026-11-05 に検証済みです。自動スリープと表紙のスリープ
> 画面も 2026-11-05 に検証済みです。長時間読書は 2026-11-06 に 250+
> ページめくりをエラー・リークなしで確認しました。KOReader Sync は
> 2026-11-06 にローカル KOSync サーバーで検証済みです。残りは BLE
> リモコンのペアリング、スリープ電流、残像の実機目視確認です。`make smoke`
> は `2.1.0-1` のツリー（sync `a2b0d48b`、2026-11-26）で両方のボードで完全実行済みです
> （PaperDIY run `20261126-203815`、Waveshare 3.97 run `20261126-193226`）。詳細は
> [`docs/paperdiy/06-porting.md`](docs/paperdiy/06-porting.md) を参照。
>
> **ダウンストリームフォーク：** `main` は `upstream/develop` のミラーで、
> `paperdiy` が作業ブランチです。`freeink-sdk` はリポジトリに同梱している
> ため、サブモジュールなしでクローンしてビルドできます。詳細は
> [`docs/paperdiy/10-fork-maintenance.md`](docs/paperdiy/10-fork-maintenance.md)
> を参照。

## このリポジトリについて

`melastmohican/m5paperdiy-arduino-examples` のサンプルリポジトリは、パネルと
ボタンが動作することを示しています。しかしその `EpubReader` は atomic14 の
リーダーの移植で、永続化、ライブラリ、設定、Wi-Fi、ディープスリープがなく、
ページごとに全画面更新します。CrossPoint は EPUB エンジン、レイアウト、
フォント、SD キャッシュ、ライブラリ、辞書、OPDS、Calibre、KOReader Sync、
Web UI、OTA をすでに解決しています。足りなかったのは PaperDIY のボード層
です。

このリポジトリが追加するもの：

- `freeink-sdk` 内の `M5PAPER_DIY` プロファイル（画面、ボタン、バッテリー、
  電源、復帰）；
- ED047TC1 パラレルバスと **M5PM1** の EPD レールを扱う `BoardPaperDiy`；
- PaperS3 のバス（同じピン）を再利用する `paperdiyLgfxConfig`；
- M5PM1 によるバッテリー/充電状態の取得；
- PM1 の電源ボタンを `BTN_POWER` として扱い、バッテリー時はシャットダウン、
  USB 時はディープスリープして A/B で復帰；
- PSRAM のフレームバッファ（`FREEINK_FB_PSRAM`）；
- 公式ファームウェアを誤って取得しないための設定可能な OTA
  （`CROSSPOINT_OTA_RELEASES_URL`）；
- PlatformIO 環境 `paperdiy`。

## ハードウェア

| | PaperDIY |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8、240 MHz |
| Flash / PSRAM | 16 MB / 8 MB Octal |
| 画面 | ED047TC1 4.7 インチ 960×540、16 階調、8 ビットパラレルバス |
| 入力 | ユーザーボタン 2 個（GPIO4 = A、GPIO3 = B）、電源ボタンは PM1 管理 |
| 電源 | M5PM1、140 mAh バッテリー、USB-C |
| SD | SPI 接続の microSD（SCLK39 / MISO40 / MOSI38 / CS47） |
| 接続 | 2.4 GHz Wi-Fi + BLE 5 |
| 非搭載 | タッチ、フロントライト、RTC、IMU、オーディオ |

パネルバスは **M5Paper S3 とピン単位で同一**です：D0–D7 =
6,14,7,12,9,11,8,10；CL=16、LE=15、SPH=13、SPV=17、CKV=18、OE=45、PWR=46。
違いは、PaperDIY では M5PM1 の EPD レール（GPIO2、SDA41/SCL42 の I²C）が
追加で必要になることです。

### 3D ケース

M5Stack の **PaperDIY Complete Kit** には PLA プリントのケースが付属します。
現行のケースは **v21** で、[`hardware/3d/v21/`](hardware/3d/v21/) に STL で
置いています。MagSafe リング用の溝付きリアカバー、フロントフレーム、
A/B 用シーソーバー、C ボタン
（電源）用レバーを含みます。旧バージョンの
[`hardware/3d/PaperDIY_kit_completo.3mf`](hardware/3d/PaperDIY_kit_completo.3mf)
は純正の 3 個のボタンを使う公式モデルの改造版で、Bambu Studio の
プロジェクトとして開けます。

元モデル、M5Stack の MIT ライセンス、M2 ネジの注意事項は
[`hardware/README.ja.md`](hardware/README.ja.md) にあります。

## 操作（2 ボタン）

CrossPoint は 2 ボタン専用の `InputStyle::DigitalTwoButton` を使用します：

| 操作 | 動作 |
|---|---|
| **A**（GPIO4）短押し | 上 / 前ページ / 選択を上へ |
| **B**（GPIO3）短押し | 下 / 次ページ / 選択を下へ |
| **A** 長押し | 戻る / 終了 |
| **B** 長押し | 決定 / 選択 |
| **A + B** | 電源ボタン（電源メニュー / スリープ） |
| 電源短押し | 設定された動作。既定はスリープ/電源オフ（PM1 がクリックをファームウェアへ渡す） |
| 電源ダブルクリック | ハードウェア電源オフ（PM1 で有効な場合） |
| 電源約 10 秒 | ダウンロードモード（赤 LED、画面が固まることがあります） |
| 電源オフ時に電源 | 電源オン |

電源の動作は出荷ファームウェアと異なります。
`PAPERDIY_PM1_APP_POWER_BUTTON=1`（既定）では、PM1 のシングルクリック
リセットを無効にして、クリックを CrossPoint に届けます。出荷時のリセットを
使いたい場合は `-DPAPERDIY_PM1_APP_POWER_BUTTON=0` でビルドし、A+B で
スリープします。

ナビゲーションは主なハードウェア上の制約です。ボタンの再割り当て、
コンテキストショートカット、**BLE ページ送り**（ビルド済み）により、
リモコンやスマートフォンでページを送れるようにする予定です。

## 含まれる機能（CrossPoint 2.0 由来）

- **EPUB 2/3 エンジン**：CSS、画像、ハイフネーション、カーニング、表、
  脚注、章ナビゲーション、CJK ルビ、RTL、フォーカスモード、画面の向き。
- **ライブラリ**：タイトル/著者インデックス、表紙、最近読んだ本、検索、
  ファイルブラウザ、SD キャッシュ。
- **読書**：位置の保存、ブックマーク、ハイライト/切り抜き、% ジャンプ、
  自動ページ送り、テーマ、ナイトモード、書体とサイズ。
- **StarDict 辞書**と単語検索。
- **同期**：KOReader Sync、Calibre ワイヤレス、OPDS（検索とページ送り）、
  WebDAV、書籍アップロード用 Web UI、OTA。
- **形式**：`.epub`、`.xtc/.xtch`、`.txt`、`.bmp`。
- **フォント**：内蔵フォント + SD カード上の TTF/OTF。
- **国際化**：35 言語の UI（スペイン語を含む）。
- **PaperDIY**：`paperdiy` 環境で BLE HID ホスト（ページ送り）と USB
  マスストレージを有効化。

## ビルド

必要なもの：PlatformIO Core、`python3`、初回ビルド時のインターネット接続
（分離された core がプラットフォーム、フレームワーク、ツールチェーンを
ダウンロード；約 5 GB）。

```bash
make build
# 次と同等：
core="$(make -s core-dir)" && PLATFORMIO_CORE_DIR="$core" pio run -e paperdiy
```

バイナリの出力先：

```
.pio/build/paperdiy/firmware.bin          # アプリ（オフセット 0x10000）
.pio/build/paperdiy/firmware.factory.bin  # 完全イメージ（オフセット 0x0）
```

グローバルの `~/.platformio` が正常なら `pio run -e paperdiy` でもビルド
できます。`Makefile` は分離された core を使うため、古いパッケージがあっても
再現性のあるビルドになります。core は `scripts/pio_core_dir.py` が選びます。
固定したプラットフォームのバージョンごとに 1 つ、リポジトリの外に置かれます
（例：`~/.platformio-cores/pioarduino-55.03.311`、`make -s core-dir` でパスを
表示）。そのバージョンのすべてのクローンと worktree で共有されるため、
約 5 GB のダウンロードはバージョンごとに 1 回だけです。別のバージョンは別の
core を使います。`custom_sdkconfig` を使う環境（`default`、`slim`、`sticky`
など）は、pioarduino が core の中でフレームワークを再ビルドするため、引き続き
チェックアウト内の `.platformio-core/` を使います。別のフォルダを使うには
`make build CORE_DIR=/パス` とします。

`custom_sdkconfig` を使う環境をビルドしない場合、以前のビルドが残した
`.platformio-core/` はもう使われないので削除できます。プラットフォームのバージョンを上げたら、
どのブランチも使わなくなった古い core を `~/.platformio-cores` から削除して
ください。core を削除すると、そのバージョンのすべてのチェックアウトが再び
ダウンロードします。`.pio/` はローカルキャッシュ（git 管理外）で、
`make build` で再生成されます。

## 書き込み

1. PaperDIY を USB-C で接続します。
2. 電源ボタンを約 10 秒長押しし、赤 LED が点滅するまで待ちます
   （ダウンロードモード）。
3. 初回インストール（ブートローダーとパーティションテーブルを含む完全
   イメージ）：

```bash
make flash-factory PORT=/dev/cu.usbmodemXXXX
```

アプリのみ更新（ブートローダー/パーティションを保持）：

```bash
make flash PORT=/dev/cu.usbmodemXXXX
```

手動で行う場合：

```bash
# アプリ更新（ブートローダー/パーティションを保持）
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x10000 .pio/build/paperdiy/firmware.bin

# 初回インストール / 復旧（完全イメージ）
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x0 .pio/build/paperdiy/firmware.factory.bin
```

初回書き込み前に元のファームウェアをバックアップしてください：

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  read_flash 0 0x1000000 paperdiy-original.bin
```

## Waveshare ESP32-S3-ePaper-3.97（実験的）

[Waveshare ESP32-S3-ePaper-3.97](https://www.waveshare.com/esp32-s3-epaper-3.97.htm)
はこのフォークの 2 台目のボードです。同じファームウェアを専用の env
（`ws397`）で動かします。サポートは、まだマージされていない上流の PR に基づいています。

| | Waveshare 3.97 |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8、240 MHz |
| フラッシュ / PSRAM | 16 MB / 8 MB Octal |
| 画面 | 3.97 インチ 800×480 白黒、SPI 接続の SSD1677 コントローラー、LUT による階調表示 |
| 入力 | 側面のロッカー（上 / OK / 下）と BOOT。PWR キーはファームウェアに届きません |
| 電源 | AXP2101 PMIC（刻印は TG28）：バッテリーと充電 |
| SD | 4 ビット SDMMC の microSD |
| その他 | PCF85063 時計、QMI8658 IMU、2.4 GHz Wi-Fi + BLE 5。ES8311 オーディオは未使用 |

| キー | 動作 |
|---|---|
| 上 / 下 | 選択の移動、ページ送り |
| OK | 決定 |
| BOOT 短押し | 戻る |
| BOOT 長押し | スリープ |
| スリープ中に BOOT | 復帰（少し押し続けてください） |

前面ボタンがないため、ボタンヒントの行は表示されません。

**インストール：** 出荷時のファームウェアを残したい場合は、先にバックアップしてください
（私たちの個体では、esptool でフラッシュ全体を一度に読み出すと失敗しました。下のリンク先を参照）。
そのうえでリリースから `crosspoint-ws397-latest.bin` をダウンロードし、
USB-C で接続した状態で書き込みます。

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX write-flash 0x0 crosspoint-ws397-latest.bin
```

`0x0` に書き込むと以前のファームウェアの設定は消えますが、SD の本は残ります。
以降のバージョンは `Check for Updates`（UI は英語表示）で入手できます（リリース内の
`crosspoint-ws397-<バージョン>-ota.bin` を探します）。このファイルを SD のルートにコピーして
`SD Card Firmware Update` を使うこともできます。自分でビルドする場合は
`make flash ENV=ws397` を使います。`File Transfer → USB Drive` で SD をパソコンにマウントできます。
このボードには M5Burner と M5Launcher はありません。

詳細、書き込み、バックアップ、制限事項は
[`docs/paperdiy/15-waveshare-397.md`](docs/paperdiy/15-waveshare-397.md)（スペイン語）を参照してください。

## 構成

```
.
├── src/                  # CrossPoint アプリ（アクティビティ、リーダー、UI、ネットワーク）
├── lib/                  # Epub、GfxRenderer、EpdFont、HAL など
├── freeink-sdk/          # ハードウェア SDK + ボードプロファイル
│   └── libs/hardware/
│       ├── BoardConfig/  # M5PAPER_DIY + M5Pm1
│       └── BoardPaperDiy/# ED047TC1 バス、PM1 レール、電源オフ
├── docs/paperdiy/        # 調査、ハードウェア、ロードマップ、移植
├── docs/upstream/        # CrossPoint の元 README/ユーザーガイド
├── hardware/3d/          # 3D ケース（v21 と Complete Kit 改造版）
├── platformio.ini        # `paperdiy` 環境
└── Makefile
```

## ドキュメント

詳細ドキュメントはスペイン語です。[ドキュメント索引](docs/paperdiy/README.ja.md)、
[ユーザーガイド](docs/paperdiy/07-user-guide.ja.md)、
[ハードウェア](docs/paperdiy/01-hardware.ja.md)、
[移植メモ](docs/paperdiy/06-porting.ja.md) は日本語でも利用できます。

- [調査と現在の状態](docs/paperdiy/00-research.md)
- [ハードウェアとピン](docs/paperdiy/01-hardware.md)
- [POC とエコシステム分析](docs/paperdiy/02-current-state.md)
- [機能マトリクス](docs/paperdiy/03-feature-matrix.md)
- [アーキテクチャ](docs/paperdiy/04-architecture.md)
- [ロードマップ](docs/paperdiy/05-roadmap.md)
- [移植メモと検証](docs/paperdiy/06-porting.md)
- [PaperDIY ユーザーガイド](docs/paperdiy/07-user-guide.md)
- [ソース](docs/paperdiy/08-sources.md)
- [先行事例：issue #4005 と PaperDIY PR](docs/paperdiy/09-prior-art.md)
- [フォークの維持と上流の更新](docs/paperdiy/10-fork-maintenance.md)
- [issue #4005 向けコメント草稿](docs/paperdiy/11-upstream-note.md)
- [USB テスト（スペイン語）](docs/paperdiy/12-serial-testing.md)
- [Waveshare ESP32-S3-ePaper-3.97、実験的（スペイン語）](docs/paperdiy/15-waveshare-397.md)

## 既知の制限

- 未測定：LUT、ページを重ねた後の残像、スリープ電流。バッテリー駆動時間は
  拡張 604050（1500 mAh）のみ実測（放電試験で 45.4 時間 / 5,448 ページ）。
  元の 140 mAh キットセルはこの試験では未測定で、両方のカーブは通常読書での
  検証が残っています。
- タッチ、フロントライト、RTC、IMU、オーディオは非搭載。UI は 2 ボタンで
  操作できる必要があります。
- 140 mAh バッテリー：スリープ時にファームウェアが PM1 へ電源オフを
  要求します。PM1 が電源を切る場合（USB 接続時も含め通常はこちら）、
  電源ボタンでのみ再起動できます。2026-11-05 の検証では、USB 接続中の
  A+B で PM1 が電源を切り、A では復帰しませんでした。USB が基板を維持
  する場合はディープスリープのフォールバックとなり、A/B で復帰します。
- 物理電源ボタンは M5PM1 が管理し、ファームウェアには GPIO ではなく I²C
  イベントとして届きます。
- `paperdiy` 環境の OTA はこのリポジトリのリリース
  （`CROSSPOINT_OTA_RELEASES_URL`）を確認し、`crosspoint-paperdiy-<version>-ota.bin`
  （`CROSSPOINT_OTA_ASSET_FORMAT`）をダウンロードします。どちらも
  `platformio.ini` で設定します。
- CrossPoint 2.0 は開発ブランチ（2.0.0）であり、安定版の 1.6.x では
  ありません。

## クレジットとライセンス

ソースコードは MIT です。エンジンと大部分のコードは
[CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
（Copyright 2025 CrossPoint Reader organization）由来です。ハードウェア SDK は
[FreeInk](https://github.com/Free-Ink/freeink-sdk)（MIT）、パネルは
M5GFX/LovyanGFX で制御しています。サードパーティのライブラリはそれぞれの
ライセンスに従います。

**ビルド済みファームウェア**（リリースと M5Burner の `.bin`）は wolfSSL を
含むため **GPLv3** です。各リリースには、ライセンス全文、サードパーティの
表示、ソースのリビジョンをまとめた `LICENSE` を添付しています。
[`licenses/README.md`](licenses/README.md) を参照してください。

3D ケースは [M5Stack](https://github.com/m5stack/M5_Hardware) の MIT モデルの
改造版で、こちらも MIT です。[LICENSE](LICENSE) と [NOTICE](NOTICE) を参照
してください。

> これはスペイン語 README の翻訳です。内容が異なる場合はスペイン語版を
> 優先します。詳細ドキュメントは現在スペイン語のみです。
