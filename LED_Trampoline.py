import time
import board
import neopixel
import random
import digitalio

pixel_pin = board.D10
pixel_count = 180
debounce_delay = 0.2  # Tweak this if you're having issues with the button changing modes

pixels = neopixel.NeoPixel(pixel_pin, pixel_count, brightness=.4, auto_write=False)

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

button_switch = digitalio.DigitalInOut(board.D9)
button_switch.direction = digitalio.Direction.INPUT
button_switch.pull = digitalio.Pull.UP

vibration_switch = digitalio.DigitalInOut(board.D7)
vibration_switch.direction = digitalio.Direction.INPUT
vibration_switch.pull = digitalio.Pull.UP

# Colors:
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
# Sparkle colors:
GOLD = (255, 222, 30)
PINK = (242, 90, 255)
AQUA = (50, 255, 255)
JADE = (0, 255, 40)
AMBER = (255, 100, 0)


def cycle_sequence(seq):
    while True:
        yield from seq


def fade_control():
    brightness_value = iter([r / 15 for r in range(15, -1, -1)])
    while True:
        # pylint: disable=stop-iteration-return
        pixels.brightness = next(brightness_value)
        pixels.show()
        yield


def sparkle_code(color_values):
    (red_value, green_value, blue_value) = color_values
    p = random.randint(0, (pixel_count - 2))
    pixels[p] = (red_value, green_value, blue_value)
    pixels.show()
    time.sleep(sparkle_delay_seconds * random.randint(0, sparkle_delay_multiplier))
    pixels[p] = (int(red_value / 2), int(green_value / 2), int(blue_value / 2))
    pixels.show()
    pixels[p + 1] = (int(red_value / 5), int(green_value / 5), int(blue_value / 5))
    pixels.show()


sparkle_delay_seconds = 0
sparkle_delay_multiplier = 0

fade = fade_control()

sparkle_list = [
    lambda: sparkle_code(PINK),
    lambda: sparkle_code(GOLD),
    lambda: sparkle_code(AQUA),
    lambda: sparkle_code(JADE),
    lambda: sparkle_code(AMBER)
]

sparkles = cycle_sequence(sparkle_list)

flash_color = cycle_sequence([RED, YELLOW, ORANGE, GREEN, TEAL, CYAN,
                              BLUE, PURPLE, MAGENTA, WHITE])

chase_color_list = (RED,
                    ORANGE,
                    YELLOW,
                    GREEN,
                    BLUE,
                    PURPLE)

chase_color_index = 0
chase_color_cycle = chase_color_list[chase_color_index]
offset = 0

chase_color_length = 3  # Time in seconds each color lasts in the color chase mode
chase_last_color = time.monotonic()
chase_next_color = chase_last_color + chase_color_length

mode = 0
initial_time = time.monotonic()

try:
    while True:
        now = time.monotonic()
        if now - initial_time > debounce_delay:
            print("Mode:", mode)
            initial_time = time.monotonic()
            if button_switch.value is False:
                print("Mode Change")
                led.value = True
                pixels.fill((0, 0, 0))
                mode += 1
                print("Mode:,", mode)
                if mode > 2:
                    mode = 0
        if mode == 0:
            try:
                if vibration_switch.value is False:
                    print("Flash and fade mode activate!")
                    fade = fade_control()
                    pixels.fill(next(flash_color))
                    pixels.show()
                next(fade)
            except StopIteration:
                pass
        if mode == 1 and vibration_switch.value is False:
            print("Sparkle mode activate!")
            next(sparkles)()
        if mode == 2 and vibration_switch.value is False:
            print("Chase mode activate!")
            for i in range(0, pixel_count):
                c = 0

                if ((offset + i) & 7) < 4:
                    c = chase_color_cycle
                pixels[i] = c
                pixels[(pixel_count - 1) - i] = c
            pixels.show()
            offset += 1
            if now >= chase_next_color:
                if chase_color_index > 5:
                    chase_color_index = 0
                chase_color_cycle = chase_color_list[chase_color_index]
                chase_color_index += 1
                for i in range(0, pixel_count):
                    pixels[i] = (0, 0, 0)
                chase_last_color = now
                chase_next_color = chase_last_color + chase_color_length
        else:
            led.value = False
except MemoryError:
    pass
