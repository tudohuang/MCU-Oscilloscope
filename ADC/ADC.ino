#include <Arduino.h>
#include "driver/adc.h"
#include "esp_adc_cal.h"

#define SAMPLE_RATE 1000  // 取樣率 (10 kHz)
#define BUFFER_SIZE 1024   // 緩衝區大小

#define ADC1_I_CHANNEL ADC1_CHANNEL_6  // GPIO 34

int16_t i_buffer[BUFFER_SIZE];
float voltage_buffer[BUFFER_SIZE];
unsigned long lastSampleTime = 0;  // 上次取樣的時間
unsigned long sampleInterval = 1000000 / SAMPLE_RATE;  // 取樣間隔（微秒）

void setupADC() {
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_I_CHANNEL, ADC_ATTEN_DB_11);
}

void setup() {
  Serial.begin(115200);
  setupADC();
  Serial.println("ADC initialized");
}

void loop() {
  static int index = 0;
  
  // 檢查是否到達取樣時間
  if (micros() - lastSampleTime >= sampleInterval) {
    lastSampleTime = micros();
    int raw = adc1_get_raw(ADC1_I_CHANNEL);
    i_buffer[index] = raw;
    
    Serial.println(raw);  // 保留4位小數
  
    index++;
    
    if (index >= BUFFER_SIZE) {
      index = 0;  // 重置索引
    }
  }
}
