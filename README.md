# ESP32-S3 ECG Monitor

**Real-Time ECG Monitoring and Heart-Rate Detection using ESP32-S3, MicroPython, GLCD, and Proteus Simulation**

---

## Overview

This project implements a real-time ECG monitoring and heart-rate estimation system using an **ESP32-S3**, **MicroPython**, a **128×64 LGM12641BS1R GLCD**, and **Proteus simulation**.

ECG samples are transmitted from a Python application through UART to the simulated ESP32-S3. The firmware processes the incoming ECG signal, detects waveform peaks, estimates heart rate from RR intervals, determines a simple ECG status, and displays the waveform and calculated information on the GLCD.

The project demonstrates the integration of:

* Embedded ECG signal processing
* UART-based biomedical data transmission
* Real-time ECG waveform visualization
* Heart-rate estimation
* MicroPython embedded development
* ESP32-S3 simulation
* KS0108-style GLCD interfacing
* Python serial communication
* Proteus-based embedded-system simulation

> **Disclaimer:** This is an educational and engineering simulation project. It is not a medical device and must not be used for diagnosis, treatment, patient monitoring, or clinical decision-making.

---

## Demo

A 30-second demonstration video is included in the repository.

The demonstration shows:

* ECG data transmission
* Real-time ECG waveform visualization
* Heart-rate estimation
* ECG status display
* NORMAL → TACHY → BRADY test sequence

### Demo Video

`media/ECG_Arrhythmia_Detector_GitHub_30s.mp4`

---

## System Architecture

```text
                 ECG Dataset
                     │
                     ▼
          ┌─────────────────────┐
          │ Python ECG          │
          │ Transmitter         │
          │                     │
          │ 128 Hz              │
          │ 115200 baud         │
          └──────────┬──────────┘
                     │
                     │ UART
                     │
                     ▼
          ┌─────────────────────┐
          │ ESP32-S3            │
          │ MicroPython         │
          │                     │
          │ • ECG reception     │
          │ • Peak detection    │
          │ • RR calculation    │
          │ • HR estimation     │
          │ • Status detection  │
          └──────────┬──────────┘
                     │
                     │ GPIO
                     ▼
          ┌─────────────────────┐
          │ LGM12641BS1R         │
          │ 128 × 64 GLCD        │
          │                     │
          │ • ECG waveform      │
          │ • Heart rate        │
          │ • ECG status        │
          └─────────────────────┘

                 Proteus
              Simulation Layer
```

The serial port is configurable and depends on the virtual COM-port configuration of the host computer.

---

## Main Features

* ESP32-S3 based ECG monitoring
* MicroPython firmware
* LGM12641BS1R 128×64 GLCD
* KS0108-style 8-bit parallel interface
* UART ECG streaming
* 128 Hz ECG sampling
* Real ECG datasets
* ECG peak detection
* RR interval calculation
* Heart-rate estimation
* Rolling RR interval history
* NORMAL / TACHY / BRADY status display
* Real-time ECG waveform rendering
* Python ECG transmitter
* Proteus simulation
* Lightweight GLCD refresh architecture
* 30-second demonstration sequence

---

## Repository Structure

The current repository is intentionally kept simple so the main project components can be opened directly from the repository root.

```text
ESP32-S3-ECG-Monitor/
│
├── README.md
├── main.py
├── send_ecg_30s.py
│
├── ecg_normal_10s.txt
├── ecg_tachy_10s.txt
├── ecg_brady_10s.txt
│
├── ECG Arrhythmia Detector.pdsprj
├── ECG Arrhythmia Detector.png
│
└── media/
    └── ECG_Arrhythmia_Detector_GitHub_30s.mp4
```

### Main Files

| File                                           | Description                   |
| ---------------------------------------------- | ----------------------------- |
| `main.py`                                      | ESP32-S3 MicroPython firmware |
| `send_ecg_30s.py`                              | Python ECG serial transmitter |
| `ecg_normal_10s.txt`                           | Normal ECG dataset            |
| `ecg_tachy_10s.txt`                            | Tachycardia test dataset      |
| `ecg_brady_10s.txt`                            | Bradycardia test dataset      |
| `ECG Arrhythmia Detector.pdsprj`               | Proteus simulation project    |
| `ECG Arrhythmia Detector.png`                  | Proteus/project image         |
| `media/ECG_Arrhythmia_Detector_GitHub_30s.mp4` | Demonstration video           |

