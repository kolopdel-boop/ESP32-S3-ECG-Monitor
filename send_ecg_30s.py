import serial
import time
from pathlib import Path


# ============================================================
# ECG → ESP32 → GLCD
# FINAL VERSION
# ============================================================

# ------------------------------------------------------------
# PROJECT DIRECTORY
# ------------------------------------------------------------

ECG_DIR = Path(r"C:\ECG_Project")


# ------------------------------------------------------------
# SERIAL SETTINGS
# ------------------------------------------------------------

SERIAL_PORT = "COM11"
BAUDRATE = 115200


# ------------------------------------------------------------
# ECG SETTINGS
# ------------------------------------------------------------

SAMPLE_RATE = 128          # samples / second
SECONDS_PER_STAGE = 10
SAMPLES_PER_STAGE = SAMPLE_RATE * SECONDS_PER_STAGE

GLCD_HEIGHT = 64
GLCD_MIN_Y = 1
GLCD_MAX_Y = 62

SERIAL_DELAY = 1.0 / SAMPLE_RATE


# ============================================================
# FIND ECG FILES AUTOMATICALLY
# ============================================================

def find_ecg_files():

    files = sorted(ECG_DIR.glob("*.txt"))

    if not files:
        raise FileNotFoundError(
            f"No ECG TXT files found in {ECG_DIR}"
        )

    normal = None
    tachy = None
    brady = None

    for file in files:

        name = file.stem.lower()

        if normal is None and (
            "normal" in name
            or "nsr" in name
            or "sinus" in name
        ):
            normal = file

        if tachy is None and (
            "tachy" in name
            or "tachycard" in name
        ):
            tachy = file

        if brady is None and (
            "brady" in name
            or "bradycard" in name
        ):
            brady = file

    # --------------------------------------------------------
    # If keyword detection failed, use remaining TXT files.
    # --------------------------------------------------------

    unused = [
        f for f in files
        if f not in {normal, tachy, brady}
    ]

    if normal is None and unused:
        normal = unused.pop(0)

    if tachy is None and unused:
        tachy = unused.pop(0)

    if brady is None and unused:
        brady = unused.pop(0)

    return normal, tachy, brady


# ============================================================
# LOAD ECG FILE
# ============================================================

def load_ecg(filename):

    values = []

    with open(filename, "r", encoding="utf-8-sig") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            # ------------------------------------------------
            # Support:
            #
            # 123
            # 123.5
            # 123,456
            # 123 456
            # ------------------------------------------------

            line = line.replace(",", " ")

            parts = line.split()

            for part in parts:

                try:
                    values.append(float(part))

                except ValueError:
                    continue

    if not values:
        raise ValueError(
            f"No numeric ECG samples found in {filename}"
        )

    return values


# ============================================================
# PREPARE EXACTLY 10 SECONDS
# ============================================================

def prepare_10_seconds(values):

    if len(values) == 0:
        raise ValueError("Empty ECG data")

    # --------------------------------------------------------
    # If file contains more than 10 seconds:
    # use first 1280 samples.
    # --------------------------------------------------------

    if len(values) >= SAMPLES_PER_STAGE:

        return values[:SAMPLES_PER_STAGE]

    # --------------------------------------------------------
    # If file contains fewer samples:
    # repeat the waveform until 1280 samples are available.
    # --------------------------------------------------------

    result = []

    while len(result) < SAMPLES_PER_STAGE:

        result.extend(values)

    return result[:SAMPLES_PER_STAGE]


# ============================================================
# NORMALIZE ECG TO GLCD Y COORDINATES
# ============================================================

def convert_to_glcd(values):

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:

        return [32] * len(values)

    result = []

    for value in values:

        normalized = (
            (value - minimum)
            / (maximum - minimum)
        )

        # ECG high value appears higher on GLCD.
        y = GLCD_MAX_Y - int(
            normalized
            * (GLCD_MAX_Y - GLCD_MIN_Y)
        )

        y = max(
            GLCD_MIN_Y,
            min(GLCD_MAX_Y, y)
        )

        result.append(y)

    return result


# ============================================================
# PRINT INFORMATION
# ============================================================

