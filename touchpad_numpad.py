from evdev import InputDevice, ecodes as e, list_devices, UInput

# ==== Automatic touchpad detection ====
devices = [InputDevice(path) for path in list_devices()]
touchpad = None
for dev in devices:
    if 'synaptics' in dev.name.lower() or 'elantech' in dev.name.lower() or 'touchpad' in dev.name.lower() or 'trackpad' in dev.name.lower():
        touchpad = dev
        break

if not touchpad:
    print("Touchpad not found! Hardcoded path is used: /dev/input/event5")
    TOUCHPAD = "/dev/input/event5"
    dev = InputDevice(TOUCHPAD)
    MAX_X = 1000
    MAX_Y = 700
else:
    dev = touchpad
    TOUCHPAD = dev.path
    abs_x = dev.absinfo(e.ABS_X)
    abs_y = dev.absinfo(e.ABS_Y)
    MAX_X = abs_x.max
    MAX_Y = abs_y.max
    print(f"Touchpad found: {TOUCHPAD}, MAX_X={MAX_X}, MAX_Y={MAX_Y}")

ui = UInput()

# Initial situation
enabled = False
x = y = 0
fingers = 0

# ==== Grid layout according to your visual design ====
# Row 0: 7 8 9 /toggle ON
# Row 1: 4 5 6 *⌫
# Row 2: 1 2 3 -  TAB
# Row 3: 0 0 . +  ENTER
grid = [
    [e.KEY_7, e.KEY_8, e.KEY_9, e.KEY_KPSLASH, "TOGGLE"],   # top line (ON)
    [e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_KPASTERISK, e.KEY_BACKSPACE],
    [e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_KPMINUS, e.KEY_TAB],
    [e.KEY_0, e.KEY_0, e.KEY_DOT, e.KEY_KPPLUS, e.KEY_ENTER],
]

print("Touchpad numpad started. Controlled by top left ON/OFF toggle.")

for event in dev.read_loop():

    # coordinate update
    if event.type == e.EV_ABS:
        if event.code == e.ABS_X:
            x = event.value
        elif event.code == e.ABS_Y:
            y = event.value
        elif event.code == e.ABS_MT_TRACKING_ID:
            if event.value == -1:
                fingers -= 1
            else:
                fingers += 1

    # touch is released
    elif event.type == e.EV_KEY and event.code == e.BTN_TOUCH:
        if event.value == 0:

            # 👆 3 finger toggle
            if fingers >= 3:
                enabled = not enabled
                print("3 finger toggle:", enabled)
                continue

            # normalized coordinate
            nx = x / MAX_X
            ny = y / MAX_Y

            # 4 columns, 4 rows (row number 4), according to your visual grid
            col = min(max(int(nx * 5), 0), 4)
            row = min(max(int(ny * 4), 0), 3)

            key = grid[row][col]

            # top left toggle
            if key == "TOGGLE":
                enabled = not enabled
                print("Manual toggle:", enabled)
                continue

            if not enabled:
                continue

            # press the button
            ui.write(e.EV_KEY, key, 1)
            ui.write(e.EV_KEY, key, 0)
            ui.syn()

            #print("Pressed:", key)
