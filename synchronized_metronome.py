import time

BPM = 130

# Every x'th beat is highlighted
SIGNIFICANT_BEAT = 8

## POSITIVE means the beep comes later
## NEGATIVE means the beep comes earlier
TIME_SHIFT = -0.15

# Frequency of metronome beeps
BASE_FREQUENCY = 440

# Frequency of the highlighted beep
SIGNIFICANT_FREQUENCY = 880

# Beep length in milliseconds
BEEP_LENGTH = 20

try:
    import winsound
except ImportError:
    import numpy as np
    import simpleaudio as sa
    sounds = {}
    def generate_sound(x,z):
        frequency = x # Our played note will be 440 Hz
        fs = 44100  # 44100 samples per second
        seconds = z  # Note duration of z seconds

        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        t = np.linspace(0, seconds, int(seconds * fs), False)

        # Generate a 440 Hz sine wave
        note = np.sin(frequency * t * 2 * np.pi)

        # Ensure that highest value is in 16-bit range
        audio = note * (2**15 - 1) / np.max(np.abs(note))
        # Convert to 16-bit data
        audio = audio.astype(np.int16)
        sounds[(frequency, seconds)] = audio

    def sound(frequency, milliseconds):
        fs = 44100  # 44100 samples per second
        seconds = milliseconds / 1000

        if (frequency, seconds) not in sounds:
            generate_sound(frequency, seconds)

        # Start playback
        play_obj = sa.play_buffer(sounds[(frequency, seconds)], 1, 2, fs)

        # Wait for playback to finish before exiting
        play_obj.wait_done()
else:
    def sound(frequency, duration):
        winsound.Beep(frequency, duration)


def _main():
    delay = 60 / BPM
    start_delay = delay * SIGNIFICANT_BEAT
    time.sleep(start_delay - (time.time() + TIME_SHIFT) % start_delay)
    while True:
        for i in range(SIGNIFICANT_BEAT):
            if i == 0:
                print(f'{time.time() % 1000:.4f}*')
                sound(SIGNIFICANT_FREQUENCY, BEEP_LENGTH)
            else:
                print(f'{time.time() % 1000:.4f}')
                sound(BASE_FREQUENCY, BEEP_LENGTH)
            time.sleep(delay - (time.time()+TIME_SHIFT) % delay)

_main()
