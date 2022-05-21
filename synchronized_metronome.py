import time
import typing

# The BPM of the metronome
BPM = 130

# Every x'th beat is highlighted
SIGNIFICANT_BEAT = 8

## POSITIVE means the beep comes later
## NEGATIVE means the beep comes earlier
TIME_SHIFT = +0.20

# Frequency of metronome beeps
BASE_FREQUENCY = 440

# Frequency of the highlighted beep
SIGNIFICANT_FREQUENCY = 880

# Beep length in milliseconds
BEEP_LENGTH = 20

# A complicated mess to make a beep sound I've hidden.
try:
    import winsound
except ImportError:
    import numpy as np
    import simpleaudio as sa # type: ignore

    # Cache generated sounds
    sounds = {}
    SAMPLE_RATE = 44100

    def generate_sound(frequency: float, seconds: float) -> np.int16:
        """ Inspired by https://stackoverflow.com/a/58251257 """
        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        array = np.linspace(0, seconds, int(seconds * SAMPLE_RATE), False)

        # Generate a sine wave at the specified frequency
        note = np.sin(frequency * array * 2 * np.pi)

        # Ensure that highest value is in 16-bit range
        audio = note * (2**15 - 1) / np.max(np.abs(note))

        # Convert to 16-bit data
        return typing.cast(np.int16, audio.astype(np.int16))

    def sound(frequency: int, milliseconds: int) -> None:
        seconds = milliseconds / 1000
        key = (frequency, seconds)

        if key not in sounds:
            sounds[key] = generate_sound(*key)

        # Start playback
        play_obj = sa.play_buffer(sounds[key], 1, 2, SAMPLE_RATE)

        # Wait for playback to finish before exiting
        play_obj.wait_done()
else:
    def sound(frequency: int, milliseconds: int) -> None:
        winsound.Beep(frequency, milliseconds) # type: ignore


def main() -> None:
    # Calculate time between each beat
    delay = 60 / BPM

    # Calculate how long between synchronized starts
    start_delay = delay * SIGNIFICANT_BEAT

    # Wait until the next synchronized start
    time.sleep(start_delay - (time.time() + TIME_SHIFT) % start_delay)


    while True:
        for i in range(SIGNIFICANT_BEAT):
            # If it's a 1, beep at a different frequency
            if i == 0:
                sound(SIGNIFICANT_FREQUENCY, BEEP_LENGTH)
            else:
                sound(BASE_FREQUENCY, BEEP_LENGTH)

            # Wait until we need to beep next time
            time.sleep(delay - (time.time()+TIME_SHIFT) % delay)

# Start the program!
main()
