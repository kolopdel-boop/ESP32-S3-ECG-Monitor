# ESP32-S3 ECG Monitor

**Real-Time ECG Monitoring and Heart-Rate Detection using ESP32-S3, MicroPython, GLCD, and Proteus Simulation**

[![MicroPython](https://img.shields.io/badge/MicroPython-ESP32--S3-blue.svg)](https://micropython.org/)
[![Proteus](https://img.shields.io/badge/Simulation-Proteus-orange.svg)](https://www.labcenter.com/)
[![ECG](https://img.shields.io/badge/Signal-ECG-red.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

---

## Overview

This project implements a real-time ECG monitoring system based on an **ESP32-S3 running MicroPython**.

The system receives ECG samples through a serial UART connection, processes the incoming signal, estimates heart rate from detected peaks, and displays the ECG waveform and heart-rate status on a **128×64 GLCD**.

The complete system is developed and tested in **Proteus**, with a Python-based ECG transmitter providing real ECG datasets to the ESP32-S3 through a virtual serial connection.

The project is designed as an educational and engineering demonstration of:

* Embedded ECG signal processing
* UART-based biomedical data transmission
* Real-time waveform visualization
* Heart-rate estimation
* MicroPython embedded development
* GLCD interfacing
* ESP32-S3 simulation in Proteus

> **Note:** This project is an educational/simulation project and is not intended for medical diagnosis or clinical use.

---

## Demo

A 30-second demonstration video is included in the repository.

The video shows the ECG waveform being received and displayed in real time, together with heart-rate information and ECG status.

**Demo video:**
`media/ECG_Arrhythmia_Detector_GitHub_30s.mp4`

---

## System Architecture

```text
                ECG Dataset
                     │
                     │
                     ▼
          ┌─────────────────────┐
          │ Python ECG           │
          │ Transmitter          │
          │                      │
          │ 128 Hz               │
          │ 115200 baud         │
          └──────────┬──────────┘
                     │
                     │ UART
                     │ COM11
                     ▼
          ┌─────────────────────┐
          │ ESP32-S3             │
          │ MicroPython          │
          │                      │
          │ • ECG reception      │
          │ • Peak detection     │
          │ • HR calculation     │
          │ • Status detection   │
          └──────────┬──────────┘
                     │
                     │ GPIO
                     ▼
          ┌─────────────────────┐
          │ LGM12641BS1R        │
          │ 128 × 64 GLCD       │
          │                      │
          │ ECG waveform         │
          │ HR                   │
          │ Status               │
          └─────────────────────┘

                 Proteus
              Simulation Layer
```

---

## Main Features

* Real-time ECG waveform display
* ESP32-S3 microcontroller
* MicroPython firmware
* 128×64 KS0108-style GLCD
* UART ECG data streaming
* 128 Hz ECG sampling rate
* Heart-rate estimation from ECG peaks
* Rolling RR interval history
* ECG status classification:

  * `NORMAL`
  * `TACHY`
  * `BRADY`
* Waiting-state display when ECG data is not yet available
* Python ECG data transmitter
* Proteus-based hardware simulation
* Lightweight GLCD refresh architecture designed for stable Proteus simulation

---

## Hardware

### Microcontroller

**ESP32-S3**

The ESP32-S3 runs the MicroPython firmware and performs:

* UART reception
* ECG sample processing
* Peak detection
* RR interval calculation
* Heart-rate estimation
* GLCD control
* Real-time waveform rendering

### Display

**LGM12641BS1R 128×64 GLCD**

The display uses a KS0108-style interface with:

* 8-bit parallel data bus
* Two controller select lines
* Data/Instruction control
* Read/Write control
* Enable signal
* Reset signal

---

## GLCD Pin Mapping

The following pin mapping is the tested configuration used by the project.

| GLCD Pin | ESP32-S3 GPIO |
| -------- | ------------: |
| BD0      |         GPIO4 |
| BD1      |         GPIO5 |
| BD2      |         GPIO6 |
| BD3      |         GPIO7 |
| BD4      |         GPIO8 |
| BD5      |         GPIO9 |
| BD6      |        GPIO10 |
| BD7      |        GPIO11 |
| DI       |        GPIO12 |
| R/W      |        GPIO13 |
| E        |        GPIO14 |
| CS1      |        GPIO15 |
| CS2      |        GPIO16 |
| RST      |        GPIO17 |

> **Important:** This pin mapping should be kept unchanged when reproducing the Proteus simulation.

---

## ECG Data

The project uses ECG datasets rather than a mathematically generated waveform.

The current test datasets represent three heart-rate conditions:

```text
ecg_normal_10s.txt
ecg_tachy_10s.txt
ecg_brady_10s.txt
```

Each dataset contains:

* 1280 samples
* 128 samples/second
* 10 seconds of ECG data

### Sampling

```text
Sampling frequency: 128 Hz
Samples per second: 128
Samples per 10 seconds: 1280
```

The transmitter sends the ECG samples as raw byte values over UART.

---

## ECG Processing

The ESP32-S3 processes the received ECG samples in real time.

Peak detection is based on a threshold and local-maximum check.

A sample is considered a candidate ECG peak when:

* Its amplitude is above the configured threshold
* It is greater than or equal to the previous sample
* It is greater than or equal to the following sample

A refractory interval is applied to prevent multiple detections of the same heartbeat.

### Heart-Rate Calculation

The firmware calculates RR intervals between detected peaks.

Several recent RR intervals are retained and averaged.

Heart rate is then estimated from:

```text
Heart Rate = Sampling Frequency × 60 / Average RR Interval
```

For this project:

```text
Sampling Frequency = 128 Hz
```

The firmware maintains a short RR history to reduce the effect of individual interval variations.

---

## ECG Status

The calculated heart rate is used to display a simple status:

|   Heart Rate | Display Status |
| -----------: | -------------- |
|   `< 60 BPM` | `BRADY`        |
| `60–100 BPM` | `NORMAL`       |
|  `> 100 BPM` | `TACHY`        |

These thresholds are used for demonstration purposes and should not be interpreted as clinical diagnostic criteria.

---

## Real-Time Display

The display area is divided into two logical sections.

### Information Area

The upper portion displays:

```text
HR:xxx    STATUS
```

Example:

```text
HR:78     NORMAL
```

### ECG Area

The lower portion displays the real-time ECG waveform.

The display uses a lightweight sweep architecture.

Instead of updating the entire GLCD framebuffer for every incoming ECG sample, the firmware groups four ECG samples for display processing.

```text
128 ECG samples/sec
        │
        ▼
4 samples/group
        │
        ▼
32 display points/sec
```

This significantly reduces unnecessary GLCD operations during Proteus simulation while maintaining a clear real-time waveform.

---

## UART Communication

The ESP32-S3 receives ECG data through UART.

### Configuration

```text
Baud rate : 115200
Data bits : 8
Parity    : None
Stop bits : 1
```

The Python transmitter sends ECG samples through the configured serial port.

The current test setup uses:

```text
COM11
```

The transmitter and Proteus simulation must run simultaneously.

---

## Python ECG Transmitter

The transmitter is located in:

```text
transmitter/send_ecg_30s.py
```

It:

1. Detects the ECG dataset files.
2. Loads the ECG samples.
3. Selects the corresponding dataset.
4. Sends the samples at 128 Hz.
5. Communicates with the ESP32-S3 through the serial interface.
6. Waits for the firmware frame acknowledgement.

The transmission sequence is:

```text
NORMAL
   ↓
TACHYCARDIA
   ↓
BRADYCARDIA
```

---

## Proteus Simulation

The complete embedded system is simulated in **Proteus**.

The Proteus simulation includes:

* ESP32-S3
* LGM12641BS1R GLCD
* GPIO connections
* UART interface
* ECG waveform display
* MicroPython firmware execution

The Python transmitter runs externally and provides the ECG stream to the simulated ESP32-S3.

### Required Runtime

Two applications should be running simultaneously:

```text
PowerShell / Python
       │
       │ ECG data
       ▼
   Serial Port
       │
       ▼
    Proteus
       │
       ▼
    ESP32-S3
       │
       ▼
      GLCD
```

---

## Project Structure

```text
ESP32-S3-ECG-Monitor/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── firmware/
│   └── Main.py
│
├── transmitter/
│   └── send_ecg_30s.py
│
├── data/
│   ├── ecg_normal_10s.txt
│   ├── ecg_tachy_10s.txt
│   └── ecg_brady_10s.txt
│
├── proteus/
│   └── ECG_Monitor.pdsprj
│
├── media/
│   └── ECG_Arrhythmia_Detector_GitHub_30s.mp4
│
└── docs/
    └── wiring.md
```

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kolopdel-boop/ESP32-S3-ECG-Monitor.git
```

```bash
cd ESP32-S3-ECG-Monitor
```

### 2. Open the Proteus Project

Open the Proteus project located in:

```text
proteus/
```

Load the ESP32-S3 simulation and verify the GLCD connections.

### 3. Load the MicroPython Firmware

Copy the firmware to the ESP32-S3 / Proteus MicroPython environment:

```text
firmware/Main.py
```

### 4. Configure the Serial Port

The Python transmitter uses the configured serial port.

Current development configuration:

```text
COM11
115200 baud
8 data bits
No parity
1 stop bit
```

If a different serial-port configuration is required, update the transmitter accordingly.

### 5. Start Proteus

Start the Proteus simulation and make sure the ESP32-S3 and GLCD are running.

### 6. Start the ECG Transmitter

From PowerShell:

```powershell
python transmitter\send_ecg_30s.py
```

Keep PowerShell running while Proteus is running.

---

## Example Runtime Output

The transmitter provides console information similar to:

```text
============================================
 ECG REAL DATA TRANSMITTER
============================================

Detected ECG files:

NORMAL      : ecg_normal_10s.txt
TACHYCARDIA : ecg_tachy_10s.txt
BRADYCARDIA : ecg_brady_10s.txt

Port : COM11
Baud : 115200

COM11 opened successfully.

============================================
START: NORMAL
============================================
```

The ESP32-S3 firmware reports frame processing and calculated heart rate:

```text
FRAME_OK HR= 78 STATUS= NORMAL
```

---

## Design Considerations

A major design consideration in this project was the computational load caused by frequent GLCD updates during Proteus simulation.

Updating the complete 128×64 framebuffer for every ECG sample creates unnecessary simulation overhead.

The current implementation therefore separates:

```text
ECG sampling rate
        ≠
GLCD refresh workload
```

The ECG data continues to arrive at:

```text
128 samples/sec
```

while display processing is decimated to:

```text
32 display points/sec
```

This allows the embedded signal-processing logic to operate at the required sampling rate without unnecessarily overloading the simulated GLCD interface.

---

## Development Environment

The project was developed and tested using:

* ESP32-S3
* MicroPython
* Proteus 8.x
* Python 3.x
* Windows
* Virtual serial communication
* LGM12641BS1R 128×64 GLCD

---

## Current Project Status

### Implemented

* [x] ESP32-S3 simulation
* [x] MicroPython firmware
* [x] GLCD initialization
* [x] 8-bit GLCD data interface
* [x] Real ECG dataset transmission
* [x] UART communication
* [x] Real-time waveform visualization
* [x] ECG peak detection
* [x] RR interval calculation
* [x] Heart-rate estimation
* [x] NORMAL / TACHY / BRADY status display
* [x] Proteus simulation
* [x] Python ECG transmitter
* [x] Live demonstration video

### Possible Future Improvements

* [ ] 60-second ECG datasets
* [ ] Additional ECG rhythms
* [ ] ECG signal filtering
* [ ] Baseline-wander removal
* [ ] More advanced QRS detection
* [ ] Pan-Tompkins-based processing
* [ ] Improved ECG scaling and timebase controls
* [ ] SD-card ECG playback
* [ ] Real ECG sensor input
* [ ] Hardware prototype
* [ ] Data logging
* [ ] Extended diagnostic visualization

---

## Disclaimer

This project is intended for **educational, simulation, and software-development purposes only**.

It is not a medical device and should not be used for diagnosis, treatment, patient monitoring, or clinical decision-making.

The ECG datasets, heart-rate thresholds, and signal-processing algorithms are demonstration components and have not been validated for clinical use.

---

## Author

**Mas Has**

GitHub:

https://github.com/kolopdel-boop

Project:

https://github.com/kolopdel-boop/ESP32-S3-ECG-Monitor

---

## License

This project is released under the **MIT License**.

See the `LICENSE` file for details.
# ESP32-S3-ECG-Monitor
Real-time ECG monitoring and heart-rate detection using ESP32-S3, MicroPython, GLCD, and Proteus simulation.
