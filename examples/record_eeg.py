#!/usr/bin/env python3
"""
Record EEG data to a CSV file

Requirements:
- muselsl stream must be running in another terminal

Usage:
    python examples/record_eeg.py                    # Records 60 seconds
    python examples/record_eeg.py --duration 120    # Records 120 seconds
    python examples/record_eeg.py --output my_session.csv
"""

import argparse
import csv
import time
from datetime import datetime
from pylsl import StreamInlet, resolve_byprop
import numpy as np

CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

def main():
    parser = argparse.ArgumentParser(description='Record EEG data to CSV')
    parser.add_argument('--duration', '-d', type=int, default=60,
                        help='Recording duration in seconds (default: 60)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output filename (default: eeg_YYYYMMDD_HHMMSS.csv)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("EEG RECORDER - Save data to CSV")
    print("=" * 50)
    print(f"\nConfigured duration: {args.duration} seconds")
    print("\nLooking for EEG stream...")
    
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("\n❌ ERROR: No EEG stream found.")
        print("   Make sure to run first:")
        print("   muselsl stream --address <YOUR_MAC_ADDRESS>")
        return
    
    inlet = StreamInlet(streams[0])
    info = inlet.info()
    fs = int(info.nominal_srate())
    
    print(f"\n✅ Connected to: {info.name()}")
    print(f"   Sample rate: {fs} Hz")
    
    # Output filename
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eeg_{timestamp}.csv"
    
    print(f"\n📁 Output file: {filename}")
    print("\n" + "-" * 50)
    print("Recording... (Ctrl+C to stop early)")
    print("-" * 50)
    
    samples_collected = 0
    total_samples = args.duration * fs
    start_time = time.time()
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp'] + CHANNELS)
            
            while samples_collected < total_samples:
                sample, timestamp = inlet.pull_sample()
                writer.writerow([timestamp] + list(sample[:4]))
                samples_collected += 1
                
                # Show progress every second
                if samples_collected % fs == 0:
                    elapsed = time.time() - start_time
                    remaining = args.duration - elapsed
                    progress = (samples_collected / total_samples) * 100
                    print(f"\r  Progress: {progress:5.1f}% | "
                          f"Time remaining: {remaining:5.1f}s | "
                          f"Samples: {samples_collected}", end="")
        
        print(f"\n\n✅ Recording completed!")
        print(f"   File: {filename}")
        print(f"   Samples: {samples_collected}")
        print(f"   Actual duration: {time.time() - start_time:.1f}s")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Recording stopped by user")
        print(f"   File: {filename}")
        print(f"   Samples recorded: {samples_collected}")

if __name__ == "__main__":
    main()
