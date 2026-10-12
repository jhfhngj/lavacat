import numpy as np
import sounddevice as sd
import sys

if "--help" in sys.argv:
    print("""
lavabird terminal synthesizer
usage:
lavabird

basic melodies to get you started:
ajsh
frfr
AbCd
?!?!
Lavabird""")

# 1. Global Setup
sample_rate = 44100

def generate_sawtooth(frequency, duration):
    """Generates a raw, buzzy sawtooth wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # The 'mod 1' operation creates a repeating ramp wave
    wave = 2.0 * (t * frequency % 1.0) - 1.0
    return wave

def apply_adsr(wave, attack, decay, sustain_level, release):
    """Shapes the volume over time so it sounds like an instrument."""
    total_samples = len(wave)
    
    # Calculate sample counts for each stage
    a_samples = int(attack * sample_rate)
    d_samples = int(decay * sample_rate)
    r_samples = int(release * sample_rate)
    s_samples = max(0, total_samples - (a_samples + d_samples + r_samples))
    
    # Create the volume curves
    attack_env = np.linspace(0.0, 1.0, a_samples)
    decay_env = np.linspace(1.0, sustain_level, d_samples)
    sustain_env = np.full(s_samples, sustain_level)
    release_env = np.linspace(sustain_level, 0.0, r_samples)
    
    # Glue the envelope together
    envelope = np.concatenate([attack_env, decay_env, sustain_env, release_env])
    
    # If the math is slightly off due to rounding, match the wave size
    if len(envelope) < total_samples:
        envelope = np.pad(envelope, (0, total_samples - len(envelope)), 'constant')
    else:
        envelope = envelope[:total_samples]
        
    return wave * envelope

# 2. Design the Synth Sound
note_frequency = 110.0  # Dropped it down 2 octaves to A2 for a fat bass sound
note_duration = 1.0     # 2 seconds long

while True:
    try:
        put = input("type anything ")
        if put == "": break;exit()
        sounds = []
        for inputt in put:
            sounds.append(((ord(inputt)*10)+920)/10)
        for sound in sounds:
            # Generate the raw buzzy sound
            raw_buzz = generate_sawtooth(sound, sound/200)

            # Apply ADSR envelope (Slow attack for a swell effect, long release)
            # Arguments: (wave, attack_sec, decay_sec, sustain_volume, release_sec)
            synth_sound = apply_adsr(raw_buzz, attack=0.3, decay=0.2, sustain_level=0.6, release=0.5)

            # Keep volume safe
            synth_sound = synth_sound * 0.3

            # 3. Play the Sound
            sd.play(synth_sound, sample_rate)
            sd.wait()
            sd.play(np.zeros(int(sample_rate * 0.05)), sample_rate)
            sd.wait()

    except:pass
