import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import serial.tools.list_ports
from collections import deque
import time
from tkinter import messagebox, filedialog
#import scipy.signal as signal
from tkinter import scrolledtext
import statistics

# 設定參數
sampling_rate = 1000
display_seconds = 0.5
data_points = int(sampling_rate * display_seconds)
#fir_coeff = signal.firwin(100, [0.03, 0.8], pass_zero=False)

# 初始化空數據陣列
voltage_data = deque(maxlen=data_points)

# 自動檢測 Arduino 的 COM 埠
def detect_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB-SERIAL" in port.description or "CP210" in port.description or "Arduino" in port.description:
            return port.device
    return None

def update_status(new_status):
    status_var.set(new_status)

def show_about():
    root.after(0, lambda: messagebox.showinfo("About", "This GUI app is a simple oscilloscope for MCU."))

def show_code():
    firmware_code = """
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
    
    // 將 ADC 數值轉換為電壓值
    //voltage_buffer[index] = (raw / 4095.0) * 3.3;

    //Serial.print("Raw: ");
    //Serial.print(i_buffer[index]);
    //Serial.print("\tVoltage: ");
    Serial.println(raw);  // 保留4位小數
    
    index++;
    
    if (index >= BUFFER_SIZE) {
      index = 0;  // 重置索引
    }
  }
}
    """
    code_window = tk.Toplevel(root)
    code_window.title("Firmware Code")
    text = scrolledtext.ScrolledText(code_window, wrap=tk.NONE, height=20, width=80, font=("Times New Roman", 10))
    text.insert(tk.END, firmware_code)
    text.configure(state='disabled')
    text.pack()

def save_code(code):
    with open("firmware_code.txt", "w") as file:
        file.write(code)
    print("Code saved to firmware_code.txt")

def copy_code(code):
    root.clipboard_clear()
    root.clipboard_append(code)
    root.update()
    print("Code copied to clipboard")




# 添加串行連接管理功能
def manage_serial_connection():
    port = detect_esp32_port()
    ports = [p.device for p in serial.tools.list_ports.comports()]
    selected_port = tk.StringVar(value=port)

    def connect():
        port = selected_port.get()
        update_status(f"Connecting to {port}...")
        threading.Thread(target=read_data, args=(port,), daemon=True).start()

    conn_window = tk.Toplevel(root)
    conn_window.title("Serial Connection Manager")
    ttk.Label(conn_window, text="Select COM Port:").pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Combobox(conn_window, values=ports, textvariable=selected_port).pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(conn_window, text="Connect", command=connect).pack(side=tk.LEFT, padx=5, pady=5)

# 保存數據到 CSV 文件
def save_data():
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filename:
        with open(filename, 'w') as file:
            file.write("Voltage (V),Frequency (Hz)\n")
            for i, v in enumerate(voltage_data):
                file.write(f"{v},{spectrum_data[i] if i < len(spectrum_data) else ''}\n")
        messagebox.showinfo("Save Data", "Data saved successfully.")

# 數據分析工具
def analyze_data():
    if voltage_data:
        max_val = max(voltage_data)
        min_val = min(voltage_data)
        mean_val = statistics.mean(voltage_data)
        std_dev = statistics.stdev(voltage_data)

        analysis_text = f"Max Voltage: {max_val:.4f} V\nMin Voltage: {min_val:.4f} V\nMean Voltage: {mean_val:.4f} V\nStd Deviation: {std_dev:.4f} V"
        messagebox.showinfo("Data Analysis", analysis_text)
    else:
        messagebox.showinfo("Data Analysis", "No data available for analysis.")

# 建立 tkinter 視窗
root = tk.Tk()
root.title("MCU Oscilloscope - Ready")

menu_bar = tk.Menu(root)

menu_bar.add_command(label="About", command=show_about)
menu_bar.add_command(label="Firmware", command=show_code)
menu_bar.add_command(label="Serial Connection", command=manage_serial_connection)
menu_bar.add_command(label="Analyze Data", command=analyze_data)
menu_bar.add_command(label="Save Data", command=save_data)
menu_bar.add_command(label="Exit", command=root.quit)



root.config(menu=menu_bar)

