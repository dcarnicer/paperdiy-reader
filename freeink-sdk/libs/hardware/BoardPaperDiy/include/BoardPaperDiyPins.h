#pragma once

// M5Stack PaperDIY pin map. The parallel-EPD bus is *identical* to the
// M5Stack PaperS3 (M5GFX board_M5PaperDIY / board_M5PaperS3 share the same
// Bus_EPD wiring); the differences are the two user buttons, the M5PM1 PMIC
// rails, and the absence of touch/RTC/IMU.

// ED047TC1 8-bit parallel data bus, D0..D7.
#define PAPERDIY_EP_D0 6
#define PAPERDIY_EP_D1 14
#define PAPERDIY_EP_D2 7
#define PAPERDIY_EP_D3 12
#define PAPERDIY_EP_D4 9
#define PAPERDIY_EP_D5 11
#define PAPERDIY_EP_D6 8
#define PAPERDIY_EP_D7 10

// Row/frame timing. Bus_EPD's stock power sequence drives OE/PWR/SPV itself;
// the PM1 GPIO2 EPD rail is raised by BoardPaperDiy::prepareEpdPower().
#define PAPERDIY_EP_SPH 13  // XSTL: start pulse, horizontal
#define PAPERDIY_EP_CL 16   // XCL: pixel clock
#define PAPERDIY_EP_LE 15   // XLE: latch enable
#define PAPERDIY_EP_SPV 17  // start pulse, vertical
#define PAPERDIY_EP_CKV 18  // vertical clock
#define PAPERDIY_EP_OE 45   // output enable
#define PAPERDIY_EP_PWR 46  // EPD rail enable (boost converter)

// Two user buttons, active-low (M5Unified BtnA = GPIO4, BtnB = GPIO3).
#define PAPERDIY_BTN_A 4
#define PAPERDIY_BTN_B 3

// M5PM1 PMIC on the internal I2C bus (shared with the EPD power rail).
#define PAPERDIY_PM1_SDA 41
#define PAPERDIY_PM1_SCL 42
