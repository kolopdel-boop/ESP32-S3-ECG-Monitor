# ESP32-S3 ECG Monitor

**Embedded ECG dataset replay, heart-rate estimation, and GLCD visualization using ESP32-S3, MicroPython, UART, and Proteus.**

> **Educational / engineering project — not a medical device and not intended for clinical diagnosis.**

---

## Overview

This project demonstrates an embedded ECG monitoring pipeline built around an **ESP32-S3 running MicroPython**.

ECG samples stored in local text files are loaded and prepared by a Python transmitter on the host computer. Each 10-second ECG stage is normalized for display, transmitted to the ESP32-S3 through UART at a nominal **128 samples/second**, processed by lightweight embedded peak detection, and visualized on a **128×64 KS0108-style GLCD**.

The firmware estimates heart rate from detected R-like peaks using RR intervals and classifies the current signal into three simple heart-rate-based states:

* `BRADY`
* `NORMAL`
* `TACHY`

The project is implemented and demonstrated in **Proteus** using an ESP32-S3 and an LGM12641BS1R 128×64 GLCD.

---

## Project Architecture

```text
ECG TXT Dataset
      │
      ▼
Python ECG Transmitter
      │
      ├── Load ECG samples
      ├── Select 10-second stage
      ├── Normalize to GLCD range
      └── Timed 128 Hz byte transmission
      │
      ▼
UART / Virtual Serial Link
      │
      ▼
ESP32-S3 + MicroPython
      │
      ├── 128-byte frame reception
      ├── Lightweight peak detection
      ├── RR interval calculation
      ├── Rolling RR history
      ├── Heart-rate estimation
      └── HR-based status classification
      │
      ▼
128×64 KS0108-style GLCD
      │
      ├── Heart rate / status
      └── ECG waveform
```

The system uses **dataset replay rather than physical ECG sensor acquisition**.

---

## Key Features

* ESP32-S3 embedded implementation using MicroPython
* ECG dataset replay through UART
* Nominal 128 samples/second transmission
* 115200 baud, 8N1 serial communication
* 128-byte ECG processing frames
* Lightweight amplitude-threshold peak detection
* Local-maximum detection
* Refractory-period control
* RR interval calculation
* Rolling average of recent RR intervals
* Heart-rate estimation
* `BRADY / NORMAL / TACHY` status classification
* 128×64 GLCD waveform visualization
* KS0108-style 8-bit GLCD interface
* Framebuffer-based display rendering
* Display decimation from 128 Hz to 32 display points/second
* 4-second visible waveform sweep
* Proteus simulation
* Python host-side ECG transmitter
* Three-stage 30-second demonstration

---

## Technology Stack

**ESP32-S3 · MicroPython · Embedded Signal Processing · UART · GLCD · Proteus · Python · PySerial**

---

## Repository Structure

```text
ESP32-S3-ECG-Monitor/
├── media/
│   └── ECG_Arrhythmia_Detector_GitHub_30s.mp4
│
├── ECG Arrhythmia Detector.pdsprj
├── ECG Arrhythmia Detector.png
├── LICENSE
├── README.md
├── ecg_brady_10s.txt
├── ecg_normal_10s.txt
├── ecg_tachy_10s.txt
├── main.py
└── send_ecg_30s.py
```

---

# ECG Data Pipeline

The host-side transmitter automatically searches the configured ECG directory for `.txt` files.

Files are identified using filename keywords such as:

* `normal`
* `nsr`
* `sinus`
* `tachy`
* `tachycard`
* `brady`
* `bradycard`

The transmitter expects three ECG stages:

```text
NORMAL
TACHYCARDIA
BRADYCARDIA
```

Each stage is prepared as exactly:

```text
128 samples/second × 10 seconds = 1280 samples
```

If a file contains more than 1280 samples, the first 1280 are used.

If it contains fewer than 1280 samples, the waveform is repeated until 1280 samples are available.

---

# Host-Side ECG Normalization

Before transmission, each ECG stage is independently normalized into the GLCD coordinate range:

