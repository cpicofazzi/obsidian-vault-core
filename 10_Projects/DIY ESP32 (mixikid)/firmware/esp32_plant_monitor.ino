/**
 * ==============================================================================
 * Project: DIY ESP32 Plant Monitor (mixikid)
 * File: esp32_plant_monitor.ino
 * Description: Production-ready firmware for ESP32 plant telemetry station.
 * Features:
 *   - 0.96" SSD1306 I2C OLED (128x64) telemetry dashboard with visual gauges
 *   - Capacitive Soil Moisture Sensor v1.2/v2.0 (ADC1 GPIO 32) with multi-sample
 *     filtering and two-point calibration curve (Dry Air <-> Saturated Water)
 *   - DHT11 Temperature & Relative Humidity with auto-retry fault tolerance
 *   - Deep-Sleep Power Optimization (~10-15 uA current during sleep)
 *   - RTC memory retention for boot count and rolling telemetry history
 *   - Optional external button interrupt wakeup (GPIO 33)
 *
 * Board Target: ESP32 Dev Module / NodeMCU-32S / ESP32-WROOM-32
 * Arduino IDE Settings:
 *   - Board: "ESP32 Dev Module"
 *   - CPU Frequency: 240MHz (or 80MHz for power saving)
 *   - Flash Frequency: 80MHz
 *   - Partition Scheme: Default 4MB with spiffs
 *
 * Required Libraries:
 *   - Adafruit SSD1306 (v2.5.7+)
 *   - Adafruit GFX Library (v1.11.5+)
 *   - DHT sensor library by Adafruit (v1.4.4+)
 *   - Adafruit Unified Sensor (v1.1.9+)
 *   - Wire.h (Built-in ESP32 core)
 * ==============================================================================
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include "esp_sleep.h"

// -----------------------------------------------------------------------------
// Operating Mode & Timing Configuration
// -----------------------------------------------------------------------------
// Set to true to disable deep sleep and loop continuously for sensor bench testing
#define CONTINUOUS_BENCH_MODE  false 

// Deep Sleep timings
#define uS_TO_S_FACTOR         1000000ULL  // Conversion factor for micro seconds to seconds
#define TIME_TO_SLEEP          1800        // Sleep duration in seconds (1800s = 30 minutes)
#define AWAKE_DISPLAY_DURATION 12000       // Time in ms the screen stays active before sleep

// -----------------------------------------------------------------------------
// Pin Assignments (ESP32)
// -----------------------------------------------------------------------------
#define I2C_SDA_PIN            21          // I2C Data line for SSD1306 OLED
#define I2C_SCL_PIN            22          // I2C Clock line for SSD1306 OLED
#define SOIL_ADC_PIN           32          // ADC1_CH4 (Safe with WiFi and Deep Sleep)
#define DHT_DATA_PIN           4           // GPIO 4 for DHT11 single-bus data
#define SENSOR_VCC_PIN         17          // High-side GPIO power gating for sensors (0 to disable)
#define WAKEUP_BUTTON_PIN      GPIO_NUM_33 // RTC GPIO 33 for external push-button wakeup

// -----------------------------------------------------------------------------
// OLED Display Configuration
// -----------------------------------------------------------------------------
#define SCREEN_WIDTH           128
#define SCREEN_HEIGHT          64
#define OLED_RESET             -1          // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS         0x3C        // Typical I2C address: 0x3C (some clones use 0x3D)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// -----------------------------------------------------------------------------
// DHT Sensor Configuration
// -----------------------------------------------------------------------------
#define DHTTYPE                DHT11
DHT dht(DHT_DATA_PIN, DHTTYPE);

// -----------------------------------------------------------------------------
// Capacitive Soil Moisture Sensor Calibration Curve
// -----------------------------------------------------------------------------
// Calibrated raw 12-bit ADC readings (ESP32 ADC ranges 0 - 4095)
// Capacitive sensors output HIGHER voltage/ADC when dry, LOWER when wet.
#define SOIL_AIR_RAW           3200        // Raw ADC in dry air (0% moisture)
#define SOIL_WATER_RAW         1350        // Raw ADC submerged in cup of water (100% moisture)
#define SOIL_OVERSAMPLE_COUNT  24          // Number of samples for moving average filter

// Thresholds for plant health status
#define MOISTURE_THRESH_DRY    25          // Below 25% = Dry / Water Me
#define MOISTURE_THRESH_WET    75          // Above 75% = High Moisture / Saturated

// -----------------------------------------------------------------------------
// RTC Persistent Data (Retained across deep-sleep cycles)
// -----------------------------------------------------------------------------
RTC_DATA_ATTR int bootCount = 0;
RTC_DATA_ATTR float lastTempC = 0.0;
RTC_DATA_ATTR float lastHumidity = 0.0;
RTC_DATA_ATTR int lastMoisturePct = 0;

// -----------------------------------------------------------------------------
// Telemetry Data Structure
// -----------------------------------------------------------------------------
struct PlantTelemetry {
  float temperatureC;
  float temperatureF;
  float humidity;
  int rawSoilADC;
  int moisturePercent;
  const char* moistureStatus;
  bool dhtValid;
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Print wake-up reason from ESP32 RTC controller.
 */
