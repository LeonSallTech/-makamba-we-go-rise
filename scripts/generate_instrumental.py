import math
import random
import wave
from array import array
from pathlib import Path


# ============================================================
# MAKAMBA WE GO RISE
# Full Instrumental Generator
# NumPy-free / Python standard library
# ============================================================

SAMPLE_RATE = 44100
BPM = 102

BEAT = 60.0 / BPM
BAR = BEAT * 4

OUTPUT = Path("stems/makamba_instrumental.wav")


# ------------------------------------------------------------
# Musical helpers
# ------------------------------------------------------------

NOTE_NAMES = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def midi_to_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def note(name, octave):
    return midi_to_freq(NOTE_NAMES[name] + (octave + 1) * 12)


def linspace(start, stop, count):
    if count <= 0:
        return []
    if count == 1:
        return [float(start)]

    step = (stop - start) / (count - 1)
    return [start + i * step for i in range(count)]


def envelope(length, attack=0.01, release=0.08):
    env = [1.0] * length

    a = min(int(SAMPLE_RATE * attack), length)
    r = min(int(SAMPLE_RATE * release), length)

    if a > 0:
        values = linspace(0.0, 1.0, a)
        for i, value in enumerate(values):
            env[i] = value

    if r > 0:
        values = linspace(1.0, 0.0, r)
        start = length - r

        for i, value in enumerate(values):
            env[start + i] *= value

    return env


def tone(freq, duration, volume=0.2, harmonics=()):
    length = max(1, int(duration * SAMPLE_RATE))

    signal = [0.0] * length
    env = envelope(length)

    for i in range(length):
        t = i / SAMPLE_RATE

        value = math.sin(
            2.0 * math.pi * freq * t
        )

        for multiple, level in harmonics:
            value += level * math.sin(
                2.0 * math.pi * freq * multiple * t
            )

        signal[i] = value * env[i] * volume

    return signal


def add_audio(track, sound, start):
    position = int(start * SAMPLE_RATE)

    if position >= len(track):
        return

    if position < 0:
        return

    end = min(position + len(sound), len(track))

    for i in range(end - position):
        track[position + i] += sound[i]


# ------------------------------------------------------------
# Drums
# ------------------------------------------------------------

def kick(duration=0.18, volume=0.55):
    length = int(duration * SAMPLE_RATE)

    signal = [0.0] * length
    phase = 0.0

    for i in range(length):
        t = i / SAMPLE_RATE

        frequency = 130.0 * math.exp(-t * 25.0) + 45.0

        phase += (
            2.0 * math.pi * frequency / SAMPLE_RATE
        )

        value = math.sin(phase)

        value *= math.exp(-t * 20.0)

        signal[i] = value * volume

    return signal


def snare(duration=0.16, volume=0.22):
    length = int(duration * SAMPLE_RATE)

    rng = random.Random(7)

    signal = [0.0] * length

    for i in range(length):
        t = i / SAMPLE_RATE

        noise = rng.gauss(0.0, 1.0)

        signal[i] = (
            noise
            * math.exp(-t * 25.0)
            * volume
        )

    return signal


def hat(duration=0.055, volume=0.075):
    length = int(duration * SAMPLE_RATE)

    rng = random.Random(length + 13)

    signal = [0.0] * length

    for i in range(length):
        t = i / SAMPLE_RATE

        noise = rng.gauss(0.0, 1.0)

        signal[i] = (
            noise
            * math.exp(-t * 65.0)
            * volume
        )

    return signal


# ------------------------------------------------------------
# Chord system
# ------------------------------------------------------------

CHORDS = {
    "C": [
        note("C", 3),
        note("E", 3),
        note("G", 3),
    ],

    "Am": [
        note("A", 2),
        note("C", 3),
        note("E", 3),
    ],

    "F": [
        note("F", 2),
        note("A", 2),
        note("C", 3),
    ],

    "G": [
        note("G", 2),
        note("B", 2),
        note("D", 3),
    ],
}


