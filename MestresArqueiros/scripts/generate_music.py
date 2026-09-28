import wave
import struct
import math
import os

os.makedirs("assets/music", exist_ok=True)
SAMPLE_RATE = 22050

def create_wave_file(filename, samples):
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        data = bytearray()
        for s in samples:
            val = max(-0.95, min(0.95, s))
            int_val = int(val * 32767)
            data.extend(struct.pack('<h', int_val))
        wf.writeframes(data)

def gen_menu_music():
    # 8-second pleasant ambient medieval harp loop (A minor: A, C, E, G, D)
    bpm = 100
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_dur = total_beats * beat_dur
    n_samples = int(SAMPLE_RATE * total_dur)
    samples = [0.0] * n_samples

    # Chord progression: Am -> F -> C -> G
    notes_timeline = [
        # Am
        (0.0, 220.00), (0.5, 261.63), (1.0, 329.63), (1.5, 440.00),
        # F
        (2.0, 174.61), (2.5, 261.63), (3.0, 349.23), (3.5, 440.00),
        # C
        (4.0, 261.63), (4.5, 329.63), (5.0, 392.00), (5.5, 523.25),
        # G / Em
        (6.0, 196.00), (6.5, 246.94), (7.0, 293.66), (7.5, 392.00),
    ]

    for start_beat, freq in notes_timeline:
        start_time = start_beat * beat_dur
        dur = beat_dur * 1.8
        start_idx = int(start_time * SAMPLE_RATE)
        dur_samples = int(dur * SAMPLE_RATE)
        for i in range(dur_samples):
            idx = (start_idx + i) % n_samples
            t = i / SAMPLE_RATE
            # Pluck envelope: quick rise, exponential decay
            env = math.sin(math.pi * min(1.0, t / 0.02)) * math.exp(-t * 2.8)
            # Warm acoustic harmonics
            harm1 = math.sin(2 * math.pi * freq * t)
            harm2 = 0.5 * math.sin(2 * math.pi * freq * 2 * t)
            harm3 = 0.25 * math.sin(2 * math.pi * freq * 3 * t)
            samples[idx] += (harm1 + harm2 + harm3) * env * 0.25

    create_wave_file("assets/music/menu.wav", samples)

def gen_game_music():
    # 12-second rhythmic fantasy battle loop (Dm pentatonic with percussion)
    bpm = 120
    beat_dur = 60.0 / bpm
    total_beats = 24
    total_dur = total_beats * beat_dur
    n_samples = int(SAMPLE_RATE * total_dur)
    samples = [0.0] * n_samples

    # Bass ostinato (D2, D3, F2, G2, A2)
    bass_line = [
        (0, 73.42), (0.75, 73.42), (1.5, 110.0), (2, 87.31), (2.75, 98.0), (3.5, 110.0),
        (4, 73.42), (4.75, 73.42), (5.5, 110.0), (6, 87.31), (6.75, 98.0), (7.5, 73.42),
        (8, 73.42), (8.75, 73.42), (9.5, 110.0), (10, 87.31), (10.75, 98.0), (11.5, 110.0)
    ]
    # Repeat for 24 beats
    for beat, freq in bass_line:
        for offset in [0, 12]:
            start_time = (beat + offset) * beat_dur
            start_idx = int(start_time * SAMPLE_RATE)
            dur = beat_dur * 0.7
            dur_samples = int(dur * SAMPLE_RATE)
            for i in range(dur_samples):
                idx = (start_idx + i) % n_samples
                t = i / SAMPLE_RATE
                env = math.sin(math.pi * min(1.0, t / 0.01)) * math.exp(-t * 5.0)
                samples[idx] += math.sin(2 * math.pi * freq * t) * env * 0.25

    # Flute/Lead melody
    melody = [
        (0.0, 293.66), (1.0, 349.23), (2.0, 392.00), (3.0, 440.00), (4.0, 523.25), (5.0, 440.00),
        (6.0, 392.00), (7.0, 349.23), (8.0, 293.66), (9.5, 349.23), (10.0, 293.66), (11.0, 261.63),
        (12.0, 293.66), (13.0, 392.00), (14.0, 440.00), (15.0, 587.33), (16.5, 523.25), (17.5, 440.00),
        (18.0, 392.00), (19.0, 349.23), (20.0, 329.63), (21.0, 293.66), (22.0, 261.63), (23.0, 220.00)
    ]
    for beat, freq in melody:
        start_time = beat * beat_dur
        dur = beat_dur * 0.9
        start_idx = int(start_time * SAMPLE_RATE)
        dur_samples = int(dur * SAMPLE_RATE)
        for i in range(dur_samples):
            idx = (start_idx + i) % n_samples
            t = i / SAMPLE_RATE
            env = math.sin(math.pi * min(1.0, t / 0.04)) * math.exp(-t * 2.2)
            vib = 1.0 + 0.02 * math.sin(2 * math.pi * 5.0 * t)
            flute = math.sin(2 * math.pi * freq * vib * t) + 0.2 * math.sin(4 * math.pi * freq * vib * t)
            samples[idx] += flute * env * 0.18

    # Drum beat (kick on beats, snare on offbeats)
    for b in range(total_beats):
        start_time = b * beat_dur
        start_idx = int(start_time * SAMPLE_RATE)
        # Kick
        for i in range(int(0.12 * SAMPLE_RATE)):
            idx = (start_idx + i) % n_samples
            t = i / SAMPLE_RATE
            freq = 110 * math.exp(-t * 30.0)
            env = math.exp(-t * 20.0)
            samples[idx] += math.sin(2 * math.pi * freq * t) * env * 0.35
        # Snare/hi-hat on offbeats
        if b % 2 == 1:
            snare_time = (b + 0.5) * beat_dur
            snare_idx = int(snare_time * SAMPLE_RATE)
            import random
            for i in range(int(0.08 * SAMPLE_RATE)):
                idx = (snare_idx + i) % n_samples
                t = i / SAMPLE_RATE
                env = math.exp(-t * 35.0)
                noise = (random.random() * 2.0 - 1.0)
                samples[idx] += noise * env * 0.15

    create_wave_file("assets/music/game.wav", samples)

if __name__ == "__main__":
    gen_menu_music()
    gen_game_music()
    print("Music tracks generated successfully!")