---

# Hardware

## Microcontroller

### ESP32-S3

The ESP32-S3 executes the MicroPython firmware and performs:

* UART reception
* ECG sample processing
* Peak detection
* RR interval calculation
* Heart-rate estimation
* ECG status determination
* GLCD control
* Real-time waveform rendering

---

## Display

### LGM12641BS1R 128×64 GLCD

The project uses a 128×64 graphical LCD with a KS0108-style interface.

The interface contains:

* 8-bit data bus
* Controller select signals
* Data/Instruction control
* Read/Write control
* Enable signal
* Reset signal

---

# GLCD Pin Mapping

The following is the **tested and working pin configuration** used by the Proteus simulation.

| GLCD Signal | ESP32-S3 GPIO |
| ----------- | ------------: |
| BD0         |         GPIO4 |
| BD1         |         GPIO5 |
| BD2         |         GPIO6 |
| BD3         |         GPIO7 |
| BD4         |         GPIO8 |
| BD5         |         GPIO9 |
| BD6         |        GPIO10 |
| BD7         |        GPIO11 |
| DI          |        GPIO12 |
| R/W         |        GPIO13 |
| E           |        GPIO14 |
| CS1         |        GPIO15 |
| CS2         |        GPIO16 |
| RST         |        GPIO17 |

> **Important:** Keep this mapping unchanged when reproducing the current Proteus simulation.

---

# ECG Data

The project uses ECG datasets for testing rather than generating a simple mathematical sine wave.

Three test conditions are included:

```text
ecg_normal_10s.txt
ecg_tachy_10s.txt
ecg_brady_10s.txt
```

Each dataset contains:

* 1280 ECG samples
* 128 samples/second
* 10 seconds of ECG data

### Sampling Configuration

```text
Sampling frequency : 128 Hz
Samples/second     : 128
Samples/stage      : 1280
Stage duration     : 10 seconds
```

The complete demonstration contains three stages:

```text
NORMAL
   ↓
TACHY
   ↓
BRADY
```

Total demonstration duration:

```text
3 × 10 seconds = 30 seconds
```

---

# ECG Processing

The ESP32-S3 processes ECG samples as they arrive through UART.

The firmware uses a lightweight peak-detection approach based on:

* Amplitude threshold
* Local maximum detection
* Refractory interval

A sample can be considered an ECG peak when:

1. Its amplitude is above the configured threshold.
2. It is greater than or equal to the previous sample.
3. It is greater than or equal to the following sample.
4. The refractory interval since the previous detected peak has elapsed.

This approach is intentionally lightweight for the MicroPython + Proteus environment.

---

# Heart-Rate Calculation

The firmware measures the number of samples between detected ECG peaks to obtain RR intervals.

Recent RR intervals are retained and averaged to reduce the effect of individual interval variations.

The heart-rate calculation is:

```text
Heart Rate = Sampling Frequency × 60 / Average RR Interval
```

For this project:

```text
Sampling Frequency = 128 Hz
```

Therefore:

```text
HR = 128 × 60 / Average RR Interval
```

The firmware maintains a short rolling RR history before updating the displayed heart rate.

---

# ECG Status

The calculated heart rate is mapped to one of three demonstration states:

| Heart Rate   | Display Status |
| ------------ | -------------- |
| `< 60 BPM`   | `BRADY`        |
| `60–100 BPM` | `NORMAL`       |
| `> 100 BPM`  | `TACHY`        |

These thresholds are used **only for this educational demonstration** and should not be interpreted as clinical diagnostic criteria.

---

# Real-Time Display

The GLCD is divided into two logical areas.

## Information Area

The upper section displays heart-rate information and status.

Example:

```text
HR:78   NORMAL
```

## ECG Waveform Area

The lower section displays the ECG waveform.

The firmware is designed to avoid unnecessarily updating the entire GLCD for every incoming ECG sample.

Instead, four ECG samples are grouped into one display point.

