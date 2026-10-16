import math
import os
import random
import struct
import wave

SAMPLE_RATE = 44100


def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write mono 16-bit PCM WAV file from float samples in [-1.0, 1.0]."""
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # Convert and clamp
        buf = bytearray(len(samples) * 2)
        for i, s in enumerate(samples):
            if s > 0.99:
                s = 0.99
            elif s < -0.99:
                s = -0.99
            val = int(s * 32767.0)
            struct.pack_into("<h", buf, i * 2, val)
        wf.writeframes(buf)
    print(f"Generated {filename} ({len(samples)/sample_rate:.2f}s)")


def envelope(t, duration, fade_in, fade_out):
    if t < fade_in and fade_in > 0:
        return 0.5 * (1.0 - math.cos(math.pi * (t / fade_in)))
    if t > duration - fade_out and fade_out > 0:
        rem = max(0.0, duration - t)
        return 0.5 * (1.0 - math.cos(math.pi * (rem / fade_out)))
    return 1.0


def generate_sfx_lluvia(filepath):
    """
    sfx-lluvia.wav (5.5s, for 0.0s - 5.5s):
    Soft cinematic rain (band-passed pink/brown noise + micro-droplets + subtle distant warm thunder around 1.8s),
    fade-in 0.3s, fade-out 0.8s (4.7s - 5.5s).
    """
    random.seed(101)
    duration = 5.5
    n_samples = int(duration * SAMPLE_RATE)
    samples = [0.0] * n_samples

    # Pink/brown noise filter states
    b0 = b1 = b2 = b3 = 0.0
    lp_rain = 0.0
    hp_rain = 0.0

    # Pre-generate micro-droplets (time_idx, freq, amp, decay)
    droplets = []
    for _ in range(180):
        idx = random.randint(0, n_samples - 1000)
        freq = random.uniform(1400.0, 3800.0)
        amp = random.uniform(0.015, 0.045)
        droplets.append((idx, freq, amp))

    # Add droplets into sample buffer first
    for idx, freq, amp in droplets:
        drop_len = int(0.018 * SAMPLE_RATE)
        for k in range(drop_len):
            if idx + k >= n_samples:
                break
            dt = k / SAMPLE_RATE
            # Pitch slightly rises like a water droplet bubble
            f_inst = freq * (1.0 + 12.0 * dt)
            env_d = math.exp(-dt * 220.0) * math.sin(math.pi * k / drop_len)
            samples[idx + k] += amp * env_d * math.sin(2.0 * math.pi * f_inst * dt)

    # Distant warm thunder around 1.8s (spanning 1.5s to 4.2s)
    thunder_lp1 = 0.0
    thunder_lp2 = 0.0

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        white = random.uniform(-1.0, 1.0)

        # Paul Kellet simplified pink noise approximation
        b0 = 0.99765 * b0 + white * 0.0990460
        b1 = 0.96300 * b1 + white * 0.2965164
        b2 = 0.57000 * b2 + white * 1.0526913
        pink = (b0 + b1 + b2 + white * 0.1848) * 0.08

        # Band-pass for velvety rain texture
        lp_rain = lp_rain + 0.18 * (pink - lp_rain)
        hp_rain = hp_rain + 0.015 * (lp_rain - hp_rain)
        rain_val = (lp_rain - hp_rain) * 0.55

        # Subtle wind swell in rain
        swell = 0.85 + 0.15 * math.sin(2.0 * math.pi * 0.35 * t)

        # Distant warm thunder around 1.8s
        thunder_val = 0.0
        if 1.4 <= t <= 4.3:
            tt = t - 1.4
            # Multi-swell rumble envelope peaking near 1.8s - 2.2s
            th_env = (
                math.exp(-((t - 1.85) ** 2) / 0.12) * 0.85
                + math.exp(-((t - 2.35) ** 2) / 0.35) * 0.55
                + math.exp(-((t - 3.05) ** 2) / 0.60) * 0.25
            )
            thunder_lp1 += 0.012 * (white - thunder_lp1)
            thunder_lp2 += 0.008 * (thunder_lp1 - thunder_lp2)
            sub_hum = math.sin(2.0 * math.pi * (52.0 - 4.0 * tt) * tt) * 0.18
            thunder_val = (thunder_lp2 * 1.8 + sub_hum) * th_env * 0.45

        env = envelope(t, duration, 0.3, 0.8)
        samples[i] = (samples[i] + rain_val * swell + thunder_val) * env

    write_wav(filepath, samples)


def generate_sfx_ambiente_calido(filepath):
    """
    sfx-ambiente-calido.wav (14.0s, for 5.0s - 19.0s):
    Warm stable & sunny pasture ambiance: soft low/mid breeze + natural country bird chirps
    with harmonic sinusoidal modulations between 2.2 kHz and 3.8 kHz spaced naturally,
    fade-in 0.8s, fade-out 0.8s.
    """
    random.seed(202)
    duration = 14.0
    n_samples = int(duration * SAMPLE_RATE)
    samples = [0.0] * n_samples

    # 1. Synthesize soft warm breeze + pasture rustle
    lp1 = 0.0
    lp2 = 0.0
    rustle_lp = 0.0
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        white = random.uniform(-1.0, 1.0)
        lp1 += 0.015 * (white - lp1)
        lp2 += 0.008 * (lp1 - lp2)
        rustle_lp += 0.09 * (white - rustle_lp)
        # Warm slow modulation of breeze
        breeze_mod = 0.65 + 0.35 * math.sin(2.0 * math.pi * 0.18 * t + 0.5)
        warm_pad = (
            0.018 * math.sin(2.0 * math.pi * 146.83 * t)  # D3 warm acoustic resonance
            + 0.012 * math.sin(2.0 * math.pi * 220.00 * t)  # A3
            + 0.008 * math.sin(2.0 * math.pi * 293.66 * t)  # D4
        )
        samples[i] = (lp2 * 0.42 + (rustle_lp - lp1) * 0.045) * breeze_mod + warm_pad

    # 2. Add natural country bird songs (2.2 kHz - 3.8 kHz with harmonic modulations)
    # Schedule bird phrases at natural intervals
    bird_events = [
        # (start_time, base_freq, f_end, dur, fm_rate, fm_depth, amp)
        (0.95, 2550, 3150, 0.14, 28.0, 180.0, 0.09),
        (1.14, 3100, 2700, 0.18, 22.0, 140.0, 0.10),
        (1.36, 2850, 3450, 0.22, 32.0, 210.0, 0.085),
        (2.80, 3300, 2450, 0.16, 18.0, 120.0, 0.08),
        (3.02, 3250, 2400, 0.19, 18.0, 120.0, 0.075),
        (4.40, 2350, 2950, 0.15, 35.0, 240.0, 0.09),
        (4.60, 2900, 3600, 0.13, 40.0, 220.0, 0.095),
        (4.78, 3500, 2650, 0.24, 24.0, 160.0, 0.08),
        (6.50, 2600, 3200, 0.17, 30.0, 190.0, 0.09),
        (6.72, 2750, 3350, 0.17, 30.0, 190.0, 0.085),
        (6.95, 3300, 2800, 0.25, 16.0, 110.0, 0.075),
        (8.60, 3650, 2900, 0.14, 42.0, 250.0, 0.08),
        (8.78, 3450, 2750, 0.16, 38.0, 230.0, 0.085),
        (9.00, 2800, 3350, 0.21, 20.0, 140.0, 0.08),
        (10.80, 2400, 3100, 0.16, 26.0, 175.0, 0.09),
        (11.02, 3050, 3700, 0.15, 32.0, 200.0, 0.085),
        (11.22, 3550, 2600, 0.23, 22.0, 150.0, 0.075),
        (12.55, 2900, 3400, 0.18, 28.0, 160.0, 0.08),
        (12.78, 3300, 2550, 0.22, 20.0, 130.0, 0.07),
    ]

    for st, f0, f1, dur, fm_rate, fm_depth, amp in bird_events:
        start_idx = int(st * SAMPLE_RATE)
        length = int(dur * SAMPLE_RATE)
        phase = 0.0
        for k in range(length):
            idx = start_idx + k
            if idx >= n_samples:
                break
            dt = k / SAMPLE_RATE
            u = k / length
            # Smooth pitch trajectory + syrinx FM trill
            f_curve = f0 + (f1 - f0) * (0.5 - 0.5 * math.cos(math.pi * u))
            f_inst = f_curve + fm_depth * math.sin(2.0 * math.pi * fm_rate * dt)
            phase += 2.0 * math.pi * f_inst / SAMPLE_RATE
            # Smooth attack & decay
            chirp_env = math.sin(math.pi * u) ** 1.4
            # Fundamental + soft 2nd harmonic
            sig = (math.sin(phase) + 0.22 * math.sin(2.0 * phase)) * amp * chirp_env
            samples[idx] += sig
            # Soft country echo (110ms and 230ms later)
            echo1 = idx + int(0.11 * SAMPLE_RATE)
            if echo1 < n_samples:
                samples[echo1] += sig * 0.28
            echo2 = idx + int(0.23 * SAMPLE_RATE)
            if echo2 < n_samples:
                samples[echo2] += sig * 0.12

    # Apply global fade-in (0.8s) and fade-out (0.8s)
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        samples[i] *= envelope(t, duration, 0.8, 0.8)

    write_wav(filepath, samples)


def generate_sfx_relincho_epico(filepath):
    """
    sfx-relincho-epico.wav (2.5s, for 19.0s - 21.5s):
    Epic horse whinny at sunrise:
    Rich harmonic synthesis with undulating/descending fundamental:
      950 Hz -> 1250 Hz -> 620 Hz -> 420 Hz,
    even and odd harmonics, natural 6.5 Hz vibrato (+horse laryngeal flutter),
    initial breath/snort burst, and open-valley reverb tail.
    """
    random.seed(303)
    duration = 2.5
    n_samples = int(duration * SAMPLE_RATE)
    dry = [0.0] * n_samples

    phase = 0.0
    flutter_phase = 0.0
    breath_lp = 0.0
    formant_lp = 0.0

    for i in range(n_samples):
        t = i / SAMPLE_RATE

        # Pitch contour active during 0.05s -> 1.85s (with tail reverb up to 2.5s)
        if t < 1.88:
            # Piecewise smooth pitch curve: 950 -> 1250 -> 620 -> 420 Hz
            if t < 0.32:
                u = t / 0.32
                s = 0.5 - 0.5 * math.cos(math.pi * u)
                f_base = 950.0 + (1250.0 - 950.0) * s
            elif t < 1.15:
                u = (t - 0.32) / (1.15 - 0.32)
                s = 0.5 - 0.5 * math.cos(math.pi * u)
                f_base = 1250.0 + (620.0 - 1250.0) * s
            else:
                u = (t - 1.15) / (1.88 - 1.15)
                s = 0.5 - 0.5 * math.cos(math.pi * u)
                f_base = 620.0 + (420.0 - 620.0) * s

            # Natural 6.5 Hz vibrato + subtle 24 Hz equine vocal fold flutter
            vib = 28.0 * math.sin(2.0 * math.pi * 6.5 * t)
            flutter = 14.0 * math.sin(2.0 * math.pi * 23.5 * t) * min(1.0, t / 0.4)
            f_inst = f_base + vib + flutter

            phase += 2.0 * math.pi * f_inst / SAMPLE_RATE
            flutter_phase += 2.0 * math.pi * 6.5 / SAMPLE_RATE

            # Amplitude envelope of vocalization with slight rhythmic pulses in the tail
            if t < 0.08:
                v_env = (t / 0.08) ** 0.8
            elif t < 1.35:
                v_env = 1.0 - 0.15 * ((t - 0.08) / 1.27)
                # Subtle equine tremolando
                v_env *= 0.88 + 0.12 * math.sin(2.0 * math.pi * 7.2 * t)
            else:
                rem = (1.88 - t) / (1.88 - 1.35)
                v_env = (rem ** 1.6) * (0.75 + 0.25 * math.sin(2.0 * math.pi * 8.5 * t))

            # Rich even & odd harmonics shaped by vocal tract formants (~1100 Hz, ~2400 Hz)
            harm_sum = 0.0
            harm_weights = [1.0, 0.78, 0.62, 0.42, 0.28, 0.18, 0.11, 0.06]
            for h_idx, w in enumerate(harm_weights, start=1):
                hf = f_inst * h_idx
                if hf < 16000.0:
                    # Formant boost around 1150 Hz and 2500 Hz
                    f_boost = (
                        1.0
                        + 0.9 * math.exp(-((hf - 1150.0) ** 2) / (450.0 ** 2))
                        + 0.7 * math.exp(-((hf - 2500.0) ** 2) / (650.0 ** 2))
                    )
                    harm_sum += w * f_boost * math.sin(h_idx * phase + 0.3 * h_idx)

            vocal = harm_sum * 0.14 * v_env
        else:
            vocal = 0.0

        # Initial nasal breath / air burst (0.0s - 0.35s) + breathiness throughout whinny
        white = random.uniform(-1.0, 1.0)
        breath_lp += 0.16 * (white - breath_lp)
        formant_lp += 0.04 * (breath_lp - formant_lp)
        band_air = breath_lp - formant_lp

        air_env = 0.0
        if t < 0.28:
            air_env = math.sin(math.pi * (t / 0.28)) * 0.28
        elif t < 1.75:
            air_env = 0.07 * max(0.0, 1.0 - (t - 0.28) / 1.47)

        dry[i] = vocal + band_air * air_env

    # Open-valley multi-tap reverb + Schroeder-style diffuse tail
    samples = dry[:]
    taps = [
        (0.065, 0.36),
        (0.135, 0.28),
        (0.220, 0.22),
        (0.340, 0.16),
        (0.480, 0.11),
        (0.640, 0.07),
    ]
    for delay_s, gain in taps:
        d_idx = int(delay_s * SAMPLE_RATE)
        lp_state = 0.0
        for i in range(d_idx, n_samples):
            lp_state += 0.25 * (dry[i - d_idx] - lp_state)
            samples[i] += lp_state * gain

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        samples[i] *= envelope(t, duration, 0.03, 0.35)

    write_wav(filepath, samples)


def generate_sfx_trocha_ovacion(filepath):
    """
    sfx-trocha-ovacion.wav (8.5s, for 25.0s - 33.5s):
    a) Rapid Colombian Trocha hoofbeats on a wooden sounding board (tabla de resonancia):
       Quadruple fast rhythm (~8.5 beats/sec, every ~0.1176s), hollow wood resonance
       (180 Hz, 420 Hz, 1100 Hz with short 45ms percussive decay and 1-2-3-4 accent variations).
    b) Vibrant stadium ovation:
       Crowd applause & cheering waves that swell in 0.0s-2.0s, 5.3s-6.0s, and erupt in 7.5s-8.5s,
       with a clean fade-out at the end.
    """
    random.seed(404)
    duration = 8.5
    n_samples = int(duration * SAMPLE_RATE)
    samples = [0.0] * n_samples

    # Part A: Taconeo rápido de trocha colombiana sobre tabla de madera (~8.5 golpes/s)
    step_interval = 1.0 / 8.5  # ~0.11765s
    accents = [1.0, 0.78, 0.90, 0.74]  # Quadruple 1-2-3-4 trocha cadence
    beat_idx = 0
    t_hit = 0.04
    while t_hit < duration - 0.15:
        jitter = random.uniform(-0.003, 0.003)
        hit_time = t_hit + jitter
        start_sample = int(hit_time * SAMPLE_RATE)
        accent = accents[beat_idx % 4] * random.uniform(0.93, 1.07)
        # Slight resonant pitch variation per hoof (front/hind hooves on wood)
        detune = [1.0, 1.04, 0.97, 1.02][beat_idx % 4]

        hit_len = int(0.085 * SAMPLE_RATE)
        noise_lp = 0.0
        for k in range(hit_len):
            idx = start_sample + k
            if idx >= n_samples:
                break
            dt = k / SAMPLE_RATE
            # Percussive 45ms decay constant (exp(-dt / 0.018) ~ -45ms effective tail)
            env_wood = math.exp(-dt / 0.016)
            env_click = math.exp(-dt / 0.0035)

            # Hollow wood board modes: 180 Hz (chest/board thump), 420 Hz (hollow box), 1100 Hz (shoe strike)
            m1 = math.sin(2.0 * math.pi * (180.0 * detune) * dt) * math.exp(-dt / 0.022)
            m2 = math.sin(2.0 * math.pi * (420.0 * detune) * dt) * env_wood * 0.85
            m3 = math.sin(2.0 * math.pi * (1100.0 * detune) * dt) * math.exp(-dt / 0.009) * 0.50

            # Sharp wood/iron transient click
            w = random.uniform(-1.0, 1.0)
            noise_lp += 0.35 * (w - noise_lp)
            click = noise_lp * env_click * 0.65

            val = (m1 + m2 + m3 + click) * 0.24 * accent
            samples[idx] += val

        t_hit += step_interval
        beat_idx += 1

    # Part B: Vibrant stadium ovation (applause + crowd roar swells)
    # Swells at 0.0s-2.0s, 5.3s-6.0s, and eruption at 7.5s-8.5s
    roar_lp1 = 0.0
    roar_lp2 = 0.0
    clap_bp1 = 0.0
    clap_bp2 = 0.0

    # Pre-place dense individual handclaps in the buffer for realistic applause texture
    n_claps = 1100
    for _ in range(n_claps):
        ct = random.uniform(0.0, duration - 0.02)
        c_idx = int(ct * SAMPLE_RATE)
        c_len = int(random.uniform(0.006, 0.014) * SAMPLE_RATE)
        c_amp = random.uniform(0.015, 0.045)
        bp_state = 0.0
        for k in range(c_len):
            if c_idx + k >= n_samples:
                break
            w = random.uniform(-1.0, 1.0)
            bp_state += 0.28 * (w - bp_state)
            env_c = math.sin(math.pi * k / c_len) * math.exp(-k / (0.4 * c_len))
            samples[c_idx + k] += (w - bp_state) * c_amp * env_c

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Crowd swell curve:
        # Base bed + swell 1 (0.0 - 2.0s) + swell 2 (5.3 - 6.0s) + grand eruption (7.5 - 8.5s)
        swell1 = 0.60 * math.exp(-((t - 0.85) ** 2) / 0.85) if t < 2.6 else 0.0
        swell2 = 0.65 * math.exp(-((t - 5.65) ** 2) / 0.22)
        swell3 = 0.85 / (1.0 + math.exp(-8.0 * (t - 7.35)))
        crowd_env = min(1.0, 0.22 + swell1 + swell2 + swell3)

        white = random.uniform(-1.0, 1.0)
        # Crowd vocal formant roar (~500 Hz - 1800 Hz)
        roar_lp1 += 0.08 * (white - roar_lp1)
        roar_lp2 += 0.02 * (roar_lp1 - roar_lp2)
        roar = (roar_lp1 - roar_lp2) * 0.42

        # Dense applause shimmer (~1.2 kHz - 4.5 kHz)
        clap_bp1 += 0.35 * (white - clap_bp1)
        clap_bp2 += 0.10 * (clap_bp1 - clap_bp2)
        shimmer = (clap_bp1 - clap_bp2) * 0.26

        samples[i] = samples[i] * (0.85 + 0.25 * crowd_env) + (roar + shimmer) * crowd_env

        # Smooth fade-in (0.2s) and clean fade-out at the end (8.0s - 8.5s)
        samples[i] *= envelope(t, duration, 0.2, 0.5)

    write_wav(filepath, samples)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    generate_sfx_lluvia(os.path.join(root, "sfx-lluvia.wav"))
    generate_sfx_ambiente_calido(os.path.join(root, "sfx-ambiente-calido.wav"))
    generate_sfx_relincho_epico(os.path.join(root, "sfx-relincho-epico.wav"))
    generate_sfx_trocha_ovacion(os.path.join(root, "sfx-trocha-ovacion.wav"))
    print("All 4 SFX WAV files successfully synthesized.")


if __name__ == "__main__":
    main()
