from machine import Pin, UART, Timer
import time


# ============================================================
# ESP32-S3 + LGM12641BS1R / KS0108 GLCD
# ============================================================
#
# DATA:
# BD0 -> GPIO4
# BD1 -> GPIO5
# BD2 -> GPIO6
# BD3 -> GPIO7
# BD4 -> GPIO8
# BD5 -> GPIO9
# BD6 -> GPIO10
# BD7 -> GPIO11
#
# CONTROL:
# DI  -> GPIO12
# RW  -> GPIO13
# E   -> GPIO14
# CS1 -> GPIO15
# CS2 -> GPIO16
# RST -> GPIO17
#
# ECG:
# 128 Hz
# 1280 samples / stage
# 10 seconds / stage
#
# DISPLAY:
# 4 ECG samples -> 1 GLCD column
# 32 display columns/sec
# 128 columns -> approximately 4 seconds visible
#
# IMPORTANT:
# GLCD is NOT updated for every sample.
# This greatly reduces Proteus CPU load.
# ============================================================


# ============================================================
# PIN CONFIGURATION
# ============================================================

DATA = [
    Pin(4, Pin.OUT),
    Pin(5, Pin.OUT),
    Pin(6, Pin.OUT),
    Pin(7, Pin.OUT),
    Pin(8, Pin.OUT),
    Pin(9, Pin.OUT),
    Pin(10, Pin.OUT),
    Pin(11, Pin.OUT)
]

DI = Pin(12, Pin.OUT)
RW = Pin(13, Pin.OUT)
E = Pin(14, Pin.OUT)

CS1 = Pin(15, Pin.OUT)
CS2 = Pin(16, Pin.OUT)

RST = Pin(17, Pin.OUT)


# ============================================================
# UART
# ============================================================

uart = UART(
    0,
    115200,
    bits=8,
    parity=None,
    stop=1
)


# ============================================================
# TIMER
# ============================================================

timer_flag = False


def timer_callback(timer):

    global timer_flag

    timer_flag = True


timer = Timer(-1)

timer.init(
    period=10,
    mode=Timer.PERIODIC,
    callback=timer_callback
)


# ============================================================
# ECG SETTINGS
# ============================================================

FS = 128

FRAME_SIZE = 128

STAGE_SAMPLES = 1280


# ============================================================
# DISPLAY DECIMATION
# ============================================================

DISPLAY_SAMPLES = 4

DISPLAY_RATE = FS // DISPLAY_SAMPLES


# ============================================================
# DISPLAY AREA
# ============================================================

ECG_TOP = 15

ECG_BOTTOM = 58

ECG_HEIGHT = ECG_BOTTOM - ECG_TOP


# ============================================================
# HR DETECTION
# ============================================================

PEAK_THRESHOLD = 52

REFRACTORY_SAMPLES = 30

RR_HISTORY_SIZE = 4


HR = 0

STATUS = "ECG."


# ============================================================
# WAITING ANIMATION
# ============================================================

WAITING_STATE = 0

WAITING_TICKS = 0

WAITING_INTERVAL = 50


# ============================================================
# HR VARIABLES
# ============================================================

sample_counter = 0

last_peak_sample = -1

rr_history = []


# ============================================================
# STAGE VARIABLES
# ============================================================

stage_sample_count = 0


# ============================================================
# DISPLAY VARIABLES
# ============================================================

display_x = 0

previous_y = None

display_samples = []


# ============================================================
# UART BUFFER
# ============================================================

rx_buffer = bytearray()


# ============================================================
# FRAMEBUFFER
# ============================================================

framebuffer = bytearray(1024)


# ============================================================
# STATUS CHANGE TRACKING
# ============================================================

last_displayed_hr = -1

last_displayed_status = ""


# ============================================================
# FONT 5x7
# ============================================================