```text
128 ECG samples/sec
        │
        ▼
4 samples/group
        │
        ▼
32 display points/sec
```

This reduces GLCD communication overhead and helps maintain stable Proteus simulation performance.

The ECG signal continues to be received and processed at the full 128 Hz rate.

---

# UART Communication

The ESP32-S3 receives ECG samples through UART.

## UART Configuration

```text
Baud rate : 115200
Data bits : 8
Parity    : None
Stop bits : 1
```

The firmware configuration is:

```python
UART(0, 115200, bits=8, parity=None, stop=1)
```

The serial port itself is **machine-dependent**.

For example, the current development configuration may use:

```text
COM11
```

If another COM port is used on the host computer, update:

```python
SERIAL_PORT = "COM11"
```

inside `send_ecg_30s.py`.

> Do not assume that `COM11` will be the correct port on another computer.

---

# Python ECG Transmitter

The ECG transmitter is:

```text
send_ecg_30s.py
```

It performs the following operations:

1. Locates the ECG dataset files.
2. Loads the ECG samples.
3. Validates/prepares the required number of samples.
4. Normalizes each stage for the GLCD display range.
5. Sends ECG samples through the configured serial port.
6. Maintains an approximately 128 Hz transmission rate.
7. Sends the three ECG stages sequentially.

The transmission sequence is:

```text
NORMAL
   ↓
TACHY
   ↓
BRADY
```

The transmitter sends the ECG samples as byte values over UART.

---

# Python Requirements

Install Python 3.x.

Install the required serial communication package:

```bash
pip install pyserial
```

Verify the installation:

```bash
python -c "import serial; print(serial.__version__)"
```

---

# Running the Project

## 1. Clone the Repository

```bash
git clone https://github.com/kolopdel-boop/ESP32-S3-ECG-Monitor.git
cd ESP32-S3-ECG-Monitor
```

---

## 2. Configure the ECG Data Directory

The current `send_ecg_30s.py` contains a configurable ECG data directory.

Example:

```python
ECG_DIR = Path(r"C:\ECG_Project")
```

Change this path to the directory containing:

```text
ecg_normal_10s.txt
ecg_tachy_10s.txt
ecg_brady_10s.txt
```

For example:

```python
ECG_DIR = Path(r"C:\ESP32-S3-ECG-Monitor")
```

if the dataset files are located in the repository root.

---

## 3. Configure the Serial Port

Open:

```text
send_ecg_30s.py
```

Find:

```python
SERIAL_PORT = "COM11"
```

Change it to the COM port used by your Proteus/virtual serial configuration.

Example:

```python
SERIAL_PORT = "COM9"
```

The baud rate must remain:

```python
BAUDRATE = 115200
```

unless the firmware configuration is changed accordingly.

---

## 4. Open Proteus

Open:

```text
ECG Arrhythmia Detector.pdsprj
```

The project should contain the ESP32-S3 and LGM12641BS1R GLCD simulation.

Verify the GLCD wiring against the pin mapping in this README.

---

## 5. Load the MicroPython Firmware

The firmware is located directly in the repository root:

```text
main.py
```

Load/run this firmware in the ESP32-S3 MicroPython environment used by the Proteus simulation.

---

## 6. Start the Proteus Simulation

Start the Proteus simulation and verify that:

* ESP32-S3 is running
* GLCD is initialized
* UART connection is configured
* GLCD wiring matches the tested pin mapping

---

## 7. Start the ECG Transmitter

Open PowerShell or a terminal in the repository directory:

```bash
python send_ecg_30s.py
```

The transmitter will send:

```text
NORMAL
   ↓
TACHY
   ↓
BRADY
```

Each stage lasts approximately 10 seconds.

---

# Proteus Simulation

The complete embedded system is simulated in Proteus.

The simulation includes:

* ESP32-S3
* LGM12641BS1R 128×64 GLCD
* 8-bit GLCD data bus
* GLCD control signals
* UART communication
* MicroPython firmware
* ECG waveform visualization
* Heart-rate calculation
* ECG status display

The Python transmitter runs externally and supplies ECG samples to the simulated ESP32-S3 through the serial connection.

### Runtime Flow