```text
1 ... 62
```

The transformation maps the minimum ECG value toward the lower display coordinate and the maximum toward the upper display coordinate.

This normalization is performed by:

```text
send_ecg_30s.py
```

before the samples are transmitted.

Therefore, the ESP32-S3 receives **normalized display-domain sample values**, rather than calibrated ECG voltage values such as millivolts.

This approach is intended for waveform visualization and embedded algorithm demonstration.

---

# UART Communication

The host transmitter uses:

```text
Baud rate: 115200
Format:    8N1
Sample rate: 128 samples/second
Payload:   1 byte/sample
```

Each normalized ECG sample is transmitted as exactly one byte:

```text
Python → UART → ESP32-S3
```

The firmware accumulates incoming bytes into frames of:

```text
128 samples/frame
```

At 128 samples/second, one frame represents approximately:

```text
1 second of ECG data
```

The firmware sends:

```text
FRAME_OK
```

after processing each frame.

The current Python transmitter does **not** read or use this acknowledgement for flow control. Therefore, the present implementation should be considered a timed streaming/replay system rather than a closed-loop ACK-controlled transport.

---

# Embedded ECG Processing

The ESP32-S3 performs lightweight peak detection directly in the MicroPython firmware.

The detector uses three main conditions.

### 1. Amplitude threshold

```python
PEAK_THRESHOLD = 52
```

A candidate sample must reach the configured threshold.

Because the transmitter normalizes ECG samples to the GLCD coordinate domain, this threshold operates on the normalized sample representation rather than on physical ECG voltage.

### 2. Local maximum

A sample is considered a peak candidate when it is greater than or equal to both neighboring samples.

Conceptually:

```text
previous <= current >= next
```

### 3. Refractory period

The firmware requires a minimum distance between accepted peaks:

```python
REFRACTORY_SAMPLES = 30
```

At 128 samples/second this corresponds to approximately:

```text
30 / 128 ≈ 234 ms
```

This prevents closely spaced local maxima from being counted as separate heartbeats.

---

# RR Interval and Heart-Rate Estimation

When a new peak is accepted, the firmware calculates the sample distance from the previous accepted peak.

```text
RR = current_peak_index - previous_peak_index
```

Accepted RR intervals are stored in a rolling history containing up to four intervals.

The average RR interval is then used to estimate heart rate:

```text
HR = (FS × 60) / average_RR
```

where:

```text
FS = 128 samples/second
```

The implementation uses integer arithmetic for the final heart-rate calculation.

---

# Heart-Rate-Based Status

The current firmware uses heart rate to assign a simple status:

```text
HR < 60       → BRADY
60 ≤ HR ≤ 100  → NORMAL
HR > 100      → TACHY
```

This classification is based only on calculated heart rate.

It is **not a clinical arrhythmia classifier** and does not attempt to identify specific ECG morphologies such as:

* atrial fibrillation
* premature ventricular contractions
* ventricular tachycardia
* ST-segment abnormalities
* conduction abnormalities

The project should therefore be considered an **embedded ECG monitor with heart-rate-based status classification**, rather than a clinical arrhythmia detection system.

---

# GLCD Interface

The project uses a:

```text
128 × 64 monochrome GLCD
```

with a KS0108-style 8-bit interface.

### Tested pin mapping

| Function | ESP32-S3 GPIO |
| -------- | ------------: |
| DB0      |         GPIO4 |
| DB1      |         GPIO5 |
| DB2      |         GPIO6 |
| DB3      |         GPIO7 |
| DB4      |         GPIO8 |
| DB5      |         GPIO9 |
| DB6      |        GPIO10 |
| DB7      |        GPIO11 |
| DI       |        GPIO12 |
| R/W      |        GPIO13 |
| E        |        GPIO14 |
| CS1      |        GPIO15 |
| CS2      |        GPIO16 |
| RST      |        GPIO17 |

The firmware maintains a:

```text
128 × 64 / 8 = 1024-byte
```

