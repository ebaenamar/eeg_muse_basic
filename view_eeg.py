#!/usr/bin/env python3
"""
EEG Visualizer for Muse using LSL
Does not require Tkinter - uses matplotlib with macosx backend
"""

import numpy as np
import matplotlib
matplotlib.use('macosx')  # Native macOS backend, no Tk required
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_byprop

# Configuration
BUFFER_LENGTH = 5  # seconds of data to display
EPOCH_LENGTH = 1   # seconds per epoch
CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']  # Muse channels

def main():
    print("Looking for EEG stream...")
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("ERROR: No EEG stream found.")
        print("Make sure 'muselsl stream' is running in another terminal.")
        return
    
    print(f"Stream found: {streams[0].name()}")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    
    # Stream info
    info = inlet.info()
    fs = int(info.nominal_srate())
    n_samples = int(BUFFER_LENGTH * fs)
    n_channels = info.channel_count()
    
    print(f"Sample rate: {fs} Hz")
    print(f"Channels: {n_channels}")
    
    # Circular buffer for data
    eeg_buffer = np.zeros((n_samples, n_channels))
    
    # Configure figure
    plt.ion()
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('Muse EEG - Real Time', fontsize=14)
    
    lines = []
    time_axis = np.linspace(-BUFFER_LENGTH, 0, n_samples)
    
    for i, ax in enumerate(axes):
        line, = ax.plot(time_axis, eeg_buffer[:, i], 'b-', linewidth=0.5)
        lines.append(line)
        ax.set_ylabel(CHANNELS[i] if i < len(CHANNELS) else f'Ch{i+1}')
        ax.set_ylim(-200, 200)  # typical microvolts
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time (s)')
    plt.tight_layout()
    
    print("Visualizing... (Ctrl+C to exit)")
    
    try:
        while plt.fignum_exists(fig.number):
            # Get data from stream
            chunk, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=12)
            
            if chunk:
                chunk = np.array(chunk)
                # Update circular buffer
                eeg_buffer = np.roll(eeg_buffer, -len(chunk), axis=0)
                eeg_buffer[-len(chunk):, :] = chunk
                
                # Update graphs
                for i, line in enumerate(lines):
                    line.set_ydata(eeg_buffer[:, i])
            
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        plt.close()

if __name__ == "__main__":
    main()