# 建立 Matplotlib 圖表
fig_voltage = Figure(figsize=(5, 2), dpi=100)
ax_voltage = fig_voltage.add_subplot(111)
ax_voltage.set_title("Voltage")
ax_voltage.set_xlabel("Time (s)", fontsize=12)
ax_voltage.set_ylabel("Voltage (V)", fontsize=12)
ax_voltage.set_xlim(0, display_seconds)
ax_voltage.set_ylim(-5, 5)
ax_voltage.set_facecolor('#000000')  # 設定背景顏色
ax_voltage.grid(color='gray', linestyle='--', linewidth=0.5)
ax_voltage.tick_params(axis='x')
ax_voltage.tick_params(axis='y')

fig_spectrum = Figure(figsize=(5, 2), dpi=100)
ax_spectrum = fig_spectrum.add_subplot(111)
ax_spectrum.set_title("Spectrum")
ax_spectrum.set_xlabel("Frequency (Hz)", fontsize=12)
ax_spectrum.set_ylabel("Amplitude", fontsize=12)
ax_spectrum.set_xlim(0, sampling_rate // 2)
ax_spectrum.set_ylim(0, 1)
ax_spectrum.set_facecolor('#000000')
ax_spectrum.grid(color='gray', linestyle='--', linewidth=0.5)
ax_spectrum.tick_params(axis='x')
ax_spectrum.tick_params(axis='y')

# 將圖表嵌入 tkinter，上下佈局
canvas_voltage = FigureCanvasTkAgg(fig_voltage, master=root)
canvas_voltage.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

canvas_spectrum = FigureCanvasTkAgg(fig_spectrum, master=root)
canvas_spectrum.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
start_t = time.time()

# 資料讀取函數
def read_data(port):
    global voltage_data, spectrum_data
    partial_line = ''
    if port is None:
        print("Port not found!")
        return
    
    ser = serial.Serial(port, 115200)
    ser.flush()
    count = 0
    while True:
        if ser.in_waiting:
            # 讀取緩衝區內所有資料
            data = partial_line + ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            
            lines = data.split('\n')
            partial_line = lines[-1]
            
            for line in lines[:-1]:
                count += 1
                try:
                    voltage = float(line) / 4095 * 3.3
                    voltage_data.append(voltage)
                except ValueError:
                    continue

def update_plots():
    global voltage_data, spectrum_data
    if len(voltage_data) < 500:
        root.after(200, update_plots)
        return
    #filtered_data = signal.lfilter(fir_coeff, 1.0, np.array(voltage_data))
    filtered_data = np.array(voltage_data)
    ax_voltage.clear()
    ax_voltage.plot(np.array(filtered_data)[100:], color='#00ff00', linewidth=1.5)
    ax_voltage.set_title("Voltage", fontsize=14)
    ax_voltage.set_xlabel("Time (s)", fontsize=12)
    ax_voltage.set_ylabel("Voltage (V)", fontsize=12)
    #ax_voltage.set_ylim(-1, 4)
    ax_voltage.set_ylim(-4,4)
    ax_voltage.set_facecolor('#000000')
    ax_voltage.grid(color='gray', linestyle='--', linewidth=0.5)
    ax_voltage.tick_params(axis='x')
    ax_voltage.tick_params(axis='y')
    canvas_voltage.draw()
    
    if len(voltage_data) > 400:
        spectrum_data = np.abs(np.fft.fft(filtered_data[-100:]))
        ax_spectrum.clear()
        ax_spectrum.plot(spectrum_data[3:], color='#00ff00', linewidth=1.5)
        ax_spectrum.set_title("Spectrum", fontsize=14)
        ax_spectrum.set_xlabel("Frequency (Hz)", fontsize=12)
        ax_spectrum.set_ylabel("Amplitude", fontsize=12)
        ax_spectrum.set_ylim(0, 50)
        ax_spectrum.set_facecolor('#000000')
        ax_spectrum.grid(color='gray', linestyle='--', linewidth=0.5)
        ax_spectrum.tick_params(axis='x')
        ax_spectrum.tick_params(axis='y')
        canvas_spectrum.draw()
        print(np.argmax(spectrum_data[5:30]))

    root.after(1, update_plots)

def check_connection():
    port = detect_esp32_port()
    if port is None:
        update_status("Error: ESP32 not found!")
        messagebox.showerror("Connection Error", "ESP32 not found. Please connect the device and try again.")
    else:
        update_status(f"ESP32 Connected on {port}")
        threading.Thread(target=read_data, args=(port,), daemon=True).start()

status_var = tk.StringVar()
status_var.set("Ready")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

update_plots()
check_connection()
root.mainloop()
