import wave
import struct
import math
import random
import os

os.makedirs("assets/sounds", exist_ok=True)
SAMPLE_RATE = 44100

def create_wave_file(filename, samples):
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        data = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s))
            int_val = int(val * 32767)
            data.extend(struct.pack('<h', int_val))
        wf.writeframes(data)

def gen_shoot():
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 18.0)
        # Twang pitch drops quickly from 480Hz to 120Hz
        freq = 120 + 360 * math.exp(-t * 25.0)
        osc = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 40.0) * 0.4
        samples.append((osc * 0.7 + noise) * env)
    create_wave_file("assets/sounds/shoot.wav", samples)

def gen_hit():
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 22.0)
        # Impact punch + squish
        freq = 80 + 160 * math.exp(-t * 30.0)
        osc = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 20.0) * 0.5
        samples.append((osc * 0.6 + noise * 0.5) * env)
    create_wave_file("assets/sounds/hit.wav", samples)

def gen_headshot():
    duration = 0.4
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 12.0)
        # Deep crunch + high chime
        bass = math.sin(2 * math.pi * 90 * t) * math.exp(-t * 20.0)
        chime1 = math.sin(2 * math.pi * 880 * t) * 0.35
        chime2 = math.sin(2 * math.pi * 1320 * t) * 0.25
        crunch = (random.random() * 2.0 - 1.0) * math.exp(-t * 35.0) * 0.6
        samples.append((bass * 0.5 + chime1 + chime2 + crunch) * env)
    create_wave_file("assets/sounds/headshot.wav", samples)

def gen_explosion():
    duration = 0.7
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 5.0)
        bass = math.sin(2 * math.pi * (50 * math.exp(-t * 3.0)) * t) * 0.6
        noise = (random.random() * 2.0 - 1.0) * 0.8
        distorted = math.tanh((bass + noise) * 1.5)
        samples.append(distorted * env * 0.9)
    create_wave_file("assets/sounds/explosion.wav", samples)

def gen_dirt():
    duration = 0.2
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 25.0)
        bass = math.sin(2 * math.pi * 70 * t) * 0.5
        noise = (random.random() * 2.0 - 1.0) * 0.5
        samples.append((bass + noise) * env * 0.6)
    create_wave_file("assets/sounds/dirt.wav", samples)

def gen_click():
    duration = 0.05
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 80.0)
        osc = math.sin(2 * math.pi * 1200 * t)
        samples.append(osc * env * 0.5)
    create_wave_file("assets/sounds/click.wav", samples)

def gen_victory():
    duration = 1.2
    n = int(SAMPLE_RATE * duration)
    samples = []
    # Simple triumphant arpeggio: C5 (523), E5 (659), G5 (784), C6 (1046)
    notes = [(0.0, 0.25, 523.25), (0.2, 0.45, 659.25), (0.4, 0.65, 783.99), (0.6, 1.2, 1046.50)]
    for i in range(n):
        t = i / SAMPLE_RATE
        val = 0.0
        for start, end, freq in notes:
            if start <= t < end:
                nt = t - start
                env = math.sin(math.pi * min(1.0, nt / 0.05)) * math.exp(-nt * 3.0)
                val += math.sin(2 * math.pi * freq * t) * env * 0.4
                val += math.sin(4 * math.pi * freq * t) * env * 0.15 # harmonic
        samples.append(val)
    create_wave_file("assets/sounds/victory.wav", samples)

def gen_defeat():
    duration = 1.0
    n = int(SAMPLE_RATE * duration)
    samples = []
    # Descending sad tone: E4 (329), D4 (293), C4 (261), A3 (220)
    notes = [(0.0, 0.3, 329.63), (0.25, 0.55, 293.66), (0.5, 0.75, 261.63), (0.7, 1.0, 220.00)]
    for i in range(n):
        t = i / SAMPLE_RATE
        val = 0.0
        for start, end, freq in notes:
            if start <= t < end:
                nt = t - start
                env = math.sin(math.pi * min(1.0, nt / 0.05)) * math.exp(-nt * 4.0)
                val += math.sin(2 * math.pi * freq * t) * env * 0.4
        samples.append(val)
    create_wave_file("assets/sounds/defeat.wav", samples)

if __name__ == "__main__":
    gen_shoot()
    gen_hit()
    gen_headshot()
    gen_explosion()
    gen_dirt()
    gen_click()
    gen_victory()
    gen_defeat()
    print("All sound effects generated successfully!")
