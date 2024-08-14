
# MCU Oscilloscope

This is a simple oscilloscope application built using Python and Tkinter, designed to read and display voltage data from a microcontroller (such as an ESP32) via its ADC. The application can automatically detect the connected microcontroller and display real-time voltage waveforms and spectrum analysis.

## Features

- **Real-time Voltage Waveform Display**: Displays real-time voltage data from the microcontroller's ADC.
- **Spectrum Analysis**: Performs FFT on the voltage data and displays a spectrum graph.
- **Data Analysis Tool**: Calculates and displays the **max**, **min**, **mean**, and **standard deviation** of the voltage data.
- **Data Saving**: Allows saving voltage and spectrum data as a CSV file.
- **Serial Connection Management**: Automatically detects and connects to the microcontroller's COM port.
- **Firmware Code Viewer**: Allows viewing and copying the microcontroller firmware code.

## Installation and Running

### Prerequisites

Before running this application, ensure you have installed the following Python libraries:

```plaintext
- matplotlib
- numpy
- pyserial
```

You can install these libraries using the following command:

```bash
pip install -r requirements.txt
```

### Running the Application

1. **Clone or download** this project to your local machine.

2. Open a **terminal** or **command prompt** and navigate to the project directory.

3. Run the following command to start the application:

   ```bash
   python main.py
   ```

4. Once the application starts, it will automatically detect the connected ESP32 or other microcontrollers and begin reading voltage data.

## Usage Instructions

1. **Connect Device**: The application will automatically detect the connected ESP32. If it fails to connect automatically, use the <kbd>Serial Connection</kbd> option to manually select the COM port and connect.

2. **View Data**: In the main window, you'll see real-time voltage waveform and spectrum plots. These plots will update based on the data received from the microcontroller.

3. **Analyze Data**: Use the <kbd>Analyze Data</kbd> option to view statistical information about the voltage data, including the **maximum**, **minimum**, **mean**, and **standard deviation**.

4. **Save Data**: You can use the <kbd>Save Data</kbd> option to save the current voltage and spectrum data to a CSV file.

5. **View and Copy Firmware Code**: Use the <kdb>Firmware</kdb> option to view or copy the microcontroller firmware code used to read ADC data.

## Firmware Code

The application includes a sample Arduino firmware code suitable for an ESP32. This code initializes the ADC and sends the read voltage data to the application via the serial port. You can upload this code directly to the ESP32 to start using the application.

```cpp
#include <Arduino.h>
#include "driver/adc.h"
#include "esp_adc_cal.h"

#define SAMPLE_RATE 1000  // Sampling rate (10 kHz)
#define BUFFER_SIZE 1024   // Buffer size

#define ADC1_I_CHANNEL ADC1_CHANNEL_6  // GPIO 34

int16_t i_buffer[BUFFER_SIZE];
float voltage_buffer[BUFFER_SIZE];
unsigned long lastSampleTime = 0;  // Last sample time
unsigned long sampleInterval = 1000000 / SAMPLE_RATE;  // Sample interval (microseconds)

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

  if (micros() - lastSampleTime >= sampleInterval) {
    lastSampleTime = micros();
    int raw = adc1_get_raw(ADC1_I_CHANNEL);
    i_buffer[index] = raw;

    Serial.println(raw);  // Keep four decimal places

    index++;

    if (index >= BUFFER_SIZE) {
      index = 0;  // Reset index
    }
  }
}
```
## Pictures
![image](https://github.com/user-attachments/assets/7b59437c-d602-4442-9086-22a3f064db66)


![image](https://github.com/user-attachments/assets/04c1b93b-7918-435a-88d9-ff189b602540)

## License

This project is licensed under the **GPL License**. See the [LICENSE](LICENSE) file for details.
