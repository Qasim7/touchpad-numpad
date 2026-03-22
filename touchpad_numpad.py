from evdev import InputDevice, ecodes as e, list_devices, UInput

# ==== Avtomatik touchpad tapmaq ====
devices = [InputDevice(path) for path in list_devices()]
touchpad = None
for dev in devices:
    if 'synaptics' in dev.name.lower() or 'elantech' in dev.name.lower() or 'touchpad' in dev.name.lower() or 'trackpad' in dev.name.lower():
        touchpad = dev
        break

if not touchpad:
    print("Touchpad tapılmadı! Hardcoded yolu istifadə olunur: /dev/input/event5")
    TOUCHPAD = "/dev/input/event5"
    dev = InputDevice(TOUCHPAD)
    MAX_X = 1940
    MAX_Y = 1297
else:
    dev = touchpad
    TOUCHPAD = dev.path
    abs_x = dev.absinfo(e.ABS_X)
    abs_y = dev.absinfo(e.ABS_Y)
    MAX_X = abs_x.max
    MAX_Y = abs_y.max
    print(f"Touchpad tapıldı: {TOUCHPAD}, MAX_X={MAX_X}, MAX_Y={MAX_Y}")

ui = UInput()

# Başlanğıc vəziyyət
enabled = False
x = y = 0
fingers = 0

# ==== Grid layout sənin vizual dizayna uyğun ====
# Row 0: 7 8 9 /  ON toggle
# Row 1: 4 5 6 *  ⌫
# Row 2: 1 2 3 -  TAB
# Row 3: 0 0 . +  ENTER
grid = [
    [e.KEY_7, e.KEY_8, e.KEY_9, e.KEY_KPSLASH, "TOGGLE"],   # üst sətir (ON)
    [e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_KPASTERISK, e.KEY_BACKSPACE],
    [e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_KPMINUS, e.KEY_TAB],
    [e.KEY_0, e.KEY_0, e.KEY_DOT, e.KEY_KPPLUS, e.KEY_ENTER],
]

print("Touchpad numpad başladı. Sol yuxarı ON/OFF toggle ilə idarə olunur.")

for event in dev.read_loop():

    # koordinat yenilənməsi
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

    # touch buraxıldı
    elif event.type == e.EV_KEY and event.code == e.BTN_TOUCH:
        if event.value == 0:

            # 👆 3 barmaq toggle
            if fingers >= 3:
                enabled = not enabled
                print("3 barmaq toggle:", enabled)
                continue

            # normalize edilmiş koordinat
            nx = x / MAX_X
            ny = y / MAX_Y

            # 4 sütun, 4 row (row sayı 4), sənin vizual grid-ə uyğun
            col = min(max(int(nx * 5), 0), 4)
            row = min(max(int(ny * 4), 0), 3)

            key = grid[row][col]

            # sol yuxarı toggle
            if key == "TOGGLE":
                enabled = not enabled
                print("Manual toggle:", enabled)
                continue

            if not enabled:
                continue

            # düyməni bas
            ui.write(e.EV_KEY, key, 1)
            ui.write(e.EV_KEY, key, 0)
            ui.syn()

            #print("Pressed:", key)
