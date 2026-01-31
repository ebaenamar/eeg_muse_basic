#!/usr/bin/env python3
"""
Real-time EEG frequency band analysis

Calculates power in the following bands:
- Delta (0.5-4 Hz): Deep sleep
- Theta (4-8 Hz): Relaxation, meditation
- Alpha (8-13 Hz): Calm, eyes closed
- Beta (13-30 Hz): Focus, alertness
- Gamma (30-50 Hz): Cognitive processing

Requirements:
- muselsl stream must be running in another terminal
- scipy installed (included in requirements.txt)

Usage:
    python examples/analyze_bands.py
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
from scipy import signal

# Configuration
FS = 256  # Muse sample rate
WINDOW = 256  # 1 second of data
CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

# EEG frequency bands
BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 50)
}

BAND_DESCRIPTIONS = {
    'Delta': 'Deep sleep',
    'Theta': 'Relaxation/Meditation',
    'Alpha': 'Calm (eyes closed)',
    'Beta': 'Focus/Alertness',
    'Gamma': 'Cognitive processing'
}

def get_band_power(data, fs, band):
    """Calculate power in a frequency band using Butterworth filter."""
    low, high = band
    nyq = fs / 2
    
    # Ensure frequencies are in valid range
    low = max(low, 0.1)
    high = min(high, nyq - 0.1)
    
    # Butterworth filter
    b, a = signal.butter(4, [low/nyq, high/nyq], btype='band')
    filtered = signal.filtfilt(b, a, data)
    
    # Power = mean of squared signal
    return np.mean(filtered ** 2)

def print_bar(value, max_val=500, width=30):
    """Generate a visual progress bar."""
    filled = int((value / max_val) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)

def main():
    print("=" * 60)
    print("EEG FREQUENCY BAND ANALYZER")
    print("=" * 60)
    print("\nLooking for EEG stream...")
    
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("\n❌ ERROR: No EEG stream found.")
        print("   Make sure to run first:")
        print("   muselsl stream --address <YOUR_MAC_ADDRESS>")
        return
    
    inlet = StreamInlet(streams[0])
    info = inlet.info()
    
    print(f"\n✅ Connected to: {info.name()}")
    print(f"   Sample rate: {info.nominal_srate()} Hz")
    
    print("\n" + "-" * 60)
    print("EEG frequency bands:")
    for name, (low, high) in BANDS.items():
        print(f"  {name:6s} ({low:4.1f}-{high:4.1f} Hz): {BAND_DESCRIPTIONS[name]}")
    print("-" * 60)
    print("\nAnalyzing channel AF7 (left frontal)...")
    print("Ctrl+C to exit\n")
    
    buffer = []
    
    try:
        while True:
            sample, _ = inlet.pull_sample()
            buffer.append(sample[1])  # AF7 channel (index 1)
            
            if len(buffer) >= WINDOW:
                data = np.array(buffer[-WINDOW:])
                
                # Clear screen and show analysis
                print("\033[H\033[J", end="")  # Clear terminal
                print("=" * 60)
                print("EEG BAND ANALYSIS - Channel AF7 (Left Frontal)")
                print("=" * 60 + "\n")
                
                total_power = 0
                powers = {}
                
                for name, band in BANDS.items():
                    power = get_band_power(data, FS, band)
                    powers[name] = power
                    total_power += power
                
                # Show relative power
                for name in BANDS.keys():
                    power = powers[name]
                    relative = (power / total_power) * 100 if total_power > 0 else 0
                    bar = print_bar(relative, max_val=50, width=25)
                    print(f"  {name:6s}: {bar} {relative:5.1f}%")
                
                print("\n" + "-" * 60)
                print(f"  Total power: {total_power:.1f}")
                print("-" * 60)
                print("\n💡 Interpretation:")
                
                # Find dominant band
                dominant = max(powers, key=powers.get)
                print(f"   Dominant band: {dominant} - {BAND_DESCRIPTIONS[dominant]}")
                
                # Alpha/Beta ratio (relaxation indicator)
                if powers['Beta'] > 0:
                    alpha_beta = powers['Alpha'] / powers['Beta']
                    if alpha_beta > 1.5:
                        state = "Relaxed 😌"
                    elif alpha_beta < 0.5:
                        state = "Focused 🧠"
                    else:
                        state = "Neutral 😐"
                    print(f"   Alpha/Beta ratio: {alpha_beta:.2f} → {state}")
                
                print("\n[Ctrl+C to exit]")
                
                # Keep 50% overlap
                buffer = buffer[-WINDOW//2:]
                
    except KeyboardInterrupt:
        print("\n\nAnalysis stopped.")

if __name__ == "__main__":
    main()