1-bit framebuffer.

The display is divided conceptually into:

```text
Upper area
──────────────
HR / status

Lower area
──────────────
ECG waveform
```

---

# Waveform Display Architecture

ECG processing remains at:

```text
128 samples/second
```

while the GLCD receives fewer display points.

Every four ECG samples are grouped into one display point:

```text
128 / 4 = 32 display points/second
```

The current implementation uses the **last sample of each four-sample group** for display.

With 128 GLCD columns:

```text
128 columns / 32 points/sec = 4 seconds
```

Therefore, the visible waveform sweep represents approximately four seconds of ECG data.

This display decimation is independent of the ECG processing rate.

---

# Embedded Display Optimization

The firmware does not continuously redraw the entire GLCD.

Instead:

* status information is updated when HR/status changes
* waveform columns are updated incrementally
* the waveform area is cleared only where required
* the framebuffer preserves the display state
* the display update rate is lower than the ECG processing rate

This reduces unnecessary GLCD traffic while keeping the waveform visually responsive in the simulation.

---

# 30-Second Demonstration

The supplied transmitter sends three 10-second ECG stages sequentially:

```text
0–10 s    NORMAL
10–20 s   TACHYCARDIA
20–30 s   BRADYCARDIA
```

The labels describe the intended dataset stages.

The displayed status, however, is calculated independently by the ESP32-S3 firmware from detected peaks and estimated heart rate.

This means the firmware does not simply trust the filename or stage label.

---

# Proteus Simulation

The project includes a Proteus simulation containing the embedded ECG monitoring environment.

The simulation demonstrates:

* ESP32-S3 firmware execution
* UART ECG data reception
* ECG processing
* heart-rate estimation
* status classification
* GLCD waveform visualization

The Proteus project is:

```text
ECG Arrhythmia Detector.pdsprj
```

The name is retained as the original project artifact; the implemented algorithm itself performs lightweight heart-rate-based ECG status classification.

---

# Running the Project

## 1. Clone the repository

```bash
git clone https://github.com/kolopdel-boop/ESP32-S3-ECG-Monitor.git
cd ESP32-S3-ECG-Monitor
```

## 2. Configure the ECG data directory

Open:

```text
send_ecg_30s.py
```

and configure:

```python
ECG_DIR = Path(r"C:\path\to\your\ECG\data")
```

Do not use the example path as a required project location.

The directory should contain the required ECG `.txt` files.

---

## 3. Configure the serial port

Set the appropriate COM port:

```python
SERIAL_PORT = "COM11"
```

The example above reflects the development setup and may need to be changed for another computer or Proteus virtual COM configuration.

---

## 4. Start the Proteus simulation

Open:

```text
ECG Arrhythmia Detector.pdsprj
```

and start the simulation with the ESP32-S3 and GLCD configured.

---

## 5. Run the ECG transmitter

Install the required Python serial package if necessary:

```bash
pip install pyserial
```

Then run:

```bash
python send_ecg_30s.py
```

The transmitter will:

1. locate the ECG files
2. load the ECG samples
3. prepare three 10-second stages
4. normalize each stage for GLCD display
5. transmit one byte per sample
6. maintain nominal 128 Hz timing
7. send NORMAL → TACHYCARDIA → BRADYCARDIA

---

# Runtime Processing Flow

For each received 128-byte frame:

```text
UART reception
      ↓
128 ECG samples
      ↓
Peak detection
      ↓
RR interval calculation
      ↓
Rolling RR history
      ↓
Heart-rate estimation
      ↓
BRADY / NORMAL / TACHY
      ↓
GLCD status update
```

At the same time, the ECG samples are processed for waveform visualization:

```text
128 samples/sec
      ↓
groups of 4 samples
      ↓
32 display points/sec
      ↓
128-column GLCD sweep
```

---

# Current Implementation Status

### Implemented