FONT = {

    "0": [0x3E, 0x51, 0x49, 0x45, 0x3E],
    "1": [0x00, 0x42, 0x7F, 0x40, 0x00],
    "2": [0x42, 0x61, 0x51, 0x49, 0x46],
    "3": [0x21, 0x41, 0x45, 0x4B, 0x31],
    "4": [0x18, 0x14, 0x12, 0x7F, 0x10],
    "5": [0x27, 0x45, 0x45, 0x45, 0x39],
    "6": [0x3C, 0x4A, 0x49, 0x49, 0x30],
    "7": [0x01, 0x71, 0x09, 0x05, 0x03],
    "8": [0x36, 0x49, 0x49, 0x49, 0x36],
    "9": [0x06, 0x49, 0x49, 0x29, 0x1E],

    "A": [0x7E, 0x11, 0x11, 0x11, 0x7E],
    "B": [0x7F, 0x49, 0x49, 0x49, 0x36],
    "C": [0x3E, 0x41, 0x41, 0x41, 0x22],
    "D": [0x7F, 0x41, 0x41, 0x22, 0x1C],
    "E": [0x7F, 0x49, 0x49, 0x49, 0x41],
    "F": [0x7F, 0x09, 0x09, 0x09, 0x01],
    "G": [0x3E, 0x41, 0x49, 0x49, 0x7A],
    "H": [0x7F, 0x08, 0x08, 0x08, 0x7F],
    "I": [0x00, 0x41, 0x7F, 0x41, 0x00],
    "J": [0x20, 0x40, 0x41, 0x3F, 0x01],
    "K": [0x7F, 0x08, 0x14, 0x22, 0x41],
    "L": [0x7F, 0x40, 0x40, 0x40, 0x40],
    "M": [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    "N": [0x7F, 0x04, 0x08, 0x10, 0x7F],
    "O": [0x3E, 0x41, 0x41, 0x41, 0x3E],
    "P": [0x7F, 0x09, 0x09, 0x09, 0x06],
    "Q": [0x3E, 0x41, 0x51, 0x21, 0x5E],
    "R": [0x7F, 0x09, 0x19, 0x29, 0x46],
    "S": [0x46, 0x49, 0x49, 0x49, 0x31],
    "T": [0x01, 0x01, 0x7F, 0x01, 0x01],
    "U": [0x3F, 0x40, 0x40, 0x40, 0x3F],
    "V": [0x1F, 0x20, 0x40, 0x20, 0x1F],
    "W": [0x7F, 0x20, 0x18, 0x20, 0x7F],
    "X": [0x63, 0x14, 0x08, 0x14, 0x63],
    "Y": [0x07, 0x08, 0x70, 0x08, 0x07],
    "Z": [0x61, 0x51, 0x49, 0x45, 0x43],

    ":": [0x00, 0x36, 0x36, 0x00, 0x00],

    ".": [0x00, 0x60, 0x60, 0x00, 0x00],

    " ": [0x00, 0x00, 0x00, 0x00, 0x00]
}


# ============================================================
# LOW LEVEL GLCD
# ============================================================

def write_bus(value):

    for i in range(8):

        if value & (1 << i):

            DATA[i].value(1)

        else:

            DATA[i].value(0)


def pulse_enable():

    E.value(1)

    time.sleep_us(2)

    E.value(0)

    time.sleep_us(2)


def send_command(value):

    DI.value(0)

    RW.value(0)

    write_bus(value)

    pulse_enable()


def send_data(value):

    DI.value(1)

    RW.value(0)

    write_bus(value)

    pulse_enable()


# ============================================================
# CONTROLLERS
# ============================================================

def left_controller():

    CS1.value(1)

    CS2.value(0)


def right_controller():

    CS1.value(0)

    CS2.value(1)


def deselect_controllers():

    CS1.value(0)

    CS2.value(0)


# ============================================================
# ADDRESS
# ============================================================

def set_page(page):

    send_command(
        0xB8 | page
    )


def set_column(column):

    send_command(
        0x40 | column
    )


# ============================================================
# INITIALIZATION
# ============================================================

def glcd_init():

    RST.value(0)

    time.sleep_ms(20)

    RST.value(1)

    time.sleep_ms(20)


    left_controller()

    send_command(0x3F)

    send_command(0xC0)


    right_controller()

    send_command(0x3F)

    send_command(0xC0)


    deselect_controllers()

    clear_screen()


# ============================================================
# FULL CLEAR
# ONLY AT STARTUP
# ============================================================

def clear_screen():

    for i in range(1024):

        framebuffer[i] = 0


    for controller in range(2):

        if controller == 0:

            left_controller()

        else:

            right_controller()


        for page in range(8):

            set_page(page)

            set_column(0)

            for x in range(64):

                send_data(0)


    deselect_controllers()


# ============================================================
# TEXT
# ============================================================

def framebuffer_draw_char(x, page, char):

    if char not in FONT:

        char = " "

    pattern = FONT[char]

    base = page * 128 + x

    for i in range(5):

        if x + i < 128:

            framebuffer[
                base + i
            ] = pattern[i]


def framebuffer_draw_text(x, page, text):

    for char in text:

        if x > 122:

            break

        framebuffer_draw_char(
            x,
            page,
            char
        )

        x += 6


# ============================================================
# STATUS
# ============================================================

def draw_status_to_framebuffer():

    # Clear page 0 only.

    for x in range(128):

        framebuffer[x] = 0


    hr_text = "HR:" + str(HR)


    framebuffer_draw_text(
        2,
        0,
        hr_text
    )


    framebuffer_draw_text(
        42,
        0,
        STATUS
    )


# ============================================================
# SEND STATUS ONLY WHEN NEEDED
# ============================================================

def update_status_display():

    global last_displayed_hr

    global last_displayed_status


    if (

        HR == last_displayed_hr

        and STATUS == last_displayed_status

    ):

        return


    draw_status_to_framebuffer()


    # LEFT controller

    left_controller()

    set_page(0)

    set_column(0)

    for x in range(64):

        send_data(
            framebuffer[x]
        )


    # RIGHT controller

    right_controller()

    set_page(0)

    set_column(0)

    for x in range(64):

        send_data(
            framebuffer[
                64 + x
            ]
        )


    deselect_controllers()


    last_displayed_hr = HR

    last_displayed_status = STATUS


# ============================================================
# WAITING ANIMATION
# ============================================================

def update_waiting_animation():

    global WAITING_TICKS

    global WAITING_STATE

    global STATUS


    if HR != 0:

        return


    WAITING_TICKS += 1


    if WAITING_TICKS >= WAITING_INTERVAL:

        WAITING_TICKS = 0

        WAITING_STATE += 1


        if WAITING_STATE > 2:

            WAITING_STATE = 0


        if WAITING_STATE == 0:

            STATUS = "ECG."

        elif WAITING_STATE == 1:

            STATUS = "ECG.."

        else:

            STATUS = "ECG..."


        update_status_display()


# ============================================================
# ECG VALUE -> SCREEN Y
# ============================================================

def ecg_to_y(value):

    if value < 0:

        value = 0

    elif value > 62:

        value = 62


    # Correct vertical direction

    y = ECG_TOP + (
        (value * ECG_HEIGHT) // 62
    )


    if y < ECG_TOP:

        y = ECG_TOP

    elif y > ECG_BOTTOM:

        y = ECG_BOTTOM


    return y


# ============================================================
# SET PIXEL
# ============================================================

def set_pixel(x, y):

    if x < 0 or x >= 128:

        return

    if y < ECG_TOP or y > ECG_BOTTOM:

        return


    page = y >> 3

    bit = y & 7

    index = (
        page * 128 + x
    )


    framebuffer[index] |= (
        1 << bit
    )


# ============================================================
# CLEAR ONE ECG COLUMN
# ============================================================

def clear_waveform_column(x):

    if x < 0 or x >= 128:

        return


    # Page 1
    # Only bit 7 = Y15 belongs to ECG.

    index = 128 + x

    framebuffer[index] &= 0x7F


    # Pages 2..6

    for page in range(2, 7):

        index = (
            page * 128 + x
        )

        framebuffer[index] = 0


    # Page 7
    # Bits 0..2 = Y56..58

    index = (
        7 * 128 + x
    )

    framebuffer[index] &= 0xF8


# ============================================================
# SEND ONE ECG COLUMN
#
# 7 data bytes only.
# ============================================================

def send_waveform_column(x):

    if x < 64:

        left_controller()

        local_x = x

    else:

        right_controller()

        local_x = x - 64


    for page in range(1, 8):

        set_page(page)

        set_column(local_x)

        index = (
            page * 128 + x
        )

        send_data(
            framebuffer[index]
        )


    deselect_controllers()


# ============================================================
# DRAW ONE DISPLAY POINT
# ============================================================

def draw_display_point(value):

    global display_x

    global previous_y


    y = ecg_to_y(value)


    # Clear the old waveform at this X.

    clear_waveform_column(
        display_x
    )


    # Draw line from previous point.

    if previous_y is not None:

        y1 = previous_y

        y2 = y

        dy = y2 - y1

        steps = abs(dy)


        if steps == 0:

            steps = 1


        for i in range(steps + 1):

            yy = y1 + (
                (dy * i) // steps
            )


            if yy < ECG_TOP:

                yy = ECG_TOP

            elif yy > ECG_BOTTOM:

                yy = ECG_BOTTOM


            set_pixel(
                display_x,
                yy
            )

    else:

        set_pixel(
            display_x,
            y
        )


    previous_y = y


    # Write ONLY current column.

    send_waveform_column(
        display_x
    )


    # Move horizontally.

    display_x += 1


    if display_x >= 128:

        display_x = 0

        previous_y = None


# ============================================================
# RESET HR FOR NEW STAGE
# ============================================================

def reset_ecg_analysis():

    global sample_counter

    global last_peak_sample

    global rr_history

    global HR

    global STATUS

    global WAITING_TICKS

    global WAITING_STATE


    sample_counter = 0

    last_peak_sample = -1

    rr_history = []

    HR = 0

    STATUS = "ECG."

    WAITING_TICKS = 0

    WAITING_STATE = 0


# ============================================================
# START NEW STAGE
# ============================================================

def start_new_stage():

    global stage_sample_count

    global display_samples

    global previous_y


    reset_ecg_analysis()


    stage_sample_count = 0

    display_samples = []

    previous_y = None


    update_status_display()


    print(
        "NEW STAGE"
    )


# ============================================================
# FINISH STAGE
# ============================================================

def finish_stage():

    global display_samples

    global previous_y


    display_samples = []

    previous_y = None


    print(
        "STAGE COMPLETE"
    )


# ============================================================
# ORIGINAL WORKING HR ALGORITHM
# ============================================================

def process_ecg(samples):

    global sample_counter

    global last_peak_sample

    global rr_history

    global HR

    global STATUS

    global WAITING_TICKS

    global WAITING_STATE


    if len(samples) < 3:

        sample_counter += len(samples)

        return


    for i in range(
        1,
        len(samples) - 1
    ):

        current = samples[i]

        previous = samples[i - 1]

        next_value = samples[i + 1]


        current_sample = (
            sample_counter + i
        )


        is_peak = (

            current >= PEAK_THRESHOLD

            and current >= previous

            and current >= next_value

        )


        if is_peak:


            if last_peak_sample < 0:

                last_peak_sample = (
                    current_sample
                )

                continue


            rr = (
                current_sample -
                last_peak_sample
            )


            if (

                rr >= REFRACTORY_SAMPLES

                and rr <= 255

            ):


                rr_history.append(
                    rr
                )


                if len(rr_history) > RR_HISTORY_SIZE:

                    rr_history.pop(0)


                last_peak_sample = (
                    current_sample
                )


                total_rr = 0


                for value in rr_history:

                    total_rr += value


                average_rr = (
                    total_rr //
                    len(rr_history)
                )


                if average_rr > 0:


                    calculated_hr = (
                        FS * 60
                    ) // average_rr


                    if calculated_hr > 0:


                        HR = calculated_hr


                        WAITING_TICKS = 0

                        WAITING_STATE = 0


                        if HR < 60:

                            STATUS = "BRADY"

                        elif HR > 100:

                            STATUS = "TACHY"

                        else:

                            STATUS = "NORMAL"


    sample_counter += len(samples)


# ============================================================
# PROCESS DISPLAY SAMPLES
#
# Every 4 ECG samples -> 1 display point.
#
# We use the LAST sample of the group.
# This avoids min/max vertical columns.
# ============================================================

def process_display_samples(samples):

    global stage_sample_count

    global display_samples


    for value in samples:

        # ----------------------------------------------------
        # Stage boundary
        # ----------------------------------------------------

        if stage_sample_count >= STAGE_SAMPLES:

            finish_stage()

            start_new_stage()


        # ----------------------------------------------------
        # Add sample to display decimation buffer
        # ----------------------------------------------------

        display_samples.append(
            value
        )


        stage_sample_count += 1


        # ----------------------------------------------------
        # 4 samples -> one GLCD point
        # ----------------------------------------------------

        if len(display_samples) >= DISPLAY_SAMPLES:

            # Use the LAST sample.
            #
            # No min/max vertical bar.
            # This preserves the actual ECG trace.

            value_to_display = (
                display_samples[
                    DISPLAY_SAMPLES - 1
                ]
            )


            draw_display_point(
                value_to_display
            )


            display_samples = []


        # ----------------------------------------------------
        # End of 1280-sample stage
        # ----------------------------------------------------

        if stage_sample_count >= STAGE_SAMPLES:

            # Do not clear display.
            # Keep waveform visible.

            finish_stage()


# ============================================================
# INITIALIZATION
# ============================================================

glcd_init()

start_new_stage()


print(
    "============================================"
)

print(
    " ECG LIVE SWEEP - PROTEUS SAFE"
)

print(
    "============================================"
)

print(
    "FS =",
    FS,
    "Hz"
)

print(
    "FRAME_SIZE =",
    FRAME_SIZE
)

print(
    "STAGE =",
    STAGE_SAMPLES,
    "samples"
)

print(
    "DISPLAY_DECIMATION =",
    DISPLAY_SAMPLES
)

print(
    "DISPLAY_RATE =",
    DISPLAY_RATE,
    "columns/sec"
)

print(
    "VISIBLE_TIME =",
    "4 seconds"
)

print(
    "MODE =",
    "LIVE SWEEP"
)

print(
    "============================================"
)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    if timer_flag:

        timer_flag = False


        # ----------------------------------------------------
        # Waiting animation
        # ----------------------------------------------------

        if HR == 0:

            update_waiting_animation()


        # ----------------------------------------------------
        # UART
        # ----------------------------------------------------

        if uart.any():

            data = uart.read()


            if data is not None:

                rx_buffer.extend(
                    data
                )


                # ------------------------------------------------
                # Complete 128-sample frames
                # ------------------------------------------------

                while len(rx_buffer) >= FRAME_SIZE:


                    frame = rx_buffer[
                        :FRAME_SIZE
                    ]


                    rx_buffer = rx_buffer[
                        FRAME_SIZE:
                    ]


                    # --------------------------------------------
                    # HR detection
                    # --------------------------------------------

                    process_ecg(
                        frame
                    )


                    # --------------------------------------------
                    # Live display
                    # --------------------------------------------

                    process_display_samples(
                        frame
                    )


                    # --------------------------------------------
                    # Update status ONLY if changed
                    # --------------------------------------------

                    update_status_display()


                    # --------------------------------------------
                    # Acknowledge transmitter
                    # --------------------------------------------

                    uart.write(
                        b"FRAME_OK"
                    )


                    print(
                        "FRAME_OK",
                        "HR=",
                        HR,
                        "STATUS=",
                        STATUS,
                        "STAGE=",
                        stage_sample_count,
                        "/",
                        STAGE_SAMPLES,
                        "X=",
                        display_x
                    )