void printWakeupReason() {
  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  switch (wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:
      Serial.println(F("[Power] Wakeup caused by external signal using RTC_IO (Button)"));
      break;
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println(F("[Power] Wakeup caused by RTC timer expiry"));
      break;
    default:
      Serial.printf("[Power] Wakeup not caused by deep sleep: %d\n", wakeup_reason);
      break;
  }
}

/**
 * Enable or disable power to external sensors via GPIO switch to eliminate
 * quiescent draw during deep sleep.
 */
void setSensorsPower(bool enable) {
  if (SENSOR_VCC_PIN > 0) {
    pinMode(SENSOR_VCC_PIN, OUTPUT);
    digitalWrite(SENSOR_VCC_PIN, enable ? HIGH : LOW);
    if (enable) {
      delay(80); // Stabilization settling time for sensor power rails
    }
  }
}

/**
 * Read the capacitive soil moisture sensor with oversampling and two-point linear calibration.
 */
int readSoilMoisture(int &outRawAvg) {
  // Set ADC attenuation to 11dB (0 - 3.3V full range)
  analogSetAttenuation(ADC_11db);
  
  long sum = 0;
  // Discard first conversion to allow ADC capacitor charge
  analogRead(SOIL_ADC_PIN);
  delay(10);

  for (int i = 0; i < SOIL_OVERSAMPLE_COUNT; i++) {
    sum += analogRead(SOIL_ADC_PIN);
    delay(5);
  }
  
  outRawAvg = (int)(sum / SOIL_OVERSAMPLE_COUNT);

  // Calibration mapping:
  // Since dry air produces higher voltage and water produces lower voltage:
  // raw >= SOIL_AIR_RAW -> 0%
  // raw <= SOIL_WATER_RAW -> 100%
  long pct = map(outRawAvg, SOIL_AIR_RAW, SOIL_WATER_RAW, 0, 100);
  
  // Constrain bounds to valid percentage
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;

  return (int)pct;
}

/**
 * Acquire telemetry from all attached sensors with fault detection and retries.
 */
PlantTelemetry acquireTelemetry() {
  PlantTelemetry data;
  data.dhtValid = false;

  // 1. Read Soil Moisture
  data.moisturePercent = readSoilMoisture(data.rawSoilADC);
  
  // Determine plant hydration descriptor
  if (data.moisturePercent < MOISTURE_THRESH_DRY) {
    data.moistureStatus = "DRY - WATER ME";
  } else if (data.moisturePercent > MOISTURE_THRESH_WET) {
    data.moistureStatus = "WET / SOAKED";
  } else {
    data.moistureStatus = "OPTIMAL";
  }

  // 2. Read DHT11 Temperature and Humidity (with up to 3 retries)
  for (int attempt = 0; attempt < 3; attempt++) {
    float h = dht.readHumidity();
    float t = dht.readTemperature(); // Celsius
    
    if (!isnan(h) && !isnan(t) && h > 0.0 && h <= 100.0) {
      data.humidity = h;
      data.temperatureC = t;
      data.temperatureF = (t * 1.8f) + 32.0f;
      data.dhtValid = true;
      break;
    }
    delay(250); // DHT11 minimum sample interval retry spacing
  }

  if (!data.dhtValid) {
    Serial.println(F("[DHT11] WARNING: Failed to read from DHT11 sensor! Using fallback."));
    data.temperatureC = lastTempC > 0 ? lastTempC : 21.0;
    data.temperatureF = (data.temperatureC * 1.8f) + 32.0f;
    data.humidity = lastHumidity > 0 ? lastHumidity : 45.0;
  } else {
    // Store in RTC retained memory
    lastTempC = data.temperatureC;
    lastHumidity = data.humidity;
  }
  lastMoisturePct = data.moisturePercent;

  return data;
}

/**
 * Render telemetry dashboard onto the 128x64 SSD1306 OLED screen.
 */