BASS = {
    "C": note("C", 2),
    "Am": note("A", 1),
    "F": note("F", 1),
    "G": note("G", 1),
}


# ------------------------------------------------------------
# Section generator
# ------------------------------------------------------------

def build_section(
    bars,
    progression,
    drums=True,
    bass=True,
    melody=True,
    intensity=1.0,
    percussion=True,
):
    duration = bars * BAR

    track = [0.0] * int(
        duration * SAMPLE_RATE
    )

    for bar_index in range(bars):

        chord_name = progression[
            bar_index % len(progression)
        ]

        chord = CHORDS[chord_name]
        bass_note = BASS[chord_name]

        bar_start = bar_index * BAR

        # ------------------------
        # Chord pad
        # ------------------------

        for chord_note in chord:

            sound = tone(
                chord_note,
                BAR * 0.95,
                volume=0.055 * intensity,
                harmonics=[
                    (2, 0.18),
                    (3, 0.06),
                ],
            )

            add_audio(
                track,
                sound,
                bar_start,
            )

        # ------------------------
        # Bass
        # ------------------------

        if bass:

            for beat in range(4):

                start = (
                    bar_start
                    + beat * BEAT
                )

                sound = tone(
                    bass_note,
                    BEAT * 0.75,
                    volume=0.16 * intensity,
                    harmonics=[
                        (2, 0.10),
                    ],
                )

                add_audio(
                    track,
                    sound,
                    start,
                )

        # ------------------------
        # Drums
        # ------------------------

        if drums:

            for beat in range(4):

                start = (
                    bar_start
                    + beat * BEAT
                )

                sound = kick(
                    volume=0.42 * intensity
                )

                add_audio(
                    track,
                    sound,
                    start,
                )

            for beat in [1, 3]:

                start = (
                    bar_start
                    + beat * BEAT
                )

                sound = snare(
                    volume=0.18 * intensity
                )

                add_audio(
                    track,
                    sound,
                    start,
                )

        # ------------------------
        # Hi-hats
        # ------------------------

        if percussion:

            for half in range(8):

                beat = half * 0.5

                sound = hat(
                    volume=0.055 * intensity
                )

                add_audio(
                    track,
                    sound,
                    bar_start + beat * BEAT,
                )

        # ------------------------
        # Melody
        # ------------------------

        if melody:

            melody_notes = [
                chord[1],
                chord[2],
                chord[1],
                chord[0],
                chord[2],
                chord[1],
                chord[0],
                chord[1],
            ]

            for i, freq in enumerate(
                melody_notes
            ):

                start = (
                    bar_start
                    + i * 0.5 * BEAT
                )

                sound = tone(
                    freq,
                    BEAT * 0.38,
                    volume=0.065 * intensity,
                    harmonics=[
                        (2, 0.20),
                        (3, 0.08),
                    ],
                )

                add_audio(
                    track,
                    sound,
                    start,
                )

    return track


# ------------------------------------------------------------
# Join audio sections
# ------------------------------------------------------------

def join_sections(sections):

    total_length = sum(
        len(section)
        for section in sections
    )

    audio = [0.0] * total_length

    position = 0

    for section in sections:

        for i, value in enumerate(section):
            audio[position + i] = value

        position += len(section)

    return audio


# ------------------------------------------------------------
# Apply fade
# ------------------------------------------------------------

def apply_fade(audio):

    fade_time = min(
        3.0,
        len(audio) / SAMPLE_RATE / 2,
    )

    fade_samples = int(
        fade_time * SAMPLE_RATE
    )

    if fade_samples <= 0:
        return

    fade_in = linspace(
        0.0,
        1.0,
        fade_samples,
    )

    fade_out = linspace(
        1.0,
        0.0,
        fade_samples,
    )

    for i in range(fade_samples):

        audio[i] *= fade_in[i]

        audio[
            len(audio) - fade_samples + i
        ] *= fade_out[i]


