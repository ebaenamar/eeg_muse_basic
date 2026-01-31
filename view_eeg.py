#!/usr/bin/env python3
"""
Visualizador EEG para Muse usando LSL
No requiere Tkinter - usa matplotlib con backend macosx
"""

import numpy as np
import matplotlib
matplotlib.use('macosx')  # Backend nativo de macOS, no requiere Tk
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_byprop

# Configuración
BUFFER_LENGTH = 5  # segundos de datos a mostrar
EPOCH_LENGTH = 1   # segundos por época
CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']  # Canales del Muse

def main():
    print("Buscando stream EEG...")
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("ERROR: No se encontró stream EEG.")
        print("Asegúrate de que 'muselsl stream' esté corriendo en otra terminal.")
        return
    
    print(f"Stream encontrado: {streams[0].name()}")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    
    # Info del stream
    info = inlet.info()
    fs = int(info.nominal_srate())
    n_samples = int(BUFFER_LENGTH * fs)
    n_channels = info.channel_count()
    
    print(f"Frecuencia de muestreo: {fs} Hz")
    print(f"Canales: {n_channels}")
    
    # Buffer circular para datos
    eeg_buffer = np.zeros((n_samples, n_channels))
    
    # Configurar figura
    plt.ion()
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('Muse EEG - Tiempo Real', fontsize=14)
    
    lines = []
    time_axis = np.linspace(-BUFFER_LENGTH, 0, n_samples)
    
    for i, ax in enumerate(axes):
        line, = ax.plot(time_axis, eeg_buffer[:, i], 'b-', linewidth=0.5)
        lines.append(line)
        ax.set_ylabel(CHANNELS[i] if i < len(CHANNELS) else f'Ch{i+1}')
        ax.set_ylim(-200, 200)  # microvolts típicos
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Tiempo (s)')
    plt.tight_layout()
    
    print("Visualizando... (Ctrl+C para salir)")
    
    try:
        while plt.fignum_exists(fig.number):
            # Obtener datos del stream
            chunk, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=12)
            
            if chunk:
                chunk = np.array(chunk)
                # Actualizar buffer circular
                eeg_buffer = np.roll(eeg_buffer, -len(chunk), axis=0)
                eeg_buffer[-len(chunk):, :] = chunk
                
                # Actualizar gráficas
                for i, line in enumerate(lines):
                    line.set_ydata(eeg_buffer[:, i])
            
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        plt.close()

if __name__ == "__main__":
    main()