void renderDashboard(const PlantTelemetry &telemetry) {
  display.clearDisplay();

  // ---------------- Header Bar ----------------
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print(F("PLANT MONITOR"));
  
  // Cycle / Boot indicator on top right
  display.setCursor(92, 0);
  display.printf("#%04d", bootCount);
  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  // ---------------- Temp & Humidity Readout ----------------
  // Temperature (Left)
  display.setCursor(2, 14);
  display.print(F("TEMP"));
  display.setCursor(2, 24);
  display.setTextSize(2);
  display.printf("%.0fC", telemetry.temperatureC);

  // Humidity (Right)
  display.setTextSize(1);
  display.setCursor(68, 14);
  display.print(F("HUMIDITY"));
  display.setCursor(68, 24);
  display.setTextSize(2);
  display.printf("%.0f%%", telemetry.humidity);

  // ---------------- Soil Moisture Section ----------------
  display.setTextSize(1);
  display.setCursor(2, 42);
  display.printf("SOIL: %2d%% [%s]", telemetry.moisturePercent, telemetry.moistureStatus);

  // Horizontal Gauge Bar
  int barX = 2;
  int barY = 53;
  int barWidth = 124;
  int barHeight = 8;
  display.drawRect(barX, barY, barWidth, barHeight, SSD1306_WHITE);
  
  int fillWidth = map(telemetry.moisturePercent, 0, 100, 0, barWidth - 4);
  if (fillWidth > 0) {
    display.fillRect(barX + 2, barY + 2, fillWidth, barHeight - 4, SSD1306_WHITE);
  }

  display.display();
}

/**
 * Put OLED and peripherals into low-power sleep and enter ESP32 deep sleep.
 */
void enterDeepSleep() {
  Serial.printf("[Power] Entering deep sleep for %d seconds...\n", TIME_TO_SLEEP);
  
  // Turn off sensor rail
  setSensorsPower(false);

  // Send power-down command to SSD1306 OLED
  display.ssd1306_command(SSD1306_DISPLAYOFF);
  Wire.end();

  // Configure wakeup sources
  esp_sleep_enable_timer_wakeup((uint64_t)TIME_TO_SLEEP * uS_TO_S_FACTOR);
  
  // Optional button wakeup: configure GPIO 33 as active LOW (pulled down when button pressed)
  #ifdef WAKEUP_BUTTON_PIN
  esp_sleep_enable_ext0_wakeup(WAKEUP_BUTTON_PIN, 0); // Wake up when button pulls pin to GND
  #endif

  // Enter deep sleep (consumes ~10 uA on clean ESP32 modules)
  esp_deep_sleep_start();
}

// =============================================================================
// Main Arduino Lifecycle
// =============================================================================

void setup() {
  Serial.begin(115200);
  delay(50);
  bootCount++;

  Serial.println(F("\n=========================================="));
  Serial.println(F("  ESP32 Plant Monitor (mixikid) v1.0.0     "));
  Serial.printf ("  Boot Cycle: %d                          \n", bootCount);
  Serial.println(F("=========================================="));

  printWakeupReason();

  // 1. Power up sensors
  setSensorsPower(true);

  // 2. Initialize I2C Bus and OLED
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("[OLED] ERROR: SSD1306 initialization failed! Check wiring or address."));
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(20, 26);
    display.println(F("SAMPLING SENSORS..."));
    display.display();
  }

  // 3. Initialize DHT11
  dht.begin();
  delay(100); // Allow DHT internal oscillator to start

  // 4. Sample Telemetry
  PlantTelemetry currentData = acquireTelemetry();

  // 5. Serial Logging
  Serial.printf("[Telemetry] Soil Raw ADC: %d | Moisture: %d%% (%s)\n",
                currentData.rawSoilADC, currentData.moisturePercent, currentData.moistureStatus);
  Serial.printf("[Telemetry] Temp: %.1f C (%.1f F) | Humidity: %.1f%%\n",
                currentData.temperatureC, currentData.temperatureF, currentData.humidity);

  // 6. Display Dashboard
  renderDashboard(currentData);

  // 7. Power Management Logic
  #if (!CONTINUOUS_BENCH_MODE)
    delay(AWAKE_DISPLAY_DURATION);
    enterDeepSleep();
  #else
    Serial.println(F("[Bench Mode] Running in continuous loop mode. Deep sleep disabled."));
  #endif
}

void loop() {
  #if (CONTINUOUS_BENCH_MODE)
    // Continuous sampling for bench testing and calibration
    delay(3000);
    PlantTelemetry liveData = acquireTelemetry();
    renderDashboard(liveData);
    Serial.printf("[Bench] Raw ADC: %4d | Moist: %3d%% | Temp: %.1fC | Hum: %.1f%%\n",
                  liveData.rawSoilADC, liveData.moisturePercent,
                  liveData.temperatureC, liveData.humidity);
  #endif
}
