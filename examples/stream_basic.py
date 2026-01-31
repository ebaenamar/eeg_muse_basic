#!/usr/bin/env python3
"""
Basic example: Read EEG data from LSL stream

Requirements:
- muselsl stream must be running in another terminal

Usage:
    python examples/stream_basic.py
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np

CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

def main():
    print("=" * 50)
    print("BASIC EXAMPLE - EEG Stream Reading")
    print("=" * 50)
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
    print(f"   Number of channels: {info.channel_count()}")
    print(f"   Channels: {', '.join(CHANNELS)}")
    print("\n" + "-" * 50)
    print("Reading data (Ctrl+C to exit)...")
    print("-" * 50 + "\n")
    
    sample_count = 0
    
    try:
        while True:
            sample, timestamp = inlet.pull_sample()
            sample_count += 1
            
            if sample_count % 256 == 0:  # Show every second approx
                data = np.array(sample)
                print(f"[{timestamp:.3f}s] ", end="")
                for i, ch in enumerate(CHANNELS):
                    print(f"{ch}: {data[i]:7.1f}μV  ", end="")
                print()
                
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total samples read: {sample_count}")

if __name__ == "__main__":
    main()