```text
Python
  │
  │ ECG samples
  ▼
Serial / Virtual COM
  │
  ▼
Proteus
  │
  ▼
ESP32-S3
  │
  │ GPIO
  ▼
LGM12641BS1R GLCD
```

---

# Display Architecture

A key design consideration was the simulation workload created by frequent GLCD operations.

A full framebuffer refresh for every ECG sample would generate unnecessary communication overhead.

The current architecture separates:

```text
ECG processing rate
        ≠
GLCD display update rate
```

ECG processing:

```text
128 samples/sec
```

Display processing:

```text
32 display points/sec
```

This allows the firmware to continue processing the ECG signal at 128 Hz while reducing the number of GLCD updates performed during Proteus simulation.

---

# Runtime Behavior

When the system starts before ECG samples are available, the display shows a waiting state.

The display then begins updating after ECG data is received.

During the three test stages, the firmware independently calculates the heart rate from detected ECG peaks.

The displayed status is determined from the calculated heart rate rather than simply using the dataset filename.

For example:

```text
HR:78   NORMAL
```

or:

```text
HR:120  TACHY
```

or:

```text
HR:52   BRADY
```

The exact calculated values depend on the ECG samples and peak-detection behavior.

---

# Development Environment

The project was developed and tested with:

* ESP32-S3
* MicroPython
* Proteus 8.x
* Python 3.x
* PySerial
* Windows
* Virtual serial communication
* LGM12641BS1R 128×64 GLCD

---

# Current Project Status

## Implemented

* [x] ESP32-S3 simulation
* [x] MicroPython firmware
* [x] GLCD initialization
* [x] 8-bit GLCD data interface
* [x] Tested ESP32-S3 ↔ GLCD pin mapping
* [x] ECG dataset transmission
* [x] UART communication
* [x] Real-time ECG waveform visualization
* [x] ECG peak detection
* [x] RR interval calculation
* [x] Heart-rate estimation
* [x] NORMAL / TACHY / BRADY status display
* [x] Proteus simulation
* [x] Python ECG transmitter
* [x] 30-second demonstration sequence
* [x] Demonstration video

## Possible Future Improvements

* [ ] Longer ECG datasets
* [ ] Additional ECG rhythms
* [ ] ECG signal filtering
* [ ] Baseline-wander removal
* [ ] More advanced QRS detection
* [ ] Pan-Tompkins-based processing
* [ ] Improved ECG scaling
* [ ] Adjustable display timebase
* [ ] SD-card ECG playback
* [ ] Real ECG sensor input
* [ ] Physical hardware prototype
* [ ] ECG data logging
* [ ] More advanced waveform analysis
* [ ] Additional GLCD visualization modes

---

# Known Limitations

This project is primarily designed as an educational embedded-systems and simulation project.

Current limitations include:

* Simple threshold-based peak detection
* No clinical-grade ECG filtering
* No validated QRS detection algorithm
* Demonstration-oriented heart-rate classification
* ECG amplitude normalization for display
* Dependence on virtual serial communication
* Proteus simulation performance limitations
* Dataset-driven input rather than a physical ECG sensor

These limitations are intentional for the current project scope.

---

# Future Development

Potential future versions may extend the project toward:

```text
ECG Dataset
     │
     ▼
Digital Filtering
     │
     ▼
QRS Detection
     │
     ▼
RR Interval Analysis
     │
     ▼
Heart-Rate Calculation
     │
     ▼
ECG Visualization
     │
     ├── GLCD
     ├── Serial Monitor
     └── Data Logging
```

Possible additions include real ECG sensor acquisition, more advanced signal processing, longer datasets, additional rhythm categories, and hardware deployment.

---

# Disclaimer

This project is intended for **educational, simulation, and software-development purposes only**.

It is **not a medical device** and must not be used for:

* Medical diagnosis
* Treatment decisions
* Patient monitoring
* Clinical decision-making

The ECG datasets, heart-rate thresholds, peak-detection algorithm, and signal-processing implementation have not been validated for clinical use.

---

# Author

**Mas Has**

GitHub:

https://github.com/kolopdel-boop

Project:

https://github.com/kolopdel-boop/ESP32-S3-ECG-Monitor

---

# License

This project is released under the **MIT License**.

See the `LICENSE` file for details.