# ------------------------------------------------------------
# Normalize
# ------------------------------------------------------------

def normalize(audio, target=0.92):

    peak = 0.0

    for value in audio:

        absolute = abs(value)

        if absolute > peak:
            peak = absolute

    if peak <= 0.0:
        return

    multiplier = target / peak

    for i in range(len(audio)):
        audio[i] *= multiplier


# ------------------------------------------------------------
# Write stereo WAV
# ------------------------------------------------------------

def write_wav(audio):

    pcm = array("h")

    for value in audio:

        value = max(
            -1.0,
            min(1.0, value),
        )

        sample = int(
            value * 32767
        )

        # Stereo: duplicate mono sample
        pcm.append(sample)
        pcm.append(sample)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(OUTPUT),
        "wb",
    ) as wav:

        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        wav.writeframes(
            pcm.tobytes()
        )


# ------------------------------------------------------------
# Build complete song
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("MAKAMBA WE GO RISE")
    print("FULL INSTRUMENTAL GENERATOR")
    print("NUMPY-FREE PYTHON BUILD")
    print("=" * 60)

    sections = []

    progression = [
        "C",
        "Am",
        "F",
        "G",
    ]

    # --------------------------------------------------------
    # INTRO
    # --------------------------------------------------------

    print("Building INTRO...")

    sections.append(
        build_section(
            bars=8,
            progression=progression,
            drums=False,
            bass=True,
            melody=True,
            intensity=0.35,
            percussion=False,
        )
    )

    # --------------------------------------------------------
    # VERSE 1
    # --------------------------------------------------------

    print("Building VERSE 1...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=0.65,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # PRE-CHORUS
    # --------------------------------------------------------

    print("Building PRE-CHORUS...")

    sections.append(
        build_section(
            bars=8,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=0.80,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # CHORUS
    # --------------------------------------------------------

    print("Building CHORUS...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=1.00,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # VERSE 2
    # --------------------------------------------------------

    print("Building VERSE 2...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=0.75,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # CALL & RESPONSE
    # --------------------------------------------------------

    print("Building CALL & RESPONSE...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=0.95,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # INSTRUMENTAL DANCE BREAK
    # --------------------------------------------------------

    print("Building DANCE BREAK...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=1.10,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # BRIDGE
    # --------------------------------------------------------

    print("Building BRIDGE...")

    sections.append(
        build_section(
            bars=8,
            progression=[
                "Am",
                "F",
                "C",
                "G",
            ],
            drums=False,
            bass=True,
            melody=True,
            intensity=0.55,
            percussion=False,
        )
    )

    # --------------------------------------------------------
    # FINAL CHORUS
    # --------------------------------------------------------

    print("Building FINAL CHORUS...")

    sections.append(
        build_section(
            bars=16,
            progression=progression,
            drums=True,
            bass=True,
            melody=True,
            intensity=1.15,
            percussion=True,
        )
    )

    # --------------------------------------------------------
    # OUTRO
    # --------------------------------------------------------

    print("Building OUTRO...")

    sections.append(
        build_section(
            bars=8,
            progression=progression,
            drums=False,
            bass=True,
            melody=True,
            intensity=0.40,
            percussion=False,
        )
    )

    # --------------------------------------------------------
    # Join sections
    # --------------------------------------------------------

    print("Joining sections...")

    audio = join_sections(sections)

    print("Applying fade...")

    apply_fade(audio)

    print("Normalizing...")

    normalize(audio)

    print("Writing WAV...")

    write_wav(audio)

    duration = len(audio) / SAMPLE_RATE

    total_bars = sum([
        8,
        16,
        8,
        16,
        16,
        16,
        16,
        8,
        16,
        8,
    ])

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Output:   {OUTPUT}")
    print(f"BPM:      {BPM}")
    print(f"Bars:     {total_bars}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Minutes:  {duration / 60:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
