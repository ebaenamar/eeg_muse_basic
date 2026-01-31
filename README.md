# Muse EEG - Complete Guide

Connect, stream, and visualize EEG data from your **Muse** headband using Python and LSL (Lab Streaming Layer).

## 📋 Prerequisites

### Hardware
- **Muse headband** (Muse 2, Muse S, or original Muse)
- **Mac** with Bluetooth (tested on macOS)
- The headband must be **charged and turned on**

### Software
- **Python 3.10+** (recommended 3.12)
- **Bluetooth enabled** on your Mac
- **Git** (to clone the repository)

---

## 🚀 Step-by-Step Installation

### 1. Clone the repository

```bash
git clone https://github.com/ebaenamar/eeg_muse_basic.git
cd eeg_muse_basic
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (macOS only) If you have Tkinter issues

If `muselsl view` gives a Tkinter error, use the alternative visualizer included (`view_eeg.py`).

---

## 🎯 Basic Usage

### Step 1: Enable Bluetooth and turn on your Muse

1. Go to **System Preferences → Bluetooth → Turn On**
2. Turn on your Muse headband (hold the button until it blinks)
3. Place it on your head for better detection

### Step 2: Find your Muse device

```bash
source venv/bin/activate
muselsl list
```

Expected output:
```
Searching for Muses, this may take up to 10 seconds...
Found device Muse-XXXX, MAC Address XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

**Save the MAC Address**, you'll need it to connect.

### Step 3: Start EEG streaming

In a terminal:

```bash
source venv/bin/activate
muselsl stream --address <YOUR_MAC_ADDRESS>
```

Example:
```bash
muselsl stream --address 4BEE1E10-85F7-FB8C-49E2-17174042399F
```

Expected output:
```
Connecting to Muse: XXXXXXXX...
Connected.
Streaming EEG...
```

**Keep this terminal open** while working with the data.

### Step 4: Visualize EEG in real-time

Open **another terminal**:

```bash
source venv/bin/activate
python view_eeg.py
```

You'll see a window with 4 graphs (one for each EEG channel):
- **TP9** - Left temporal
- **AF7** - Left frontal
- **AF8** - Right frontal
- **TP10** - Right temporal

---

## 📊 Working with the EEG Stream

### Option A: Record data to CSV

```bash
muselsl record --duration 60
```

This records 60 seconds of EEG data to a CSV file.

### Option B: Access the stream from Python

```python
from pylsl import StreamInlet, resolve_byprop
import numpy as np

# Find EEG stream
print("Looking for EEG stream...")
streams = resolve_byprop('type', 'EEG', timeout=10)

if not streams:
    print("No stream found. Is 'muselsl stream' running?")
    exit()

# Connect to stream
inlet = StreamInlet(streams[0])
info = inlet.info()

print(f"Connected to: {info.name()}")
print(f"Sample rate: {info.nominal_srate()} Hz")
print(f"Channels: {info.channel_count()}")

# Read data continuously
while True:
    sample, timestamp = inlet.pull_sample()
    print(f"[{timestamp:.3f}] {np.array(sample)}")
```

### Option C: Analyze frequency bands

```python
from pylsl import StreamInlet, resolve_byprop
import numpy as np
from scipy import signal

# Configuration
FS = 256  # Muse sample rate
WINDOW = 256  # 1 second of data

# EEG frequency bands
BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 50)
}

def get_band_power(data, fs, band):
    """Calculate power in a frequency band."""
    low, high = band
    # Butterworth filter
    b, a = signal.butter(4, [low/(fs/2), high/(fs/2)], btype='band')
    filtered = signal.filtfilt(b, a, data)
    return np.mean(filtered ** 2)

# Connect to stream
streams = resolve_byprop('type', 'EEG', timeout=10)
inlet = StreamInlet(streams[0])

buffer = []

print("Analyzing frequency bands...")
print("-" * 50)

while True:
    sample, _ = inlet.pull_sample()
    buffer.append(sample[0])  # TP9 channel
    
    if len(buffer) >= WINDOW:
        data = np.array(buffer[-WINDOW:])
        
        print("\nPower by band (TP9):")
        for name, band in BANDS.items():
            power = get_band_power(data, FS, band)
            bar = "█" * int(power / 10)
            print(f"  {name:6s}: {power:8.2f} {bar}")
        
        buffer = buffer[-WINDOW//2:]  # 50% overlap
```

---

## 🔧 Useful muselsl Commands

| Command | Description |
|---------|-------------|
| `muselsl list` | Find nearby Muse devices |
| `muselsl stream -a <MAC>` | Start EEG streaming |
| `muselsl stream -a <MAC> -p` | Include PPG data (heart rate) |
| `muselsl stream -a <MAC> --acc` | Include accelerometer |
| `muselsl stream -a <MAC> --gyro` | Include gyroscope |
| `muselsl record -d 60` | Record 60 seconds to CSV |
| `muselsl view` | Visualize (requires Tkinter) |

---

## 🐛 Troubleshooting

### "Bluetooth device is turned off"
- Enable Bluetooth in System Preferences → Bluetooth

### "No Muse devices found"
- Make sure the headband is on (light blinking)
- Move it closer to the computer
- Restart the headband (turn off/on)
- Check it's not connected to another app (Mind Monitor, Muse app)

### "No EEG stream found"
- First run `muselsl stream` in another terminal
- Wait until it says "Streaming EEG..."

### Tkinter error with `muselsl view`
- Use `python view_eeg.py` instead (included in this repo)

### Noisy or flat signal
- Adjust the headband properly on your head
- Slightly moisten the sensors
- Make sure the ear sensors have good contact

### Frequent disconnections
- Fully charge the headband
- Reduce distance to computer
- Close other apps using Bluetooth

---

## 📁 Project Structure

```
eeg_muse_basic/
├── README.md           # This documentation
├── requirements.txt    # Python dependencies
├── view_eeg.py         # EEG visualizer (no Tkinter)
└── examples/           # Example scripts
    ├── record_eeg.py   # Record data to CSV
    ├── analyze_bands.py # Frequency band analysis
    └── stream_basic.py # Basic reading example
```

---

## 📚 Additional Resources

- [muselsl GitHub](https://github.com/alexandrebarachant/muse-lsl)
- [pylsl Documentation](https://labstreaminglayer.readthedocs.io/)
- [Muse Developer Resources](https://choosemuse.com/development/)

---

## 📄 License

MIT License - Use this code however you want.
