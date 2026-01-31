#!/usr/bin/env python3
"""
Análisis de bandas de frecuencia EEG en tiempo real

Calcula la potencia en las bandas:
- Delta (0.5-4 Hz): Sueño profundo
- Theta (4-8 Hz): Relajación, meditación
- Alpha (8-13 Hz): Calma, ojos cerrados
- Beta (13-30 Hz): Concentración, alerta
- Gamma (30-50 Hz): Procesamiento cognitivo

Requisitos:
- muselsl stream debe estar corriendo en otra terminal
- scipy instalado (incluido en requirements.txt)

Uso:
    python examples/analyze_bands.py
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
from scipy import signal

# Configuración
FS = 256  # Frecuencia de muestreo del Muse
WINDOW = 256  # 1 segundo de datos
CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

# Bandas de frecuencia EEG
BANDS = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 50)
}

BAND_DESCRIPTIONS = {
    'Delta': 'Sueño profundo',
    'Theta': 'Relajación/Meditación',
    'Alpha': 'Calma (ojos cerrados)',
    'Beta': 'Concentración/Alerta',
    'Gamma': 'Procesamiento cognitivo'
}

def get_band_power(data, fs, band):
    """Calcula la potencia en una banda de frecuencia usando filtro Butterworth."""
    low, high = band
    nyq = fs / 2
    
    # Asegurar que las frecuencias estén en rango válido
    low = max(low, 0.1)
    high = min(high, nyq - 0.1)
    
    # Filtro butterworth
    b, a = signal.butter(4, [low/nyq, high/nyq], btype='band')
    filtered = signal.filtfilt(b, a, data)
    
    # Potencia = media del cuadrado de la señal
    return np.mean(filtered ** 2)

def print_bar(value, max_val=500, width=30):
    """Genera una barra de progreso visual."""
    filled = int((value / max_val) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)

def main():
    print("=" * 60)
    print("ANALIZADOR DE BANDAS DE FRECUENCIA EEG")
    print("=" * 60)
    print("\nBuscando stream EEG...")
    
    streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not streams:
        print("\n❌ ERROR: No se encontró stream EEG.")
        print("   Asegúrate de ejecutar primero:")
        print("   muselsl stream --address <TU_MAC_ADDRESS>")
        return
    
    inlet = StreamInlet(streams[0])
    info = inlet.info()
    
    print(f"\n✅ Conectado a: {info.name()}")
    print(f"   Frecuencia: {info.nominal_srate()} Hz")
    
    print("\n" + "-" * 60)
    print("Bandas de frecuencia EEG:")
    for name, (low, high) in BANDS.items():
        print(f"  {name:6s} ({low:4.1f}-{high:4.1f} Hz): {BAND_DESCRIPTIONS[name]}")
    print("-" * 60)
    print("\nAnalizando canal AF7 (frontal izquierdo)...")
    print("Ctrl+C para salir\n")
    
    buffer = []
    
    try:
        while True:
            sample, _ = inlet.pull_sample()
            buffer.append(sample[1])  # Canal AF7 (índice 1)
            
            if len(buffer) >= WINDOW:
                data = np.array(buffer[-WINDOW:])
                
                # Limpiar pantalla y mostrar análisis
                print("\033[H\033[J", end="")  # Limpiar terminal
                print("=" * 60)
                print("ANÁLISIS DE BANDAS EEG - Canal AF7 (Frontal Izquierdo)")
                print("=" * 60 + "\n")
                
                total_power = 0
                powers = {}
                
                for name, band in BANDS.items():
                    power = get_band_power(data, FS, band)
                    powers[name] = power
                    total_power += power
                
                # Mostrar potencia relativa
                for name in BANDS.keys():
                    power = powers[name]
                    relative = (power / total_power) * 100 if total_power > 0 else 0
                    bar = print_bar(relative, max_val=50, width=25)
                    print(f"  {name:6s}: {bar} {relative:5.1f}%")
                
                print("\n" + "-" * 60)
                print(f"  Potencia total: {total_power:.1f}")
                print("-" * 60)
                print("\n💡 Interpretación:")
                
                # Encontrar banda dominante
                dominant = max(powers, key=powers.get)
                print(f"   Banda dominante: {dominant} - {BAND_DESCRIPTIONS[dominant]}")
                
                # Ratio Alpha/Beta (indicador de relajación)
                if powers['Beta'] > 0:
                    alpha_beta = powers['Alpha'] / powers['Beta']
                    if alpha_beta > 1.5:
                        state = "Relajado 😌"
                    elif alpha_beta < 0.5:
                        state = "Concentrado 🧠"
                    else:
                        state = "Neutral 😐"
                    print(f"   Ratio Alpha/Beta: {alpha_beta:.2f} → {state}")
                
                print("\n[Ctrl+C para salir]")
                
                # Mantener overlap del 50%
                buffer = buffer[-WINDOW//2:]
                
    except KeyboardInterrupt:
        print("\n\nAnálisis detenido.")

if __name__ == "__main__":
    main()