def print_file_info(name, filename, values):

    print()
    print("--------------------------------------------")
    print(name)
    print("--------------------------------------------")
    print("File    :", filename.name)
    print("Samples :", len(values))
    print("Minimum :", min(values))
    print("Maximum :", max(values))
    print("Duration:", len(values) / SAMPLE_RATE, "seconds")


# ============================================================
# SEND ECG STAGE
# ============================================================

def send_stage(ser, name, samples):

    print()
    print("============================================")
    print("START:", name)
    print("============================================")

    start_time = time.perf_counter()

    for index, y in enumerate(samples):

        # ----------------------------------------------------
        # Send exactly ONE byte
        # ----------------------------------------------------

        ser.write(bytes((y,)))

        # ----------------------------------------------------
        # Accurate 128 Hz timing
        # ----------------------------------------------------

        target = start_time + (
            (index + 1) * SERIAL_DELAY
        )

        remaining = target - time.perf_counter()

        if remaining > 0:
            time.sleep(remaining)

    print("END:", name)


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print()
    print("============================================")
    print(" ECG REAL DATA TRANSMITTER")
    print("============================================")
    print()

    # --------------------------------------------------------
    # Find files
    # --------------------------------------------------------

    normal_file, tachy_file, brady_file = find_ecg_files()

    if normal_file is None:
        raise FileNotFoundError(
            "NORMAL ECG file not found."
        )

    if tachy_file is None:
        raise FileNotFoundError(
            "TACHYCARDIA ECG file not found."
        )

    if brady_file is None:
        raise FileNotFoundError(
            "BRADYCARDIA ECG file not found."
        )


    print("Detected ECG files:")
    print()
    print("NORMAL      :", normal_file)
    print("TACHYCARDIA :", tachy_file)
    print("BRADYCARDIA :", brady_file)


    # --------------------------------------------------------
    # Load files
    # --------------------------------------------------------

    normal_raw = load_ecg(normal_file)
    tachy_raw = load_ecg(tachy_file)
    brady_raw = load_ecg(brady_file)


    # --------------------------------------------------------
    # Prepare exactly 10 seconds
    # --------------------------------------------------------

    normal = prepare_10_seconds(normal_raw)
    tachy = prepare_10_seconds(tachy_raw)
    brady = prepare_10_seconds(brady_raw)


    # --------------------------------------------------------
    # Display information
    # --------------------------------------------------------

    print_file_info(
        "NORMAL",
        normal_file,
        normal
    )

    print_file_info(
        "TACHYCARDIA",
        tachy_file,
        tachy
    )

    print_file_info(
        "BRADYCARDIA",
        brady_file,
        brady
    )


    # --------------------------------------------------------
    # Convert to GLCD coordinates
    # --------------------------------------------------------

    normal_y = convert_to_glcd(normal)
    tachy_y = convert_to_glcd(tachy)
    brady_y = convert_to_glcd(brady)


    # --------------------------------------------------------
    # Open serial port
    # --------------------------------------------------------

    print()
    print("============================================")
    print("SERIAL")
    print("============================================")

    print("Port :", SERIAL_PORT)
    print("Baud :", BAUDRATE)

    ser = serial.Serial(
        SERIAL_PORT,
        BAUDRATE,
        timeout=1
    )

    print("COM11 opened successfully.")


    # --------------------------------------------------------
    # Send three ECG stages
    # --------------------------------------------------------

    try:

        # 0 - 10 seconds
        send_stage(
            ser,
            "NORMAL",
            normal_y
        )

        # 10 - 20 seconds
        send_stage(
            ser,
            "TACHYCARDIA",
            tachy_y
        )

        # 20 - 30 seconds
        send_stage(
            ser,
            "BRADYCARDIA",
            brady_y
        )


    except KeyboardInterrupt:

        print()
        print("Transmission interrupted by user.")


    finally:

        ser.close()

        print()
        print("============================================")
        print("TRANSMISSION COMPLETE")
        print("============================================")
        print()
        print("NORMAL      : 0 - 10 seconds")
        print("TACHYCARDIA : 10 - 20 seconds")
        print("BRADYCARDIA : 20 - 30 seconds")
        print()
        print("COM11 closed.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()