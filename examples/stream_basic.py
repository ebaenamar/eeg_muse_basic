#!/usr/bin/env python3
"""
Ejemplo básico: Leer datos EEG del stream LSL

Requisitos:
- muselsl stream debe estar corriendo en otra terminal

Uso:
    python examples/stream_basic.py
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np

CHANNELS = ['TP9', 'AF7', 'AF8', 'TP10']

def main():
    print("=" * 50)
    print("EJEMPLO BÁSICO - Lectura de Stream EEG")
    print("=" * 50)
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
    print(f"   Frecuencia de muestreo: {info.nominal_srate()} Hz")
    print(f"   Número de canales: {info.channel_count()}")
    print(f"   Canales: {', '.join(CHANNELS)}")
    print("\n" + "-" * 50)
    print("Leyendo datos (Ctrl+C para salir)...")
    print("-" * 50 + "\n")
    
    sample_count = 0
    
    try:
        while True:
            sample, timestamp = inlet.pull_sample()
            sample_count += 1
            
            if sample_count % 256 == 0:  # Mostrar cada segundo aprox
                data = np.array(sample)
                print(f"[{timestamp:.3f}s] ", end="")
                for i, ch in enumerate(CHANNELS):
                    print(f"{ch}: {data[i]:7.1f}μV  ", end="")
                print()
                
    except KeyboardInterrupt:
        print(f"\n\nDetenido. Total de muestras leídas: {sample_count}")

if __name__ == "__main__":
    main()