* [x] ESP32-S3 MicroPython firmware
* [x] UART ECG streaming
* [x] 115200 baud communication
* [x] 128 samples/second nominal replay
* [x] 128-sample processing frames
* [x] ECG dataset loading
* [x] 10-second stage preparation
* [x] Per-stage display normalization
* [x] Lightweight peak detection
* [x] Refractory-period control
* [x] RR interval calculation
* [x] Rolling RR history
* [x] Heart-rate estimation
* [x] HR-based status classification
* [x] 128×64 GLCD framebuffer
* [x] Incremental waveform rendering
* [x] Display decimation
* [x] Proteus simulation
* [x] 30-second three-stage demonstration
* [x] Frame acknowledgement from ESP32-S3

---

# Limitations

This implementation is intentionally lightweight and educational.

### Signal processing

The current firmware does not implement:

* band-pass ECG filtering
* baseline-wander removal
* power-line interference suppression
* Pan-Tompkins QRS detection
* adaptive thresholding
* morphology analysis
* clinical QRS validation

### Data acquisition

The current system uses ECG files replayed from a host computer.

It does not currently acquire ECG from a physical analog front end or ECG sensor.

### Signal representation

The host transmitter normalizes each stage independently into the GLCD display range before transmission.

Therefore, the ESP32-S3 does not receive calibrated ECG amplitude values.

### Classification

The current `BRADY / NORMAL / TACHY` classification is based on calculated heart rate only.

It should not be interpreted as clinical arrhythmia diagnosis.

### Serial flow control

The firmware sends `FRAME_OK` after each frame, but the current Python transmitter does not consume or use these acknowledgements.

### Timing

The host transmitter uses Python scheduling and the operating system's serial stack. The 128 Hz rate is therefore a **nominal timed replay rate**, not a hard real-time acquisition guarantee.

### Validation

The current project demonstrates the embedded processing pipeline and simulation behavior. It does not provide clinical validation or diagnostic performance evaluation.

---

# Future Development

Possible extensions include:

### ECG signal conditioning

* digital band-pass filtering
* baseline-wander removal
* 50/60 Hz interference suppression
* amplitude calibration

### Improved QRS detection

* adaptive thresholding
* Pan-Tompkins-style processing
* slope and width constraints
* more robust refractory logic
* false-positive / false-negative evaluation

### Advanced ECG analysis

* morphology-based beat classification
* PVC detection
* AF-oriented analysis
* HRV metrics
* beat-to-beat monitoring

### Embedded hardware

* physical ECG analog front end
* ADC-based ECG acquisition
* real sensor input
* SD-card logging
* hardware UART acquisition
* real-time embedded sampling

### Communication

* ACK-based flow control
* frame sequence numbers
* packet validation
* dropped-frame detection
* host/embedded synchronization

### Display

* scrolling timebase
* adjustable gain
* grid rendering
* waveform scaling
* multi-page monitoring screens
* event indicators

---

# Engineering Focus

This project demonstrates the integration of several embedded engineering layers rather than relying on a single software algorithm:

```text
Biomedical Data
      ↓
Python Data Pipeline
      ↓
Timed Serial Transport
      ↓
ESP32-S3 Firmware
      ↓
Embedded ECG Processing
      ↓
Heart-Rate Estimation
      ↓
GLCD Rendering
      ↓
Proteus System Simulation
```

The main engineering focus is the integration of **embedded firmware, biomedical signal replay, serial communication, lightweight signal processing, and constrained graphical display**.

---

# Demonstration

A 30-second demonstration video is available in:

```text
media/ECG_Arrhythmia_Detector_GitHub_30s.mp4
```

The demonstration shows the three-stage ECG replay and the corresponding ESP32-S3 processing and GLCD visualization.

---

# Disclaimer

This project is intended for **education, experimentation, and embedded-systems engineering practice**.

It is not a medical device and has not been clinically validated.

Heart-rate thresholds and ECG processing methods shown in this repository are simplified engineering implementations and must not be used for medical diagnosis or treatment decisions.

---

# License

This project is released under the **MIT License**.

See [`LICENSE`](LICENSE) for details.
